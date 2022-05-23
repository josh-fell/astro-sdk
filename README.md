<h1 align="center">
  astro
</h1>
  <h3 align="center">
  workflows made easy<br><br>
</h3>

[![Python versions](https://img.shields.io/pypi/pyversions/astro-sdk-python.svg)](https://pypi.org/pypi/astro-sdk-python)
[![License](https://img.shields.io/pypi/l/astro-sdk-python.svg)](https://pypi.org/pypi/astro-sdk-python)
[![Development Status](https://img.shields.io/pypi/status/astro-sdk-python.svg)](https://pypi.org/pypi/astro-sdk-python)
[![PyPI downloads](https://img.shields.io/pypi/dm/astro-sdk-python.svg)](https://pypistats.org/packages/astro-sdk-python)
[![Contributors](https://img.shields.io/github/contributors/astronomer/astro-sdk)](https://github.com/astronomer/astro-sdk)
[![Commit activity](https://img.shields.io/github/commit-activity/m/astronomer/astro-sdk)](https://github.com/astronomer/astro-sdk)
[![CI](https://github.com/astronomer/astro-sdk/actions/workflows/ci.yaml/badge.svg)](https://github.com/astronomer/astro-sdk)
[![codecov](https://codecov.io/gh/astronomer/astro-sdk/branch/main/graph/badge.svg?token=MI4SSE50Q6)](https://codecov.io/gh/astronomer/astro-sdk)

**Astro SDK Python** allows rapid and clean development of {Extract, Load, Transform} workflows using Python.
It helps DAG authors to achieve more with less code.
It is powered by [Apache Airflow](https://airflow.apache.org) and maintained by [Astronomer](https://astronomer.io).

> :warning: **Disclaimer** This project is in a **preview** release state. In other words, it is not production-ready yet.
The interfaces may change. We welcome users to try out the interfaces and provide us with feedback.

## Install

**Astro SDK Python** is available at [PyPI](https://pypi.org/project/astro-sdk-python/). Use the standard Python
[installation tools](https://packaging.python.org/en/latest/tutorials/installing-packages/).

To install a cloud-agnostic version of **Astro SDK Python**, run:

```
pip install astro-sdk-python
```

If using cloud providers, install using the optional dependencies of interest:

```commandline
pip install astro-sdk-python[amazon,google,snowflake,postgres]
```

## Requirements

**Astro SDK Python** depends on Apache Airflow >= 2.1.0.

## Supported technologies

| Databases       |
|-----------------|
| Google BigQuery | 
| Postgres        | 
| Snowflake       |
| SQLite          | 

| File types |
|------------|
| CSV        | 
| JSON       | 
| NDJSON     | 
| Parquet    |

| File stores |
|------------ |
| Amazon S3   |
| Filesystem  |
| Google GCS  |

## Available operations

A summary of the currently available operations in **Astro SDK Python**. More details are available in the [reference guide](REFERENCE.md).
* `load_file`: load a given file into a SQL table
* `transform`: applies a SQL select statement to a source table and saves the result to a destination table
* `truncate`: remove all records from a SQL table
* `run_raw_sql`: run any SQL statement without handling its output
* `append`: insert rows from the source SQL table into the destination SQL table, if there are no conflicts
* `merge`: insert rows from the source SQL table into the destination SQL table, depending on conflicts:
  * ignore: do not add rows that already exist
  * update: replace existing rows with new ones
* `export_file`: export SQL table rows into a destination file
* `dataframe`: export given SQL table into in-memory Pandas data-frame

## Documentation

The documentation is a work in progress--we aim to follow the [Diátaxis](https://diataxis.fr/) system:
* **[Tutorial](https://github.com/astronomer/astro-sdk/blob/main/TUTORIAL.md)**: a hands-on introduction to **Astro SDK Python**
* **How-to guides**: simple step-by-step user guides to accomplish specific tasks
* **[Reference guide](docs/OLD_README.md)**: commands, modules, classes and methods
* **Explanation**: Clarification and discussion of key decisions when designing the project.

## Changelog

We follow Semantic Versioning for releases. Check the [changelog](docs/CHANGELOG.md) for the latest changes.

## Release Managements

To learn more about our release philosophy and steps, check [here](docs/RELEASE.md)

## Contribution Guidelines

All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.

Read the [Contribution Guideline](docs/CONTRIBUTING.md) for a detailed overview on how to contribute.

As contributors and maintainers to this project, you should abide by the [Contributor Code of Conduct](docs/CODE_OF_CONDUCT.md).

## License

[Apache Licence 2.0](LICENSE)
