import streamlit as st
import components


if __name__ == "__main__":

    st.header("Генератор датасетов")

    components.configuration()

    components.groups()

    components.students()
