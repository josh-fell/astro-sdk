import pytest
from pandas import DataFrame

from astro import settings
from astro.databases.base import BaseDatabase
from astro.sql.table import Metadata, Table


class DatabaseSubclass(BaseDatabase):
    pass


def test_subclass_missing_not_implemented_methods_raise_exception():
    db = DatabaseSubclass(conn_id="fake_conn_id")
    with pytest.raises(NotImplementedError):
        db.hook

    with pytest.raises(NotImplementedError):
        db.sqlalchemy_engine

    with pytest.raises(NotImplementedError):
        db.connection

    with pytest.raises(NotImplementedError):
        db.default_metadata

    with pytest.raises(NotImplementedError):
        db.run_sql("SELECT * FROM inexistent_table")


def test_subclass_missing_load_pandas_dataframe_to_table_raises_exception():
    db = DatabaseSubclass(conn_id="fake_conn_id")
    table = Table()
    df = DataFrame()
    with pytest.raises(NotImplementedError):
        db.load_pandas_dataframe_to_table(df, table)


def test_subclass_missing_append_table_raises_exception():
    db = DatabaseSubclass(conn_id="fake_conn_id")
    source_table = Table()
    target_table = Table()
    with pytest.raises(NotImplementedError):
        db.append_table(source_table, target_table)


def test_populate_table_metadata_with_database_default_metadata():
    class DatabaseWithDefaultMetadata(BaseDatabase):
        @property
        def default_metadata(self):
            return Metadata(schema="conn_default_schema")

    temp_table = Table(conn_id="")
    database = DatabaseWithDefaultMetadata("")
    database.populate_table_metadata(temp_table)
    assert temp_table.metadata.schema == "conn_default_schema"


def test_populate_table_metadata_without_database_default_metadata():
    class DatabaseWithoutDefaultMetadata(BaseDatabase):
        @property
        def default_metadata(self):
            return None

    temp_table = Table(conn_id="")
    database = DatabaseWithoutDefaultMetadata("")
    database.populate_table_metadata(temp_table)
    assert temp_table.metadata.schema == settings.SCHEMA
