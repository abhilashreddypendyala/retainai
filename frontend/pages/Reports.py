import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header

inject_global_styles()

page_header(
    "REPORTS",
    "Reports & Export",
    "Generate executive reports and export customer analytics.",
    None
)

@st.cache_data(ttl=600)
def fetch_executive_summary():
    return api_client.get_executive_summary()

@st.cache_data(ttl=600)
def fetch_report(report_type):
    if report_type == "customer": return api_client.get_customer_report_csv()
    if report_type == "high_risk": return api_client.get_high_risk_report_csv()
    if report_type == "segment": return api_client.get_segment_summary_csv()

def generate_pdf_report(title, text):
    from utils.pdf_utils import create_pdf_report
    return create_pdf_report(title, text)

def generate_pdf_csv(title, csv_data):
    from utils.pdf_utils import create_pdf_from_csv
    return create_pdf_from_csv(title, csv_data)


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
        summary_data = fetch_executive_summary()
        
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
        pdf_data = generate_pdf_report("RETAIN-AI EXECUTIVE SUMMARY", report_text)
        st.download_button(
            label="📄 Download Report (.pdf)",
            data=pdf_data,
            file_name="executive_summary.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# CSV Data Exports
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Raw Data</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Exports</div>", unsafe_allow_html=True)

csv_cols = st.columns(3)

# 1. Full Customer Report
with csv_cols[0]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Full Customer Base")
    st.markdown("Complete export of all customers including their segment, CLV, and churn probability.")
    try:
        csv_data = fetch_report("customer")
        dl1, dl2 = st.columns(2)
        with dl1: st.download_button("📥 CSV", data=csv_data, file_name="full_customer_report.csv", mime="text/csv", use_container_width=True)
        with dl2: st.download_button("📄 PDF", data=generate_pdf_csv("Full Customer Base", csv_data), file_name="full_customer_report.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

# 2. High Risk Customers
with csv_cols[1]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### High-Risk Interventions")
    st.markdown("Filtered export containing only customers who are predicted to churn (Prediction = 1).")
    try:
        csv_data = fetch_report("high_risk")
        dl1, dl2 = st.columns(2)
        with dl1: st.download_button("📥 CSV", data=csv_data, file_name="high_risk_customers.csv", mime="text/csv", use_container_width=True)
        with dl2: st.download_button("📄 PDF", data=generate_pdf_csv("High Risk Customers", csv_data), file_name="high_risk_customers.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Segment Summary
with csv_cols[2]:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Segment Analytics")
    st.markdown("Aggregated summary grouped by behavioral segments, showing average CLV and counts.")
    try:
        csv_data = fetch_report("segment")
        dl1, dl2 = st.columns(2)
        with dl1: st.download_button("📥 CSV", data=csv_data, file_name="segment_summary.csv", mime="text/csv", use_container_width=True)
        with dl2: st.download_button("📄 PDF", data=generate_pdf_csv("Segment Summary", csv_data), file_name="segment_summary.pdf", mime="application/pdf", use_container_width=True)
    except Exception as e:
        st.error(f"Error: {str(e)}")
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
    
    dl1, dl2 = st.columns(2)
    with dl1: st.download_button("📥 Session History (CSV)", data=hist_csv, file_name="session_predictions.csv", mime="text/csv")
    from utils.pdf_utils import create_pdf_from_csv
    with dl2: st.download_button("📄 Session History (PDF)", data=create_pdf_from_csv("Session Predictions", hist_csv), file_name="session_predictions.pdf", mime="application/pdf")
else:
    st.info("No predictions have been run in this session yet. Visit the Prediction Center to run some!")

st.markdown("</div>", unsafe_allow_html=True)
