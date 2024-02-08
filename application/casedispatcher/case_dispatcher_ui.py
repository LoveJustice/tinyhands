import streamlit as st

st.set_page_config(
    page_title="Hello LoveJustice",
    page_icon="👋",
)

st.write("# Welcome to the CaseDispatcher! 👋")

st.sidebar.success("Select one of the above.")

st.markdown(
    """
This user interface allows the user to select a country and update the case dispatcher accordingly.
Soon the user will also be able to update the prioritisation model.
Please navigate to the __update__ tab to update the case dispatcher.
"""
)
