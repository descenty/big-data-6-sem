from pyarrow import csv, parquet

table = csv.read_csv("../datasets/students/students.csv")
parquet.write_table(table, "students.parquet")
