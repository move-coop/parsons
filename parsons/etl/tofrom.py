import gzip
import io
import json
from pathlib import Path
from typing import Literal

import petl

from parsons.utilities import files, zip_archive


class ToFrom:
    def to_dataframe(self, index=None, exclude=None, columns=None, coerce_float=False):
        """
        Outputs table as a Pandas Dataframe

        Args:
            index: str, list
                Field of array to use as the index, alternately a specific set
                of input labels to use
            exclude: list
                Columns or fields to exclude
            columns: list
                Column names to use. If the passed data do not have names
                associated with them, this argument provides names for the
                columns. Otherwise this argument indicates the order of the
                columns in the result (any names not found in the data will
                become all-NA columns)

        Returns:
            dataframe
                Pandas DataFrame object

        """

        return petl.todataframe(
            self.table,
            index=index,
            exclude=exclude,
            columns=columns,
            coerce_float=coerce_float,
        )

    def to_html(
        self,
        local_path=None,
        encoding=None,
        errors="strict",
        index_header=False,
        caption=None,
        tr_style=None,
        td_styles=None,
        truncate=None,
    ):
        """
        Outputs table to html.

        .. warning::
                If a file already exists at the given location, it will be
                overwritten.

        Args:
            local_path: str
                The path to write the html locally. If not specified, a temporary file will be
                created and returned, and that file will be removed automatically when the script
                is done running.
            encoding: str
                The encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            index_header: boolean
                Prepend index to column names; Defaults to False.
            caption: str
                A caption to include with the html table.
            tr_style: str or callable
                Style to be applied to the table row.
            td_styles: str, dict or callable
                Styles to be applied to the table cells.
            truncate: int
                Length of cell data.

        Returns:
            str
                The path of the new file

        """

        if not local_path:
            local_path = files.create_temp_file(suffix=".html")

        petl.tohtml(
            self.table,
            source=local_path,
            encoding=encoding,
            errors=errors,
            caption=caption,
            index_header=index_header,
            tr_style=tr_style,
            td_styles=td_styles,
            truncate=truncate,
        )

        return local_path

    def to_avro(
        self,
        target,
        schema=None,
        sample=9,
        codec: Literal["null", "deflate", "bzip2", "snappy", "zstandard", "lz4", "xz"] = "deflate",
        compression_level=None,
        **avro_args,
    ):
        """
        Outputs table to an Avro file.

        In order to use this method, you must have the `fastavro` library installed.
        If using limited dependencies, you can install it with `pip install parsons[avro]`.

        Write the table into a new avro file according to schema passed.

        This method assume that each column has values with the same type
        for all rows of the source `table`.

        Avro is a data serialization framework that is generally is faster
        and safer than text formats like Json, XML or CSV.

        Args:
            target: str
                the file path for creating the avro file.
                Note that if a file already exists at the given location, it will be
                overwritten.
            schema: dict
                defines the rows field structure of the file.
                Check fastavro [documentation](https://fastavro.readthedocs.io/en/latest/) and Avro schema [reference](https://avro.apache.org/docs/1.8.2/spec.html#schemas) for details.
            sample: int, optional
                defines how many rows are inspected
                for discovering the field types and building a schema for the avro file
                when the `schema` argument is not passed. Default is 9.
            codec: str, optional
                The `codec` argument (string, optional) sets the compression codec used to
                shrink data in the file. It can be 'null', 'deflate' (default), 'bzip2' or
                'snappy', 'zstandard', 'lz4', 'xz' (if installed)
            compression_level: int, optional
                sets the level of compression to use with the specified codec (if the codec supports it)
            `**avro_args`: kwargs
                Additionally there are support for passing extra options in the
                argument `**avro_args` that are fowarded directly to fastavro. [Check the
                fastavro documentation](https://fastavro.readthedocs.io/en/latest/) for reference.

        Example usage for writing files::

            >>> # set up a Avro file to demonstrate with
            >>> table2 = [['name', 'friends', 'age'],
            ...           ['Bob', 42, 33],
            ...           ['Jim', 13, 69],
            ...           ['Joe', 86, 17],
            ...           ['Ted', 23, 51]]
            ...
            >>> schema2 = {
            ...     'doc': 'Some people records.',
            ...     'name': 'People',
            ...     'namespace': 'test',
            ...     'type': 'record',
            ...     'fields': [
            ...         {'name': 'name', 'type': 'string'},
            ...         {'name': 'friends', 'type': 'int'},
            ...         {'name': 'age', 'type': 'int'},
            ...     ]
            ... }
            ...
            >>> # now demonstrate writing with toavro()
            >>> from parsons import Table

            >>> Table.toavro(table2, 'example.file2.avro', schema=schema2)
            ...
            >>> # this was what was saved above
            >>> tbl2 = Table.fromavro('example.file2.avro')
            >>> tbl2
            +-------+---------+-----+
            | name  | friends | age |
            +=======+=========+=====+
            | 'Bob' |      42 |  33 |
            +-------+---------+-----+
            | 'Jim' |      13 |  69 |
            +-------+---------+-----+
            | 'Joe' |      86 |  17 |
            +-------+---------+-----+
            | 'Ted' |      23 |  51 |
            +-------+---------+-----+

        """

        return petl.toavro(
            self.table,
            target,
            schema=schema,
            sample=sample,
            codec=codec,
            compression_level=compression_level,
            **avro_args,
        )

    def append_avro(self, target, schema=None, sample=9, **avro_args):
        """
        Append table to an existing Avro file.

        Write the table into an existing avro file according to schema passed.

        This method assume that each column has values with the same type
        for all rows of the source `table`.

        Args:
            target: str
                the file path for creating the avro file.
            schema: dict
                defines the rows field structure of the file.
                Check fastavro [documentation](https://fastavro.readthedocs.io/en/latest/) and Avro schema [reference](https://avro.apache.org/docs/1.8.2/spec.html#schemas) for details.
            sample: int, optional
                defines how many rows are inspected
                for discovering the field types and building a schema for the avro file
                when the `schema` argument is not passed. Default is 9.
            `**avro_args`: kwargs
                Additionally there are support for passing extra options in the
                argument `**avro_args` that are fowarded directly to fastavro. Check the
                fastavro [documentation](https://fastavro.readthedocs.io/en/latest/) for reference.

        """

        return petl.appendavro(self.table, target, schema=schema, sample=sample, **avro_args)

    def to_csv(
        self,
        local_path=None,
        temp_file_compression=None,
        encoding=None,
        errors="strict",
        write_header=True,
        csv_name=None,
        **csvargs,
    ):
        r"""
        Outputs table to a CSV. Additional key word arguments are passed to ``csv.writer()``. So,
        e.g., to override the delimiter from the default CSV dialect, provide the delimiter
        keyword argument.

        .. warning::
                If a file already exists at the given location, it will be
                overwritten.

        Args:
            local_path: str
                The path to write the csv locally. If it ends in ".gz" or ".zip", the file will be
                compressed. If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            temp_file_compression: str
                If a temp file is requested (ie. no ``local_path`` is specified), the compression
                type for that file. Currently "None", "gzip" or "zip" are supported.
                If a ``local_path`` is specified, this argument is ignored.
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            write_header: boolean
                Include header in output
            csv_name: str
                If ``zip`` compression (either specified or inferred), the name of csv file
                within the archive.
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments

        Returns:
            str
                The path of the new file

        """

        # If a zip archive.
        if files.zip_check(local_path, temp_file_compression):
            return self.to_zip_csv(
                archive_path=local_path,
                encoding=encoding,
                errors=errors,
                write_header=write_header,
                csv_name=csv_name,
                **csvargs,
            )

        if not local_path:
            suffix = ".csv" + files.suffix_for_compression_type(temp_file_compression)
            local_path = files.create_temp_file(suffix=suffix)

        # Create normal csv/.gzip
        petl.tocsv(
            self.table,
            source=local_path,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            **csvargs,
        )

        return local_path

    def append_csv(self, local_path, encoding=None, errors="strict", **csvargs):
        r"""
        Appends table to an existing CSV.

        Additional additional key word arguments
        are passed to ``csv.writer()``. So, e.g., to override the delimiter
        from the default CSV dialect, provide the delimiter keyword argument.

        Args:
            local_path: str
                The local path of an existing CSV file. If it ends in ".gz", the file will
                be compressed.
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments

        Returns:
            str
                The path of the file

        """

        petl.appendcsv(self.table, source=local_path, encoding=encoding, errors=errors, **csvargs)
        return local_path

    def to_zip_csv(
        self,
        archive_path=None,
        csv_name=None,
        encoding=None,
        errors="strict",
        write_header=True,
        if_exists: Literal["replace", "append"] = "replace",
        **csvargs,
    ):
        r"""
        Outputs table to a CSV in a zip archive. Additional key word arguments are passed to
        ``csv.writer()``. So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument. Use thismethod if you would like to write
        multiple csv files to the same archive.

        .. warning::
                If a file already exists in the archive, it will be overwritten.

        Args:
            archive_path: str
                The path to zip achive. If not specified, a temporary file will be created and
                returned, and that file will be removed automatically when the script is done
                running.
            csv_name: str
                The name of the csv file to be stored in the archive. If ``None`` will use
                the archive name.
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            write_header: boolean
                Include header in output
            if_exists: str
                If archive already exists, one of 'replace' or 'append'
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments

        Returns:
            str
                The path of the archive

        """

        if not archive_path:
            archive_path = files.create_temp_file(suffix=".zip")

        cf = self.to_csv(encoding=encoding, errors=errors, write_header=write_header, **csvargs)

        if not csv_name:
            csv_name = files.extract_file_name(archive_path, include_suffix=False) + ".csv"

        return zip_archive.create_archive(archive_path, cf, file_name=csv_name, if_exists=if_exists)

    def to_json(self, local_path=None, temp_file_compression=None, line_delimited=False):
        """
        Outputs table to a JSON file

        .. warning::
                If a file already exists at the given location, it will be
                overwritten.

        Args:
            local_path: str
                The path to write the JSON locally. If it ends in ".gz", it will be
                compressed first. If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            temp_file_compression: str
                If a temp file is requested (ie. no ``local_path`` is specified), the compression
                type for that file. Currently "None" and "gzip" are supported.
                If a ``local_path`` is specified, this argument is ignored.
            line_delimited: bool
                Whether the file will be line-delimited JSON (with a row on each line), or a proper
                JSON file.

        Returns:
            str
                The path of the new file

        """

        if not local_path:
            suffix = ".json" + files.suffix_for_compression_type(temp_file_compression)
            local_path = files.create_temp_file(suffix=suffix)

        # Note we don't use the much simpler petl.tojson(), since that method reads the whole
        # table into memory before writing to file.

        if files.is_gzip_path(local_path):
            open_fn = gzip.open
            mode = "w+t"
        else:
            open_fn = open
            mode = "w"

        with open_fn(local_path, mode) as file:
            if not line_delimited:
                file.write("[")

            for i, row in enumerate(self):
                if i:
                    if not line_delimited:
                        file.write(",")
                    file.write("\n")
                json.dump(row, file)

            if not line_delimited:
                file.write("]")

        return local_path

    def to_dicts(self):
        """
        Output table as a list of dicts.

        Returns:
            list

        """

        return list(petl.dicts(self.table))

    def to_sftp_csv(
        self,
        remote_path,
        host,
        username,
        password,
        port=22,
        encoding=None,
        compression=None,
        errors="strict",
        write_header=True,
        rsa_private_key_file=None,
        **csvargs,
    ):
        r"""
        Writes the table to a CSV file on a remote SFTP server

        Args:
            remote_path: str
                The remote path of the file. If it ends in '.gz', the file will be compressed.
            host: str
                The remote host
            username: str
                The username to access the SFTP server
            password: str
                The password to access the SFTP server
            port: int
                The port number of the SFTP server
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            write_header: boolean
                Include header in output
            rsa_private_key_file str
                Absolute path to a private RSA key used
                to authenticate stfp connection
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments

        """

        from parsons.sftp import SFTP

        sftp = SFTP(host, username, password, port, rsa_private_key_file)

        compression = files.compression_type_for_path(remote_path)

        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            **csvargs,
        )
        sftp.put_file(local_path, remote_path)

    def to_s3_csv(
        self,
        bucket,
        key,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        compression=None,
        encoding=None,
        errors="strict",
        write_header=True,
        acl="bucket-owner-full-control",
        public_url=False,
        public_url_expires=3600,
        use_env_token=True,
        **csvargs,
    ):
        r"""
        Writes the table to an s3 object as a CSV

        Args:
            bucket: str
                The s3 bucket to upload to
            key: str
                The s3 key to name the file. If it ends in '.gz' or '.zip', the file will be
                compressed.
            aws_access_key_id: str
                Required if not included as environmental variable
            aws_secret_access_key: str
                Required if not included as environmental variable
            compression: str
                The compression type for the s3 object. Currently "None", "zip" and "gzip" are
                supported. If specified, will override the key suffix.
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            write_header: boolean
                Include header in output
            public_url: boolean
                Create a public link to the file
            public_url_expire: 3600
                The time, in seconds, until the url expires if ``public_url`` set to ``True``.
            acl: str
                The S3 permissions on the file
            use_env_token: boolean
                Controls use of the ``AWS_SESSION_TOKEN`` environment variable for S3. Defaults
                to ``True``. Set to ``False`` in order to ignore the ``AWS_SESSION_TOKEN`` env
                variable even if the ``aws_session_token`` argument was not passed in.
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments
        Returns:
            Public url if specified. If not ``None``.

        """

        compression = compression or files.compression_type_for_path(key)

        csv_name = files.extract_file_name(key, include_suffix=False) + ".csv"

        # Save the CSV as a temp file
        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            csv_name=csv_name,
            **csvargs,
        )

        # Put the file on S3
        from parsons.aws import S3

        self.s3 = S3(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_env_token=use_env_token,
        )
        self.s3.put_file(bucket, key, local_path, acl=acl)

        if public_url:
            return self.s3.get_url(bucket, key, expires_in=public_url_expires)
        else:
            return None

    def to_gcs_csv(
        self,
        bucket_name,
        blob_name,
        gcs_client=None,
        app_creds=None,
        project=None,
        compression=None,
        encoding=None,
        errors="strict",
        write_header=True,
        public_url=False,
        public_url_expires=60,
        **csvargs,
    ):
        r"""
        Writes the table to a Google Cloud Storage blob as a CSV.

        Args:
            bucket_name: str
                The bucket to upload to
            blob_name: str
                The blob to name the file. If it ends in '.gz' or '.zip', the file will be
                compressed.
            app_creds: str
                A credentials json string or a path to a json file. Not required
                if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project: str
                The project which the client is acting on behalf of. If not passed
                then will use the default inferred environment.
            compression: str
                The compression type for the csv. Currently "None", "zip" and "gzip" are
                supported. If specified, will override the key suffix.
            encoding: str
                The CSV encoding type for `csv.writer()
                <https://docs.python.org/2/library/csv.html#csv.writer/>`_
            errors: str
                Raise an Error if encountered
            write_header: boolean
                Include header in output
            public_url: boolean
                Create a public link to the file
            public_url_expire: 60
                The time, in minutes, until the url expires if ``public_url`` set to ``True``.
            `**csvargs`: kwargs
                ``csv_writer`` optional arguments
        Returns:
            Public url if specified. If not ``None``.

        """

        compression = compression or files.compression_type_for_path(blob_name)

        csv_name = files.extract_file_name(blob_name, include_suffix=False) + ".csv"

        # Save the CSV as a temp file
        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            csv_name=csv_name,
            **csvargs,
        )

        if not gcs_client:
            from parsons.google.google_cloud_storage import GoogleCloudStorage

            gcs_client = GoogleCloudStorage(app_creds=app_creds, project=project)

        gcs_client.put_blob(bucket_name, blob_name, local_path)

        if public_url:
            return gcs_client.get_url(bucket_name, blob_name, expires_in=public_url_expires)
        else:
            return None

    def to_redshift(
        self,
        table_name,
        username=None,
        password=None,
        host=None,
        db=None,
        port=None,
        **copy_args,
    ):
        r"""
        Write a table to a Redshift database. Note, this requires you to pass
        AWS S3 credentials or store them as environmental variables.

        Args:
            table_name: str
                The table name and schema (``my_schema.my_table``) to point the file.
            username: str
                Required if env variable ``REDSHIFT_USERNAME`` not populated
            password: str
                Required if env variable ``REDSHIFT_PASSWORD`` not populated
            host: str
                Required if env variable ``REDSHIFT_HOST`` not populated
            db: str
                Required if env variable ``REDSHIFT_DB`` not populated
            port: int
                Required if env variable ``REDSHIFT_PORT`` not populated. Port 5439 is typical.
            `**copy_args`: kwargs
                See :func:`~parsons.databases.Redshift.copy`` for options.

        """

        from parsons.databases.redshift import Redshift

        rs = Redshift(username=username, password=password, host=host, db=db, port=port)
        rs.copy(self, table_name, **copy_args)

    def to_postgres(
        self,
        table_name,
        username=None,
        password=None,
        host=None,
        db=None,
        port=None,
        **copy_args,
    ):
        r"""
        Write a table to a Postgres database.

        Args:
            table_name: str
                The table name and schema (``my_schema.my_table``) to point the file.
            username: str
                Required if env variable ``PGUSER`` not populated
            password: str
                Required if env variable ``PGPASSWORD`` not populated
            host: str
                Required if env variable ``PGHOST`` not populated
            db: str
                Required if env variable ``PGDATABASE`` not populated
            port: int
                Required if env variable ``PGPORT`` not populated.
            `**copy_args`: kwargs
                See :func:`~parsons.databases.Postgres.copy`` for options.

        """

        from parsons.databases.postgres import Postgres

        pg = Postgres(username=username, password=password, host=host, db=db, port=port)
        pg.copy(self, table_name, **copy_args)

    def to_bigquery(
        self,
        table_name: str,
        app_creds: str | None = None,
        project: str | None = None,
        **kwargs,
    ):
        """
        Write a table to BigQuery

        Args:
            table_name: str
                Table name to write to in BigQuery; this should be in `schema.table` format
            app_creds: str
                A credentials json string or a path to a json file. Not required
                if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project: str
                The project which the client is acting on behalf of. If not passed
                then will use the default inferred environment.
            `**kwargs`: kwargs
                Additional keyword arguments passed into the `.copy()` function (`if_exists`,
                `max_errors`, etc.)

        """

        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)
        bq.copy(self, table_name=table_name, **kwargs)

    def to_petl(self):
        return self.table

    def to_civis(
        self,
        table,
        api_key=None,
        db=None,
        max_errors=None,
        existing_table_rows: Literal["fail", "truncate", "append", "drop"] = "fail",
        diststyle: Literal["even", "all", "key"] | None = None,
        distkey=None,
        sortkey1=None,
        sortkey2=None,
        wait=True,
        **civisargs,
    ):
        """
        Write the table to a Civis Redshift cluster. Additional key word
        arguments can passed to `civis.io.dataframe_to_civis()
        <https://civis-python.readthedocs.io/en/v1.9.0/generated/civis.io.dataframe_to_civis.html#civis.io.dataframe_to_civis>`_

        `Args`
            table: str
                The schema and table you want to upload to. E.g.,
                'scratch.table'. Schemas or tablenames with periods must be
                double quoted, e.g. 'scratch."my.table"'.
            api_key: str
                Your Civis API key. If not given, the CIVIS_API_KEY environment
                variable will be used.
            db: str or int
                The Civis Database. Can be database name or ID
            max_errors: int
                The maximum number of rows with errors to remove from
                the import before failing.
            diststyle: str
                The distribution style for the table. One of `'even'`, `'all'`
                or `'key'`.
            existing_table_rows: str
                The behaviour if a table with the requested name already
                exists. One of `'fail'`, `'truncate'`, `'append'` or `'drop'`.
                Defaults to `'fail'`.
            distkey: str
                The column to use as the distkey for the table.
            sortkey1: str
                The column to use as the sortkey for the table.
            sortkey2: str
                The second column in a compound sortkey for the table.
            wait: boolean
                Wait for write job to complete before exiting method.
        """

        from parsons.civis.civisclient import CivisClient

        civis = CivisClient(db=db, api_key=api_key)
        return civis.table_import(
            self,
            table,
            max_errors=max_errors,
            existing_table_rows=existing_table_rows,
            diststyle=diststyle,
            distkey=distkey,
            sortkey1=sortkey1,
            sortkey2=sortkey2,
            wait=wait,
            **civisargs,
        )

    @classmethod
    def from_avro(cls, local_path, limit=None, skips=0, **avro_args):
        r"""
        Create a ``parsons table`` from an Avro file.

        Args:
            local_path: str
                The path to the Avro file.
            limit: int, optional
                The maximum number of rows to extract. Default is ``None`` (all rows).
            skips: int, optional
                The number of rows to skip from the start. Default is 0.
            `**avro_args`: kwargs
                Additional arguments passed to `fastavro.reader`.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        return cls(petl.fromavro(local_path, limit=limit, skips=skips, **avro_args))

    @classmethod
    def from_csv(cls, local_path, **csvargs):
        r"""
        Create a ``parsons table`` object from a CSV file

        Args:
            local_path: obj
                A csv formatted local path, url or ftp. If this is a
                file path that ends in ".gz", the file will be decompressed first.
            `**csvargs`: kwargs
                ``csv_reader`` optional arguments
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        remote_prefixes = ["http://", "https://", "ftp://", "s3://"]
        is_remote_file = bool(any(map(local_path.startswith, remote_prefixes)))

        if not is_remote_file and not files.has_data(local_path):
            raise ValueError("CSV file is empty")

        return cls(petl.fromcsv(local_path, **csvargs))

    @classmethod
    def from_csv_string(cls, str, **csvargs):
        """
        Create a ``parsons table`` object from a string representing a CSV.

        Args:
            str: str
                The string object to convert to a table
            `**csvargs`: kwargs
                ``csv_reader`` optional arguments
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        bytesio = io.BytesIO(str.encode("utf-8"))
        memory_source = petl.io.sources.MemorySource(bytesio.read())
        return cls(petl.fromcsv(memory_source, **csvargs))

    @classmethod
    def from_columns(cls, cols, header=None):
        """
        Create a ``parsons table`` from a list of lists organized as columns

        Args:
            cols: list
                A list of lists organized as columns
            header: list
                List of column names. If not specified, will use dummy column names
        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        return cls(petl.fromcolumns(cols, header=header))

    @classmethod
    def from_json(cls, local_path, header=None, line_delimited=False):
        """
        Create a ``parsons table`` from a json file

        Args:
            local_path: list
                A JSON formatted local path, url or ftp. If this is a
                file path that ends in ".gz", the file will be decompressed first.
            header: list
                List of columns to use for the destination table. If omitted, columns will
                be inferred from the initial data in the file.
            line_delimited: bool
                Whether the file is line-delimited JSON (with a row on each line), or a proper
                JSON file.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        if line_delimited:
            open_fn = gzip.open if files.is_gzip_path(local_path) else open

            with open_fn(local_path, "r") as file:
                rows = [json.loads(line) for line in file]
            return cls(rows)

        else:
            return cls(petl.fromjson(local_path, header=header))

    @classmethod
    def from_redshift(cls, sql, username=None, password=None, host=None, db=None, port=None):
        """
        Create a ``parsons table`` from a Redshift query.

        To pull an entire Redshift table, use a query like ``SELECT * FROM tablename``.

        Args:
            sql: str
                A valid SQL statement
            username: str
                Required if env variable ``REDSHIFT_USERNAME`` not populated
            password: str
                Required if env variable ``REDSHIFT_PASSWORD`` not populated
            host: str
                Required if env variable ``REDSHIFT_HOST`` not populated
            db: str
                Required if env variable ``REDSHIFT_DB`` not populated
            port: int
                Required if env variable ``REDSHIFT_PORT`` not populated. Port 5439 is typical.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """

        from parsons.databases.redshift import Redshift

        rs = Redshift(username=username, password=password, host=host, db=db, port=port)
        return rs.query(sql)

    @classmethod
    def from_postgres(cls, sql, username=None, password=None, host=None, db=None, port=None):
        """
        Args:
            sql: str
                A valid SQL statement
            username: str
                Required if env variable ``PGUSER`` not populated
            password: str
                Required if env variable ``PGPASSWORD`` not populated
            host: str
                Required if env variable ``PGHOST`` not populated
            db: str
                Required if env variable ``PGDATABASE`` not populated
            port: int
                Required if env variable ``PGPORT`` not populated.

        """

        from parsons.databases.postgres import Postgres

        pg = Postgres(username=username, password=password, host=host, db=db, port=port)
        return pg.query(sql)

    @classmethod
    def from_s3_csv(
        cls,
        bucket,
        key,
        from_manifest=False,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        **csvargs,
    ):
        r"""
        Create a ``parsons table`` from a key in an S3 bucket.

        Args:
            bucket: str
                The S3 bucket.
            key: str
                The S3 key
            from_manifest: bool
                If True, treats `key` as a manifest file and loads all urls into a `parsons.Table`.
                Defaults to False.
            aws_access_key_id: str
                Required if not included as environmental variable.
            aws_secret_access_key: str
                Required if not included as environmental variable.
            `**csvargs`: kwargs
                ``csv_reader`` optional arguments
        Returns:
            `parsons.Table` object

        """

        from parsons.aws import S3

        s3 = S3(aws_access_key_id, aws_secret_access_key)

        if from_manifest:
            with Path(s3.get_file(bucket, key)).open() as fd:
                manifest = json.load(fd)

            s3_keys = [x["url"] for x in manifest["entries"]]

        else:
            s3_keys = [f"s3://{bucket}/{key}"]

        tbls = []
        for key in s3_keys:
            # TODO handle urls that end with '/', i.e. urls that point to "folders"
            _, _, bucket_, key_ = key.split("/", 3)
            file_ = s3.get_file(bucket_, key_)
            if files.compression_type_for_path(key_) == "zip":
                file_ = zip_archive.unzip_archive(file_)

            tbls.append(petl.fromcsv(file_, **csvargs))

        return cls(petl.cat(*tbls))

    @classmethod
    def from_bigquery(cls, sql: str, app_creds: str | None = None, project: str | None = None):
        """
        Create a ``parsons table`` from a BigQuery statement.

        To pull an entire BigQuery table, use a query like ``SELECT * FROM {{ table }}``.

        Args:
            sql: str
                A valid SQL statement
            app_creds: str
                A credentials json string or a path to a json file. Not required
                if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project: str
                The project which the client is acting on behalf of. If not passed
                then will use the default inferred environment.

        Returns:
            Parsons Table
                See :ref:`parsons-table` for output options.

        """
        # TODO: Should users be able to pass in kwargs here? For parameters?

        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)

        return bq.query(sql=sql)

    @classmethod
    def from_dataframe(cls, dataframe, include_index=False):
        """
        Create a ``parsons table`` from a Pandas dataframe.

        Args:
            dataframe: dataframe
                A valid Pandas dataframe objectt
            include_index: boolean
                Include index column

        """

        return cls(petl.fromdataframe(dataframe, include_index=include_index))
