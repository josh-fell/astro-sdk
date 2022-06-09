import logging
import pathlib

import pytest
from airflow.decorators import task
from airflow.utils import timezone

from astro import sql as aql
from astro.constants import Database
from astro.files import File
from astro.sql.table import Table
from tests.sql.operators import utils as test_utils

# Import Operator

log = logging.getLogger(__name__)
DEFAULT_DATE = timezone.datetime(2016, 1, 1)
CWD = pathlib.Path(__file__).parent


@task()
def add_one(input):
    print(f"current number is {input}")
    return input + 1


@aql.transform
def select_all(input_table: Table):
    return "SELECT * FROM {{input_table}}"


@pytest.mark.parametrize(
    "database_table_fixture",
    [
        {
            "database": Database.SQLITE,
            "file": File(path=str(CWD) + "/../../data/homes2.csv"),
        },
    ],
    indirect=True,
)
def test_cleanup_dag(sample_astro_dag, database_table_fixture):
    db, test_table = database_table_fixture
    with sample_astro_dag:
        for i in range(3):
            add_one(i)
        select_all(test_table)

    test_utils.run_dag(sample_astro_dag)
