from os import path
from random import choices, random
from typing import Generator
import pandas as pd
from config import load_config
from pyarrow import csv
from pydantic import BaseModel, Field


class Group(BaseModel):
    name: str = Field(str, title="Название")
    speciality: str = Field(str, title="Специальность")


def get_actual_groups_count(groups_filename="groups/groups.csv") -> int:
    if not path.isfile(groups_filename):
        return 0
    return csv.read_csv(groups_filename).num_rows


def get_groups(groups_filename="groups/groups.csv") -> pd.DataFrame:
    if not path.isfile(groups_filename):
        return pd.DataFrame(columns=[f.title for f in Group.model_fields.values()])
    return pd.read_csv(groups_filename)


def random_speciality() -> Generator[str, None, None]:
    specialities = load_config().specialties
    choices_weights = [random() for _ in range(len(specialities))]
    while True:
        yield choices(specialities, weights=choices_weights)[0]


def get_all_possible_groups_names() -> list[str]:
    return [
        f"И{letter}БО-{id_number:02d}-{year:02d}"
        for letter in "АВКМН"
        for id_number in range(1, 1000)
        for year in range(4, 25)
    ]


def groups_generator(used_groups_names: list[str] = []) -> Generator[Group, None, None]:
    speciality_generator: Generator[str, None, None] = random_speciality()
    all_groups_names = get_all_possible_groups_names()
    free_groups_names = sorted(
        set(all_groups_names) - set(used_groups_names),
        # ИКБО-32-21: first by 32, then by ИКБО, then by 21
        key=lambda x: (int(x[-2:]), x[:4], int(x[x.find("-") + 1 : x.find("-", 5)])),
    )
    while True:
        if len(free_groups_names) == 0:
            raise ValueError(
                f"Нет свободных названий групп (использовано {len(all_groups_names)})"
            )
        group_name = free_groups_names.pop(0)
        group = Group(
            name=group_name,
            speciality=next(speciality_generator),
        )
        yield group


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
                f.write(f"{group.name},{group.speciality}\n")


def clear_groups_dataset(groups_filename="groups/groups.csv") -> None:
    if path.isfile(groups_filename):
        with open(groups_filename, "w", encoding="utf-8") as f:
            f.write(
                ",".join([f.title or "" for f in Group.model_fields.values()]) + "\n"
            )
