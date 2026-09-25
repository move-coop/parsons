from __future__ import annotations

import gzip
import io
import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, overload

import petl

from parsons.utilities import files, zip_archive

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    from civis.futures import CivisFuture
    from pandas import DataFrame

    from parsons import Table
    from parsons.google.google_cloud_storage import GoogleCloudStorage


class ToFrom:
    """ToFrom methods for parsons Tables."""

    table: petl.util.base.Table
    __iter__: Callable[[], Iterator[dict[str, Any]]]

    def to_dataframe(
        self,
        index: str | Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        columns: Sequence[str] | None = None,
        coerce_float: bool = False,
    ) -> DataFrame:
        """
        Output Table as a Pandas Dataframe.

        In order to use this method, you must have the pandas library installed.
        You can install it with `pip install parsons[pandas]`.

        Args:
            index:
                Field of array to use as the index,
                alternately a specific set of input labels to use.
            exclude:
                Columns or fields to exclude
            columns:
                Column names to use. If the passed data do not have names
                associated with them, this argument provides names for the
                columns. Otherwise this argument indicates the order of the
                columns in the result (any names not found in the data will
                become all-NA columns).

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
        local_path: Path | str | None = None,
        encoding: str | None = None,
        errors: str | None = "strict",
        index_header: bool = False,
        caption: str | None = None,
        tr_style: str | Callable | None = None,
        td_styles: str | Callable | dict[str, str | Callable] | None = None,
        truncate: int | None = None,
    ) -> str:
        """
        Output table to HTML file.

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the html locally.
                If not specified, a temporary file will be created and returned.
            encoding:
                The encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`__
            errors: Raise an Error if encountered
            index_header: Prepend index to column names; Defaults to False.
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

        return str(local_path)

    def to_avro(
        self,
        target: Path | str,
        schema: dict | None = None,
        sample: int = 9,
        codec: Literal["null", "deflate", "bzip2", "snappy", "zstandard", "lz4", "xz"] = "deflate",
        compression_level: int | None = None,
        **avro_args,
    ) -> str:
        """
        Output table to an Avro file.

        In order to use this method, you must have the fastavro library installed.
        You can install it with `pip install parsons[avro]`.

        Write the table into a new avro file according to schema passed.

        This method assume that each column has values with the same type
        for all rows of the source `table`.

        Avro is a data serialization framework that is generally is faster
        and safer than text formats like Json, XML or CSV.

        Args:
            target:
                The file path for creating the avro file. Note that if a
                file already exists at the given location, it will be overwritten.
            schema:
                Defines the rows field structure of the file.
                Check `fastavro documentation <https://fastavro.readthedocs.io/en/latest/>`__ and
                `Avro schema reference <https://avro.apache.org/docs/++version++/specification/_print/>`__ for details.
            sample:
                Defines how many rows are inspectedfor discovering the field types
                and building a schema for the avro file when the `schema` argument is not passed.
            codec:
                The `codec` argument (string, optional) sets the compression codec used to
                shrink data in the file.
            compression_level:
                Sets the level of compression to use with the specified codec, if supported.
            `**avro_args`:
                Additional options to foward directly to fastavro.
                See `fastavro documentation <https://fastavro.readthedocs.io/en/latest/>`__ for reference.

        Returns:
            The path of the written file

        .. code-block:: python
            :caption: Example usage for writing files

            table2 = [
                ['name', 'friends', 'age'],
                ['Bob', 42, 33],
                ['Jim', 13, 69],
                ['Joe', 86, 17],
                ['Ted', 23, 51].
            ]

            # Define Avro schema
            schema2 = {
                'doc': 'Some people records.',
                'name': 'People',
                'namespace': 'test',
                'type': 'record',
                'fields': [
                    {'name': 'name', 'type': 'string'},
                    {'name': 'friends', 'type': 'int'},
                    {'name': 'age', 'type': 'int'},
                ],
            }

            # Demonstrate writing with Table.toavro()
            from parsons import Table

            Table.toavro(table2, 'example.file2.avro', schema=schema2)

            # Read back with with Table.fromavro()
            tbl2 = Table.fromavro('example.file2.avro')

        .. table:: tbl2

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

        return str(target)

    def append_avro(
        self, target: Path | str, schema: dict | None = None, sample: int = 9, **avro_args
    ) -> str:
        """
        Append table to an existing Avro file.

        In order to use this method, you must have the fastavro library installed.
        You can install it with `pip install parsons[avro]`.

        This method assume that each column has values with the same type for all rows of the source table.

        Args:
            target: The file path for an existing avro file.
            schema:
                Defines the rows field structure of the file.
                Check `fastavro documentation <https://fastavro.readthedocs.io/en/latest/>`__ and
                `Avro schema reference <https://avro.apache.org/docs/++version++/specification/_print/>`__ for details.
            sample:
                Defines how many rows are inspectedfor discovering the field types
                and building a schema for the avro file when the `schema` argument is not passed.
            `**avro_args`:
                Additional options to foward directly to fastavro.
                See `fastavro documentation <https://fastavro.readthedocs.io/en/latest/>`__ for reference.

        Returns:
            The path of the updated file

        """
        petl.appendavro(self.table, target, schema=schema, sample=sample, **avro_args)

        return str(target)

    def to_csv(
        self,
        local_path: Path | str | None = None,
        temp_file_compression: Literal["gzip", "zip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        csv_name: str | None = None,
        **csvargs,
    ) -> str:
        """
        Output table to a CSV.

        Additional key word arguments are passed to :func:`csv.writer`. So, e.g.,
        to override the delimiter from the default CSV dialect, provide the delimiter keyword argument.

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the csv locally. If it ends in ``.gz`` or ``.zip``, the file will be
                compressed. If not specified, a temporary file will be created and returned,
                and that file will be removed automatically when the script is done running.
            temp_file_compression:
                If a temp file is requested (ie. no `local_path` is specified), the compression
                type for that file. Currently ``None``, ``gzip`` or ``zip`` are supported.
                If a `local_path` is specified, this argument is ignored.
            encoding:
                The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            write_header: Include header in output
            csv_name:
                If ``zip`` compression (either specified or inferred),
                the name of csv file within the archive.
            `**csvargs`: Additional arguments to pass to :func:`csv.writer`

        Returns:
            The path of the new file

        """
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

        return str(local_path)

    def append_csv(
        self, local_path: Path | str, encoding: str | None = None, errors: str = "strict", **csvargs
    ) -> str:
        """
        Append table to an existing CSV.

        Additional keyword arguments are passed to :func:`csv.writer`.
        So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument.

        Args:
            local_path:
                The local path of an existing CSV file.
                If it ends in ``.gz``, the file will be compressed.
            encoding:
                The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            `**csvargs`: Additional keyword arguments are passed to :func:`csv.writer`.

        Returns:
            The path of the updated csv file

        """
        petl.appendcsv(self.table, source=local_path, encoding=encoding, errors=errors, **csvargs)

        return str(local_path)

    def to_zip_csv(
        self,
        archive_path: Path | str | None = None,
        csv_name: str | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        if_exists: Literal["replace", "append"] = "replace",
        **csvargs,
    ) -> str:
        """
        Output table to a CSV in a zip archive.

        Additional key word arguments are passed to :func:`csv.writer`.
        So, e.g., to override the delimiter from the default CSV dialect,
        provide the delimiter keyword argument. Use this method if you would like to write
        multiple csv files to the same archive.

        .. warning::

            If a file already exists in the archive, it will be overwritten.

        Args:
            archive_path:
                The path to zip achive.
                If not specified, a temporary file will be created and returned.
            csv_name:
                The name of the csv file to be stored in the archive.
                If ``None``, will use the archive name.
            encoding:
                The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            write_header: Include header in output
            if_exists: What to do if archive already exists.
            `**csvargs`: Additional keyword arguments passed to :func:`csv.writer`.

        Returns:
            The path of the archive

        """
        if not archive_path:
            archive_path = files.create_temp_file(suffix=".zip")

        cf = self.to_csv(encoding=encoding, errors=errors, write_header=write_header, **csvargs)

        if not csv_name:
            csv_name = files.extract_file_name(str(archive_path), include_suffix=False) + ".csv"

        return str(
            zip_archive.create_archive(archive_path, cf, file_name=csv_name, if_exists=if_exists)
        )

    def to_json(
        self,
        local_path: Path | str | None = None,
        temp_file_compression: Literal["gzip"] | None = None,
        line_delimited: bool = False,
    ) -> str:
        """
        Output table to a JSON file.

        .. warning::

            If a file already exists at the given location, it will be overwritten.

        Args:
            local_path:
                The path to write the JSON locally. If it ends in ``.gz``, it will be
                compressed first. If not specified, a temporary file will be created and returned.
            temp_file_compression:
                If a temp file is requested (ie. no `local_path` is specified), the compression
                type for that file. If a `local_path` is specified, this argument is ignored.
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

        open_fn = gzip.open if files.is_gzip_path(local_path) else open

        with open_fn(local_path, "wt") as file:
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

        return str(local_path)

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
        errors: str = "strict",
        write_header: bool = True,
        rsa_private_key_file: Path | str | None = None,
        **csvargs,
    ) -> None:
        """
        Write the table to a CSV file on a remote SFTP server.

        Args:
            remote_path:
                The remote path of the file.
                If it ends in ``.gz``, the file will be compressed.
            host: The remote host
            username: The username to access the SFTP server
            password: The password to access the SFTP server
            port: The port number of the SFTP server
            encoding:
                The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            write_header: Include header in output
            rsa_private_key_file: str
                Absolute path to a private RSA key used to authenticate SFTP connection
            `**csvargs`: Additional keyword arguments passed to :func:`csv.writer`.

        """
        from parsons.sftp import SFTP

        rsa_private_key_file = str(rsa_private_key_file) if rsa_private_key_file else None
        compression = files.compression_type_for_path(remote_path)

        sftp_conn = SFTP(host, username, password, port, rsa_private_key_file)

        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            **csvargs,
        )

        sftp_conn.put_file(local_path, remote_path)

    @overload
    def to_s3_csv(
        self,
        bucket: str,
        key: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        compression: Literal["gzip", "zip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        acl: str = "bucket-owner-full-control",
        public_url: Literal[True] = ...,
        public_url_expires: int = 3600,
        use_env_token: bool = True,
        **csvargs,
    ) -> str: ...

    @overload
    def to_s3_csv(
        self,
        bucket: str,
        key: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        compression: Literal["gzip", "zip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        acl: str = "bucket-owner-full-control",
        public_url: Literal[False] = False,
        public_url_expires: int = 3600,
        use_env_token: bool = True,
        **csvargs,
    ) -> None: ...

    def to_s3_csv(
        self,
        bucket: str,
        key: str,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        compression: Literal["gzip", "zip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        acl: str = "bucket-owner-full-control",
        public_url: bool = False,
        public_url_expires: int = 3600,
        use_env_token: bool = True,
        **csvargs,
    ) -> str | None:
        """
        Write the table to an s3 object as a CSV.

        Args:
            bucket: The s3 bucket to upload to
            key:
                The s3 key to name the file.
                If it ends in ``.gz`` or ``.zip``, the file will be compressed.
            aws_access_key_id: Required if not included as environmental variable
            aws_secret_access_key: Required if not included as environmental variable
            compression: str
                The compression type for the s3 object.
                If specified, will override the key suffix.
            encoding: The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            write_header: Include header in output
            acl: The S3 permissions on the file
            public_url: Create a public link to the file
            public_url_expire:
                The time, in seconds, until the url expires (if `public_url` set to ``True``).
            use_env_token:
                Controls use of the ``AWS_SESSION_TOKEN`` environment variable for S3.
                Defaults to ``True``. Set to ``False`` in order to ignore the ``AWS_SESSION_TOKEN`` env
                variable even if the `aws_session_token` argument was not passed in.
            `**csvargs`: Additional arguments to pass to :func:`csv.reader`

        Returns:
            If `public_url` is ``True``, the public url of the file. Otherwise ``None``.

        """
        compression = compression or files.compression_type_for_path(key)
        csv_name = files.extract_file_name(key, include_suffix=False) + ".csv"

        local_path = self.to_csv(
            temp_file_compression=compression,
            encoding=encoding,
            errors=errors,
            write_header=write_header,
            csv_name=csv_name,
            **csvargs,
        )

        from parsons.aws import S3

        self.s3 = S3(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            use_env_token=use_env_token,
        )
        self.s3.put_file(bucket, key, local_path, acl=acl)

        if public_url:
            return self.s3.get_url(bucket, key, expires_in=public_url_expires)

        return None

    def to_gcs_csv(
        self,
        bucket_name: str,
        blob_name: str,
        gcs_client: GoogleCloudStorage | None = None,
        app_creds: str | None = None,
        project: str | None = None,
        compression: Literal["zip", "gzip"] | None = None,
        encoding: str | None = None,
        errors: str = "strict",
        write_header: bool = True,
        public_url: bool = False,
        public_url_expires: int = 60,
        **csvargs,
    ) -> str | None:
        """
        Write the table to a Google Cloud Storage blob as a CSV.

        Args:
            bucket_name: The bucket to upload to
            blob_name:
                The blob to name the file.
                If it ends in ``.gz`` or ``.zip``, the file will be compressed.
            gcs_client:
                The GCS client to use.
                If not specified, a default client will be initialized.
            app_creds:
                A credentials json string or a path to a json file.
                Not required if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project:
                The project which the client is acting on behalf of. If not passed
                then will use the default inferred environment.
            compression:
                The compression type for the csv.
                If specified, will override the key suffix.
            encoding:
                The CSV encoding type for `csv.writer() <https://docs.python.org/library/csv.html#csv.writer/>`_
            errors: Raise an Error if encountered
            write_header: Include header in output
            public_url: Create a public link to the file
            public_url_expire: The time, in minutes, until the url expires if `public_url` set to ``True``.
            `**csvargs`: Additional arguments to pass to :func:`csv.reader`

        Returns:
            If `public_url` is ``True``, the public url of the file. Otherwise ``None``.

        """
        compression = compression or files.compression_type_for_path(blob_name)
        csv_name = files.extract_file_name(blob_name, include_suffix=False) + ".csv"

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

        return None

    def to_redshift(
        self,
        table_name: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
        **copy_args,
    ) -> None:
        """
        Write a table to a Redshift database.

        Note, this requires you to pass AWS S3 credentials or store them as environmental variables.

        Args:
            table_name: The table name and schema (``my_schema.my_table``) to point the file.
            username: Required if env variable ``REDSHIFT_USERNAME`` not populated
            password: Required if env variable ``REDSHIFT_PASSWORD`` not populated
            host: Required if env variable ``REDSHIFT_HOST`` not populated
            db: Required if env variable ``REDSHIFT_DB`` not populated
            port: Required if env variable ``REDSHIFT_PORT`` not populated. Port 5439 is typical.
            `**copy_args`: See :meth:`~parsons.databases.redshift.redshift.Redshift.copy` for options.

        """
        from parsons.databases.redshift import Redshift

        rs = Redshift(username=username, password=password, host=host, db=db, port=port)
        rs.copy(self, table_name, **copy_args)

    def to_postgres(
        self,
        table_name: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
        **copy_args,
    ) -> None:
        """
        Write a table to a Postgres database.

        Args:
            table_name: The table name and schema (``my_schema.my_table``) to point the file.
            username: Required if env variable ``PGUSER`` not populated
            password: Required if env variable ``PGPASSWORD`` not populated
            host: Required if env variable ``PGHOST`` not populated
            db: Required if env variable ``PGDATABASE`` not populated
            port: Required if env variable ``PGPORT`` not populated.
            `**copy_args`: See :meth:`~parsons.databases.postgres.postgres.Postgres.copy` for options.

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
        Write a table to BigQuery.

        Args:
            table_name:
                Table name to write to in BigQuery.
                This should be in ``schema.table`` format.
            app_creds:
                A credentials json string or a path to a json file.
                Not required if ``GOOGLE_APPLICATION_CREDENTIALS`` env variable set.
            project:
                The project which the client is acting on behalf of.
                If not passed then will use the default inferred environment.
            `**kwargs`:
                Additional keyword arguments passed to :meth:`parsons.google.google_bigquery.GoogleBigQuery.copy`.
                (``if_exists``, ``max_errors``, etc.)

        """
        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)
        bq.copy(self, table_name=table_name, **kwargs)

    def to_petl(self) -> petl.util.base.Table:
        """Provide only the petl table."""
        return self.table

    @overload
    def to_civis(
        self,
        table: str,
        api_key: str | None = None,
        db: str | None = None,
        max_errors: int | None = None,
        existing_table_rows: Literal["fail", "truncate", "append", "drop"] = "fail",
        diststyle: Literal["even", "all", "key"] | None = None,
        distkey: str | None = None,
        sortkey1: str | None = None,
        sortkey2: str | None = None,
        wait: Literal[False] = ...,
        **civisargs,
    ) -> None: ...

    @overload
    def to_civis(
        self,
        table: str,
        api_key: str | None = None,
        db: str | None = None,
        max_errors: int | None = None,
        existing_table_rows: Literal["fail", "truncate", "append", "drop"] = "fail",
        diststyle: Literal["even", "all", "key"] | None = None,
        distkey: str | None = None,
        sortkey1: str | None = None,
        sortkey2: str | None = None,
        wait: Literal[True] = True,
        **civisargs,
    ) -> CivisFuture: ...

    def to_civis(
        self,
        table: str,
        api_key: str | None = None,
        db: str | None = None,
        max_errors: int | None = None,
        existing_table_rows: Literal["fail", "truncate", "append", "drop"] = "fail",
        diststyle: Literal["even", "all", "key"] | None = None,
        distkey: str | None = None,
        sortkey1: str | None = None,
        sortkey2: str | None = None,
        wait: bool = True,
        **civisargs,
    ) -> CivisFuture | None:
        """
        Write the table to a Civis Redshift cluster.

        Additional keyword arguments can passed to :func:`civis.io.dataframe_to_civis`.

        Args:
            table: str
                The schema and table you want to upload to (e.g. ``scratch.table``).
                Schemas or tablenames with periods must be double quoted (e.g. ``scratch."my.table"``).
            api_key:
                Your Civis API key. If not given,
                the CIVIS_API_KEY environment variable will be used.
            db: The Civis Database. Can be database name or ID
            max_errors:
                The maximum number of rows with errors to remove from the import before failing.
            existing_table_rows: The behaviour if a table with the requested name already exists.
            diststyle: The distribution style for the table.
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
        cls, local_path: Path | str, limit: int | None = None, skips: int | None = 0, **avro_args
    ) -> Table:
        """
        Create a Table from an Avro file.

        Args:
            local_path: The path to the Avro file.
            limit:
                The maximum number of rows to extract.
                Default is ``None`` (all rows).
            skips: The number of rows to skip from the start.
            `**avro_args`: Additional arguments passed to :func:`fastavro.reader`.

        """
        from parsons import Table

        return Table(petl.fromavro(local_path, limit=limit, skips=skips, **avro_args))

    @classmethod
    def from_csv(cls, local_path: Path | str, **csvargs) -> Table:
        """
        Create a Table from a CSV file.

        Args:
            local_path:
                A csv formatted local path, url or ftp.
                If this is a file path that ends in ``.gz``,
                the file will be decompressed first.
            `**csvargs`: Additional arguments to pass to :func:`csv.reader`

        """
        from parsons import Table

        remote_prefixes = ("http://", "https://", "ftp://", "s3://")
        if isinstance(local_path, str):
            is_remote_file = bool(any(map(local_path.startswith, remote_prefixes)))

        if not is_remote_file and not files.has_data(local_path):
            err_msg = "CSV file is empty"
            raise ValueError(err_msg)

        return Table(petl.fromcsv(local_path, **csvargs))

    @classmethod
    def from_csv_string(cls, csv_string: str, *, str: str | None = None, **csvargs) -> Table:
        """
        Create a Table from a string representing a CSV.

        Args:
            csv_string: The string object to convert to a table
            `**csvargs`: Additional arguments to pass to :func:`csv.reader`

        """
        from parsons import Table

        if str:
            warnings.warn(
                "`str` keyword argument to `from_csv_string` is deprecated, use `csv_string`",
                DeprecationWarning,
                stacklevel=2,
            )
            csv_string = str

        bytesio = io.BytesIO(csv_string.encode("utf-8"))
        memory_source = petl.io.sources.MemorySource(bytesio.read())

        return Table(petl.fromcsv(memory_source, **csvargs))

    @classmethod
    def from_columns(
        cls, cols: Sequence[Sequence[str]], header: Sequence[str] | None = None
    ) -> Table:
        """
        Create a Table from a list of lists organized as columns.

        Args:
            cols: A list of lists organized as columns
            header: List of column names. If not specified, will use dummy column names

        """
        from parsons import Table

        return Table(petl.fromcolumns(cols, header=header))

    @classmethod
    def from_json(
        cls,
        local_path: Path | str,
        header: Sequence[str] | None = None,
        line_delimited: bool = False,
    ) -> Table:
        """
        Create a Table from a json file.

        Args:
            local_path:
                A JSON formatted local path, url or ftp. If this is a
                file path that ends in ``.gz``, the file will be decompressed first.
            header:
                List of columns to use for the destination table.
                If omitted, columns will be inferred from the initial data in the file.
            line_delimited:
                Whether the file is line-delimited JSON (with a row on each line),
                or a proper JSON file. If ``True``, `local_path` must not be a remote file path.

        """
        from parsons import Table

        if line_delimited:
            open_fn = gzip.open if files.is_gzip_path(local_path) else open

            with open_fn(local_path, "r") as file:
                rows = [json.loads(line) for line in file]

            return Table(rows)

        return Table(petl.fromjson(local_path, header=header))

    @classmethod
    def from_redshift(
        cls,
        sql: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
        sql_parameters: list[Any] | dict[str, Any] | None = None,
    ) -> Table | None:
        """
        Create a Table from a Redshift query.

        To pull an entire Redshift table, use a query like ``SELECT * FROM tablename``.

        Args:
            sql: A valid SQL statement
            username: Required if env variable ``REDSHIFT_USERNAME`` not populated
            password: Required if env variable ``REDSHIFT_PASSWORD`` not populated
            host: Required if env variable ``REDSHIFT_HOST`` not populated
            db: Required if env variable ``REDSHIFT_DB`` not populated
            port: Required if env variable ``REDSHIFT_PORT`` not populated. Port 5439 is typical.
            sql_parameters:
                To include python variables in your query, it is recommended to pass them as parameters, following the documentation for
                `passing parameters to SQL queries <https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries>`__.
                Using the `sql_parameters` argument ensures that values are escaped properly, and avoids SQL injection attacks.

        """
        from parsons.databases.redshift import Redshift

        rs = Redshift(username=username, password=password, host=host, db=db, port=port)

        return rs.query(sql, parameters=sql_parameters)

    @classmethod
    def from_postgres(
        cls,
        sql: str,
        username: str | None = None,
        password: str | None = None,
        host: str | None = None,
        db: str | None = None,
        port: int | None = None,
        sql_parameters: list | None = None,
    ) -> Table | None:
        """
        Create a Table from a Postgres query.

        Args:
            sql: A valid SQL statement
            username: Required if env variable ``PGUSER`` not populated
            password: Required if env variable ``PGPASSWORD`` not populated
            host: Required if env variable ``PGHOST`` not populated
            db: Required if env variable ``PGDATABASE`` not populated
            port: Required if env variable ``PGPORT`` not populated.
            sql_parameters:
                To include python variables in your query, it is recommended to pass them as parameters, following the
                `psycopg style <http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries>`_.
                Using the `sql_parameters` argument ensures that values are escaped properly, and avoids SQL injection attacks.

        """
        from parsons.databases.postgres import Postgres

        pg = Postgres(username=username, password=password, host=host, db=db, port=port)

        return pg.query(sql, parameters=sql_parameters)

    @classmethod
    def from_s3_csv(
        cls,
        bucket: str,
        key: str,
        from_manifest: bool = False,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        **csvargs,
    ) -> Table:
        """
        Create a Table from a key in an S3 bucket.

        Args:
            bucket: The S3 bucket.
            key: The S3 key
            from_manifest: bool
                If True, treats `key` as a manifest file and loads all urls into a :ref:`Table`.
            aws_access_key_id: Required if not included as environmental variable.
            aws_secret_access_key: Required if not included as environmental variable.
            `**csvargs`: Additional arguments to pass to :func:`csv.reader`

        """
        from parsons import Table
        from parsons.aws import S3

        s3 = S3(aws_access_key_id, aws_secret_access_key)

        if from_manifest:
            with Path(s3.get_file(bucket, key)).open() as fd:
                manifest = json.load(fd)

            s3_keys = [x["url"] for x in manifest["entries"]]

        else:
            s3_keys = [f"s3://{bucket}/{key}"]

        tbls = []
        for s3_key in s3_keys:
            # TODO(dannyboy15): handle urls that end with '/', i.e. urls that point to "folders"
            _, _, bucket_, key_ = s3_key.split("/", 3)
            file_ = s3.get_file(bucket_, key_)
            if files.compression_type_for_path(key_) == "zip":
                file_ = zip_archive.unzip_archive(file_)

            tbls.append(petl.fromcsv(file_, **csvargs))

        return Table(petl.cat(*tbls))

    @classmethod
    def from_bigquery(
        cls,
        sql: str,
        app_creds: str | None = None,
        project: str | None = None,
        sql_parameters: list | dict | None = None,
    ) -> Table | None:
        """
        Create a Table from a BigQuery statement.

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
            sql_parameters:
                To include python variables in your query, it is recommended to pass them as parameters.
                Using the `sql_parameters` argument ensures that values are escaped properly, and avoids SQL injection attacks.

        """
        from parsons import GoogleBigQuery as BigQuery

        bq = BigQuery(app_creds=app_creds, project=project)

        # TODO(willyraedy): Should users be able to pass in kwargs here? For parameters? See PR #875
        return bq.query(sql=sql, parameters=sql_parameters)

    @classmethod
    def from_dataframe(cls, dataframe: DataFrame, include_index: bool = False) -> Table:
        """
        Create a Table from a Pandas dataframe.

        Args:
            dataframe: A valid Pandas dataframe objectt
            include_index: Include index column

        """
        from parsons import Table

        return Table(petl.fromdataframe(dataframe, include_index=include_index))
