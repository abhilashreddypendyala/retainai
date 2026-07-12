# pyright: reportMissingImports=false

import streamlit as st

from utils.dashboard_utils import inject_global_styles, page_header


st.set_page_config(page_title="RETAIN-AI", page_icon="💠", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()

page_header(
    "RETAIN-AI",
    "CLV-driven churn prediction and retention optimization",
    "Customer risk, customer value, and retention actions.",
    ["Overview", "Customer Segments"],
)

st.markdown("<div class='section-kicker'>Navigation</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Choose a page</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Open the dashboard sections below.</div>", unsafe_allow_html=True)

links = st.columns(2)
with links[0]:
    st.page_link("pages/Dashboard.py", label="Open Overview", icon="📈")
with links[1]:
    st.page_link("pages/Segmentation_Analytics.py", label="Open Segments", icon="📊")

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)