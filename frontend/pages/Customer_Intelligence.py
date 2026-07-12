import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header, metric_card, dark_table
from components.customer_table import render_customer_table

st.set_page_config(page_title="RETAIN-AI | Customer Intelligence", page_icon="👥", layout="wide")
inject_global_styles()

page_header(
    "CUSTOMER INTELLIGENCE",
    "Customer Explorer",
    "Browse, search, and filter the customer base.",
    ["Customer Data", "Search", "Filter"]
)

if "customer_page" not in st.session_state:
    st.session_state.customer_page = 1
if "active_search" not in st.session_state:
    st.session_state.active_search = ""
if "active_segment" not in st.session_state:
    st.session_state.active_segment = "All"
if "active_country" not in st.session_state:
    st.session_state.active_country = "All"
if "active_churn" not in st.session_state:
    st.session_state.active_churn = "All"
if "selected_customer_360" not in st.session_state:
    st.session_state.selected_customer_360 = None

st.sidebar.markdown("### Dynamic Segmentation")
sim_risk_slider = st.sidebar.slider(
    "High-Risk Threshold (Churn %)",
    min_value=10, max_value=90, value=50, step=5,
    help="Customers with churn probability above this are classified as High Risk."
) / 100.0

sim_clv_slider = st.sidebar.slider(
    "High-Value CLV Cutoff ($)",
    min_value=100, max_value=2000, value=500, step=50,
    help="Customers with CLV above this are classified as Whales or Champions."
)

st.markdown("<div class='section-kicker'>Discovery</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Search & Filter</div>", unsafe_allow_html=True)

COUNTRIES = [
    "All", "Australia", "Austria", "Bahrain", "Belgium", "Brazil", "Canada",
    "Channel Islands", "Cyprus", "Czech Republic", "Denmark", "EIRE",
    "European Community", "Finland", "France", "Germany", "Greece",
    "Iceland", "Israel", "Italy", "Japan", "Lebanon", "Lithuania", "Malta",
    "Netherlands", "Norway", "Poland", "Portugal", "RSA", "Saudi Arabia",
    "Singapore", "Spain", "Sweden", "Switzerland", "USA",
    "United Arab Emirates", "United Kingdom", "Unspecified"
]

SEGMENTS = [
    "All", 
    "High-Risk Whales (Immediate Action)", 
    "Loyal Champions (Reward/Upsell)", 
    "At-Risk Regulars (Automated Win-back)", 
    "Safe Regulars (Monitor)",
    "Unknown"
]

with st.form("search_filter_form"):
    search_col, filter_col = st.columns([1, 2])
    with search_col:
        search_input = st.text_input("Search by Customer ID", value=st.session_state.active_search, placeholder="e.g. 12345")
    
    with filter_col:
        col1, col2, col3 = st.columns(3)
        with col1:
            try:
                seg_idx = SEGMENTS.index(st.session_state.active_segment)
            except ValueError:
                seg_idx = 0
            segment_filter = st.selectbox("Segment", options=SEGMENTS, index=seg_idx)
        with col2:
            try:
                ctry_idx = COUNTRIES.index(st.session_state.active_country)
            except ValueError:
                ctry_idx = 0
            country_filter = st.selectbox("Country", options=COUNTRIES, index=ctry_idx)
        with col3:
            churn_options = ["All", "High Risk (1)", "Low Risk (0)"]
            try:
                ch_idx = churn_options.index(st.session_state.active_churn)
            except ValueError:
                ch_idx = 0
            churn_filter = st.selectbox("Churn Status", options=churn_options, index=ch_idx)

    submit_button = st.form_submit_button("Fetch Customers")

if submit_button:
    st.session_state.active_search = search_input
    st.session_state.active_segment = segment_filter
    st.session_state.active_country = country_filter
    st.session_state.active_churn = churn_filter
    st.session_state.customer_page = 1
    st.session_state.selected_customer_360 = None # Clear 360 view on new search

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

