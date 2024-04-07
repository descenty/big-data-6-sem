from os import path
from random import choice, randint
from typing import Generator

import pandas as pd
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
    return pd.read_csv(students_filename).shape[0]


def get_students() -> pd.DataFrame:
    if not path.isfile(students_filename):
        return pd.DataFrame(columns=[f.title for f in Student.model_fields.values()])
    return pd.read_csv(students_filename)


def students_generator(
    group_name: str,
    used_student_ids: list[str] = [],
) -> Generator[Student, None, None]:
    while True:
        attempt = 0
        # 21И1460
        while (
            student_id := f"{randint(20, 23)}И{randint(1, 99999):05d}"
        ) in used_student_ids:
            attempt += 1
            if attempt > 10:
                raise ValueError(
                    "Превышено количество попыток генерации уникального личного номера студента"
                )
        used_student_ids.append(student_id)

        gender = choice("МЖ")
        yield Student(
            id=f"{randint(20, 23)}И{randint(1, 9999):04d}",
            fio=faker.name_male() if gender == "М" else faker.name_female(),
            group=group_name,
            financing=choice("БК"),
            gender=gender,
            permanent_registration_city=choice(
                load_config().permanent_registration_cities
            ),
        )


def generate_students(used_student_ids: list[str]) -> list[Student]:
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
        students: Generator[Student, None, None] = students_generator(
            group_name, used_student_ids
        )
        generated_students.extend([next(students) for _ in range(students_count)])
    return generated_students


def update_students_dataset() -> None:
    if not path.isfile(students_filename):
        with open(students_filename, "w", encoding="utf-8") as f:
            f.write(
                ",".join([f.title or "" for f in Student.model_fields.values()]) + "\n"
            )

    used_student_ids = pd.read_csv(students_filename)["Личный номер"].tolist()

    students_to_write = generate_students(used_student_ids)
    if len(students_to_write) > 0:
        with open(students_filename, "a", encoding="utf-8") as f:
            for student in generate_students(used_student_ids):
                f.write(
                    ",".join([value or "" for value in student.model_dump().values()])
                    + "\n"
                )
