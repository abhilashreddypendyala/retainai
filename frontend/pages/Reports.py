import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header

st.set_page_config(page_title="RETAIN-AI | Reports & Export", page_icon="📑", layout="wide")
inject_global_styles()

page_header(
    "REPORTS & EXPORT",
    "Data Delivery Center",
    "Export backend-generated executive summaries and batch prediction results for offline analysis.",
    ["Export", "CSV", "Reporting"]
)

# ---------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------
st.markdown("<div class='section-kicker'>High Level</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Executive Summary</div>", unsafe_allow_html=True)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    **Executive Summary Report**
    Generates a high-level overview of the entire customer base, identifying total risk exposure and aggregate lifetime value.
    """)
with col2:
    try:
        summary_data = api_client.get_executive_summary()
        
        # Format as text report since native PDF requires 3rd party OS libraries
        report_text = f"""====================================================
RETAIN-AI EXECUTIVE SUMMARY
Generated: {summary_data['generated_timestamp']}
====================================================

CUSTOMER BASE
-------------
Total Active Customers: {summary_data['total_customers']:,}
High Risk Customers:    {summary_data['high_risk_customers']:,}

FINANCIAL EXPOSURE
------------------
Total Revenue Base:     ${summary_data['total_revenue']:,.2f}
Revenue At Risk:        ${summary_data['revenue_at_risk']:,.2f}
Average CLV:            ${summary_data['average_clv']:,.2f}

====================================================
"""
        st.download_button(
            label="📄 Download Report (.txt)",
            data=report_text,
            file_name="executive_summary.txt",
            mime="text/plain",
            use_container_width=True
        )
    except Exception as e:
        st.error("Backend offline.")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CSV Data Exports
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Raw Data</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>CSV Exports</div>", unsafe_allow_html=True)

csv_cols = st.columns(3)

# 1. Full Customer Report
with csv_cols[0]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Full Customer Base")
    st.markdown("Complete export of all customers including their segment, CLV, and churn probability.")
    try:
        csv_data = api_client.get_customer_report_csv()
        st.download_button("📥 Download CSV", data=csv_data, file_name="full_customer_report.csv", mime="text/csv", use_container_width=True)
    except:
        st.error("Unavailable")
    st.markdown("</div>", unsafe_allow_html=True)

# 2. High Risk Customers
with csv_cols[1]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### High-Risk Interventions")
    st.markdown("Filtered export containing only customers who are predicted to churn (Prediction = 1).")
    try:
        csv_data = api_client.get_high_risk_report_csv()
        st.download_button("📥 Download CSV", data=csv_data, file_name="high_risk_customers.csv", mime="text/csv", use_container_width=True)
    except:
        st.error("Unavailable")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Segment Summary
with csv_cols[2]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Segment Analytics")
    st.markdown("Aggregated summary grouped by behavioral segments, showing average CLV and counts.")
    try:
        csv_data = api_client.get_segment_summary_csv()
        st.download_button("📥 Download CSV", data=csv_data, file_name="segment_summary.csv", mime="text/csv", use_container_width=True)
    except:
        st.error("Unavailable")
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session History
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Session</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Live Prediction History</div>", unsafe_allow_html=True)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.markdown("Export the manual ML predictions you've run during this current session in the Prediction Center.")

if "recent_predictions" in st.session_state and st.session_state.recent_predictions:
    hist_df = pd.DataFrame(st.session_state.recent_predictions)
    hist_csv = hist_df.to_csv(index=False)
    st.download_button("📥 Download Session History (CSV)", data=hist_csv, file_name="session_predictions.csv", mime="text/csv")
else:
    st.info("No predictions have been run in this session yet. Visit the Prediction Center to run some!")

st.markdown("</div>", unsafe_allow_html=True)
