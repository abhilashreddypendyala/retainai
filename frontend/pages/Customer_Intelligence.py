import streamlit as st
import pandas as pd
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header, metric_card, dark_table
from components.customer_table import render_customer_table

inject_global_styles()

page_header(
    "CUSTOMER INTELLIGENCE",
    "Customer Explorer",
    "Search, filter, and inspect individual customer profiles.",
    None
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

if "ci_risk_slider" not in st.session_state:
    st.session_state.ci_risk_slider = 50
if "ci_risk_manual" not in st.session_state:
    st.session_state.ci_risk_manual = 50
if "ci_clv_slider" not in st.session_state:
    st.session_state.ci_clv_slider = 500
if "ci_clv_manual" not in st.session_state:
    st.session_state.ci_clv_manual = 500

def ci_sync_risk_from_slider():
    st.session_state.ci_risk_manual = st.session_state.ci_risk_slider
def ci_sync_risk_from_manual():
    st.session_state.ci_risk_slider = st.session_state.ci_risk_manual

def ci_sync_clv_from_slider():
    st.session_state.ci_clv_manual = st.session_state.ci_clv_slider
def ci_sync_clv_from_manual():
    st.session_state.ci_clv_slider = st.session_state.ci_clv_manual

st.sidebar.markdown("### Dynamic Segmentation")
st.sidebar.slider("High-Risk Threshold (Churn %)", min_value=0, max_value=100, step=1, key="ci_risk_slider", on_change=ci_sync_risk_from_slider)
st.sidebar.number_input("Manual Input: Risk (%)", min_value=0, max_value=100, step=1, key="ci_risk_manual", on_change=ci_sync_risk_from_manual)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.slider("High-Value CLV Cutoff ($)", min_value=0, max_value=10000, step=50, key="ci_clv_slider", on_change=ci_sync_clv_from_slider)
st.sidebar.number_input("Manual Input: Cutoff ($)", min_value=0, max_value=10000, step=50, key="ci_clv_manual", on_change=ci_sync_clv_from_manual)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.button("Fetch Data", type="primary", use_container_width=True)

sim_risk_slider = st.session_state.ci_risk_slider / 100.0
sim_clv_slider = st.session_state.ci_clv_slider

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

def on_filter_change():
    st.session_state.customer_page = 1
    st.session_state.selected_customer_360 = None

@st.cache_data(ttl=300)
def fetch_all_customer_ids():
    try:
        return api_client.get_all_customer_ids()
    except:
        return []

all_ids = fetch_all_customer_ids()
customer_options = ["All"] + all_ids

search_col, filter_col = st.columns([1, 2])
with search_col:
    def on_search_change():
        st.session_state.customer_page = 1
        st.session_state.selected_customer_360 = None
        val = st.session_state.search_dropdown
        st.session_state.active_search = "" if val == "All" else val

    try:
        search_idx = customer_options.index(st.session_state.active_search) if st.session_state.active_search in customer_options else 0
    except ValueError:
        search_idx = 0
        
    st.selectbox("Search by Customer ID", options=customer_options, index=search_idx, key="search_dropdown", on_change=on_search_change)

with filter_col:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.selectbox("Segment", options=SEGMENTS, key="active_segment", on_change=on_filter_change)
    with col2:
        st.selectbox("Country", options=COUNTRIES, key="active_country", on_change=on_filter_change)
    with col3:
        churn_options = ["All", "High Risk (1)", "Low Risk (0)"]
        st.selectbox("Churn Status", options=churn_options, key="active_churn", on_change=on_filter_change)


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
        view_btn = st.form_submit_button("View Customer 360", type="primary")
        
    if view_btn:
        st.session_state.selected_customer_360 = selected_id

    if st.session_state.selected_customer_360:
        try:
            with st.spinner("Loading Customer 360..."):
                profile_data = api_client.get_customer_360(st.session_state.selected_customer_360, sim_risk=sim_risk_slider, sim_clv=sim_clv_slider)
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
                
                churn_subtext = "High Risk" if c_data['churn_probability'] >= 0.5 else "Low Risk"
                priority_subtext = "Urgent" if rec_data['priority'] == "High" else "Standard"
                
                with r1: metric_card("Churn Probability", f"{c_data['churn_probability']:.1%}", churn_subtext)
                with r2: metric_card("Recommended Action", rec_data['action'], "")
                with r3: metric_card("Priority Level", rec_data['priority'], priority_subtext)
                with r4: metric_card("Estimated ROI", rec_data['estimated_roi'], "")
                
                st.info(f"**AI Reasoning:** {rec_data['reason']}")
                
                st.markdown("<br>", unsafe_allow_html=True)
                # Order Summary Table
                st.markdown("#### Order Summary")
                if tx_data:
                    raw_df = pd.DataFrame(tx_data)
                    raw_df.columns = ["Invoice", "Date", "Items", "Total Items Bought", "Total Order Amount"]
                    
                    # Add Serial Number
                    raw_df.insert(0, "#", range(1, len(raw_df) + 1))
                    
                    from utils.pdf_utils import create_pdf_table
                    
                    # Generate Downloads (Unformatted for accuracy)
                    csv_data = raw_df.to_csv(index=False).encode('utf-8')
                    pdf_data = create_pdf_table(f"CUSTOMER {c_data['customer_id']} ORDER SUMMARY", raw_df)
                    
                    # Create beautifully formatted UI version
                    ui_df = raw_df.copy()
                    ui_df["Total Order Amount"] = ui_df["Total Order Amount"].apply(lambda x: f"${float(x):,.2f}")
                    
                    # Layout buttons
                    dl1, dl2, dl3 = st.columns([1, 1, 2])
                    with dl1: st.download_button("Download CSV", data=csv_data, file_name=f"Customer_{c_data['customer_id']}_Orders.csv", mime="text/csv", use_container_width=True)
                    with dl2: st.download_button("Download PDF", data=pdf_data, file_name=f"Customer_{c_data['customer_id']}_Orders.pdf", mime="application/pdf", use_container_width=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.dataframe(dark_table(ui_df).set_properties(subset=ui_df.columns, **{"text-align": "left"}), use_container_width=True, hide_index=True)
                else:
                    st.info("No order history found for this customer.")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error("⚠️ Failed to load Customer 360 profile. The backend service may be unavailable.")
