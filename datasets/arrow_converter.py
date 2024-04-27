import os
from functools import lru_cache

from pyarrow import Table as ArrowTable
from pyarrow import csv, parquet
from pyiceberg.catalog import load_catalog
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.table import Table as IcebergTable


@lru_cache
def iceberg_sqlite_catalog() -> SqlCatalog:
    warehouse_path = "iceberg_catalog"
    if not os.path.exists(warehouse_path):
        os.makedirs(warehouse_path)
    catalog = SqlCatalog(
        "default",
        **{
            "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.sqlite",
            "warehouse": f"file://{warehouse_path}",
        },
    )
    if (
        len(catalog.list_namespaces()) == 0
        or "default" not in catalog.list_namespaces()[0]
    ):
        catalog.create_namespace("default")
    return catalog


@lru_cache
def iceberg_rest_catalog() -> RestCatalog:
    catalog = RestCatalog(
        "default",
        **{
            "uri": "http://127.0.0.1:8181",
            "s3.endpoint": "http://127.0.0.1:9000",
            "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "minioadmin",
        },
    )
    if (
        len(catalog.list_namespaces()) == 0
        or "default" not in catalog.list_namespaces()[0]
    ):
        catalog.create_namespace("default")
    return catalog


def get_catalog() -> RestCatalog:
    catalog = iceberg_rest_catalog()
    return catalog


def csv_to_parquet(filename: str, output_filename: str):
    table: ArrowTable = csv.read_csv(filename)
    parquet.write_table(table, output_filename)


def parquet_to_iceberg_table(filename: str): ...


def csv_to_iceberg_table(filename: str) -> IcebergTable:
    arrow_table: ArrowTable = csv.read_csv(filename)
    catalog: RestCatalog = get_catalog()
    iceberg_table: IcebergTable = catalog.create_table(
        identifier=f"default.{filename.split('/')[-1].split('.')[0]}",
        schema=arrow_table.schema,
        location="s3://warehouse/",
    )
    iceberg_table.append(arrow_table)
    return iceberg_table


if __name__ == "__main__":
    # csv_to_iceberg_table("students/students.csv")
    # csv_to_iceberg_table("students/students.csv")
    csv_to_parquet("groups/groups.csv", "groups/groups")
    print(get_catalog().list_tables("default"))
    # get_catalog().register_table("default.students", "s3://warehouse/students")
    print(get_catalog().load_table("default.students"))
