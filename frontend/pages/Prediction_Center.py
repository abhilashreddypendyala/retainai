import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import api_client
from utils.dashboard_utils import inject_global_styles, page_header, dark_table
from components.prediction_result import render_prediction_result

st.set_page_config(page_title="RETAIN-AI | Prediction Center", page_icon="🔮", layout="wide")
inject_global_styles()

page_header(
    "PREDICTION CENTER",
    "Live Churn Predictions",
    "Run real-time predictions using the trained Logistic Regression model.",
    ["Machine Learning", "Inference", "Interactive"]
)

# Initialize recent predictions list in session state
if "recent_predictions" not in st.session_state:
    st.session_state.recent_predictions = []

st.markdown("<div class='section-kicker'>Inference</div>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Prediction Mode</div>", unsafe_allow_html=True)

mode = st.radio("Select Input Method", ["Existing Customer", "New Customer"], horizontal=True)

prediction_response = None
recommended_action = ""
customer_identifier = ""

if mode == "Existing Customer":
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Search Existing Customer")
    
    with st.form("existing_customer_form"):
        search_col, _ = st.columns([1, 1])
        with search_col:
            search_query = st.text_input("Customer ID (or part of it)", placeholder="e.g. 12345")
        search_btn = st.form_submit_button("Search")
        
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
        with st.form("predict_existing_form"):
            selected_id = st.selectbox("Select Customer to Predict", options=customer_options)
            predict_btn = st.form_submit_button("Generate Prediction")
            
        if predict_btn:
            try:
                with st.spinner("Fetching features and running model..."):
                    # 1. Fetch 360 profile to get all features
                    c_data = api_client.get_customer_360(selected_id)["customer"]
                    
                    # 2. Build feature dictionary
                    features = {
                        "Recency": float(c_data["recency"]),
                        "Frequency": float(c_data["frequency"]),
                        "Monetary": float(c_data["monetary"]),
                        "Tenure": float(c_data.get("customer_lifespan", 0)),
                        "Velocity": float(c_data.get("purchase_frequency", 0)),
                        "AOV": float(c_data.get("avg_order_value", 0)),
                        "ItemDiversity": float(c_data.get("item_diversity", 0))
                    }
                    
                    # 3. Call prediction API
                    prediction_response = api_client.predict_customer(features)
                    customer_identifier = selected_id
                    
                    # Compute recommendation
                    if prediction_response["churn_prediction"] == 1:
                        recommended_action = "Win-Back Campaign (VIP)" if features["Monetary"] > 1000 else "Discount Offer (15%)"
                    else:
                        recommended_action = "Loyalty Program / Upsell" if features["Monetary"] > 1000 else "Standard Marketing Drip"
                        
            except Exception as e:
                st.error("⚠️ Failed to generate prediction. The backend service may be unavailable.")
                
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.markdown("#### Enter Manual Features")
    
    with st.form("manual_prediction_form"):
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
            
        predict_btn = st.form_submit_button("Generate Prediction")
        
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
                
                # Compute recommendation
                if prediction_response["churn_prediction"] == 1:
                    recommended_action = "Win-Back Campaign (VIP)" if features["Monetary"] > 1000 else "Discount Offer (15%)"
                else:
                    recommended_action = "Loyalty Program / Upsell" if features["Monetary"] > 1000 else "Standard Marketing Drip"
                    
        except Exception as e:
            st.error("⚠️ Failed to generate prediction. The backend service may be unavailable.")
            
    st.markdown("</div>", unsafe_allow_html=True)


if prediction_response:
    render_prediction_result(prediction_response, recommended_action)
    
    # Store in history
    hist_record = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Customer": customer_identifier,
        "Risk Level": prediction_response["risk_level"],
        "Probability": f"{prediction_response['churn_probability']:.1%}"
    }
    st.session_state.recent_predictions.insert(0, hist_record)
    st.session_state.recent_predictions = st.session_state.recent_predictions[:10] # Keep last 10

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
