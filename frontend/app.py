import streamlit as st
from utils.dashboard_utils import inject_global_styles

st.set_page_config(page_title="RETAIN-AI", page_icon="💠", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()

dashboard = st.Page("pages/Dashboard.py", title="Dashboard",  default=True)
segments = st.Page("pages/Segmentation_Analytics.py", title="Segmentation Analytics")
customer = st.Page("pages/Customer_Intelligence.py", title="Customer Intelligence")
prediction = st.Page("pages/Prediction_Center.py", title="Prediction Center")
reports = st.Page("pages/Reports.py", title="Reports")
model = st.Page("pages/Model_Insights.py", title="Model Insights")

pg = st.navigation([
    dashboard,
    segments,
    customer,
    prediction,
    reports,
    model
])

pg.run()