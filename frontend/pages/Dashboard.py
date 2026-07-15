import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.dashboard_utils import (
    build_segmented_frame,
    dark_table,
    get_recommendation,
    inject_global_styles,
    metric_card,
    page_header,
)
from utils.api_client import api_client

inject_global_styles()

try:
    with st.spinner("Connecting to backend services..."):
        # We fetch summary_data just in case we need fallbacks, but we'll calculate KPIs dynamically
        summary_data = api_client.get_dashboard_summary()
        charts_data = api_client.get_dashboard_charts()
        interventions_data = api_client.get_dashboard_interventions()
        model_data = api_client.get_model_summary()
except Exception:
    st.error("⚠️ The backend service is currently unavailable. Please ensure the FastAPI server is running and try again.")
    st.stop()

# Reconstruct necessary dataframe for scatter plot simulation
df_scatter = pd.DataFrame(charts_data.get("risk_vs_value", []))
if not df_scatter.empty:
    # Rename columns to match what dashboard_utils expects
    df_scatter.rename(columns={"clv": "predicted_90d_clv", "churn_probability": "Churn_Probability", "customer_id": "CustomerID"}, inplace=True)
    max_clv = int(df_scatter["predicted_90d_clv"].max())
    default_clv = int(df_scatter["predicted_90d_clv"].quantile(0.75))
else:
    max_clv = 1000
    default_clv = 500

if "sim_risk_slider" not in st.session_state:
    st.session_state.sim_risk_slider = 50
if "sim_risk_manual" not in st.session_state:
    st.session_state.sim_risk_manual = 50
if "sim_clv_slider" not in st.session_state:
    st.session_state.sim_clv_slider = default_clv
if "sim_clv_manual" not in st.session_state:
    st.session_state.sim_clv_manual = default_clv

def sync_risk_from_slider():
    st.session_state.sim_risk_manual = st.session_state.sim_risk_slider
def sync_risk_from_manual():
    st.session_state.sim_risk_slider = st.session_state.sim_risk_manual

def sync_clv_from_slider():
    st.session_state.sim_clv_manual = st.session_state.sim_clv_slider
def sync_clv_from_manual():
    st.session_state.sim_clv_slider = st.session_state.sim_clv_manual

st.sidebar.markdown("### Scenario Controls")
st.sidebar.slider("Churn Risk Threshold (%)", min_value=0, max_value=100, step=1, key="sim_risk_slider", on_change=sync_risk_from_slider)
st.sidebar.number_input("Manual Input: Risk (%)", min_value=0, max_value=100, step=1, key="sim_risk_manual", on_change=sync_risk_from_manual)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.slider("High-Value Cutoff ($)", min_value=0, max_value=10000, step=50, key="sim_clv_slider", on_change=sync_clv_from_slider)
st.sidebar.number_input("Manual Input: Cutoff ($)", min_value=0, max_value=10000, step=50, key="sim_clv_manual", on_change=sync_clv_from_manual)

# The form is removed to allow live syncing, but we keep the button for UX continuity
st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.button("Fetch Data", type="primary", use_container_width=True)

sim_risk = st.session_state.sim_risk_slider / 100.0
sim_clv = st.session_state.sim_clv_slider

# ---------------------------------------------------------
# DYNAMIC KPI CALCULATIONS BASED ON SCENARIO SLIDERS
# ---------------------------------------------------------
if not df_scatter.empty:
    # Ensure columns are properly typed for calculation
    df_scatter["predicted_90d_clv"] = pd.to_numeric(df_scatter["predicted_90d_clv"], errors="coerce").fillna(0.0)
    df_scatter["Churn_Probability"] = pd.to_numeric(df_scatter["Churn_Probability"], errors="coerce").fillna(0.0)
    
    # Explicitly calculate the 4 portfolio segments based on BOTH scenario controls
    
    # 1. High-Risk Whales (High Risk, High Value)
    whales_df = df_scatter[(df_scatter["Churn_Probability"] >= float(sim_risk)) & (df_scatter["predicted_90d_clv"] >= float(sim_clv))]
    
    # 2. At-Risk Regulars (High Risk, Low Value)
    at_risk_regulars_df = df_scatter[(df_scatter["Churn_Probability"] >= float(sim_risk)) & (df_scatter["predicted_90d_clv"] < float(sim_clv))]
    
    # 3. Loyal Champions (Safe, High Value)
    champions_df = df_scatter[(df_scatter["Churn_Probability"] < float(sim_risk)) & (df_scatter["predicted_90d_clv"] >= float(sim_clv))]
    
    # 4. Safe Regulars (Safe, Low Value)
    safe_regulars_df = df_scatter[(df_scatter["Churn_Probability"] < float(sim_risk)) & (df_scatter["predicted_90d_clv"] < float(sim_clv))]
    
    # Revenue at risk = At-Risk Regulars + High-Risk Whales (as requested)
    rev_at_risk = float(whales_df["predicted_90d_clv"].sum()) + float(at_risk_regulars_df["predicted_90d_clv"].sum())
    
    # Secured revenue = Safe Regulars + Loyal Champions
    safe_rev = float(champions_df["predicted_90d_clv"].sum()) + float(safe_regulars_df["predicted_90d_clv"].sum())
    
    # Total revenue remains the total of all segments
    total_rev = rev_at_risk + safe_rev
    
    # High-Risk Whales count for the KPI card
    whale_count = len(whales_df)
