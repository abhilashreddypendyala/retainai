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

st.sidebar.markdown("### Scenario Controls")
with st.sidebar.form("dashboard_scenario_form"):
    sim_risk = st.slider("Churn Risk Threshold (%)", min_value=10, max_value=90, value=50, step=5) / 100.0
    sim_clv = st.slider("High-Value Cutoff ($)", min_value=50, max_value=max_clv, value=default_clv, step=50)
    st.form_submit_button("Fetch Data", use_container_width=True)

# ---------------------------------------------------------
# DYNAMIC KPI CALCULATIONS BASED ON SCENARIO SLIDERS
# ---------------------------------------------------------
if not df_scatter.empty:
    # Total revenue remains the total of all customers
    total_rev = df_scatter["predicted_90d_clv"].sum()
    
    # Revenue at risk: anyone at or above the selected risk threshold
    at_risk_df = df_scatter[df_scatter["Churn_Probability"] >= sim_risk]
    rev_at_risk = at_risk_df["predicted_90d_clv"].sum()
    
    # Secured revenue is the rest
    safe_rev = total_rev - rev_at_risk
    
    # High-Risk Whales: at or above risk threshold AND at or above value threshold
    whales_df = at_risk_df[at_risk_df["predicted_90d_clv"] >= sim_clv]
    whale_count = len(whales_df)
else:
    total_rev = summary_data.get("projected_revenue", 0)
    rev_at_risk = summary_data.get("revenue_at_risk", 0)
    safe_rev = total_rev - rev_at_risk
    whale_count = summary_data.get("high_risk_customers", 0)

page_header(
    "RETAIN-AI Overview",
    "Customer risk and value",
    "Overall portfolio view.",
    ["Churn scoring", "Customer value", "VIP actions", "Scenario controls"],
)

tab_overview, tab_hood = st.tabs(["Overview", "Under the Hood"])

with tab_overview:
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

with tab_hood:
    st.markdown("<div class='section-kicker'>Model Metrics</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Under the Hood</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Historical trend, segment distribution, and technical metrics.</div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1])
    with left:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Customer Base</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Segment Distribution</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Current customer segmentation breakdown.</div>", unsafe_allow_html=True)

        df_segments = pd.DataFrame(charts_data.get("segment_distribution", []))
        if not df_segments.empty:
            fig_segments = px.pie(
                df_segments, 
                names="segment", 
                values="count",
                hole=0.4,
                color_discrete_sequence=["#60a5fa", "#5eead4", "#34d399", "#f59e0b", "#fb7185", "#c084fc", "#94a3b8"]
            )
            fig_segments.update_layout(
                template="plotly_dark",
                height=360,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
            )
            st.plotly_chart(fig_segments, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Historical Context</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Total monthly revenue over time.</div>", unsafe_allow_html=True)

        df_history = pd.DataFrame(charts_data.get("revenue_trend", []))
        if not df_history.empty:
            fig_history = px.line(df_history, x="date", y="revenue", markers=True)
            fig_history.update_traces(line=dict(color="#5eead4", width=3), marker=dict(color="#60a5fa", size=7))
            fig_history.update_layout(
                template="plotly_dark",
                height=360,
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
                xaxis=dict(title="Month", gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(title="Revenue ($)", gridcolor="rgba(255,255,255,0.06)"),
                showlegend=False,
            )
            st.plotly_chart(fig_history, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    metric_cols = st.columns(4)

    with metric_cols[0]:
        metric_card("ROC-AUC", f"{model_data.get('roc_auc', 0):.3f}", "Churn classification")
    with metric_cols[1]:
        metric_card("F1 Score", f"{model_data.get('f1_score', 0):.3f}", "Churn classification")
    with metric_cols[2]:
        metric_card("Accuracy", f"{model_data.get('accuracy', 0):.3f}", "Overall accuracy")
    with metric_cols[3]:
        metric_card("Precision", f"{model_data.get('precision', 0):.3f}", "True positive rate")