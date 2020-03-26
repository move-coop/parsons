"""
This library addresses the issue of trying to process a large number of items with some action
in an AWS Lambda instance, if the current maximum (15min) Lambda duration is not sufficient.

It does this by first copying the data to S3 and then dispatching multiple
Lambda invocations to process different ranges of the csv -- only loading in the data range
required.

At time of writing (Fall 2019):
* Web API calls from Lambda often process about 2/second ~> maximum of 15*60*2 = 1800 max records
* SQS messages are sent around 1600/minute ~> maximum of 15*1600 = 24000 max records processed
* Lambda uploads to an S3 bucket (in the same region) are around 8M/second, suggesting if
  each 'row' of data is around 512 bytes then the same 24K items can be send in less than 2 seconds
  which suggests = 10million max records processed
                   ^^^^^^^^^ (This is better)

TODO: rework this or remove it
With a Table and a function to process them, we want to divide up the table and distribute the rows.
The function's signature must take a Table as its first argument, e.g.
   `def foo_processor(table, arg1=None, arg2=None)`
Then:
```
from parsons.aws import distribute_task

...
    distribute_task(list_data_to_process, foo_processor, s3bucket_name,
                    func_kwargs={'arg1': 'jsonabledata'....})
```
"""

import csv
import datetime
from io import TextIOWrapper, BytesIO, StringIO
import logging
import sys
import traceback
import uuid

import boto3

from parsons.aws.aws_async import get_func_task_path, import_and_get_task, run as maybe_async_run
from parsons.etl.table import Table

logger = logging.getLogger(__name__)

EXPIRATION_DURATION = {'days': 1}


class S3Storage:

    def __init__(self):
        self.s3 = boto3.client('s3')

    def put(self, bucket, key, data):
        # TODO: make EXPIRATION_DURATION configurable
        return self.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            Expires=datetime.datetime.now() + datetime.timedelta(**EXPIRATION_DURATION))

    def get_range(self, bucket, key, rangestart, rangeend):
        get_args = {'Bucket': bucket, 'Key': key}
        if rangestart:
            # bytes is INCLUSIVE for the rangeend parameter, unlike python
            # so e.g. while python returns 2 bytes for data[2:4]
            # Range: bytes=2-4 will return 3!! So we subtract 1
            get_args['Range'] = 'bytes={}-{}'.format(rangestart, rangeend - 1)
        response = self.s3.get_object(**get_args)
        return response['Body'].read()


class TestStorage:

    def __init__(self):
        self.data = {}

    def put(self, bucket, key, data):
        self.data[key] = data

    def get_range(self, bucket, key, rangestart, rangeend):
        return self.data[key][rangestart:rangeend]


STORAGES = {
    's3': S3Storage(),
    'test': TestStorage()
}


def distribute_task_csv(csv_bytes_utf8, func_to_run, bucket,
                        header=None,
                        func_kwargs=None,
                        func_class=None,
                        func_class_kwargs=None,
                        catch=False,
                        group_count=100,
                        storage='s3'):
    """
    The same as distribute_task, but instead of a table, the
    first argument is bytes of a csv encoded into utf8.
    This function is used by distribute_task() which you should use instead.
    """
    func_name = get_func_task_path(func_to_run, func_class)
    row_chunks = csv_bytes_utf8.split(b'\n')
    cursor = 0
    row_ranges = []
    # gather start/end bytes for each row
    for rowc in row_chunks:
        rng = [cursor]
        cursor = cursor + len(rowc) + 1  # +1 is the \n character
        rng.append(cursor)
        row_ranges.append(rng)

    # group the rows and get start/end bytes for each group
    group_ranges = []
    # table csv writer appends a terminal \r\n, so we do len-1
    for grpstep in range(0, len(row_ranges) - 1, group_count):
        end = min(len(row_ranges) - 1, grpstep + group_count - 1)
        group_ranges.append((row_ranges[grpstep][0], row_ranges[end][1]))

    # upload data
    # TODO: make storagekey configurable or at least prefix?
    storagekey = str(uuid.uuid4())
    groupcount = len(group_ranges)
    logger.debug(f'distribute_task_csv storagekey {storagekey} w/ {groupcount} groups')

    response = STORAGES[storage].put(bucket, storagekey, csv_bytes_utf8)

    # start processes
    results = [
        maybe_async_run(
            process_task_portion,
            [bucket, storagekey, grp[0], grp[1], func_name, header,
             storage, func_kwargs, catch, func_class_kwargs])
        for grp in group_ranges]
    return {'DEBUG_ONLY': 'results may vary depending on context/platform',
            'results': results,
            'put_response': response}


