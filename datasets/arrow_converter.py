import os
from functools import lru_cache

from pyarrow import Table as ArrowTable
from pyarrow import csv, parquet
from pyiceberg.catalog.sql import SqlCatalog
from pyiceberg.table import Table as IcebergTable


@lru_cache
def iceberg_catalog() -> SqlCatalog:
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
    catalog.create_namespace("default")
    return catalog


def csv_to_parquet(filename: str, output_filename: str):
    table: ArrowTable = csv.read_csv(filename)
    parquet.write_table(table, f"{output_filename}.parquet")


def parquet_to_iceberg_table(filename: str): ...


def csv_to_iceberg_table(filename: str) -> IcebergTable:
    arrow_table: ArrowTable = csv.read_csv(filename)
    catalog: SqlCatalog = iceberg_catalog()
    iceberg_table: IcebergTable = catalog.create_table(
        f"default.{filename.split('/')[-1].split('.')[0]}", arrow_table.schema
    )
    iceberg_table.append(arrow_table)
    return iceberg_table


if __name__ == "__main__":
    csv_to_iceberg_table("students/students.csv")
