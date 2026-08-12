import io
import time
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header, dark_table, metric_card
from utils.pdf_utils import create_pdf_table
from components.prediction_result import render_prediction_result
from components.customer_table import render_customer_table

inject_global_styles()

page_header(
    "PREDICTION CENTER",
    "Churn Prediction & Intelligence",
    "Predict churn probability for existing customers, new profiles, or batch transactions.",
    None
)

# Initialize session state tracking
if "recent_predictions" not in st.session_state:
    st.session_state.recent_predictions = []
if "dataset_intelligence_results" not in st.session_state:
    st.session_state.dataset_intelligence_results = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "dataset_proc_time" not in st.session_state:
    st.session_state.dataset_proc_time = "N/A"
if "dataset_date_range" not in st.session_state:
    st.session_state.dataset_date_range = "N/A"
if "di_cust_page" not in st.session_state:
    st.session_state.di_cust_page = 1
if "di_seg_page" not in st.session_state:
    st.session_state.di_seg_page = 1


# -------------------------------------------------------------
# DATASET INTELLIGENCE HELPER & TAB RENDER FUNCTIONS
# -------------------------------------------------------------
def get_di_recommendation(segment: str, monetary: float, churn_prob: float = 0.5) -> str:
    seg_str = str(segment)
    if "High-Risk Whales" in seg_str:
        return "VIP Win-Back Concierge: Dispatch urgent personalized email & phone outreach offering exclusive loyalty incentives or personal account manager."
    elif "Loyal Champions" in seg_str:
        return "Reward & Upsell Program: Enroll in VIP loyalty tier, offer early access to new product drops and volume-based discounts."
    elif "At-Risk Regulars" in seg_str:
        return "Automated Win-Back Drip: Trigger automated 15% discount promotional email series highlighting popular new catalog items."
    else:
        return "Standard Engagement Drip: Maintain regular bi-weekly newsletter communications and seasonal promotional updates."


def render_di_upload_tab():
    st.markdown("#### Batch Dataset Ingest & Pipeline Orchestration")
    st.markdown("Upload a raw retail transaction dataset (CSV or Excel) with schema matching Online Retail II (Invoice, StockCode, Quantity, Price, CustomerID, InvoiceDate). Runs entirely in-memory without altering live database records.")

    uploaded_file = st.file_uploader("Upload Raw Transactions Dataset (.csv, .xlsx, .xls)", type=["csv", "xlsx", "xls"], key="di_uploader")
    
    if uploaded_file is not None and uploaded_file.name != st.session_state.uploaded_file_name:
        st.session_state.dataset_intelligence_results = None

    col_btn1, col_btn2, _ = st.columns([1, 1, 2])
    with col_btn1:
        analyze_btn = st.button("🚀 Analyze Dataset", type="primary", use_container_width=True)
    with col_btn2:
        if st.session_state.dataset_intelligence_results is not None:
            if st.button("🔄 Reset Analysis", type="secondary", use_container_width=True):
                st.session_state.dataset_intelligence_results = None
                st.session_state.uploaded_file_name = None
                st.rerun()

    if analyze_btn:
        if uploaded_file is None:
            st.warning("⚠️ Please upload a CSV or Excel transaction file before clicking Analyze.")
        else:
            try:
                with st.spinner("⏳ Executing Stage 1 (Cleaning, RFM, Feature Engineering) and Stage 2 (ML Churn & CLV Inference)..."):
                    t0 = time.time()
                    file_bytes = uploaded_file.read()
                    res = api_client.analyze_dataset(file_bytes, uploaded_file.name)
                    elapsed = time.time() - t0
                    
                    date_range_str = "N/A (No date col)"
                    try:
                        if uploaded_file.name.lower().endswith('.csv'):
                            df_temp = pd.read_csv(io.BytesIO(file_bytes), nrows=15000)
                        else:
                            xl = pd.ExcelFile(io.BytesIO(file_bytes))
                            sheet = "Year 2010-2011" if "Year 2010-2011" in xl.sheet_names else xl.sheet_names[0]
                            df_temp = xl.parse(sheet)
                        date_col = next((c for c in df_temp.columns if 'date' in str(c).lower()), None)
                        if date_col:
                            dates = pd.to_datetime(df_temp[date_col], errors='coerce').dropna()
                            if not dates.empty:
                                date_range_str = f"{dates.min().strftime('%Y-%m-%d')} to {dates.max().strftime('%Y-%m-%d')}"
                    except Exception:
                        pass
                        
                    st.session_state.dataset_intelligence_results = res
                    st.session_state.uploaded_file_name = uploaded_file.name
                    st.session_state.dataset_proc_time = f"{elapsed:.2f}s"
                    st.session_state.dataset_date_range = date_range_str
                    st.success(f"✅ Successfully processed {res['kpi_summary']['total_customers']:,} customer profiles in {elapsed:.2f}s!")
            except Exception as e:
                st.error(f"⚠️ Dataset Analysis Failed: {str(e)}")

    if st.session_state.dataset_intelligence_results is not None:
        res = st.session_state.dataset_intelligence_results
        kpi = res["kpi_summary"]
        num_countries = len(set(str(c.get('country', 'Unspecified')) for c in res['customers'] if c.get('country')))
        
        st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Overview</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Dataset Summary</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-subtitle'>Live processing metrics for <b>{st.session_state.uploaded_file_name}</b>. Switch tabs above to explore your analytics workspace.</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            metric_card("Dataset Name", str(st.session_state.uploaded_file_name), "Active Workspace File")
            st.markdown("<br>", unsafe_allow_html=True)
            metric_card("Total Customers", f"{kpi['total_customers']:,}", "Unique Analyzed Profiles")
        with c2:
            metric_card("Date Range", str(st.session_state.dataset_date_range), "Inferred Timeline")
            st.markdown("<br>", unsafe_allow_html=True)
            metric_card("Total Transactions", f"{kpi['total_transactions']:,}", "Invoices Processed")
        with c3:
            metric_card("Processing Time", str(st.session_state.dataset_proc_time), "Two-Stage Pipeline Run", accent="linear-gradient(90deg, #34d399, #10b981)")
            st.markdown("<br>", unsafe_allow_html=True)
            metric_card("Total Countries", f"{num_countries:,}", "Geographic Distribution", accent="linear-gradient(90deg, #60a5fa, #3b82f6)")


