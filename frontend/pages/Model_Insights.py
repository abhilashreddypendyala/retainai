import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header, metric_card

inject_global_styles()

page_header(
    "MODEL INSIGHTS",
    "Model Performance",
    "Evaluate prediction quality and model reliability.",
    None
)

try:
    with st.spinner("Loading model insights..."):
        insights = api_client.get_model_insights()
except Exception as e:
    st.error("⚠️ Failed to load model insights. The backend service may be unavailable.")
    st.stop()

# ---------------------------------------------------------
# 1. Overview & Metrics
# ---------------------------------------------------------
st.markdown("<div class='section-kicker'>Architecture</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Model Overview</div>", unsafe_allow_html=True)

o_cols = st.columns(len(insights["overview"]))
for idx, (key, value) in enumerate(insights["overview"].items()):
    with o_cols[idx]:
        st.markdown(f"**{key}**<br><span style='color: #a3a3a3; font-size: 14px;'>{value}</span>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Validation</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Performance Metrics</div>", unsafe_allow_html=True)
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

m_cols = st.columns(len(insights["metrics"]))
for idx, (metric_name, metric_value) in enumerate(insights["metrics"].items()):
    with m_cols[idx]:
        metric_card(metric_name, f"{metric_value:.1%}", "")
        
st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. Charts (ROC & Confusion Matrix)
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### Receiver Operating Characteristic (ROC)")
    roc_data = insights["roc_curve"]
    roc_df = pd.DataFrame({"False Positive Rate": roc_data["fpr"], "True Positive Rate": roc_data["tpr"]})
    
    fig_roc = px.line(roc_df, x="False Positive Rate", y="True Positive Rate", color_discrete_sequence=["#FF4B4B"])
    fig_roc.add_shape(type='line', line=dict(dash='dash', color='#a3a3a3'), x0=0, x1=1, y0=0, y1=1)
    fig_roc.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#333333"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_roc, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### Confusion Matrix")
    cm = insights["confusion_matrix"]
    z = [[cm["True Negatives"], cm["False Positives"]],
         [cm["False Negatives"], cm["True Positives"]]]
    
    fig_cm = go.Figure(data=go.Heatmap(
        z=z,
        x=['Predicted Safe', 'Predicted Churn'],
        y=['Actual Safe', 'Actual Churn'],
        colorscale='Blues',
        text=[[str(cm["True Negatives"]), str(cm["False Positives"])],
              [str(cm["False Negatives"]), str(cm["True Positives"])]],
        texttemplate="%{text}",
        textfont={"size": 20}
    ))
    fig_cm.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff"),
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig_cm, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. Feature Importance
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-kicker'>Explainability</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Feature Drivers</div>", unsafe_allow_html=True)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.markdown("### Relative Feature Importance (Logistic Regression Coefficients)")

imp_dict = insights["feature_importance"]
imp_df = pd.DataFrame(list(imp_dict.items()), columns=["Feature", "Impact"])
# Sort by absolute impact
imp_df['Abs_Impact'] = imp_df['Impact'].abs()
imp_df = imp_df.sort_values(by="Abs_Impact", ascending=True)

# Color coding: Green for retention drivers (negative churn), Red for churn drivers (positive)
imp_df['Color'] = imp_df['Impact'].apply(lambda x: "#FF4B4B" if x > 0 else "#00C853")

fig_imp = px.bar(imp_df, x="Impact", y="Feature", orientation='h', color='Color', color_discrete_map="identity")
fig_imp.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ffffff"),
    xaxis=dict(title="Driver Weight (Negative = Protects, Positive = Causes Churn)", showgrid=True, gridcolor="#333333", zeroline=True, zerolinecolor="#a3a3a3"),
    yaxis=dict(title="", showgrid=False),
    margin=dict(l=0, r=0, t=30, b=0),
    showlegend=False
)
st.plotly_chart(fig_imp, use_container_width=True)

st.markdown("#### Business Interpretation")
for insight in insights["business_interpretation"]:
    st.markdown(f"- {insight}")

st.markdown("</div>", unsafe_allow_html=True)
