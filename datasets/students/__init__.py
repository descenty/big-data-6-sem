from functools import lru_cache
from os import path
import random
from random import choices
from typing import Generator
from pyarrow import csv

import pandas as pd
import pyarrow
from config import load_config
from faker import Faker
from groups import get_groups
from pydantic import BaseModel, Field

faker = Faker("ru_RU")

students_filename = "students/students.csv"


# Личный номер,Фамилия,Имя,Отчество,Группа,Финансирование,Пол,Постоянная регистрация,
class Student(BaseModel):
    id: str = Field(str, title="Личный номер")
    fio: str = Field(str, title="ФИО")
    group: str = Field(str, title="Группа")
    financing: str = Field(str, title="Финансирование")
    gender: str = Field(str, title="Пол")
    permanent_registration_city: str = Field(str, title="Город постоянной регистрации")


def get_actual_students_count() -> int:
    if not path.isfile(students_filename):
        return 0
    return csv.read_csv(students_filename).num_rows


def get_students() -> pd.DataFrame:
    if not path.isfile(students_filename):
        return pd.DataFrame(columns=[f.title for f in Student.model_fields.values()])
    return pd.read_csv(students_filename)


@lru_cache
def cities_choices_weights() -> list[float]:
    return [
        random.random() for _ in range(len(load_config().permanent_registration_cities))
    ]


def random_registration_city() -> Generator[str, None, None]:
    cities: list[str] = load_config().permanent_registration_cities
    choices_weights = cities_choices_weights()
    while True:
        yield choices(cities, weights=choices_weights)[0]


def students_generator(
    group_name: str, last_student_id_year: int, last_student_id: int, max_id_digits: int
) -> Generator[Student, None, None]:
    city_generator: Generator[str, None, None] = random_registration_city()

    while True:
        last_student_id += 1
        student_id: str = (
            f"{last_student_id_year:2d}И{str(last_student_id).zfill(max_id_digits)}"
        )
        if last_student_id >= 10**max_id_digits - 1:
            last_student_id = 1
            last_student_id_year += 1

        gender: str = choices(population=["М", "Ж"], weights=[0.7321, 0.2679])[0]

        yield Student(
            id=student_id,
            fio=faker.name_male() if gender == "М" else faker.name_female(),
            group=group_name,
            financing=choices(population=["Б", "К"], weights=[0.5937, 0.4063])[0],
            gender=gender,
            permanent_registration_city=next(city_generator),
        )


def generate_students(max_id_digits: int) -> list[Student]:
    actual_groups: pd.DataFrame = get_groups()

    group_names = actual_groups["Название"].unique()

    actual_students: pd.DataFrame = get_students()
    students_in_groups = actual_students.groupby("Группа").size().to_dict()

    students_to_generate: dict[str, int] = {
        group_name: load_config().students_per_group
        - students_in_groups.get(group_name, 0)
        for group_name in group_names
    }

    generated_students: list[Student] = []
    for group_name, students_count in students_to_generate.items():
        if students_count <= 0:
            continue

        if len(generated_students) == 0:
            max_student_id = str(actual_students["Личный номер"].max())
            if max_student_id == "nan":
                max_student_id = f"04И{str(0).zfill(max_id_digits)}"
        else:
            max_student_id = str(generated_students[-1].id)
        students: Generator[Student, None, None] = students_generator(
            group_name,
            last_student_id_year=int(max_student_id[0:2]),
            last_student_id=int(max_student_id[3:]),
            max_id_digits=max_id_digits,
        )
        generated_students.extend([next(students) for _ in range(students_count)])
    return generated_students


def update_students_dataset() -> None:
    max_id_digits = load_config().max_student_id_digits

    if not path.isfile(students_filename):
        with open(students_filename, "w", encoding="utf-8") as f:
            f.write(
                ",".join([f.title or "" for f in Student.model_fields.values()]) + "\n"
            )

    students_to_write: list[Student] = generate_students(max_id_digits)
    if len(students_to_write) > 0:
        with open(students_filename, "a", encoding="utf-8") as f:
            for student in students_to_write:
                f.write(
                    ",".join([value or "" for value in student.model_dump().values()])
                    + "\n"
                )


def clear_students_dataset() -> None:
    if path.isfile(students_filename):
        with open(students_filename, "w", encoding="utf-8") as f:
            f.write(
                ",".join([f.title or "" for f in Student.model_fields.values()]) + "\n"
            )
