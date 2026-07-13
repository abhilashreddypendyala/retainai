import streamlit as st
from utils.dashboard_utils import metric_card

def render_prediction_result(result_data: dict, action: str):
    """
    Renders the prediction result block.
    result_data should contain: churn_probability, churn_prediction, confidence_score, risk_level
    """
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("### Prediction Results")
    st.markdown("<br>", unsafe_allow_html=True)
    
    r1, r2, r3, r4 = st.columns(4)
    
    risk_level = result_data.get("risk_level", "Unknown")
    prediction = "At Risk" if result_data.get("churn_prediction") == 1 else "Safe"
    prob = result_data.get("churn_probability", 0.0)
    conf = result_data.get("confidence_score", 0.0)
    
    # Subtexts
    prob_subtext = "High Risk" if prediction == "At Risk" else "Low Risk"
    
    with r1: metric_card("Prediction", prediction, "")
    with r2: metric_card("Risk Level", risk_level, "")
    with r3: metric_card("Probability", f"{prob:.1%}", prob_subtext)
    retention_prob = 1.0 - prob
    with r4: metric_card("Retention Prob.", f"{retention_prob:.1%}", "")
    
    st.info(f"**Recommended Action:** {action}")
    
    st.markdown("</div>", unsafe_allow_html=True)
