import plotly.express as px
import pandas as pd
import streamlit as st

from utils.dashboard_utils import build_segmented_frame, dark_table, inject_global_styles, load_data, page_header


inject_global_styles()

df_master = load_data()

if "sa_risk_slider" not in st.session_state:
    st.session_state.sa_risk_slider = 50
if "sa_risk_manual" not in st.session_state:
    st.session_state.sa_risk_manual = 50

default_clv = int(df_master["predicted_90d_clv"].quantile(0.75))
if "sa_clv_slider" not in st.session_state:
    st.session_state.sa_clv_slider = default_clv
if "sa_clv_manual" not in st.session_state:
    st.session_state.sa_clv_manual = default_clv

def sa_sync_risk_from_slider():
    st.session_state.sa_risk_manual = st.session_state.sa_risk_slider
def sa_sync_risk_from_manual():
    st.session_state.sa_risk_slider = st.session_state.sa_risk_manual

def sa_sync_clv_from_slider():
    st.session_state.sa_clv_manual = st.session_state.sa_clv_slider
def sa_sync_clv_from_manual():
    st.session_state.sa_clv_slider = st.session_state.sa_clv_manual

st.sidebar.markdown("### Scenario Controls")
st.sidebar.slider("Churn Risk Threshold (%)", min_value=0, max_value=100, step=1, key="sa_risk_slider", on_change=sa_sync_risk_from_slider)
st.sidebar.number_input("Manual Input: Risk (%)", min_value=0, max_value=100, step=1, key="sa_risk_manual", on_change=sa_sync_risk_from_manual)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.slider("High-Value Cutoff ($)", min_value=0, max_value=10000, step=50, key="sa_clv_slider", on_change=sa_sync_clv_from_slider)
st.sidebar.number_input("Manual Input: Cutoff ($)", min_value=0, max_value=10000, step=50, key="sa_clv_manual", on_change=sa_sync_clv_from_manual)

st.sidebar.markdown("<br>", unsafe_allow_html=True)
st.sidebar.button("Fetch Data", type="primary", use_container_width=True)

sim_risk = st.session_state.sa_risk_slider / 100.0
sim_clv = st.session_state.sa_clv_slider

df_sim = build_segmented_frame(df_master, sim_risk, sim_clv)

page_header(
    "SEGMENTATION ANALYTICS",
    "Customer Segmentation",
    "Analyze customer groups based on value, engagement, and churn risk.",
    None
)

segment_summary = df_sim.groupby("Segment", as_index=False)["predicted_90d_clv"].sum().sort_values("predicted_90d_clv", ascending=False)

fig = px.pie(
    segment_summary,
    names="Segment",
    values="predicted_90d_clv",
    hole=0.48,
    color="Segment",
    color_discrete_map={
        "High-Risk Whales": "#ff3b30",
        "Loyal Champions": "#34c759",
        "At-Risk Regulars": "#ff9500",
        "Safe Regulars": "#8e8e93",
    },
)
fig.update_layout(
    template="plotly_dark",
    height=520,
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

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Revenue Mix</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Segment revenue share</div>", unsafe_allow_html=True)
st.markdown("<div class='section-subtitle'>Revenue share by customer segment.</div>", unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='content-panel'>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Segment Table</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Portfolio counts by segment</div>", unsafe_allow_html=True)
segment_counts = df_sim.groupby("Segment").size().reset_index(name="Customers")
segment_download = segment_counts.to_csv(index=False).encode("utf-8")
detail_download = df_sim[
    ["CustomerID", "Segment", "Churn_Probability", "predicted_90d_clv", "Recency", "Frequency"]
].sort_values(["Segment", "predicted_90d_clv"], ascending=[True, False])
detail_download_csv = detail_download.to_csv(index=False).encode("utf-8")

download_left, download_right = st.columns(2)
with download_left:
    st.download_button(
        "Download segment summary CSV",
        data=segment_download,
        file_name="segment_summary.csv",
        mime="text/csv",
        use_container_width=True,
    )
with download_right:
    st.download_button(
        "Download customer segment CSV",
        data=detail_download_csv,
        file_name="customer_segment_export.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.dataframe(dark_table(segment_counts), use_container_width=True, hide_index=True)
st.markdown("</div>", unsafe_allow_html=True)