import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.dashboard_utils import (
    build_segmented_frame,
    compute_churn_driver_scores,
    compute_churn_metrics,
    compute_monthly_aov_trend,
    dark_table,
    get_recommendation,
    inject_global_styles,
    load_data,
    load_transactions,
    metric_card,
    page_header,
)


st.set_page_config(page_title="RETAIN-AI | Overview", page_icon="💠", layout="wide", initial_sidebar_state="expanded")
inject_global_styles()

df_master = load_data()

st.sidebar.markdown("### Scenario Controls")
sim_risk = st.sidebar.slider("Churn Risk Threshold (%)", min_value=10, max_value=90, value=50, step=5) / 100.0
default_clv = int(df_master["predicted_90d_clv"].quantile(0.75))
max_clv = int(df_master["predicted_90d_clv"].max())
sim_clv = st.sidebar.slider("High-Value Cutoff ($)", min_value=50, max_value=max_clv, value=default_clv, step=50)

df_sim = build_segmented_frame(df_master, sim_risk, sim_clv)
total_rev = df_sim["predicted_90d_clv"].sum()
rev_at_risk = df_sim[df_sim["Churn_Probability"] >= sim_risk]["predicted_90d_clv"].sum()
safe_rev = total_rev - rev_at_risk
whale_count = len(df_sim[df_sim["Segment"] == "High-Risk Whales"])

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

    vips = df_sim[df_sim["Segment"] == "High-Risk Whales"].sort_values("predicted_90d_clv", ascending=False)
    if len(vips) == 0:
        st.info("No High-Risk Whales detected under the current scenario.")
    else:
        vip_display = vips[["CustomerID", "predicted_90d_clv", "Churn_Probability", "Recency", "Frequency"]].copy()
        vip_display["Recommended Action"] = vips.apply(get_recommendation, axis=1)
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
        st.download_button(
            "Download VIP interventions CSV",
            data=vip_csv,
            file_name="vip_interventions.csv",
            mime="text/csv",
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
    st.markdown("<div class='section-subtitle'>Feature drivers, historical trend, and technical metrics.</div>", unsafe_allow_html=True)

    driver_df = compute_churn_driver_scores(df_master)
    history_df = compute_monthly_aov_trend(load_transactions())
    metrics = compute_churn_metrics(df_master)

    left, right = st.columns([1, 1])
    with left:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Explainability</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Top Churn Drivers</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Higher bars indicate stronger association with churn.</div>", unsafe_allow_html=True)

        fig_drivers = go.Figure(
            go.Bar(
                x=driver_df["Score"],
                y=driver_df["Driver"],
                orientation="h",
                marker=dict(color=["#60a5fa", "#5eead4", "#34d399", "#f59e0b", "#fb7185", "#c084fc", "#94a3b8"][: len(driver_df)]),
                hovertemplate="%{y}: %{x:.3f}<extra></extra>",
            )
        )
        fig_drivers.update_layout(
            template="plotly_dark",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
            xaxis=dict(title="Relative score", gridcolor="rgba(255,255,255,0.08)"),
            yaxis=dict(title="", categoryorder="total ascending"),
        )
        st.plotly_chart(fig_drivers, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Historical Context</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-title' style='font-size: 18px; margin-bottom: 6px;'>Monthly average order value</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-subtitle'>Baseline trend before the 90-day forecast window.</div>", unsafe_allow_html=True)

        fig_history = px.line(history_df, x="Month", y="AOV", markers=True)
        fig_history.update_traces(line=dict(color="#5eead4", width=3), marker=dict(color="#60a5fa", size=7))
        fig_history.update_layout(
            template="plotly_dark",
            height=360,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
            xaxis=dict(title="Month", gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(title="AOV ($)", gridcolor="rgba(255,255,255,0.06)"),
            showlegend=False,
        )
        st.plotly_chart(fig_history, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    metric_cols = st.columns(5)

    cm = metrics["confusion_matrix"]
    cm_fig = go.Figure(
        data=go.Heatmap(
            z=cm,
            x=["Predicted 0", "Predicted 1"],
            y=["Actual 0", "Actual 1"],
            colorscale=[[0, "#0f172a"], [0.5, "#60a5fa"], [1, "#5eead4"]],
            showscale=False,
            text=cm,
            texttemplate="%{text}",
            textfont={"color": "#f8fbff", "size": 16},
        )
    )
    cm_fig.update_layout(
        template="plotly_dark",
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#e5eefb"},
    )

    with metric_cols[0]:
        metric_card("ROC-AUC", f"{metrics['roc_auc']:.3f}", "Churn classification")
    with metric_cols[1]:
        metric_card("F1 Score", f"{metrics['f1']:.3f}", "Churn classification")
    with metric_cols[2]:
        metric_card("MAE", f"${metrics['mae']:,.2f}", "CLV proxy")
    with metric_cols[3]:
        metric_card("RMSE", f"${metrics['rmse']:,.2f}", "CLV proxy")
    with metric_cols[4]:
        st.markdown("<div class='content-panel' style='padding-top: 12px;'>", unsafe_allow_html=True)
        st.markdown("<div class='section-kicker'>Confusion Matrix</div>", unsafe_allow_html=True)
        st.plotly_chart(cm_fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)