else:
    total_rev = float(summary_data.get("projected_revenue", 0))
    rev_at_risk = float(summary_data.get("revenue_at_risk", 0))
    safe_rev = total_rev - rev_at_risk
    whale_count = int(summary_data.get("high_risk_customers", 0))

page_header(
    "RETAIN-AI",
    "Executive Dashboard",
    "Monitor churn risk, customer value, and portfolio performance.",
    None,
)


st.markdown("<div class='section-kicker'>Business Impact</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Portfolio overview</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Use the controls in the sidebar to update the portfolio view.</div>", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("Projected 90-Day Revenue", f"${total_rev:,.0f}", "Total portfolio forecast")
with col2:
    metric_card("Secured Revenue", f"${safe_rev:,.0f}", "Stable / low-risk accounts")
with col3:
    metric_card("Revenue at Risk", f"${rev_at_risk:,.0f}", "Requires immediate action", "linear-gradient(90deg, var(--warning), var(--danger))")
with col4:
    metric_card("High-Risk Whales", f"{whale_count}", "VIP accounts churning soon")

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Customer Map</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Risk vs. value scatter matrix</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Each dot is a customer. Lower risk is on the left, higher value is higher up.</div>", unsafe_allow_html=True)

if not df_scatter.empty:
    # Apply local simulation segmenting for the visual chart colors based on slider input
    df_sim = build_segmented_frame(df_scatter, sim_risk, sim_clv)
    
    fig_sim = px.scatter(
        df_sim,
        x="Churn_Probability",
        y="predicted_90d_clv",
        color="Segment",
        hover_name="CustomerID",
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
        height=470,
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
    fig_sim.update_xaxes(showgrid=False, zeroline=False, range=[0, 1.05])
    fig_sim.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False, type="log", title="Predicted 90-Day CLV (Log Scale)")
    st.plotly_chart(fig_sim, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Retention Ops</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Priority VIP interventions</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Customers in the highest-priority segment are listed below.</div>", unsafe_allow_html=True)

vips = pd.DataFrame(interventions_data)
if not vips.empty:
    # Dynamically filter the interventions table based on the slider thresholds!
    vips = vips[
        (vips["churn_probability"] >= sim_risk) &
        (vips["clv"] >= sim_clv)
    ]

if vips.empty:
    st.info("No High-Risk Whales detected under the current scenario.")
else:
    vip_display = vips[["customer_id", "clv", "churn_probability", "recency", "frequency"]].copy()
    # Rename columns to match old calculations and component expectations
    vip_display.columns = ["CustomerID", "predicted_90d_clv", "Churn_Probability", "Recency", "Frequency"]
    vip_display["Recommended Action"] = vip_display.apply(get_recommendation, axis=1)
    vip_display["Projected Loss Value"] = pd.to_numeric(vip_display["predicted_90d_clv"], errors="coerce").fillna(0.0)
    vip_display["Intervention Cost Value"] = vip_display["Recommended Action"].map(
        {
            "Win-Back Campaign": 0.06,
            "VIP Concierge": 0.10,
            "Exclusive Loyalty": 0.04,
        }
    ).fillna(0.05) * vip_display["Projected Loss Value"]
    vip_display["Net ROI Value"] = vip_display["Projected Loss Value"] - vip_display["Intervention Cost Value"]
    vip_display["Projected Loss"] = vip_display["Projected Loss Value"].apply(lambda x: f"${x:,.2f}")
    vip_display["Intervention Cost ($)"] = vip_display["Intervention Cost Value"].apply(lambda x: f"${x:,.2f}")
    vip_display["Net ROI ($)"] = vip_display["Net ROI Value"].apply(lambda x: f"${x:,.2f}")
    vip_display["Churn Risk"] = vip_display["Churn_Probability"].apply(lambda x: f"{x:.1%}")
    vip_display["Days Inactive"] = vip_display["Recency"].astype(int)
    vip_display = vip_display[["CustomerID", "Recommended Action", "Projected Loss", "Intervention Cost ($)", "Net ROI ($)", "Churn Risk", "Days Inactive"]]

    vip_csv = vip_display.to_csv(index=False).encode("utf-8")
    dl1, dl2 = st.columns(2)
    with dl1:
        st.download_button(
            "Download VIP interventions (CSV)",
            data=vip_csv,
            file_name="vip_interventions.csv",
            mime="text/csv",
            use_container_width=True,
        )
    from utils.pdf_utils import create_pdf_table
    with dl2:
        st.download_button(
            "Download VIP interventions (PDF)",
            data=create_pdf_table("VIP Interventions", vip_display),
            file_name="vip_interventions.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    styled_vips = dark_table(vip_display).set_properties(subset=vip_display.columns, **{"text-align": "left"})
    st.dataframe(
        styled_vips,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Recommended Action": st.column_config.TextColumn("Recommended Action"),
        },
    )