def distribute_task(table, func_to_run, bucket,
                    func_kwargs=None,
                    func_class=None,
                    func_class_kwargs=None,
                    catch=False,
                    group_count=100,
                    storage='s3'):
    """
    Distribute processing rows in a table across multiple AWS Lambda invocations.
    TODO: document WHY we would use this
    TODO: check_env for defaults, including for bucket
    TODO: document env variables and how/why one runs this
    TODO: document needing to include parsons.aws.event_command in Lambda handler

    `Args:`
        table: Table
           The bucket name
        func_to_run: function
           The function you want to run whose
           first argument will be a subset of table
        bucket: str
           The bucket name to use for s3 upload to process the whole table
        func_kwargs: dict
           If the function has other arguments to pass along with `table`
           then provide them as a dict here. They must all be JSON-able.
        func_class: class
           If the function is a classmethod or function on a class,
           then pass the pure class here.
           E.g. If you passed `ActionKit.bulk_upload_table`,
           then you would pass `ActionKit` here.
        func_class_kwargs: dict
           If it is a class function, and the class must be instantiated,
           then pass the kwargs to instantiate the class here.
           E.g. If you passed `ActionKit.bulk_upload_table` as the function,
           then you would pass {'domain': ..., 'username': ... etc} here.
           This must all be JSON-able data.
        catch: bool
           Lambda will retry running an event three times if there's an
           exception -- if you want to prevent this, set `catch=True`
           and then it will catch any errors and stop retries.
           The error will be in CloudWatch logs with string "Distribute Error"
           This might be important if row-actions are not idempotent and your
           own function might fail causing repeats.
        group_count: int
           Set this to how many rows to process with each Lambda invocation (Default: 100)
    `Returns:`
        Debug information -- do not rely on the output, as it will change
        depending on how this method is invoked.
    """

    csvdata = StringIO()
    outcsv = csv.writer(csvdata)
    outcsv.writerows(table.table.data())
    return distribute_task_csv(csvdata.getvalue().encode('utf-8-sig'),
                               func_to_run,
                               bucket,
                               header=table.table.header(),
                               func_kwargs=func_kwargs,
                               func_class=func_class,
                               func_class_kwargs=func_class_kwargs,
                               catch=catch,
                               group_count=group_count,
                               storage=storage)


def process_task_portion(bucket, storagekey, rangestart, rangeend, func_name, header,
                         storage='s3', func_kwargs=None, catch=False,
                         func_class_kwargs=None):

    logger.debug(f'process_task_portion func_name {func_name}, storagekey {storagekey}, range {rangestart}-{rangeend}')
    func = import_and_get_task(func_name, func_class_kwargs)
    filedata = STORAGES[storage].get_range(bucket, storagekey, rangestart, rangeend)

    lines = list(csv.reader(TextIOWrapper(BytesIO(filedata), encoding='utf-8-sig')))
    table = Table([header] + lines)
    if catch:
        try:
            func(table, **func_kwargs)
        except Exception:
            # In Lambda you can search for '"Distribute Error"' in the logs
            type_, value_, traceback_ = sys.exc_info()
            err_traceback_str = '\n'.join(traceback.format_exception(type_, value_, traceback_))
            return {'Exception': 'Distribute Error',
                    'error': err_traceback_str,
                    'rangestart': rangestart,
                    'rangeend': rangeend,
                    'func_name': func_name,
                    'bucket': bucket,
                    'storagekey': storagekey}
    else:
        func(table, **func_kwargs)


def test():
    """Small test function to test local methods"""
    a = [(a, a+1, a+2) for a in range(21)]
    a[0:0] = [['a', 'b', 'c']]  # header
    csvdata = StringIO()
    outcsv = csv.writer(csvdata)
    outcsv.writerows(a)
    distribute_task_csv(csvdata.getvalue().encode(), print, 'x',
                        group_count=5, storage='test', func_kwargs={'foo': 'bar'})
