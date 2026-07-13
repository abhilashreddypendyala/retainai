import plotly.express as px
import pandas as pd
import streamlit as st

from utils.dashboard_utils import build_segmented_frame, dark_table, inject_global_styles, load_data, page_header


inject_global_styles()

df_master = load_data()

st.sidebar.markdown("### Scenario Controls")
with st.sidebar.form("segmentation_scenario_form"):
    sim_risk = st.slider("Churn Risk Threshold (%)", min_value=10, max_value=90, value=50, step=5) / 100.0
    default_clv = int(df_master["predicted_90d_clv"].quantile(0.75))
    max_clv = int(df_master["predicted_90d_clv"].max())
    sim_clv = st.slider("High-Value Cutoff ($)", min_value=50, max_value=max_clv, value=default_clv, step=50)
    st.form_submit_button("Fetch Data", use_container_width=True)

df_sim = build_segmented_frame(df_master, sim_risk, sim_clv)

page_header(
    "Customer Segments",
    "Customer segment breakdown",
    "Segment-level revenue view.",
    ["Segmentation", "Revenue distribution", "Portfolio mix"],
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