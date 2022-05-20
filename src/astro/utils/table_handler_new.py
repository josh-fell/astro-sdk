import inspect
from typing import Optional

from astro.sql.table import Table


def _pull_first_table_from_parameters(parameters) -> Optional[Table]:
    first_table = None
    params_of_table_type = [
        param for param in parameters.values() if isinstance(param, Table)
    ]
    if (
        len(params_of_table_type) == 1
        or len({param.conn_id for param in params_of_table_type}) == 1
    ):
        first_table = params_of_table_type[0]
    return first_table


def _pull_first_table_from_op_kwargs(op_kwargs, python_callable) -> Optional[Table]:
    first_table = None
    kwargs_of_table_type = [
        op_kwargs[kwarg.name]
        for kwarg in inspect.signature(python_callable).parameters.values()
        if isinstance(op_kwargs[kwarg.name], Table)
    ]
    if (
        len(kwargs_of_table_type) == 1
        or len({kwarg.conn_id for kwarg in kwargs_of_table_type}) == 1
    ):
        first_table = kwargs_of_table_type[0]
    return first_table


def _pull_first_table_from_op_args(op_args) -> Optional[Table]:
    first_table = None
    args_of_table_type = [arg for arg in op_args if isinstance(arg, Table)]
    # Check to see if all tables belong to same conn_id. Otherwise, we this can go wrong for cases
    # 1. When we have tables from different DBs.
    # 2. When we have tables from different conn_id, since they can be configured with different
    # database/schema etc.
    if (
        len(args_of_table_type) == 1
        or len({arg.conn_id for arg in args_of_table_type}) == 1
    ):
        first_table = args_of_table_type[0]
    return first_table


def find_first_table(
    op_args, op_kwargs, python_callable, parameters
) -> Optional[Table]:
    """
    When we create our SQL operation, we run with the assumption that the first table given is the "main table".
    This means that a user doesn't need to define default conn_id, database, etc. in the function unless they want
    to create default values.
    """
    first_table: Optional[Table] = None
    if op_args:
        first_table = _pull_first_table_from_op_args(op_args=op_args)

    if not first_table and op_kwargs and python_callable:
        first_table = _pull_first_table_from_op_kwargs(
            op_kwargs=op_kwargs, python_callable=python_callable
        )

    # If there is no first table via op_ags or kwargs, we check the parameters
    if not first_table and parameters:
        first_table = _pull_first_table_from_parameters(parameters=parameters)
    return first_table
