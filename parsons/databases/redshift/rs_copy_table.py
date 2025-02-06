import os
from parsons.aws.s3 import S3
import time
import logging

logger = logging.getLogger(__name__)

S3_TEMP_KEY_PREFIX = "Parsons_RedshiftCopyTable"


class RedshiftCopyTable(object):
    aws_access_key_id = None
    aws_secret_access_key = None
    iam_role = None

    def __init__(self, use_env_token=True):
        self.use_env_token = use_env_token

    def copy_statement(
        self,
        table_name,
        bucket,
        key,
        manifest=False,
        data_type="csv",
        csv_delimiter=",",
        max_errors=0,
        statupdate=None,
        compupdate=None,
        ignoreheader=1,
        acceptanydate=True,
        dateformat="auto",
        timeformat="auto",
        emptyasnull=True,
        blanksasnull=True,
        nullas=None,
        acceptinvchars=True,
        truncatecolumns=False,
        specifycols=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        compression=None,
        bucket_region=None,
        json_option="auto",
    ):
        logger.info(f"Data type is {data_type}")
        # Source / Destination
        source = f"s3://{bucket}/{key}"

        # Add column list for mapping or if there are fewer columns on source file
        col_list = f"({', '.join(specifycols)})" if specifycols is not None else ""

        sql = f"copy {table_name}{col_list} \nfrom '{source}' \n"

        # Generate credentials
        sql += self.get_creds(aws_access_key_id, aws_secret_access_key)

        # Other options
        if manifest:
            sql += "manifest \n"
        if bucket_region:
            sql += f"region '{bucket_region}'\n"
            logger.info("Copying data from S3 bucket %s in region %s", bucket, bucket_region)
        sql += f"maxerror {max_errors} \n"

        # Redshift has some default behavior when statupdate is left out
        # vs when it is explicitly set as on or off.
        if statupdate is not None:
            if statupdate:
                sql += "statupdate on\n"
            else:
                sql += "statupdate off\n"

        # Redshift has some default behavior when compupdate is left out
        # vs when it is explicitly set as on or off.
        if compupdate is not None:
            if compupdate:
                sql += "compupdate on\n"
            else:
                sql += "compupdate off\n"

        if ignoreheader:
            sql += f"ignoreheader {ignoreheader} \n"
        if acceptanydate:
            sql += "acceptanydate \n"
        sql += f"dateformat '{dateformat}' \n"
        sql += f"timeformat '{timeformat}' \n"
        if emptyasnull:
            sql += "emptyasnull \n"
        if blanksasnull:
            sql += "blanksasnull \n"
        if nullas:
            sql += f"null as {nullas}"
        if acceptinvchars:
            sql += "acceptinvchars \n"
        if truncatecolumns:
            sql += "truncatecolumns \n"

        # Data Type
        if data_type == "csv":
            sql += f"csv delimiter '{csv_delimiter}' \n"
        elif data_type == "json":
            sql += f"json '{json_option}' \n"
        else:
            raise TypeError("Invalid data type specified.")

        if compression == "gzip":
            sql += "gzip \n"

        sql += ";"

        return sql

    def get_creds(self, aws_access_key_id, aws_secret_access_key):
        if aws_access_key_id and aws_secret_access_key:
            # When we have credentials, then we don't need to set them again
            pass

        elif self.iam_role:
            # bail early, since the bottom is specifically formatted with creds
            return f"credentials 'aws_iam_role={self.iam_role}'\n"

        elif self.aws_access_key_id and self.aws_secret_access_key:
            aws_access_key_id = self.aws_access_key_id
            aws_secret_access_key = self.aws_secret_access_key

        elif "AWS_ACCESS_KEY_ID" in os.environ and "AWS_SECRET_ACCESS_KEY" in os.environ:
            aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            aws_secret_access_key = os.environ["AWS_SECRET_ACCESS_KEY"]

        else:
            s3 = S3(use_env_token=self.use_env_token)
            creds = s3.aws.session.get_credentials()
            aws_access_key_id = creds.access_key
            aws_secret_access_key = creds.secret_key

        return "credentials 'aws_access_key_id={};aws_secret_access_key={}'\n".format(
            aws_access_key_id, aws_secret_access_key
        )

    def temp_s3_copy(
        self,
        tbl,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        csv_encoding="utf-8",
    ):
        if not self.s3_temp_bucket:
            raise KeyError(
                (
                    "Missing S3_TEMP_BUCKET, needed for transferring data to Redshift. "
                    "Must be specified as env vars or kwargs"
                )
            )

        # Coalesce S3 Key arguments
        aws_access_key_id = aws_access_key_id or self.aws_access_key_id
        aws_secret_access_key = aws_secret_access_key or self.aws_secret_access_key

        self.s3 = S3(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_env_token=self.use_env_token,
        )

        hashed_name = hash(time.time())
        key = f"{S3_TEMP_KEY_PREFIX}/{hashed_name}.csv.gz"
        if self.s3_temp_bucket_prefix:
            key = self.s3_temp_bucket_prefix + "/" + key

        # Convert table to compressed CSV file, to optimize the transfers to S3 and to
        # Redshift.
        local_path = tbl.to_csv(temp_file_compression="gzip", encoding=csv_encoding)
        # Copy table to bucket
        self.s3.put_file(self.s3_temp_bucket, key, local_path)

        return key

    def temp_s3_delete(self, key):
        if key:
            self.s3.remove_file(self.s3_temp_bucket, key)
