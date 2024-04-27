import streamlit as st
import components


if __name__ == "__main__":

    st.header("Генератор датасетов")

    components.configuration()

    components.csv_converter()

    components.groups()

    components.students()

    components.attendance()

    components.marks()
