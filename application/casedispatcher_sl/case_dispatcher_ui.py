import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages, show_pages_from_config

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
# 690797329461.dkr.ecr.eu-west-2.amazonaws.com/mysgmakerecr
# arn:aws:ecr:ap-southeast-2:038365619140:repository/mlopsanish
# arn:aws:ecr:us-west-2:690797329461:repository/mysgmakerecr