try:
    with st.spinner("Fetching customer data..."):
        if st.session_state.active_search:
            data = api_client.search_customers(st.session_state.active_search, sim_risk=sim_risk_slider, sim_clv=sim_clv_slider)
            total_items = len(data)
            items = data
        elif st.session_state.active_segment != "All" or st.session_state.active_country != "All" or st.session_state.active_churn != "All":
            seg_val = st.session_state.active_segment if st.session_state.active_segment != "All" else None
            country_val = st.session_state.active_country if st.session_state.active_country != "All" else None
            churn_val = None
            if st.session_state.active_churn == "High Risk (1)": churn_val = 1
            if st.session_state.active_churn == "Low Risk (0)": churn_val = 0
            
            data = api_client.filter_customers(segment=seg_val, country=country_val, churn_prediction=churn_val, sim_risk=sim_risk_slider, sim_clv=sim_clv_slider)
            total_items = len(data)
            items = data
        else:
            data = api_client.get_customers(page=st.session_state.customer_page, page_size=50, sim_risk=sim_risk_slider, sim_clv=sim_clv_slider)
            total_items = data.get("total", 0)
            items = data.get("items", [])

        render_customer_table(items)

        if not st.session_state.active_search and st.session_state.active_segment == "All" and st.session_state.active_country == "All" and st.session_state.active_churn == "All":
            total_pages = max(1, (total_items + 49) // 50)
            st.markdown(f"<div style='text-align: center; color: var(--muted); margin-bottom: 10px;'>Page {st.session_state.customer_page} of {total_pages} (Total: {total_items:,} customers)</div>", unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3 = st.columns([1, 2, 1])
            with p_col1:
                if st.button("← Previous", disabled=(st.session_state.customer_page <= 1), use_container_width=True):
                    st.session_state.customer_page -= 1
                    st.session_state.selected_customer_360 = None
                    st.rerun()
            with p_col3:
                if st.button("Next →", disabled=(st.session_state.customer_page >= total_pages), use_container_width=True):
                    st.session_state.customer_page += 1
                    st.session_state.selected_customer_360 = None
                    st.rerun()
        else:
            st.markdown(f"<div style='text-align: center; color: var(--muted); margin-bottom: 10px;'>Showing {total_items:,} matching customers.</div>", unsafe_allow_html=True)

except Exception as e:
    st.error("⚠️ The backend service is currently unavailable. Please ensure the FastAPI server is running and try again.")
    items = []

st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# CUSTOMER 360 SECTION
# -------------------------------------------------------------
if items:
    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Deep Dive</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Customer 360 Profile</div>", unsafe_allow_html=True)
    
    with st.form("customer_360_form"):
        customer_ids = [item["customer_id"] for item in items]
        selected_id = st.selectbox("Select Customer", options=customer_ids)
        view_btn = st.form_submit_button("View Customer 360")
        
    if view_btn:
        st.session_state.selected_customer_360 = selected_id

    if st.session_state.selected_customer_360:
        try:
            with st.spinner("Loading Customer 360..."):
                profile_data = api_client.get_customer_360(st.session_state.selected_customer_360)
                c_data = profile_data["customer"]
                tx_data = profile_data["recent_transactions"]
                rec_data = profile_data["recommendation"]
                
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                
                # Header
                st.markdown(f"### Customer ID: {c_data['customer_id']} 🌍 {c_data['country']}")
                st.markdown(f"**Segment:** {c_data['segment']}")
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Metrics Row 1: Business
                st.markdown("#### Business Metrics")
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1: metric_card("Customer Lifetime Value", f"${c_data['clv']:,.2f}", "")
                with m2: metric_card("Total Revenue", f"${c_data['monetary']:,.2f}", "")
                with m3: metric_card("Total Orders", f"{c_data['frequency']:,}", "")
                with m4: metric_card("Avg Order Value", f"${c_data['avg_order_value']:,.2f}", "")
                with m5: metric_card("Purchase Freq.", f"{c_data['purchase_frequency']:.2f}", "")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Metrics Row 2: Risk & Rec
                st.markdown("#### Risk & Retention Strategy")
                r1, r2, r3, r4 = st.columns(4)
                
                churn_subtext = "High Risk" if c_data['churn_prediction'] == 1 else "Low Risk"
                priority_subtext = "Urgent" if rec_data['priority'] == "High" else "Standard"
                
                with r1: metric_card("Churn Probability", f"{c_data['churn_probability']:.1%}", churn_subtext)
                with r2: metric_card("Recommended Action", rec_data['action'], "")
                with r3: metric_card("Priority Level", rec_data['priority'], priority_subtext)
                with r4: metric_card("Estimated ROI", rec_data['estimated_roi'], "")
                
                st.info(f"**AI Reasoning:** {rec_data['reason']}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Transactions Table
                st.markdown("#### Recent Purchases")
                if tx_data:
                    tx_df = pd.DataFrame(tx_data)
                    tx_df.columns = ["Invoice", "Date", "Description", "Quantity", "Unit Price", "Total Amount"]
                    tx_df["Unit Price"] = tx_df["Unit Price"].apply(lambda x: f"${float(x):,.2f}")
                    tx_df["Total Amount"] = tx_df["Total Amount"].apply(lambda x: f"${float(x):,.2f}")
                    st.dataframe(dark_table(tx_df).set_properties(subset=tx_df.columns, **{"text-align": "left"}), use_container_width=True, hide_index=True)
                else:
                    st.info("No recent transactions found for this customer.")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error("⚠️ Failed to load Customer 360 profile. The backend service may be unavailable.")
