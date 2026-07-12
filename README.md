# 💠 RETAIN-AI: CLV-Driven Churn Prediction & Retention Optimization

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Machine Learning](https://img.shields.io/badge/Machine_Learning-XGBoost_%7C_BGNBD-orange.svg)
![Status](https://img.shields.io/badge/Status-Production_Ready-success.svg)

## 📌 Executive Summary
**RETAIN-AI** is an advanced decision-support system designed to solve a critical flaw in traditional e-commerce retention strategies. While standard machine learning models simply predict *if* a customer will churn, they fail to quantify *how much* that churn will cost the business. 

This project bridges the gap between Data Science and Business Intelligence by intersecting **Predictive Churn Modeling** (Logistic Regression / XGBoost) with **Probabilistic Customer Lifetime Value Projections** (BG/NBD & Gamma-Gamma). The result is an actionable, prioritized "VIP Intervention" framework that allows account managers to focus their budget strictly on high-risk, high-value accounts.

## 🚀 Core Features
* **Granular Risk Assessment:** Calculates exact churn probabilities (0-100%) rather than binary outputs.
* **Financial Forecasting:** Projects the 90-day monetary value of every individual customer.
* **Strategic Segmentation Matrix:** Dynamically classifies users into actionable quadrants (e.g., *High-Risk Whales*, *Loyal Champions*).
* **VIP Command Center:** A Streamlit-powered interactive dashboard that generates real-time, personalized intervention strategies to prevent critical revenue leakage.

## 🧠 System Architecture
The project follows a modular, scalable pipeline architecture:

1. **Data Engineering (`notebooks/01-03`):** Cleanses the raw e-commerce dataset, engineers behavioral RFM (Recency, Frequency, Monetary) features, and handles temporal train/test splitting.
2. **Machine Learning Engine (`notebooks/04`):** Trains and tunes the classification models, utilizing SMOTE for class imbalance and outputting a serialized `lr_champion.pkl` inference engine.
3. **Probabilistic Modeling (`notebooks/05`):** Fits the `lifetimes` library models to transaction logs to calculate expected future purchases and average order value.
4. **Frontend Dashboard (`app/app.py`):** An interactive SaaS-style web application built with Streamlit and Plotly for executive-level data consumption.

## 📂 Repository Structure
```text
clv-churn-retail/
├── app/                           # Frontend Web Application
│   └── app.py                     # Streamlit Command Center
├── data/                          # Data Storage (Git-ignored)
│   ├── raw/                       # Original E-Commerce Dataset
│   └── processed/                 # Engineered Parquet files
├── models/                        # Serialized ML Artifacts
│   └── churn/                     
│       ├── lr_champion.pkl        # Champion Classification Model
│       └── feature_scaler.pkl     # StandardScaler for inference
├── notebooks/                     # Iterative Development Environment
│   ├── 01_data_cleaning.ipynb
│   ├── 02_eda_and_rfm.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_churn_modeling.ipynb
│   ├── 05_clv_modeling.ipynb
│   └── 06_customer_segmentation.ipynb
├── requirements.txt               # Environment Dependencies
└── README.md                      # System Documentation