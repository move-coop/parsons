from parsons.sftp.sftp import SFTP
from parsons.etl.table import Table
from parsons.utilities.files import create_temp_file
from parsons.utilities import check_env
import xml.etree.ElementTree as ET
import uuid
import time
import logging
import xmltodict


TS_STFP_HOST = 'transfer.targetsmart.com'
TS_SFTP_PORT = 22
TS_SFTP_DIR = 'automation'

logger = logging.getLogger(__name__)

# Automation matching documentation can be found here:
# https://docs.targetsmart.com/developers/automation/index.html

# The columns are heavily customized by TS, so while I would like
# to do more column validation and mapping, I'm not sure that is
# going to be possible.


class TargetSmartAutomation(object):

    def __init__(self, sftp_username=None, sftp_password=None):

        self.sftp_host = TS_STFP_HOST
        self.sftp_port = TS_SFTP_PORT
        self.sftp_dir = TS_SFTP_DIR
        self.sftp_username = check_env.check('TS_SFTP_USERNAME', sftp_username)
        self.sftp_password = check_env.check('TS_SFTP_PASSWORD', sftp_password)
        self.sftp = SFTP(self.sftp_host, self.sftp_username, self.sftp_password, self.sftp_port)

    def match(self, table, job_type, job_name=None, emails=None, call_back=None, remove_files=True):
        """
        Match a table to TargetSmart using their bulk matching service.

        .. warning::
            Table Columns
              The automation job does not validates the file by column indexes
              rather than columns names. So, if it expected 10 columns and you
              only provide 9, it will fail. However, if you provide 10 columns that
              are out of order, the job will succeed, but the records will not
              match.

        Args:
            table: Parsons Table Object
                A table object with the required columns. (Required columns provided be TargetSmart)
            job_type: str
                The match job type. **This is case sensitive.** (Match job names provided by TargetSmart)
            job_name: str
                Optional job name.
            emails: list
                A list of emails that will received status notifications. This
                is useful in debugging failed jobs.
            call_back: str
                A callback url to which the status will be posted. See
                `TargetSmart documentation <https://docs.targetsmart.com/developers/automation/index.html#http-callback>`_
                for more details.
            remove_files: boolean
                Remove the configuration, file to be matched and matched file from
                the TargetSmart FTP upon completion or failure of match.
        """ # noqa: E501,E261

        # Generate a match job
        job_name = job_name or str(uuid.uuid1())

        try:
            # Upload table
            self.sftp.put_file(table.to_csv(), f'{self.sftp_dir}/{job_name}_input.csv')
            logger.info(f'Table with {table.num_rows} rows uploaded to TargetSmart.')

            # Create/upload XML configuration
            xml = self.create_job_xml(job_type, job_name, emails=emails,
                                      status_key=job_name, call_back=call_back)
            self.sftp.put_file(xml, f'{self.sftp_dir}/{job_name}.job.xml')
            logger.info(f'Match configuration uploaded to TargetSmart.')

            # Check xml configuration status
            self.poll_config_status(job_name)

            # Check the status of the match
            self.match_status(job_name)

            # Download the resulting file
            tbl = Table.from_csv(self.sftp.get_file(f'{self.sftp_dir}/{job_name}_output.csv'))

        finally:
            # Clean up files
            if remove_files:
                self.remove_files(job_name)

            # Log Stats
            # TO DO: Provide some stats on the match

        # Return file as a Table
        return tbl

    def create_job_xml(self, job_type, job_name, emails=None, status_key=None, call_back=None):
        # Internal method to create a valid job xml

        job = ET.Element("job")

        # Generate Base XML
        input_file = ET.SubElement(job, 'inputfile')
        input_file.text = job_name + '_input.csv'
        output_file = ET.SubElement(job, 'outputfile')
        output_file.text = job_name + '_output.csv'
        jobtype = ET.SubElement(job, 'jobtype', text=job_type)
        jobtype.text = job_type

        # Add status key
        args = ET.SubElement(job, "args")
        statuskey = ET.SubElement(args, "arg", name="__status_key")
        statuskey.text = status_key or job_name

        # Option args
        if call_back:
            callback = ET.SubElement(args, "arg", name="__http_callback")
            callback.text = call_back

        if emails:
            emails_el = ET.SubElement(args, "arg", name="__emails")
            emails_el.text = ','.join(emails)

        # Write xml to file object
        local_path = create_temp_file(suffix='.xml')
        tree = ET.ElementTree(job)
        tree.write(local_path)
        return local_path

    def poll_config_status(self, job_name, polling_interval=20):
        #  Poll the configuration status

        while True:

            time.sleep(polling_interval)
            if self.config_status(job_name):
                return True
            logger.info(f'Waiting on {job_name} job configuration...')

    def config_status(self, job_name):
        # Check the status of the configuration by parsing the
        # the files in the SFTP directory.

        for f in self.sftp.list_directory(remote_path=self.sftp_dir):

            if f == f'{job_name}.job.xml.good':
                logger.info(f'Match job {job_name} configured.')
                return True

            elif f == f'{job_name}.job.xml.bad':
                logger.info(f'Match job {job_name} configuration error.')
                #  To Do: Lift up the configuration error.
                raise ValueError('Job configuration failed. If you provided an email'
                                 'address, you will be sent more details.')

            else:
                pass

        return False

    def match_status(self, job_name, polling_interval=60):
        # You could also poll their API for the status, which was what the original
        # version of the automation matching did. Note: The polling API is public
        # and does expose some metadata. This happens regardless of anything that
        # we do. However, the actually data is only exposed on the secure SFTP.

        while True:

            logger.debug('Match running...')
            for file_name in self.sftp.list_directory(remote_path=self.sftp_dir):

                if file_name == f'{job_name}.finish.xml':

                    xml_file = self.sftp.get_file(f'{self.sftp_dir}/{job_name}.finish.xml')
                    with open(xml_file, 'rb') as x:
                        xml = xmltodict.parse(x, dict_constructor=dict)

                    if xml['jobcontext']['state'] == 'error':
                        # To Do: Parse these in a pretty way
                        logger.info(f"Match Error: {xml['jobcontext']['errors']}")
                        raise ValueError(f"Match job failed. {xml['jobcontext']['errors']}")

                    elif xml['jobcontext']['state'] == 'success':
                        logger.info('Match complete.')

                        return True

            time.sleep(polling_interval)

    def remove_files(self, job_name):
        # Remove all of the files for the match.

        for file_name in self.sftp.list_directory(remote_path=self.sftp_dir):
            if job_name in file_name:
                self.sftp.remove_file(f'{self.sftp_dir}/{file_name}')
                logger.info(f'{file_name} removed from SFTP.')
