from functools import lru_cache
from pydantic import BaseModel


class DatasetsConfig(BaseModel):
    semesters_count: int
    subjects_per_semester: int
    students_per_group: int
    groups_per_year: int
    max_groups_count: int
    max_student_id_digits: int
    specialties: list[str]
    subjects: list[str]
    permanent_registration_cities: list[str]

@lru_cache
def load_config(filename="config/config.json") -> DatasetsConfig:
    return DatasetsConfig.model_validate_json(open(filename, encoding="utf-8").read())
