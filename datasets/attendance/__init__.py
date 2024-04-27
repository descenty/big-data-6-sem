from concurrent.futures._base import Future
from os import path
import os
from random import choice
import shutil
from typing import Generator
from numpy import ndarray
import pandas as pd
from pandas import DataFrame
from pydantic import BaseModel, Field
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
from tqdm import tqdm


lessons_count = 16
attendance_filename = "attendance/attendance.csv"


class Attendance(BaseModel):
    student_id: str = Field(str, title="Номер студента")
    subject_id: int = Field(str, title="Номер предмета")
    lesson_number: int = Field(int, title="Номер занятия")


def get_actual_attendance_count(attendance_filename=attendance_filename) -> int:
    if not path.isfile(attendance_filename):
        return 0
    return pd.read_csv(attendance_filename).shape[0]


def get_attendance(attendance_filename=attendance_filename) -> pd.DataFrame:
    if not path.isfile(attendance_filename):
        return pd.DataFrame(columns=[f.title for f in Attendance.model_fields.values()])
    return pd.read_csv(attendance_filename)


def attendance_generator(
    students_ids: list[str],
    subjects_ids: list[int],
) -> Generator[list, None, None]:
    attendance_examples = pd.read_csv("attendance/attendance_examples.csv")
    while len(students_ids) > 0:
        student_id = choice(students_ids)
        students_ids.remove(student_id)
        for subject_id in subjects_ids:
            sample_attendance: DataFrame = attendance_examples.sample(1)
            for lesson_number in range(1, lessons_count + 1):
                # if is "+"
                if sample_attendance[str(lesson_number)].values[0] == "+":
                    yield [student_id, subject_id, lesson_number]


def generate_attendance(students_ids: list[str] | ndarray) -> DataFrame:
    generator: Generator[list, None, None] = attendance_generator(
        list(students_ids),
        pd.read_csv("subjects/subjects.csv")["Номер"].tolist(),
    )

    attendance_data: list[list[str]] = []

    while True:
        try:
            attendance_data.append(next(generator))
        except StopIteration:
            break
    return pd.DataFrame(
        attendance_data, columns=[f.title for f in Attendance.model_fields.values()]
    )


def update_attendance_task(students_ids: list[str] | ndarray) -> int:
    new_attendance: pd.DataFrame = generate_attendance(students_ids)
    new_attendance.to_csv(f"attendance/temp/{students_ids[0]}.csv", index=False)
    return new_attendance.shape[0]


def update_attendance_dataset(
    max_futures: int | None = None,
    max_workers: int = cpu_count() // 2,
    batch_size: int = 100,
) -> None:
    if not os.path.isdir("attendance/temp"):
        os.makedirs("attendance/temp")
    # merge all chunks
    if len(os.listdir("attendance/temp")) > 0:
        data: DataFrame = pd.concat(
            [
                pd.read_csv(f"attendance/temp/{file}")
                for file in os.listdir("attendance/temp")
            ]
        )
        data.to_csv(attendance_filename, index=False)
        print(f"Merged {data.shape[0]} records from temp folder")
        shutil.rmtree("attendance/temp")

    students_ids: ndarray | list = pd.read_csv("students/students.csv")[
        "Личный номер"
    ].unique()
    if os.path.isfile(attendance_filename):
        used_students_ids = pd.read_csv(attendance_filename, on_bad_lines="warn")[
            "Номер студента"
        ].unique()
        if len(used_students_ids) > 0:
            students_ids = list(set(students_ids) - set(used_students_ids))

    pool = ProcessPoolExecutor(max_workers=max_workers)

    students_ids_chunks = [
        students_ids[i : i + batch_size]
        for i in range(0, len(students_ids), batch_size)
    ]

    if len(students_ids_chunks) == 0:
        print("No new students for updating attendance dataset")

        print("Counting records in attendance dataset...")
        print(f"Attendance contains {get_actual_attendance_count()} records")
        return

    print(f"Futures left: {len(students_ids_chunks)}")

    if max_futures:
        students_ids_chunks = students_ids_chunks[:max_futures]
    futures: list[Future[int]] = [
        pool.submit(update_attendance_task, students_ids_chunk)
        for students_ids_chunk in students_ids_chunks
    ]

    print(f"Started {len(futures)} futures for updating attendance dataset")
    print(f"Workers: {max_workers}")

    # progress bar with tqdm
    for f in tqdm(futures):
        print(f"Added {f.result()} new attendance records", end="\r")

    print("All futures for updating attendance dataset are completed")

    # merge all chunks
    data = pd.concat(
        [
            pd.read_csv(f"attendance/temp/{students_ids_chunk[0]}.csv")
            for students_ids_chunk in students_ids_chunks
        ]
    )
    print(f"Merged {data.shape[0]} records from temp folder")
    data.to_csv(attendance_filename, mode="a", index=False)
    shutil.rmtree("attendance/temp")

    print("Counting records in attendance dataset...")
    print(f"Attendance contains {get_actual_attendance_count()} records")
