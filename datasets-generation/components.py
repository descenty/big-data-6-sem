import streamlit as st
from config import DatasetsConfig, load_config
from groups import get_actual_groups_count, get_groups, update_groups_dataset
from students import get_actual_students_count, get_students, update_students_dataset


def update_all_datasets(groups_count: int) -> None:
    update_groups_dataset(groups_count)
    update_students_dataset()


def configuration() -> None:
    config: DatasetsConfig = load_config()

    with st.expander("Конфигурация"):
        st.json(config.model_dump())


def groups() -> None:
    actual_groups_count: int = get_actual_groups_count()
    st.subheader(f"Список групп ({actual_groups_count})")
    if actual_groups_count < 1000:
        groups_count: int = round(
            st.slider(
                "Количество групп",
                step=10,
                min_value=actual_groups_count,
                max_value=1000,
                value=actual_groups_count,
            )
        )
        st.button(
            "Применить",
            on_click=update_all_datasets,
            kwargs={"groups_count": groups_count},
        )
    else:
        st.text("Достигнуто максимальное количество групп")
    st.dataframe(get_groups(), use_container_width=True)


def students() -> None:
    df = get_students()
    st.subheader(f"Список студентов ({get_actual_students_count()})")
    st.dataframe(df)
