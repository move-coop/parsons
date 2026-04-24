from __future__ import annotations

import gzip
import io
import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import petl
from typing_extensions import Self

from parsons.utilities import files, zip_archive

if TYPE_CHECKING:
    from collections.abc import Callable

    import civis
    import pandas  # noqa: ICN001 unconventional-import-alias

    from parsons import Table


class ToFrom:
    def to_dataframe(
        self,
        index: str | list[str] | None = None,
        exclude: list[str] | None = None,
        columns: list[str] | None = None,
        coerce_float: bool = False,
    ) -> pandas.DataFrame:
        """
        Outputs table as a Pandas Dataframe

        Args:
            index:
                Field of array to use as the index, alternately a specific set
                of input labels to use
            exclude: Columns or fields to exclude
            columns:
                Column names to use.
                If the passed data do not have names associated with them,
                this argument provides names for the columns.
                Otherwise this argument indicates the order of the
                columns in the result (any names not found in the data will
                become all-NA columns)

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
        local_path: str | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        index_header: bool = False,
        caption: str | None = None,
        tr_style: str | Callable | None = None,
        td_styles: str | dict | Callable | None = None,
        truncate: int | None = None,
    ) -> str:
        """
        Outputs table to html.

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the html locally. If not specified, a temporary file will be
                created and returned, and that file will be removed automatically when the script
                is done running.
            encoding:
                The encoding type for
                `csv.writer() <https://docs.python.org/3/library/csv.html#csv.writer/>`__
            errors: Raise an Error if encountered
            index_header:
                Prepend index to column names.
                Defaults to False.
            caption: A caption to include with the html table.
            tr_style: Style to be applied to the table row.
            td_styles: Styles to be applied to the table cells.
            truncate: Length of cell data.

        Returns:
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
        target: str,
        schema: dict | None = None,
        sample: int = 9,
        codec: Literal["null", "deflate", "bzip2", "snappy", "zstandard", "lz4", "xz"] = "deflate",
        compression_level: int | None = None,
        **avro_args,
    ) -> None:
        """
        Outputs table to an Avro file.

        In order to use this method, you must have the `fastavro` library installed.
        If using limited dependencies, you can install it with `pip install parsons[avro]`.

        Write the table into a new avro file according to schema passed.

        This method assume that each column has values with the same type
        for all rows of the source :ref:`Table`.

        Avro is a data serialization framework that is generally is faster
        and safer than text formats like Json, XML or CSV.

        Args:
            target:
                The file path for creating the avro file.
                Note that if a file already exists at the given location, it will be
                overwritten.
            schema:
                Defines the rows field structure of the file.
                Check `fastavro documentation`_ and `Avro schema reference`_ for details.
            sample:
                Defines how many rows are inspected
                for discovering the field types and building a schema for the avro file
                when the `schema` argument is not passed. Default is 9.
            codec:
                The `codec` argument (string, optional) sets the compression codec used to
                shrink data in the file. It can be 'null', 'deflate' (default), 'bzip2' or
                'snappy', 'zstandard', 'lz4', 'xz' (if installed)
            compression_level:
                Sets the level of compression to use with the specified codec (if the codec supports it)
            `**avro_args`:
                Additionally there are support for passing extra options in the
                argument `**avro_args` that are fowarded directly to fastavro. Check the
                `fastavro documentation`_ for reference.

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

        petl.toavro(
            self.table,
            target,
            schema=schema,
            sample=sample,
            codec=codec,
            compression_level=compression_level,
            **avro_args,
        )

    def append_avro(
        self, target: str, schema: dict | None = None, sample: int = 9, **avro_args
    ) -> None:
        """
        Append table to an existing Avro file.

        Write the table into an existing avro file according to schema passed.

        This method assume that each column has values with the same type
        for all rows of the source :ref:`Table`.

        Args:
            target: The file path for creating the avro file.
            schema:
                Defines the rows field structure of the file.
                Check `fastavro documentation`_ and `Avro schema reference`_ for details.
            sample:
                Defines how many rows are inspected for discovering the field types and
                building a schema for the avro file when the `schema` argument is not passed.
                Default is 9.
            `**avro_args`:
                Extra options fowarded directly to fastavro via :func:`petl.io.avro.appendavro`.
                Check the `fastavro documentation`_ for reference.

        """

        return petl.appendavro(self.table, target, schema=schema, sample=sample, **avro_args)

    def to_csv(
        self,
        local_path: str | None = None,
        temp_file_compression: Literal["gzip", "zip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        csv_name: str | None = None,
        **csvargs,
    ) -> str:
        r"""
        Outputs table to a CSV.

        Additional key word arguments are passed to :func:`csv.writer`.
        So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument.

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the csv locally.
                If it ends in ".gz" or ".zip", the file will be compressed.
                If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            temp_file_compression:
                If a temp file is requested (ie. no ``local_path`` is specified), the compression
                type for that file. Currently "None", "gzip" or "zip" are supported.
                If a ``local_path`` is specified, this argument is ignored.
            encoding:
                The CSV encoding type for :func:`csv.writer`.
            errors: Raise an Error if encountered
            write_header: Include header in output
            csv_name:
                If ``zip`` compression (either specified or inferred),
                the name of csv file within the archive.
            `**csvargs`: :func:`csv.writer` optional arguments.

        Returns:
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

    def append_csv(
        self, local_path: str, encoding: str | None = None, errors: str = "strict", **csvargs
    ) -> str:
        r"""
        Appends table to an existing CSV.

        Additional additional key word arguments are passed to :func:`csv.writer`.
        So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument.

        Args:
            local_path:
                The local path of an existing CSV file.
                If it ends in ".gz", the file will be compressed.
            encoding:
                The CSV encoding type for :func:`csv.writer`.
            errors: Raise an Error if encountered
            `**csvargs`: :func:`csv.writer` optional arguments

        Returns:
            The path of the file

        """

        petl.appendcsv(self.table, source=local_path, encoding=encoding, errors=errors, **csvargs)
        return local_path

    def to_zip_csv(
        self,
        archive_path: str | None = None,
        csv_name: str | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        if_exists: Literal["replace", "append"] = "replace",
        **csvargs,
    ) -> str:
        r"""
        Outputs table to a CSV in a zip archive. Additional key word arguments are passed to
        :func:`csv.writer`. So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument. Use thismethod if you would like to write
        multiple csv files to the same archive.

        .. warning::

            If a file already exists in the archive, it will be overwritten.

        Args:
            archive_path:
                The path to zip achive.
                If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            csv_name:
                The name of the csv file to be stored in the archive.
                If ``None`` will use the archive name.
            encoding:
                The CSV encoding type for :func:`csv.writer`.
            errors: Raise an Error if encountered
            write_header: Include header in output
            if_exists:
                If archive already exists, one of 'replace' or 'append'.
                See :func:`parsons.utilities.zip_archive.create_archive`.
            `**csvargs`: :func:`csv.writer` optional arguments

        Returns:
            The path of the archive

        Raises:
            ValueError: If CSV file name could not be extracted from the archive path.

        """

        if not archive_path:
            archive_path = files.create_temp_file(suffix=".zip")

        cf = self.to_csv(encoding=encoding, errors=errors, write_header=write_header, **csvargs)

        csv_name = files.extract_file_name(archive_path, include_suffix=False)
        if not csv_name:
            err_msg = f"Could not extract CSV name from {archive_path}"
            raise ValueError(err_msg)
        csv_filename = csv_name + ".csv"

        return zip_archive.create_archive(
            archive_path, cf, file_name=csv_filename, if_exists=if_exists
        )

    def to_json(
        self,
        local_path: str | None = None,
        temp_file_compression: Literal["gzip"] | None = None,
        line_delimited: bool = False,
    ) -> str:
        """
        Outputs table to a JSON file

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the JSON locally.
                If it ends in ".gz", it will be compressed first.
                If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            temp_file_compression:
                If a temp file is requested (ie. no ``local_path`` is specified),
                the compression type for that file.
                Currently "None" and "gzip" are supported.
                If a ``local_path`` is specified, this argument is ignored.
            line_delimited:
                Whether the file will be line-delimited JSON (with a row on each line),
                or a proper JSON file.

        Returns:
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

    def to_dicts(self) -> list[dict]:
        """Output table as a list of dicts."""

        return list(petl.dicts(self.table))

    def to_sftp_csv(
        self,
        remote_path: str,
        host: str,
        username: str,
        password: str,
        port: int = 22,
        encoding: str | None = None,
        compression: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        rsa_private_key_file: str | None = None,
        **csvargs,
    ) -> None:
        r"""
        Writes the table to a CSV file on a remote SFTP server

        Args:
            remote_path:
                The remote path of the file.
                If it ends in '.gz', the file will be compressed.
            host: The remote host
            username: The username to access the SFTP server
            password: The password to access the SFTP server
            port: The port number of the SFTP server
            encoding:
                The CSV encoding type for :func:`csv.writer`.
            errors: Raise an Error if encountered
            write_header: Include header in output
            rsa_private_key_file:
                Absolute path to a private RSA key used to authenticate stfp connection
            `**csvargs`: :func:`csv.writer` optional arguments.

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
        bucket: str,
        key: str,
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
    ) -> str | None:
        r"""
        Writes the table to an s3 object as a CSV

        Args:
            bucket: str
                The s3 bucket to upload to
            key: str
                The s3 key to name the file.
                If it ends in '.gz' or '.zip', the file will be compressed.
            aws_access_key_id: str
                Required if not included as environmental variable
            aws_secret_access_key: str
                Required if not included as environmental variable
            compression: str
                The compression type for the s3 object. Currently "None", "zip" and "gzip" are
                supported. If specified, will override the key suffix.
            encoding: str
                The CSV encoding type for :func:`csv.writer`.
            errors: str
                Raise an Error if encountered
            write_header: bool
                Include header in output
            public_url: bool
                Create a public link to the file
            public_url_expire: 3600
                The time, in seconds, until the url expires if ``public_url`` set to ``True``.
            acl: str
                The S3 permissions on the file
            use_env_token: bool
                Controls use of the ``AWS_SESSION_TOKEN`` environment variable for S3. Defaults
                to ``True``. Set to ``False`` in order to ignore the ``AWS_SESSION_TOKEN`` env
                variable even if the ``aws_session_token`` argument was not passed in.
            `**csvargs`: kwargs
                :func:`csv.writer` optional arguments.

        Returns:
            Public url if specified, or ``None`` if not.

        Raises:
            ValueError: If the CSV file name could not be extracted from the s3 key.

        """

        compression = compression or files.compression_type_for_path(key)

        csv_name = files.extract_file_name(key, include_suffix=False)
        if not csv_name:
            err_msg = f"Could not extract CSV name from {key}"
            raise ValueError(err_msg)
        csv_filename = csv_name + ".csv"

        # Save the CSV as a temp file
        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            csv_name=csv_filename,
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
                The blob to name the file. If it ends in '.gz' or '.zip', the file will be compressed.
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
                The CSV encoding type for :func:`csv.writer`.
            errors: str
                Raise an Error if encountered
            write_header: bool
                Include header in output
            public_url: bool
                Create a public link to the file
            public_url_expire: 60
                The time, in minutes, until the url expires if ``public_url`` set to ``True``.
            `**csvargs`: kwargs
                :func:`csv.writer` optional arguments.

        Returns:
            Public url if specified. If not ``None``.

        Raises:
            ValueError: If the CSV file name could not be extracted from the blob name.

        """

        compression = compression or files.compression_type_for_path(blob_name)

        csv_name = files.extract_file_name(blob_name, include_suffix=False)
        if not csv_name:
            err_msg = f"Could not extract CSV name from {blob_name}"
            raise ValueError(err_msg)
        csv_filename = csv_name + ".csv"

        # Save the CSV as a temp file
        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            csv_name=csv_filename,
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
                See :meth:`~parsons.databases.redshift.redshift.Redshift.copy` for options.

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
                See :meth:`~parsons.databases.postgres.postgres.Postgres.copy` for options.

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
    ) -> None:
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
                Additional keyword arguments passed into
                :meth:`~parsons.google.google_bigquery.GoogleBigQuery.copy` (`if_exists`, `max_errors`, etc.)

        """

        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)
        bq.copy(self, table_name=table_name, **kwargs)

    def to_petl(self) -> petl.Table:
        """Access as PETL table."""
        return self.table

    def to_civis(
        self,
        table: str,
        api_key: str | None = None,
        db: str | int | None = None,
        max_errors: int | None = None,
        existing_table_rows: Literal["fail", "truncate", "append", "drop"] = "fail",
        diststyle: Literal["even", "all", "key"] | None = None,
        distkey: str | None = None,
        sortkey1: str | None = None,
        sortkey2: str | None = None,
        wait: bool = True,
        **civisargs,
    ) -> dict | civis.futures.CivisFuture:
        """
        Write the table to a Civis Redshift cluster.

        Additional key word arguments can passed to :func:`civis.io.dataframe_to_civis`.

        Args:
            table:
                The schema and table you want to upload to. E.g. 'scratch.table'.
                Schemas or tablenames with periods must be double quoted, e.g. 'scratch."my.table"'.
            api_key:
                Your Civis API key.
                If not given, the CIVIS_API_KEY environment variable will be used.
            db:
                The Civis Database.
                Can be the database name or ID.
            max_errors:
                The maximum number of rows with errors to remove from the import before failing.
            diststyle:
                The distribution style for the table.
                One of `'even'`, `'all'` or `'key'`.
            existing_table_rows:
                The behaviour if a table with the requested name already exists.
                One of `'fail'`, `'truncate'`, `'append'` or `'drop'`.
                Defaults to `'fail'`.
            distkey: The column to use as the distkey for the table.
            sortkey1: The column to use as the sortkey for the table.
            sortkey2: The second column in a compound sortkey for the table.
            wait: Wait for write job to complete before exiting method.

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
    def from_avro(
        cls, local_path: str, limit: int | None = None, skips: int = 0, **avro_args
    ) -> Self:
        r"""
        Create a `:ref:`Table`` from an Avro file.

        Args:
            local_path: The path to the Avro file.
            limit:
                The maximum number of rows to extract.
                Default is ``None`` (all rows).
            skips:
                The number of rows to skip from the start.
                Default is 0.
            `**avro_args`: Additional arguments passed to :class:`fastavro._read_py.reader`.

        """

        return cls(petl.fromavro(local_path, limit=limit, skips=skips, **avro_args))

    @classmethod
    def from_csv(cls, local_path: str, **csvargs) -> Self:
        r"""
        Create a `:ref:`Table`` object from a CSV file

        Args:
            local_path:
                A csv formatted local path, url or ftp.
                If this is a file path that ends in ".gz", the file will be decompressed first.
            `**csvargs`: :func:`csv.reader` optional arguments

        Raises:
            ValueError: If the CSV file is empty.

        """

        remote_prefixes = ["http://", "https://", "ftp://", "s3://"]
        is_remote_file = bool(any(map(local_path.startswith, remote_prefixes)))

        if not is_remote_file and not files.has_data(local_path):
            raise ValueError("CSV file is empty")

        return cls(petl.fromcsv(local_path, **csvargs))

    @classmethod
    def from_csv_string(cls, str: str, **csvargs) -> Self:
        """
        Create a `:ref:`Table`` object from a string representing a CSV.

        Args:
            str: The string object to convert to a table
            `**csvargs`: :func:`csv.reader` optional arguments

        """

        bytesio = io.BytesIO(str.encode("utf-8"))
        memory_source = petl.io.sources.MemorySource(bytesio.read())
        return cls(petl.fromcsv(memory_source, **csvargs))

    @classmethod
    def from_columns(cls, cols: list[list], header: list[str] | None = None) -> Self:
        """
        Create a `:ref:`Table`` from a list of lists organized as columns

        Args:
            cols: A list of lists organized as columns
            header:
                List of column names.
                If not specified, will use dummy column names

        """

        return cls(petl.fromcolumns(cols, header=header))

    @classmethod
    def from_json(
        cls, local_path: str, header: list[str] | None = None, line_delimited: bool = False
    ) -> Self:
        """
        Create a `:ref:`Table`` from a json file

        Args:
            local_path:
                A JSON formatted local path, url or ftp.
                If this is a file path that ends in ".gz", the file will be decompressed first.
            header:
                List of columns to use for the destination table.
                If omitted, columns will be inferred from the initial data in the file.
            line_delimited:
                Whether the file is line-delimited JSON (with a row on each line), or a proper JSON file.

        """

        if line_delimited:
            open_fn = gzip.open if files.is_gzip_path(local_path) else open

            with open_fn(local_path, "r") as file:
                rows = [json.loads(line) for line in file]
            return cls(rows)

        else:
            return cls(petl.fromjson(local_path, header=header))

    @classmethod
    def from_redshift(
        cls,
        sql: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
    ) -> Table:
        """
        Create a `:ref:`Table`` from a Redshift query.

        To pull an entire Redshift table, use a query like ``SELECT * FROM tablename``.

        Args:
            sql: A valid SQL statement
            username: Required if env variable ``REDSHIFT_USERNAME`` not populated
            password: Required if env variable ``REDSHIFT_PASSWORD`` not populated
            host: Required if env variable ``REDSHIFT_HOST`` not populated
            db: Required if env variable ``REDSHIFT_DB`` not populated
            port:
                Required if env variable ``REDSHIFT_PORT`` not populated.
                Port 5439 is typical.

        """

        from parsons.databases.redshift import Redshift

        rs = Redshift(username=username, password=password, host=host, db=db, port=port)
        return rs.query(sql)

    @classmethod
    def from_postgres(
        cls,
        sql: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
    ) -> Table | None:
        """
        Args:
            sql: A valid SQL statement
            username: Required if env variable ``PGUSER`` not populated
            password: Required if env variable ``PGPASSWORD`` not populated
            host: Required if env variable ``PGHOST`` not populated
            db: Required if env variable ``PGDATABASE`` not populated
            port: Required if env variable ``PGPORT`` not populated.

        """

        from parsons.databases.postgres import Postgres

        pg = Postgres(username=username, password=password, host=host, db=db, port=port)
        return pg.query(sql)

    @classmethod
    def from_s3_csv(
        cls,
        bucket: str,
        key: str,
        from_manifest: bool = False,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        **csvargs,
    ) -> Self:
        r"""
        Create a `:ref:`Table`` from a key in an S3 bucket.

        Args:
            bucket: The S3 bucket.
            key: The S3 key
            from_manifest:
                If True, treats `key` as a manifest file and loads all urls into a :ref:`Table`.
                Defaults to False.
            aws_access_key_id: Required if not included as environmental variable.
            aws_secret_access_key: Required if not included as environmental variable.
            `**csvargs`: :func:`csv.reader` optional arguments

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
    def from_bigquery(
        cls, sql: str, app_creds: str | None = None, project: str | None = None
    ) -> Self:
        """
        Create a `:ref:`Table`` from a BigQuery statement.

        To pull an entire BigQuery table, use a query like ``SELECT * FROM {{ table }}``.

        Args:
            sql: A valid SQL statement.
            app_creds:
                A credentials json string or a path to a json file.
                Not required if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project:
                The project which the client is acting on behalf of.
                If not passed then will use the default inferred environment.

        """
        # TODO: Should users be able to pass in kwargs here? For parameters?

        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)

        return bq.query(sql=sql)

    @classmethod
    def from_dataframe(cls, dataframe: pandas.DataFrame, include_index: bool = False) -> Self:
        """
        Create a `:ref:`Table`` from a Pandas dataframe.

        Args:
            dataframe: A valid Pandas dataframe objectt
            include_index: Include index column

        """

        return cls(petl.fromdataframe(dataframe, include_index=include_index))
