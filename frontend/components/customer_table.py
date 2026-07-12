import pandas as pd
import streamlit as st
from utils.dashboard_utils import dark_table

def render_customer_table(customers_data: list):
    if not customers_data:
        st.info("No customers found matching the given criteria.")
        return

    df = pd.DataFrame(customers_data)
    
    # Map the JSON keys to friendly display names
    display_df = df[["customer_id", "country", "segment", "clv", "churn_probability", "churn_prediction"]].copy()
    display_df.columns = ["Customer ID", "Country", "Segment", "CLV", "Churn Probability", "Churn Prediction"]
    
    # Format currency and percentages
    display_df["CLV"] = display_df["CLV"].apply(lambda x: f"${float(x):,.2f}" if pd.notnull(x) else "$0.00")
    display_df["Churn Probability"] = display_df["Churn Probability"].apply(lambda x: f"{float(x):.1%}" if pd.notnull(x) else "0.0%")
    display_df["Churn Prediction"] = display_df["Churn Prediction"].apply(lambda x: "High Risk" if x == 1 else "Low Risk")

    # Apply the existing global dark table styles
    styled_df = dark_table(display_df).set_properties(subset=display_df.columns, **{"text-align": "left"})
    
    st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
    )
