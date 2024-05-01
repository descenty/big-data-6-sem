from pandas import DataFrame
import pyarrow
import streamlit as st
from config import DatasetsConfig, load_config
from groups import (
    clear_groups_dataset,
    get_actual_groups_count,
    get_groups,
    update_groups_dataset,
)
from students import (
    get_actual_students_count,
    get_students,
    update_students_dataset,
    clear_students_dataset,
)


def update_all_datasets(groups_count: int) -> None:
    update_groups_dataset(groups_count)
    update_students_dataset()


def clear_all_datasets():
    clear_groups_dataset()
    clear_students_dataset()


def configuration() -> None:
    config: DatasetsConfig = load_config()

    with st.expander("Конфигурация"):
        st.json(config.model_dump())


def groups() -> None:
    max_groups_count: int = load_config().max_groups_count
    students_per_group: int = load_config().students_per_group

    actual_groups_count: int = get_actual_groups_count()
    actual_students_count = get_actual_students_count()

    st.subheader(f"Список групп ({actual_groups_count})")
    if actual_groups_count < max_groups_count:
        groups_count: int = round(
            st.slider(
                "Количество групп",
                step=10,
                min_value=actual_groups_count,
                max_value=max_groups_count,
                value=actual_groups_count,
            )
        )
        st.button(
            "Применить",
            key="update_groups",
            on_click=update_all_datasets,
            kwargs={"groups_count": groups_count},
        )
    else:
        st.text("Достигнуто максимальное количество групп")
    if actual_groups_count > 0:
        st.button(
            "Очистить",
            key="clear_groups",
            on_click=clear_all_datasets,
        )
        if (
            actual_students_count
            < actual_groups_count * load_config().students_per_group
        ):
            st.button(
                f"Наполнить группы до {students_per_group} человек",
                key="fill_groups",
                on_click=update_students_dataset,
            )
        else:
            st.text("Все группы заполнены")

    df: DataFrame = get_groups()

    # st.dataframe(df.head(10), use_container_width=True)
    st.dataframe(df.tail(10), use_container_width=True)


def students() -> None:
    df: DataFrame = get_students()

    actual_students_count: int = get_actual_students_count()
    st.subheader(f"Список студентов ({actual_students_count})")
    if actual_students_count > 0:
        st.button("Очистить", key="clear_students", on_click=clear_students_dataset)
    st.dataframe(df.tail(300), use_container_width=True)


def attendance() -> None: ...


def marks() -> None: ...


def csv_converter() -> None:
    st.button("Конвертировать в Parquet", key="csv_to_parquet")
