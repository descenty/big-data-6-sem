from os import path
from random import choice, randint
from typing import Generator
import pandas as pd
from config import load_config
from pydantic import BaseModel, Field


class Group(BaseModel):
    name: str = Field(str, title="Название")
    specialty: str = Field(str, title="Специальность")


def get_actual_groups_count(groups_filename="groups/groups.csv") -> int:
    if not path.isfile(groups_filename):
        return 0
    return pd.read_csv(groups_filename).shape[0]


def get_groups(groups_filename="groups/groups.csv") -> pd.DataFrame:
    if not path.isfile(groups_filename):
        return pd.DataFrame(columns=[f.title for f in Group.model_fields.values()])
    return pd.read_csv(groups_filename)


def groups_generator(used_groups_names: list[str] = []) -> Generator[Group, None, None]:
    while True:
        attempt = 0
        while (
            group_name := f"И{choice('ВКЛМНЭ')}БО-{randint(1, 99):02d}-{randint(20, 23):02d}"
        ) in used_groups_names:
            attempt += 1
            if attempt > 10:
                raise ValueError(
                    "Превышено количество попыток генерации уникального имени группы"
                )
        used_groups_names.append(group_name)
        yield Group(
            name=group_name,
            specialty=choice(load_config().specialties),
        )


def generate_groups(count: int, used_groups_names: list[str]) -> list[Group]:
    groups: Generator[Group, None, None] = groups_generator(used_groups_names)
    return [next(groups) for _ in range(count)]


def update_groups_dataset(
    groups_count: int, groups_filename="groups/groups.csv"
) -> None:
    if not path.isfile(groups_filename):
        with open(groups_filename, "w", encoding="utf-8") as f:
            f.write(
                ",".join([f.title or "" for f in Group.model_fields.values()]) + "\n"
            )
    used_groups_names = pd.read_csv(groups_filename)["Название"].tolist()
    actual_groups_count = len(used_groups_names)

    if groups_count == actual_groups_count:
        return

    if groups_count < actual_groups_count:
        raise ValueError("Уменьшение количества групп недопустимо")

    if actual_groups_count == 0 or groups_count == 0:
        with open(groups_filename, "w", encoding="utf-8") as f:
            f.write("Название,Специальность\n")

    if groups_count - actual_groups_count > 0:
        with open(groups_filename, "a", encoding="utf-8") as f:
            for group in generate_groups(
                groups_count - actual_groups_count, used_groups_names
            ):
                f.write(f"{group.name},{group.specialty}\n")
