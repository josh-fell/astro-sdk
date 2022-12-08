.. _databricks:

======================
Databricks Integration
======================
Introduction

The Astro Python SDK now allows users to easily access and work with data stored in Databricks through the Delta API.

The Astro Python SDK provides a simple, yet powerful interface for working with Spark and Delta tables in Databricks, allowing users to take advantage of the scalability and performance of Databricks while maintaining the flexibility of Airflow DAG authoring and all the benefits of Airflow scheduling.

Installation
============
To use the Astro Python SDK with Databricks, complete the following steps:

The first step is to install the databricks submodule of the astro-sdk-python pip library. This can be done by running the following command:

.. code-block:: bash

    pip install 'astro-sdk-python[databricks]'

The second step is to create a connection to your Databricks cluster.
This requires creating a `personal access token <https://docs.databricks.com/dev-tools/api/latest/authentication.html>`_ in Databricks and creating a cluster with an http_endpoint. Once you have these, you can create a connection using the following syntax:


.. code-block:: yaml

    - conn_id: databricks_conn
      conn_type: databricks
      host: https://my-cluster.cloud.databricks.com/
      password: my-token
      extra:
        http_path: /sql/1.0/warehouses/foobar

.. note::

    You need to update the ``password`` with your token from Databricks.

You can also set a default databricks cluster to run all jobs against with this environment variable:

.. code-block:: bash

    AIRFLOW__ASTRO_SDK__DATABRICKS_CLUSTER_ID=<my databricks cluster>

Loading Data
============
Once you have installed the astro-sdk package and created a connection to your Databricks cluster, you can begin loading data into your Databricks cluster.

To load data into your Databricks cluster, you can use the same ``aql.load_file()`` function that works for all other databases.
The only thing that is different with delta is that you now can use the ``delta_options`` parameter to specify delta specific parameters(such as ``copy_options`` and ``format_options`` for the ``COPY INTO`` command).
Please note that when loading data into Delta using ``COPY INTO``, you must specify the filetype as Databricks does not automatically infer the data (this is not the case for autoloader).

Currently, only local files can be loaded using the ``aql.load_file()`` function. Support for loading data from S3 and GCS will be added soon.

To use the ``aql.load_file()`` function, you will need to specify the path to the file you want to load, the target Delta table you want to pass the result to.g

.. code-block:: python

    aql.load_file(
        input_file=File("data.csv"),
        output_table=Table(conn_id="my_databricks_conn"),
    )

If you have extra options you would like to add, you can user the ``load_options`` parameter to pass ``copy_into_parameters`` into the ``COPY INTO`` command.

Please note that we by default set ``header`` and ``inferSchema`` to true, so if you pass in your own commands you will need to set those values explicitly.

.. code-block:: python

    from astro.databricks.load_options import DeltaLoadOptions

    aql.load_file(
        input_file=File("data.csv"),
        output_table=Table(conn_id="my_databricks_conn"),
        databricks_options=DeltaLoadOptions(copy_into_format_options={"header": "true"}),
    )

We also offer a ``astro.databricks.load_options.default_delta_options`` for those who do not want to manually set options.
If you wish to use the defaults, you only need to set the ``AIRFLOW__ASTRO_SDK__DATABRICKS_CLUSTER_ID`` env variable
so the Astro SDK knows where to send your load_file job.


Querying Data
=============
Once you have loaded your data into Databricks, you can use the ``aql.transform()`` functions to create queries against the Delta tables. We currently do not support arbitrary Spark Python, but users can pass resulting Delta tables into local Pandas DataFrames (though please be careful of how large of a table you are passing).

For example, you can use the ``aql.transform()`` function decorator to create a query that selects all users over the age of 30 and returns the results as a Pandas DataFrame:

.. code-block:: python

    @aql.transform()
    def get_eligible_users(user_table):
        return "SELECT * FROM {{user_table}} WHERE age > 30"


    with dag:
        user_table = aql.load_file(
            input_file=File("data.csv"),
            output_table=Table(conn_id="my_databricks_conn"),
            databricks_options={
                "copy_into_options": {"format_options": {"header": "true"}}
            },
        )
        results = get_eligible_users(user_table)

Parameterized Queries
=====================

The aql.transform() function in the Astro Python SDK allows users to create parameterized queries that can be executed with different values for the parameters. This is useful for reusing queries and for preventing SQL injection attacks.

To create a parameterized query, you can use double brackets ({{ and }}) to enclose the parameter names in the query string. The aql.transform() function will replace the parameter names with the corresponding values when the query is executed.

For example, you can create a parameterized query to select all users over a specified age like this:

.. code-block:: python

    @aql.transform()
    def my_query(table: Table, age: int):
        return "SELECT * FROM {{ table }} WHERE age > {{ age }}"

The aql.transform() function will replace {{ table }} with users and {{ age }} with 30, and then run the resulting query against the Delta table.