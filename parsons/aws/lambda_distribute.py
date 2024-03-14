import csv
from io import TextIOWrapper, BytesIO, StringIO
import logging
import sys
import traceback
import time

from parsons.aws.aws_async import (
    get_func_task_path,
    import_and_get_task,
    run as maybe_async_run,
)
from parsons.aws.s3 import S3
from parsons.etl.table import Table
from parsons.utilities.check_env import check

logger = logging.getLogger(__name__)


class DistributeTaskException(Exception):
    pass


class TestStorage:
    def __init__(self):
        self.data = {}

    def put_object(self, bucket, key, object_bytes):
        self.data[key] = object_bytes

    def get_range(self, bucket, key, rangestart, rangeend):
        return self.data[key][rangestart:rangeend]


class S3Storage:
    """
    These methods are pretty specialized, so we keep them
    inside this file rather than s3.py
    """

    def __init__(self, use_env_token=True):
        self.s3 = S3(use_env_token=use_env_token)

    def put_object(self, bucket, key, object_bytes, **kwargs):
        return self.s3.client.put_object(Bucket=bucket, Key=key, Body=object_bytes, **kwargs)

    def get_range(self, bucket, key, rangestart, rangeend):
        """
        Gets an explicit byte-range of an S3 file
        """
        # bytes is INCLUSIVE for the rangeend parameter, unlike python
        # so e.g. while python returns 2 bytes for data[2:4]
        # Range: bytes=2-4 will return 3!! So we subtract 1
        response = self.s3.client.get_object(
            Bucket=bucket, Key=key, Range="bytes={}-{}".format(rangestart, rangeend - 1)
        )
        return response["Body"].read()


FAKE_STORAGE = TestStorage()
S3_TEMP_KEY_PREFIX = "Parsons_DistributeTask"


def distribute_task_csv(
    csv_bytes_utf8,
    func_to_run,
    bucket,
    header=None,
    func_kwargs=None,
    func_class=None,
    func_class_kwargs=None,
    catch=False,
    group_count=100,
    storage="s3",
    use_s3_env_token=True,
):
    """
    The same as distribute_task, but instead of a table, the
    first argument is bytes of a csv encoded into utf8.
    This function is used by distribute_task() which you should use instead.
    """
    global FAKE_STORAGE
    func_name = get_func_task_path(func_to_run, func_class)
    row_chunks = csv_bytes_utf8.split(b"\n")
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
    filename = hash(time.time())
    storagekey = f"{S3_TEMP_KEY_PREFIX}/{filename}.csv"
    groupcount = len(group_ranges)
    logger.debug(f"distribute_task_csv storagekey {storagekey} w/ {groupcount} groups")

    response = None
    if storage == "s3":
        response = S3Storage(use_env_token=use_s3_env_token).put_object(
            bucket, storagekey, csv_bytes_utf8
        )
    else:
        response = FAKE_STORAGE.put_object(bucket, storagekey, csv_bytes_utf8)

    # start processes
    results = [
        maybe_async_run(
            process_task_portion,
            [
                bucket,
                storagekey,
                grp[0],
                grp[1],
                func_name,
                header,
                storage,
                func_kwargs,
                catch,
                func_class_kwargs,
                use_s3_env_token,
            ],
            # if we are using local storage, then it must be run locally, as well
            # (good for testing/debugging)
            remote_aws_lambda_function_name="FORCE_LOCAL" if storage == "local" else None,
        )
        for grp in group_ranges
    ]
    return {
        "DEBUG_ONLY": "results may vary depending on context/platform",
        "results": results,
        "put_response": response,
    }


def distribute_task(
    table,
    func_to_run,
    bucket=None,
    func_kwargs=None,
    func_class=None,
    func_class_kwargs=None,
    catch=False,
    group_count=100,
    storage="s3",
    use_s3_env_token=True,
):
    """
    Distribute processing rows in a table across multiple AWS Lambda invocations.

    `Args:`
        table: Parsons Table
           Table of data you wish to distribute processing across Lambda invocations
           of `func_to_run` argument.
        func_to_run: function
           The function you want to run whose
           first argument will be a subset of table
        bucket: str
           The bucket name to use for s3 upload to process the whole table
           Not required if you set environment variable ``S3_TEMP_BUCKET``
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
        storage: str
           Debugging option: Defaults to "s3". To test distribution locally without s3,
           set to "local".
        use_s3_env_token: str
           If storage is set to "s3", sets the use_env_token parameter on the S3 storage.
    `Returns:`
        Debug information -- do not rely on the output, as it will change
        depending on how this method is invoked.
    """
    if storage not in ("s3", "local"):
        raise DistributeTaskException("storage argument must be s3 or local")
    bucket = check("S3_TEMP_BUCKET", bucket)
    csvdata = StringIO()
    outcsv = csv.writer(csvdata)
    outcsv.writerows(table.table.data())
    return distribute_task_csv(
        csvdata.getvalue().encode("utf-8-sig"),
        func_to_run,
        bucket,
        header=table.columns,
        func_kwargs=func_kwargs,
        func_class=func_class,
        func_class_kwargs=func_class_kwargs,
        catch=catch,
        group_count=group_count,
        storage=storage,
        use_s3_env_token=use_s3_env_token,
    )


def process_task_portion(
    bucket,
    storagekey,
    rangestart,
    rangeend,
    func_name,
    header,
    storage="s3",
    func_kwargs=None,
    catch=False,
    func_class_kwargs=None,
    use_s3_env_token=True,
):
    global FAKE_STORAGE

    logger.debug(
        f"process_task_portion func_name {func_name}, "
        f"storagekey {storagekey}, byterange {rangestart}-{rangeend}"
    )
    func = import_and_get_task(func_name, func_class_kwargs)
    if storage == "s3":
        filedata = S3Storage(use_env_token=use_s3_env_token).get_range(
            bucket, storagekey, rangestart, rangeend
        )
    else:
        filedata = FAKE_STORAGE.get_range(bucket, storagekey, rangestart, rangeend)

    lines = list(csv.reader(TextIOWrapper(BytesIO(filedata), encoding="utf-8-sig")))
    table = Table([header] + lines)
    if catch:
        try:
            func(table, **func_kwargs)
        except Exception:
            # In Lambda you can search for '"Distribute Error"' in the logs
            type_, value_, traceback_ = sys.exc_info()
            err_traceback_str = "\n".join(traceback.format_exception(type_, value_, traceback_))
            return {
                "Exception": "Distribute Error",
                "error": err_traceback_str,
                "rangestart": rangestart,
                "rangeend": rangeend,
                "func_name": func_name,
                "bucket": bucket,
                "storagekey": storagekey,
            }
    else:
        func(table, **func_kwargs)
