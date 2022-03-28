import os
from typing import Union

from airflow.hooks.base import BaseHook
from airflow.models import BaseOperator

from astro.constants import DEFAULT_CHUNK_SIZE
from astro.sql.table import Table, TempTable, create_table_name
from astro.utils import get_hook

from astro.utils.file import get_filetype, get_size, is_binary, is_small
from astro.utils.load import (
    copy_remote_file_to_local,
    load_dataframe_into_sql_table,
    load_file_into_dataframe,
    load_file_into_sql_table,
    load_file_rows_into_dataframe,
)
from astro.utils.path import (
    get_location,
    get_paths,
    get_transport_params,
    is_local,
    validate_path,
)

from astro.utils.task_id_helper import get_task_id


class AgnosticLoadFile(BaseOperator):
    """Load S3/local table to postgres/snowflake database.

    :param path: File path.
    :type path: str
    :param output_table_name: Name of table to create.
    :type output_table_name: str
    :param file_conn_id: Airflow connection id of input file (optional)
    :type file_conn_id: str
    :param output_conn_id: Database connection id.
    :type output_conn_id: str
    """

    template_fields = (
        "output_table",
        "file_conn_id",
        "path",
    )

    def __init__(
        self,
        path,
        output_table: Union[TempTable, Table],
        file_conn_id="",
        chunksize=DEFAULT_CHUNK_SIZE,
        if_exists="replace",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.output_table: Union[TempTable, Table] = output_table
        self.path = path
        self.chunksize = chunksize
        self.file_conn_id = file_conn_id
        self.kwargs = kwargs
        self.output_table = output_table
        self.if_exists = if_exists

    def execute(self, context):
        """
        Load an existing dataset from a supported file into a SQL table.
        """
        if self.file_conn_id:
            BaseHook.get_connection(self.file_conn_id)

        hook = get_hook(
            conn_id=self.output_table.conn_id,
            database=self.output_table.database,
            schema=self.output_table.schema,
            warehouse=self.output_table.warehouse,
        )
        paths = get_paths(self.path, self.file_conn_id)
        transport_params = get_transport_params(paths[0], self.file_conn_id)

        if self.output_table.database == "postgres":
            return self.load_to_postgres(context, paths, hook, transport_params)
        else:
            return self.load_using_pandas(context, paths, hook, transport_params)

    def load_using_pandas(self, context, paths, hook, transport_params):
        """Loads csv/parquet table from local/S3/GCS with Pandas.

        Infers SQL database type based on connection then loads table to db.
        """
        self._configure_output_table(context)
        self.log.info(f"Loading {self.path} into {self.output_table}...")
        if_exists = self.if_exists
        for path in paths:
            pandas_dataframe = self._load_file_into_dataframe(path, transport_params)
            load_dataframe_into_sql_table(
                pandas_dataframe,
                self.output_table,
                hook,
                self.chunksize,
                if_exists=if_exists,
            )
            if_exists = "append"
        self.log.info(f"Completed loading the data into {self.output_table}.")
        return self.output_table

    def load_to_postgres(self, context, paths, hook, transport_params):
        """
        Loads a sequence of files into Postgres.
        Based on the size of the first file, either use `load_using_pandas` or use the Postgres native COPY statement.
        The implementation assumes that, if we have multiple files, that they all are similar in size to the first
        one. We may want to review this approach in the future.
        """
        # Steps used to load to Postgres:
        # 1. Download file(s), if not local
        # 2. Check size
        #    * small: use Pandas dataframe (takes less than 2s), job completed!
        #    * not small: continue to step (3) & following ones
        # 3. If the table does not exist, create it automagically identifying the column types by:
        #     i) loading a subset of rows into a Pandas dataframe (this varies depending on the original file type)
        #     ii) creating a SQL table in the target DB using the Pandas dataframe created in 3.i
        #     iii) emptying the table, so we can use the COPY command consistently to upload all the files
        # 4. Convert the original file to .csv with "," separators
        # 5. Use the COPY command to move the data into Postgres
        # 6. Delete the local file
        # 7. Repeat steps (1), (4), (5) and (6) until all files were copied to Postgres

        first_filepath = paths[0]
        file_type = get_filetype(first_filepath)

        credentials = transport_params

        # Identify if the files are remote. If they are, make a local copy of the first one.
        remote_source = False
        if not is_local(first_filepath):
            remote_source = True
            is_bin = is_binary(file_type)
            local_filepath = copy_remote_file_to_local(
                first_filepath, is_binary=is_bin, transport_params=credentials
            )

        # Performance tests (inside tests/benchmark) have shown that we can load small files efficiently using pandas
        # across all the supported databases. Therefore, if the files are small, we default to this strategy.
        if is_small(local_filepath):
            return self.load_using_pandas(context, paths, hook, credentials)
        else:
            engine = self.get_sql_alchemy_engine()
            if not sqlalchemy.inspect(engine).has_table(
                self.output_table.table_name, schema=self.output_table.schema
            ):
                self._create_an_empty_table_using_pandas(
                    local_filepath, file_type, hook
                )
            for path in paths:
                if remote_source and path != local_filepath:
                    local_filepath = copy_remote_file_to_local(
                        path, is_binary=is_bin, transport_params=credentials
                    )
                load_file_into_sql_table(
                    local_filepath, file_type, self.output_table.table_name, engine
                )
                if remote_source:
                    os.remove(local_filepath)
            return self.output_table

    def _configure_output_table(self, context):
        # TODO: Move this function to the SQLDecorator, so it can be reused across operators
        if isinstance(self.output_table, TempTable):
            self.output_table = self.output_table.to_table(
                create_table_name(context=context)
            )
        else:  # ?
            self.output_table.schema = self.output_table.schema or SCHEMA
        if not self.output_table.table_name:
            self.output_table.table_name = create_table_name(context=context)

    def _load_file_into_dataframe(self, filepath, transport_params):
        """Read file with Pandas.

        Select method based on `file_type` (S3 or local).
        """
        validate_path(filepath)
        filetype = get_filetype(filepath)
        return load_file_into_dataframe(filepath, filetype, transport_params)


def load_file(
    path,
    output_table=None,
    file_conn_id=None,
    task_id=None,
    if_exists="replace",
    **kwargs,
):
    """Convert AgnosticLoadFile into a function.

    Returns an XComArg object.

    :param path: File path.
    :type path: str
    :param output_table: Table to create
    :type output_table: Table
    :param file_conn_id: Airflow connection id of input file (optional)
    :type file_conn_id: str
    :param task_id: task id, optional.
    :type task_id: str
    """

    # Note - using path for task id is causing issues as it's a pattern and
    # contain chars like - ?, * etc. Which are not acceptable as task id.
    task_id = task_id if task_id is not None else get_task_id("load_file", "")

    return AgnosticLoadFile(
        task_id=task_id,
        path=path,
        output_table=output_table,
        file_conn_id=file_conn_id,
        if_exists=if_exists,
        **kwargs,
    ).output