def render_di_dashboard_tab(res):
    if res is None:
        st.info("ℹ️ Please upload and analyze a dataset in the **Upload** tab first.")
        return
        
    kpi = res["kpi_summary"]
    st.markdown("<div class='section-kicker'>Intelligence Report</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Business KPI Summary</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Key retention metrics computed in-memory across the uploaded dataset cohort.</div>", unsafe_allow_html=True)

    row1_col1, row1_col2, row1_col3, row1_col4 = st.columns(4)
    with row1_col1:
        metric_card("Total Customers", f"{kpi['total_customers']:,}", "Analyzed Profiles")
    with row1_col2:
        metric_card("Total Transactions", f"{kpi['total_transactions']:,}", "Invoices Ingested")
    with row1_col3:
        metric_card("Total Revenue", f"${kpi['total_revenue']:,.2f}", "Cumulative Spend")
    with row1_col4:
        metric_card("Avg Predicted CLV", f"${kpi['average_predicted_clv']:,.2f}", "90-Day Expected Value", accent="linear-gradient(90deg, #34d399, #10b981)")

    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
    with row2_col1:
        metric_card("High Risk Customers", f"{kpi['high_risk_customers']:,}", "Probability ≥ 50%", accent="linear-gradient(90deg, #fb7185, #e11d48)")
    with row2_col2:
        metric_card("Medium Risk Customers", f"{kpi['medium_risk_customers']:,}", "Probability 30% - 50%", accent="linear-gradient(90deg, #f59e0b, #d97706)")
    with row2_col3:
        metric_card("Low Risk Customers", f"{kpi['low_risk_customers']:,}", "Probability < 30%", accent="linear-gradient(90deg, #38bdf8, #0284c7)")
    with row2_col4:
        metric_card("VIP Customers", f"{kpi['vip_customers']:,}", "Top Tier Whales", accent="linear-gradient(90deg, #a855f7, #6366f1)")

    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Visual Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distributions & Behavioral Patterns</div>", unsafe_allow_html=True)

    df_cust = pd.DataFrame(res["customers"])

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("#### Churn Risk Distribution")
        risk_counts = df_cust['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        color_map = {"High": "#fb7185", "Medium": "#f59e0b", "Low": "#34d399"}
        fig_risk = px.pie(risk_counts, names='Risk Level', values='Count', color='Risk Level', color_discrete_map=color_map, hole=0.5)
        fig_risk.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5eefb", margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("#### Strategic Quadrant Segments")
        seg_counts = df_cust['segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']
        fig_seg = px.bar(seg_counts, x='Count', y='Segment', orientation='h', color='Segment', color_discrete_sequence=["#60a5fa", "#5eead4", "#f43f5e", "#fbbf24"])
        fig_seg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#e5eefb", showlegend=False, margin=dict(t=20, b=20, l=20, r=20), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_seg, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_di_customers_tab(res):
    if res is None:
        st.info("ℹ️ Please upload and analyze a dataset in the **Upload** tab first.")
        return
        
    st.markdown("<div class='section-kicker'>Explorer</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Customer 360 & Directory</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Search, filter, sort, and inspect individual customer profiles in your active batch dataset.</div>", unsafe_allow_html=True)
    
    df_all = pd.DataFrame(res["customers"])
    
    with st.expander("🔍 Filter & Sort Controls", expanded=True):
        search_id = st.text_input("Search by Customer ID", placeholder="Type ID (e.g. 12345)...", key="di_c_s").strip().lower()
        
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            countries = ["All"] + sorted([str(c) for c in df_all['country'].unique() if pd.notna(c)])
            selected_country = st.selectbox("Filter by Country", countries, key="di_c_c")
        with fc2:
            segments = ["All"] + sorted(list(df_all['segment'].unique()))
            selected_seg = st.selectbox("Filter by Segment", segments, key="di_c_seg")
        with fc3:
            selected_risk = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"], key="di_c_risk")
            
        sc1, sc2 = st.columns(2)
        with sc1:
            sort_by = st.selectbox("Sort By", ["Predicted CLV", "Churn Probability", "Historical Revenue"], key="di_c_sort")
        with sc2:
            sort_order = st.selectbox("Order", ["Descending", "Ascending"], key="di_c_ord")

    df_filt = df_all.copy()
    if search_id:
        df_filt = df_filt[df_filt['customer_id'].astype(str).str.lower().str.contains(search_id)]
    if selected_country != "All":
        df_filt = df_filt[df_filt['country'] == selected_country]
    if selected_seg != "All":
        df_filt = df_filt[df_filt['segment'] == selected_seg]
    if selected_risk != "All":
        df_filt = df_filt[df_filt['risk_level'] == selected_risk]

    sort_col_map = {"Predicted CLV": "clv", "Churn Probability": "churn_probability", "Historical Revenue": "monetary"}
    df_filt = df_filt.sort_values(by=sort_col_map[sort_by], ascending=(sort_order == "Ascending"))
    
    total_items = len(df_filt)
    page_size = 20
    total_pages = max(1, (total_items + page_size - 1) // page_size)
    if st.session_state.di_cust_page > total_pages:
        st.session_state.di_cust_page = total_pages
        
    start_idx = (st.session_state.di_cust_page - 1) * page_size
    end_idx = min(total_items, start_idx + page_size)
    page_df = df_filt.iloc[start_idx:end_idx]
    
    st.markdown(f"#### Matching Customers ({total_items:,} found)")
    if total_items == 0:
        st.warning("No customers match the selected filters.")
        return

    table_display = page_df[["customer_id", "country", "segment", "risk_level", "clv", "churn_probability", "monetary"]].copy()
    table_display.columns = ["Customer ID", "Country", "Segment", "Risk Level", "Predicted CLV ($)", "Churn Probability", "Historical Spend ($)"]
    table_display["Predicted CLV ($)"] = table_display["Predicted CLV ($)"].apply(lambda x: f"${float(x):,.2f}")
    table_display["Historical Spend ($)"] = table_display["Historical Spend ($)"].apply(lambda x: f"${float(x):,.2f}")
    table_display["Churn Probability"] = table_display["Churn Probability"].apply(lambda x: f"{float(x):.1%}")
    st.dataframe(dark_table(table_display), use_container_width=True, hide_index=True)
    
    # Pagination buttons
    if total_pages > 1:
        pc1, pc2, pc3 = st.columns([1, 2, 1])
        with pc1:
            if st.button("← Previous Page", disabled=(st.session_state.di_cust_page <= 1), key="di_cp_prev"):
                st.session_state.di_cust_page -= 1
                st.rerun()
        with pc2:
            st.markdown(f"<div style='text-align: center; color: var(--muted); margin-top: 6px;'>Page {st.session_state.di_cust_page} of {total_pages}</div>", unsafe_allow_html=True)
        with pc3:
            if st.button("Next Page →", disabled=(st.session_state.di_cust_page >= total_pages), key="di_cp_next"):
                st.session_state.di_cust_page += 1
                st.rerun()

    # Customer 360 Deep Dive
    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Deep Dive</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Customer 360 Explorer</div>", unsafe_allow_html=True)
    
    selected_360_id = st.selectbox("📌 Select Customer ID to open 360 Deep Dive & Retention Strategy:", options=df_filt["customer_id"].tolist(), key="di_360_sel")
    cust_data = df_filt[df_filt["customer_id"] == selected_360_id].iloc[0]
    
    with st.expander(f"👤 Customer 360 Profile — ID: {cust_data['customer_id']} ({cust_data['country']})", expanded=True):
        clean_segment = str(cust_data['segment']).split(' (')[0].strip()
        st.markdown(f"**Strategic Segment:** `{clean_segment}` | **Risk Rating:** `{cust_data['risk_level']}` | **VIP Status:** `{'Yes 👑' if cust_data['is_vip'] else 'No'}`")
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("##### 📈 Business Metrics")
        bm1, bm2, bm3, bm4 = st.columns(4)
        with bm1: metric_card("Historical Spend", f"${cust_data['monetary']:,.2f}", "Total Cumulative")
        with bm2: metric_card("Predicted 90D CLV", f"${cust_data['clv']:,.2f}", "Expected Value", accent="linear-gradient(90deg, #34d399, #10b981)")
        with bm3: metric_card("Churn Probability", f"{cust_data['churn_probability']:.1%}", f"{cust_data['risk_level']} Risk", accent="linear-gradient(90deg, #fb7185, #e11d48)" if cust_data['churn_probability']>=0.5 else "linear-gradient(90deg, #38bdf8, #0284c7)")
        with bm4: metric_card("Customer Segment", clean_segment, "Strategic Quadrant", accent="linear-gradient(90deg, #a855f7, #6366f1)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### ⚙️ Behavioral Features")
        bf1, bf2, bf3, bf4 = st.columns(4)
        with bf1: metric_card("Recency & Freq", f"{cust_data['recency']:.0f}d | {cust_data['frequency']:.0f} orders", "Last purchase & volume")
        with bf2: metric_card("Monetary", f"${cust_data['monetary']:,.2f}", "Lifetime revenue")
        with bf3: metric_card("Tenure & Velocity", f"{cust_data['tenure']:.0f}d | {cust_data['velocity']:.2f}/mo", "Account span & pace")
        with bf4: metric_card("AOV & Diversity", f"${cust_data['aov']:,.2f} | {cust_data['item_diversity']:.0f} items", "Basket size & variety")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### 💡 Business Recommendation")
        st.info(f"**Recommended Retention Strategy:** {get_di_recommendation(cust_data['segment'], cust_data['monetary'], cust_data['churn_probability'])}")


def render_di_segmentation_tab(res):
    if res is None:
        st.info("ℹ️ Please upload and analyze a dataset in the **Upload** tab first.")
        return
        
    st.markdown("<div class='section-kicker'>Portfolio Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Segmentation Analytics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Analyze customer groups based on value, engagement, and churn risk using dynamic scenario controls.</div>", unsafe_allow_html=True)

    df_seg = pd.DataFrame(res["customers"])

    # Initialize Scenario Controls in session state
    if "di_sa_risk_slider" not in st.session_state:
        st.session_state.di_sa_risk_slider = 50
    if "di_sa_risk_manual" not in st.session_state:
        st.session_state.di_sa_risk_manual = 50

    default_clv = int(df_seg["clv"].quantile(0.75)) if len(df_seg) > 0 and pd.notnull(df_seg["clv"].quantile(0.75)) else 400
    if "di_sa_clv_slider" not in st.session_state:
        st.session_state.di_sa_clv_slider = default_clv
    if "di_sa_clv_manual" not in st.session_state:
        st.session_state.di_sa_clv_manual = default_clv

    def sync_risk_slider():
        st.session_state.di_sa_risk_manual = st.session_state.di_sa_risk_slider
    def sync_risk_manual():
        st.session_state.di_sa_risk_slider = st.session_state.di_sa_risk_manual
    def sync_clv_slider():
        st.session_state.di_sa_clv_manual = st.session_state.di_sa_clv_slider
    def sync_clv_manual():
        st.session_state.di_sa_clv_slider = st.session_state.di_sa_clv_manual

    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Simulation</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 12px;'>Scenario Controls</div>", unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        st.slider("Churn Risk Threshold (%)", min_value=0, max_value=100, step=1, key="di_sa_risk_slider", on_change=sync_risk_slider)
        st.number_input("Manual Input: Risk (%)", min_value=0, max_value=100, step=1, key="di_sa_risk_manual", on_change=sync_risk_manual)
    with sc2:
        st.slider("High-Value Cutoff ($)", min_value=0, max_value=10000, step=50, key="di_sa_clv_slider", on_change=sync_clv_slider)
        st.number_input("Manual Input: Cutoff ($)", min_value=0, max_value=10000, step=50, key="di_sa_clv_manual", on_change=sync_clv_manual)

    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Fetch Data", type="primary", use_container_width=True, key="di_sa_fetch")
    st.markdown("</div>", unsafe_allow_html=True)

    # Calculate dynamically segmented frame matching existing application logic
    sim_risk = st.session_state.di_sa_risk_slider / 100.0
    sim_clv = float(st.session_state.di_sa_clv_slider)

    df_sim = df_seg.copy()
    conditions = [
        (df_sim["churn_probability"] >= sim_risk) & (df_sim["clv"] >= sim_clv),
        (df_sim["churn_probability"] < sim_risk) & (df_sim["clv"] >= sim_clv),
        (df_sim["churn_probability"] >= sim_risk) & (df_sim["clv"] < sim_clv),
        (df_sim["churn_probability"] < sim_risk) & (df_sim["clv"] < sim_clv),
    ]
    choices = ["High-Risk Whales", "Loyal Champions", "At-Risk Regulars", "Safe Regulars"]
    df_sim["Segment"] = np.select(conditions, choices, default="Unknown")

    # Full-width Risk vs. Value Scatter Matrix (Styled matching Main Dashboard)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Customer Map</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Risk vs. value scatter matrix</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle' style='margin-bottom: 12px;'>Each dot is a customer. Lower risk is on the left, higher value is higher up.</div>", unsafe_allow_html=True)
    
    fig_sim = px.scatter(
        df_sim,
        x="churn_probability",
        y="clv",
        color="Segment",
        hover_name="customer_id",
        hover_data=["country", "risk_level"],
        opacity=0.8,
        color_discrete_map={
            "High-Risk Whales": "#ff3b30",
            "Loyal Champions": "#34c759",
            "At-Risk Regulars": "#ff9500",
            "Safe Regulars": "#8e8e93",
        },
    )
    fig_sim.add_vline(x=sim_risk, line_dash="dash", line_color="#c7c7cc")
    fig_sim.add_hline(y=sim_clv, line_dash="dash", line_color="#c7c7cc")
    fig_sim.update_layout(
        template="plotly_dark",
        height=480,
        xaxis_tickformat=".0%",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title="",
            bgcolor="rgba(7, 17, 31, 0.88)",
            bordercolor="rgba(148, 163, 184, 0.18)",
            borderwidth=1,
            font=dict(color="#f8fbff"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
    )
    fig_sim.update_xaxes(showgrid=False, zeroline=False, range=[0, 1.05], title="Churn_Probability")
    fig_sim.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, type="log", title="Predicted 90-Day CLV (Log Scale)")
    st.plotly_chart(fig_sim, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Full-width Revenue Mix Pie Chart (Styled matching Segmentation Analytics)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Revenue Mix</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Segment revenue share</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle' style='margin-bottom: 12px;'>Revenue share distribution by strategic retention cohort.</div>", unsafe_allow_html=True)
    
    segment_summary = df_sim.groupby("Segment", as_index=False)["clv"].sum().sort_values("clv", ascending=False)
    fig_pie = px.pie(
        segment_summary,
        names="Segment",
        values="clv",
        hole=0.48,
        color="Segment",
        color_discrete_map={
            "High-Risk Whales": "#ff3b30",
            "Loyal Champions": "#34c759",
            "At-Risk Regulars": "#ff9500",
            "Safe Regulars": "#8e8e93",
        },
    )
    fig_pie.update_layout(
        template="plotly_dark",
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title="",
            bgcolor="rgba(7, 17, 31, 0.88)",
            bordercolor="rgba(148, 163, 184, 0.18)",
            borderwidth=1,
            font=dict(color="#f8fbff"),
        ),
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Segment Summary Cards
    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Strategies</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Segment Summary Cards</div>", unsafe_allow_html=True)
    
    seg_groups = df_sim.groupby("Segment")
    seg_names = ["High-Risk Whales", "Loyal Champions", "At-Risk Regulars", "Safe Regulars"]
    cols = st.columns(len(seg_names))
    for idx, sname in enumerate(seg_names):
        with cols[idx]:
            if sname in seg_groups.groups:
                s_df = seg_groups.get_group(sname)
                s_cnt = len(s_df)
                s_clv = s_df['clv'].mean()
                s_prob = s_df['churn_probability'].mean()
                rec = get_di_recommendation(sname, s_clv, s_prob)
            else:
                s_cnt, s_clv, s_prob = 0, 0.0, 0.0
                rec = "No matching customers in cohort."
            accent_c = "linear-gradient(90deg, #ff3b30, #e11d48)" if "High" in sname else "linear-gradient(90deg, #34c759, #10b981)" if "Loyal" in sname else "linear-gradient(90deg, #ff9500, #d97706)" if "At-Risk" in sname else "linear-gradient(90deg, #38bdf8, #0284c7)"
            metric_card(sname.upper(), f"{s_cnt:,} users", f"Avg CLV: ${s_clv:,.0f} | Avg Churn: {s_prob:.1%}", accent=accent_c)
            st.caption(f"**Action:** {rec}")

    # Customer Segment Table
    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>Segment Table</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Customer Segment Portfolio</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle' style='margin-bottom: 15px;'>Select a dynamic segment from the Summary Cards above to inspect its specific customer cohort.</div>", unsafe_allow_html=True)
    
    def reset_di_seg_page():
        st.session_state.di_seg_page = 1

    scol1, scol2, scol3 = st.columns([2, 1.5, 1.5])
    with scol1:
        selected_table_seg = st.selectbox(
            "📌 Select Segment Cohort", 
            ["All Segments", "High-Risk Whales", "Loyal Champions", "At-Risk Regulars", "Safe Regulars"], 
            key="di_st_seg_filter",
            on_change=reset_di_seg_page
        )
    with scol2:
        seg_search = st.text_input("🔍 Search Customer ID", key="di_st_s", on_change=reset_di_seg_page).strip().lower()
    with scol3:
        seg_sort = st.selectbox("Sort Table By", ["Predicted CLV", "Churn Probability"], key="di_st_sort", on_change=reset_di_seg_page)
        
    df_stable = df_sim.copy()
    if selected_table_seg != "All Segments":
        df_stable = df_stable[df_stable['Segment'] == selected_table_seg]
    if seg_search:
        df_stable = df_stable[df_stable['customer_id'].astype(str).str.lower().str.contains(seg_search)]
    df_stable = df_stable.sort_values(by="clv" if seg_sort=="Predicted CLV" else "churn_probability", ascending=False)
    
    spage_size = 15
    stotal_items = len(df_stable)
    stotal_pages = max(1, (stotal_items + spage_size - 1) // spage_size)
    if st.session_state.di_seg_page > stotal_pages: st.session_state.di_seg_page = stotal_pages
    sstart = (st.session_state.di_seg_page - 1) * spage_size
    send = min(stotal_items, sstart + spage_size)
    spage_df = df_stable.iloc[sstart:send]
    
    st.markdown(f"**Cohort View:** `{selected_table_seg}` — Showing `{stotal_items:,}` matching customers")
    if stotal_items == 0:
        st.info(f"No customers found matching `{selected_table_seg}` under the current scenario settings.")
    else:
        st_display = spage_df[["customer_id", "Segment", "clv", "churn_probability", "country"]].copy()
        st_display.columns = ["Customer ID", "Segment", "Predicted CLV ($)", "Churn Probability", "Country"]
        st_display["Predicted CLV ($)"] = st_display["Predicted CLV ($)"].apply(lambda x: f"${float(x):,.2f}")
        st_display["Churn Probability"] = st_display["Churn Probability"].apply(lambda x: f"{float(x):.1%}")
        st.dataframe(dark_table(st_display), use_container_width=True, hide_index=True)
        
        if stotal_pages > 1:
            p1, p2, p3 = st.columns([1, 2, 1])
            with p1:
                if st.button("← Previous", disabled=(st.session_state.di_seg_page <= 1), key="di_sp_prev"):
                    st.session_state.di_seg_page -= 1
                    st.rerun()
            with p2:
                st.markdown(f"<div style='text-align: center; color: var(--muted); margin-top: 6px;'>Page {st.session_state.di_seg_page} of {stotal_pages}</div>", unsafe_allow_html=True)
            with p3:
                if st.button("Next →", disabled=(st.session_state.di_seg_page >= stotal_pages), key="di_sp_next"):
                    st.session_state.di_seg_page += 1
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_di_reports_tab(res):
    if res is None:
        st.info("ℹ️ Please upload and analyze a dataset in the **Upload** tab first.")
        return
        
    st.markdown("<div class='section-kicker'>Exports</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Export Center & Reports</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Download professional CSV spreadsheets and executive summary PDFs for your batch analysis.</div>", unsafe_allow_html=True)
    
    df_all = pd.DataFrame(res["customers"])
    kpi = res["kpi_summary"]
    
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### 1. Core Analytical Exports")
    r_c1, r_c2 = st.columns(2)
    with r_c1:
        csv_data = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Complete Predictions (CSV)",
            data=csv_data,
            file_name=f"dataset_predictions_{st.session_state.uploaded_file_name}.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True
        )
        st.caption("Includes all RFM features, churn probabilities, CLV estimates, and risk segments for all customers.")
    with r_c2:
        summary_records = []
        for k, v in kpi.items():
            summary_records.append({"Metric": k.replace("_", " ").title(), "Value": f"${v:,.2f}" if "revenue" in k or "clv" in k else f"{v:,}"})
        summary_df = pd.DataFrame(summary_records)
        try:
            pdf_bytes = create_pdf_table(f"Executive Summary - {st.session_state.uploaded_file_name}", summary_df)
            st.download_button(
                label="📄 Download Executive Summary (PDF)",
                data=pdf_bytes,
                file_name=f"Executive_Summary_{st.session_state.uploaded_file_name}.pdf",
                mime="application/pdf",
                type="secondary",
                use_container_width=True
            )
            st.caption("A publication-grade PDF executive report detailing KPI totals and primary analysis outcomes.")
        except Exception as e:
            st.error(f"Failed to generate PDF Report: {e}")
            
    st.markdown("<br><hr style='border-color: #1a1e23;'><br>", unsafe_allow_html=True)
    st.markdown("#### 2. Specialized Cohort Exports")
    o_c1, o_c2 = st.columns(2)
    with o_c1:
        df_high = df_all[df_all['risk_level'] == 'High'].copy()
        high_csv = df_high.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="🚨 Download High Risk Customers (CSV)",
            data=high_csv,
            file_name=f"high_risk_{st.session_state.uploaded_file_name}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption(f"Filtered export consisting solely of the {len(df_high):,} customers with Churn Probability ≥ 50%.")
    with o_c2:
        seg_sum = df_all.groupby("segment", as_index=False).agg(
            Customer_Count=("customer_id", "count"),
            Total_Spend=("monetary", "sum"),
            Avg_Predicted_CLV=("clv", "mean"),
            Avg_Churn_Prob=("churn_probability", "mean")
        )
        seg_csv = seg_sum.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📊 Download Segment Summary (CSV)",
            data=seg_csv,
            file_name=f"segment_summary_{st.session_state.uploaded_file_name}.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.caption("Aggregated statistical overview broken out by strategic portfolio quadrants.")
    st.markdown("</div>", unsafe_allow_html=True)


# -------------------------------------------------------------
# MAIN UI ROUTING BY PREDICTION MODE
# -------------------------------------------------------------
st.markdown("<div class='section-kicker'>Inference</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Prediction Mode</div>", unsafe_allow_html=True)

mode = st.radio("Select Input Method", ["Existing Customer", "New Customer", "Dataset Intelligence"], horizontal=True)

prediction_response = None
recommended_action = ""
customer_identifier = ""

if mode == "Existing Customer":
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Search Existing Customer")
    
    search_col, _ = st.columns([1, 1])
    with search_col:
        search_query = st.text_input("Customer ID (or part of it)", placeholder="e.g. 12345")
    search_btn = st.button("Search", type="primary")
        
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
        
    if search_btn and search_query:
        try:
            with st.spinner("Searching..."):
                st.session_state.search_results = api_client.search_customers(search_query)
        except Exception:
            st.error("Failed to connect to the backend.")
            
    if st.session_state.search_results:
        customer_options = [c["customer_id"] for c in st.session_state.search_results]
        selected_id = st.selectbox("Select Customer to Predict", options=customer_options)
        predict_btn = st.button("Generate Prediction", type="primary")
            
        if predict_btn:
            try:
                with st.spinner("Fetching features and running model..."):
                    c_data = api_client.get_customer_360(selected_id)["customer"]
                    features = {
                        "Recency": float(c_data["recency"]),
                        "Frequency": float(c_data["frequency"]),
                        "Monetary": float(c_data["monetary"]),
                        "Tenure": float(c_data.get("customer_lifespan", 0)),
                        "Velocity": float(c_data.get("purchase_frequency", 0)),
                        "AOV": float(c_data.get("avg_order_value", 0)),
                        "ItemDiversity": float(c_data.get("item_diversity", 0))
                    }
                    prediction_response = api_client.predict_customer(features)
                    customer_identifier = selected_id
                    
                    if prediction_response["churn_prediction"] == 1:
                        recommended_action = "Win-Back Campaign (VIP)" if features["Monetary"] > 1000 else "Discount Offer (15%)"
                    else:
                        recommended_action = "Loyalty Program / Upsell" if features["Monetary"] > 1000 else "Standard Marketing Drip"
            except Exception as e:
                st.error("⚠️ Failed to generate prediction. The backend service may be unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

elif mode == "New Customer":
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Enter Manual Features")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        recency = st.number_input("Recency (Days)", min_value=0.0, value=30.0)
        tenure = st.number_input("Tenure (Days)", min_value=0.0, value=150.0)
        item_diversity = st.number_input("Item Diversity", min_value=1.0, value=15.0)
    with col2:
        frequency = st.number_input("Frequency (Orders)", min_value=1.0, value=5.0)
        velocity = st.number_input("Velocity (Orders/Mo)", min_value=0.0, value=1.5)
    with col3:
        monetary = st.number_input("Monetary Value ($)", min_value=0.0, value=1000.0)
        aov = st.number_input("Average Order Value ($)", min_value=0.0, value=200.0)
        
    predict_btn = st.button("Generate Prediction", type="primary")
        
    if predict_btn:
        try:
            with st.spinner("Running model..."):
                features = {
                    "Recency": recency,
                    "Frequency": frequency,
                    "Monetary": monetary,
                    "Tenure": tenure,
                    "Velocity": velocity,
                    "AOV": aov,
                    "ItemDiversity": item_diversity
                }
                prediction_response = api_client.predict_customer(features)
                customer_identifier = "Manual Input"
                
                if prediction_response["churn_prediction"] == 1:
                    recommended_action = "Win-Back Campaign (VIP)" if features["Monetary"] > 1000 else "Discount Offer (15%)"
                else:
                    recommended_action = "Loyalty Program / Upsell" if features["Monetary"] > 1000 else "Standard Marketing Drip"
        except Exception as e:
            st.error("⚠️ Failed to generate prediction. The backend service may be unavailable.")
    st.markdown("</div>", unsafe_allow_html=True)

else: # Dataset Intelligence Mode (Self-contained tabbed workspace)
    st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
    tab_upl, tab_dash, tab_cust, tab_seg, tab_rep = st.tabs([
        "📁 1. Upload", 
        "📊 2. Dashboard", 
        "👥 3. Customers", 
        "🔮 4. Segmentation", 
        "📥 5. Reports"
    ])
    
    with tab_upl:
        render_di_upload_tab()
    with tab_dash:
        render_di_dashboard_tab(st.session_state.dataset_intelligence_results)
    with tab_cust:
        render_di_customers_tab(st.session_state.dataset_intelligence_results)
    with tab_seg:
        render_di_segmentation_tab(st.session_state.dataset_intelligence_results)
    with tab_rep:
        render_di_reports_tab(st.session_state.dataset_intelligence_results)
        
    st.markdown("</div>", unsafe_allow_html=True)


# Render single prediction outputs and history only for Existing & New Customer modes
if mode != "Dataset Intelligence":
    if prediction_response:
        render_prediction_result(prediction_response, recommended_action)
        
        hist_record = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Customer": customer_identifier,
            "Risk Level": prediction_response["risk_level"],
            "Probability": f"{prediction_response['churn_probability']:.1%}"
        }
        st.session_state.recent_predictions.insert(0, hist_record)
        st.session_state.recent_predictions = st.session_state.recent_predictions[:10]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-kicker'>History</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Recent Predictions</div>", unsafe_allow_html=True)
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

    if st.session_state.recent_predictions:
        hist_df = pd.DataFrame(st.session_state.recent_predictions)
        st.dataframe(dark_table(hist_df).set_properties(subset=hist_df.columns, **{"text-align": "left"}), use_container_width=True, hide_index=True)
    else:
        st.info("No predictions generated yet in this session.")
        
    st.markdown("</div>", unsafe_allow_html=True)
