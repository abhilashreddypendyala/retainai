import os

import numpy as np
import pandas as pd
import streamlit as st
from pandas.io.formats.style import Styler


def inject_global_styles() -> None:
    st.logo("frontend/assets/logo.png")
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #07111f;
            --bg-2: #0b1729;
            --panel: rgba(10, 18, 33, 0.80);
            --panel-border: rgba(148, 163, 184, 0.18);
            --text: #e5eefb;
            --muted: #9fb0c8;
            --accent: #5eead4;
            --accent-2: #60a5fa;
            --danger: #fb7185;
            --warning: #f59e0b;
            --success: #34d399;
        }

        html, body, [class*="css"] {
            font-family: Inter, "Segoe UI", sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(96, 165, 250, 0.24), transparent 28%),
                radial-gradient(circle at top right, rgba(94, 234, 212, 0.16), transparent 24%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-1) 100%);
        }

        html, body {
            min-height: 100%;
            background-color: var(--bg-1);
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        [data-testid="stSidebar"] {
            background-color: transparent !important;
        }
        
        [data-testid="stLogo"] {
            height: 3.5rem !important;
        }

        [data-testid="stAppViewContainer"] > .main {
            background:
                radial-gradient(circle at top left, rgba(96, 165, 250, 0.24), transparent 28%),
                radial-gradient(circle at top right, rgba(94, 234, 212, 0.16), transparent 24%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 45%, var(--bg-1) 100%) !important;
        }

        [data-testid="stAppViewContainer"] {
            color: var(--text);
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div,
        label,
        p,
        li,
        span,
        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            color: var(--text);
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}

        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }

        .hero-shell {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.94), rgba(30, 41, 59, 0.84));
            border: 1px solid var(--panel-border);
            border-radius: 28px;
            padding: 26px 28px;
            box-shadow: 0 24px 60px rgba(2, 6, 23, 0.45);
            margin-bottom: 18px;
        }

        .hero-shell::after {
            content: "";
            position: absolute;
            inset: auto -120px -140px auto;
            width: 320px;
            height: 320px;
            background: radial-gradient(circle, rgba(94, 234, 212, 0.22), transparent 68%);
            pointer-events: none;
        }

        .eyebrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 12px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--accent);
            border: 1px solid rgba(94, 234, 212, 0.18);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hero-title {
            margin: 14px 0 8px;
            font-size: 38px;
            line-height: 1.05;
            letter-spacing: -0.04em;
            color: var(--text);
            font-weight: 800;
        }

        .hero-copy {
            max-width: 940px;
            color: var(--muted);
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 18px;
        }

        .hero-badges, .page-links {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .hero-badge, .page-link-card {
            padding: 10px 14px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.06);
            color: var(--text);
            border: 1px solid rgba(255, 255, 255, 0.08);
            font-size: 12px;
            font-weight: 600;
        }

        .page-link-card {
            display: block;
            text-decoration: none;
            min-width: 180px;
        }

        .section-kicker {
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 11px;
            font-weight: 700;
            margin: 4px 0 6px;
        }

        .section-title {
            color: var(--text);
            font-size: 24px;
            font-weight: 750;
            letter-spacing: -0.03em;
            margin: 0 0 8px;
        }

        .section-subtitle {
            color: var(--muted);
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 10px;
        }

        .kpi-card {
            background: linear-gradient(180deg, rgba(17, 24, 39, 0.94), rgba(15, 23, 42, 0.84));
            border-radius: 22px;
            padding: 22px 22px 20px;
            box-shadow: 0 18px 44px rgba(2, 6, 23, 0.28);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            height: 100%;
            border: 1px solid var(--panel-border);
            position: relative;
            overflow: hidden;
        }

        .kpi-card::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(135deg, rgba(255,255,255,0.06), transparent 55%);
            pointer-events: none;
        }

        .kpi-accent {
            height: 4px;
            border-radius: 999px;
            margin-bottom: 18px;
            background: linear-gradient(90deg, var(--accent-2), var(--accent));
        }

        .kpi-title {
            color: var(--muted);
            font-size: 14px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 36px;
            font-weight: 650;
            color: var(--text);
            line-height: 1.2;
        }

        .kpi-subtext {
            font-size: 13px;
            font-weight: 500;
            margin-top: 8px;
        }

        .text-green { color: var(--success); }
        .text-red { color: var(--danger); }
        .text-gray { color: var(--muted); }

        .chart-container, .content-panel {
            background: var(--panel);
            border-radius: 24px;
            padding: 20px 20px 12px;
            box-shadow: 0 18px 50px rgba(2, 6, 23, 0.28);
            margin-top: 18px;
            border: 1px solid var(--panel-border);
            backdrop-filter: blur(18px);
        }

        .content-panel {
            padding: 18px 18px 16px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(8, 15, 28, 0.95), rgba(7, 17, 31, 0.9)) !important;
            backdrop-filter: saturate(180%) blur(20px);
            border-right: 1px solid rgba(148, 163, 184, 0.12);
        }

        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }

        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] .stMarkdown span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {
            color: var(--text) !important;
        }

        .stDataFrame {
            background: transparent;
        }

        [data-testid="stDataFrame"] {
            background: rgba(8, 15, 28, 0.96) !important;
            border: 1px solid rgba(148, 163, 184, 0.20) !important;
            border-radius: 18px;
            overflow: hidden;
        }

        [data-testid="stDataFrame"] div,
        [data-testid="stDataFrame"] span,
        [data-testid="stDataFrame"] td,
        [data-testid="stDataFrame"] th {
            color: #f8fbff !important;
        }

        [data-testid="stDataFrame"] * {
            color: #f8fbff !important;
            fill: #f8fbff !important;
            stroke: #f8fbff !important;
        }

        [data-testid="stDataFrame"] thead th {
            background: rgba(15, 23, 42, 0.98) !important;
            color: #f8fbff !important;
        }

        [data-testid="stDataFrame"] tbody tr:nth-child(even) {
            background: rgba(15, 23, 42, 0.72) !important;
        }

        [data-testid="stDataFrame"] tbody tr:nth-child(odd) {
            background: rgba(10, 18, 33, 0.72) !important;
        }

        [data-testid="stDataFrame"] button,
        [data-testid="stDataFrame"] [role="button"],
        [data-testid="stDataFrame"] a {
            color: #f8fbff !important;
            background: transparent !important;
        }

        .stButton button, .stDownloadButton button {
            color: #f8fbff !important;
            background: rgba(96, 165, 250, 0.16) !important;
            border: 1px solid rgba(148, 163, 184, 0.22) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.2s ease !important;
        }

        .stButton button:hover, .stDownloadButton button:hover {
            background: rgba(94, 234, 212, 0.22) !important;
            border-color: rgba(94, 234, 212, 0.45) !important;
            transform: translateY(-1px);
        }

        [data-testid="stDataFrame"] button svg,
        [data-testid="stDataFrame"] [role="button"] svg,
        [data-testid="stDataFrame"] a svg {
            fill: #f8fbff !important;
            stroke: #f8fbff !important;
        }

        .stSelectbox,
        .stTextInput,
        .stNumberInput,
        .stDateInput,
        .stMultiSelect {
            color: var(--text);
        }

        [data-baseweb="select"] > div,
        [data-baseweb="input"] {
            background: rgba(255, 255, 255, 0.04) !important;
            color: var(--text) !important;
            border-color: rgba(148, 163, 184, 0.18) !important;
        }

        .stSlider [data-baseweb="slider"] {
            padding-top: 0.4rem;
            padding-bottom: 0.4rem;
        }
        
        /* Form borders and Alert styling */
        [data-testid="stForm"] {
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 12px !important;
        }
        
        .stAlert {
            background: rgba(15, 23, 42, 0.75) !important;
            border: 1px solid rgba(148, 163, 184, 0.18) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
            backdrop-filter: blur(12px);
        }
        [data-testid="stAlert"] svg {
            fill: var(--text) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(app_dir))
    data_path = os.path.join(root_dir, "data", "processed", "master_customer_dataset.parquet")
    df = pd.read_parquet(data_path)
    df["All_Customers"] = "Total Customer Base"
    return df


@st.cache_data
def load_transactions() -> pd.DataFrame:
    app_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(app_dir))
    data_path = os.path.join(root_dir, "data", "processed", "cleaned_online_retail.parquet")
    return pd.read_parquet(data_path)


def build_segmented_frame(df_master: pd.DataFrame, sim_risk: float, sim_clv: int) -> pd.DataFrame:
    df_sim = df_master.copy()
    conditions = [
        (df_sim["Churn_Probability"] >= sim_risk) & (df_sim["predicted_90d_clv"] >= sim_clv),
        (df_sim["Churn_Probability"] < sim_risk) & (df_sim["predicted_90d_clv"] >= sim_clv),
        (df_sim["Churn_Probability"] >= sim_risk) & (df_sim["predicted_90d_clv"] < sim_clv),
        (df_sim["Churn_Probability"] < sim_risk) & (df_sim["predicted_90d_clv"] < sim_clv),
    ]
    choices = ["High-Risk Whales", "Loyal Champions", "At-Risk Regulars", "Safe Regulars"]
    df_sim["Segment"] = np.select(conditions, choices, default="Unknown")
    return df_sim


def get_recommendation(row: pd.Series) -> str:
    if row["Recency"] > 90:
        return "Win-Back Campaign"
    if row["Frequency"] > 15:
        return "VIP Concierge"
    return "Exclusive Loyalty"


def compute_churn_driver_scores(df_master: pd.DataFrame) -> pd.DataFrame:
    feature_map = {
        "Recency": "Days Since Last Purchase",
        "Frequency": "Purchase Frequency",
        "Monetary": "Monetary Value",
        "Tenure": "Customer Tenure",
        "Velocity": "Purchase Velocity",
        "AOV": "Average Order Value",
        "ItemDiversity": "Item Diversity",
    }

    scores = []
    churn = pd.to_numeric(df_master["Churn"], errors="coerce")
    for column, label in feature_map.items():
        series = pd.to_numeric(df_master[column], errors="coerce")
        correlation = series.corr(churn)
        score = 0.0 if pd.isna(correlation) else abs(float(correlation))
        scores.append((label, score))

    result = pd.DataFrame(scores, columns=["Driver", "Score"]).sort_values("Score", ascending=False).head(6)
    return result


def compute_monthly_aov_trend(df_transactions: pd.DataFrame) -> pd.DataFrame:
    monthly = df_transactions.copy()
    monthly["Month"] = pd.to_datetime(monthly["Date"]).dt.to_period("M").dt.to_timestamp()
    grouped = monthly.groupby("Month", as_index=False).agg(
        Revenue=("TotalAmount", "sum"),
        Orders=("InvoiceNo", "nunique"),
    )
    grouped["AOV"] = grouped["Revenue"] / grouped["Orders"]
    return grouped[["Month", "AOV"]]


def compute_churn_metrics(df_master: pd.DataFrame) -> dict:
    actual = pd.to_numeric(df_master["Churn"], errors="coerce").fillna(0).astype(int)
    probability = pd.to_numeric(df_master["Churn_Probability"], errors="coerce").fillna(0.0)
    predicted = (probability >= 0.5).astype(int)

    tp = int(((predicted == 1) & (actual == 1)).sum())
    tn = int(((predicted == 0) & (actual == 0)).sum())
    fp = int(((predicted == 1) & (actual == 0)).sum())
    fn = int(((predicted == 0) & (actual == 1)).sum())

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    ranks = probability.rank(method="average")
    positive_ranks = ranks[actual == 1].sum()
    n_pos = int((actual == 1).sum())
    n_neg = int((actual == 0).sum())
    roc_auc = ((positive_ranks - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)) if n_pos and n_neg else 0.0

    clv_actual = pd.to_numeric(df_master["Monetary"], errors="coerce").fillna(0.0)
    clv_pred = pd.to_numeric(df_master["predicted_90d_clv"], errors="coerce").fillna(0.0)
    mae = float((clv_pred - clv_actual).abs().mean())
    rmse = float(np.sqrt(((clv_pred - clv_actual) ** 2).mean()))

    return {
        "confusion_matrix": [[tn, fp], [fn, tp]],
        "roc_auc": float(roc_auc),
        "f1": float(f1),
        "mae": mae,
        "rmse": rmse,
    }


def page_header(eyebrow: str, title: str, subtitle: str, badges: list[str] | None = None) -> None:
    badge_html = ""
    if badges:
        badge_html = "".join(f'<span class="hero-badge">{badge}</span>' for badge in badges)

    st.markdown(
        f"""
        <div class="hero-shell">
            <div class="eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-copy">{subtitle}</div>
            <div class="hero-badges">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(title: str, value: str, subtext: str, accent: str = "linear-gradient(90deg, var(--accent-2), var(--accent))") -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-accent" style="background: {accent};"></div>
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def dark_table(df: pd.DataFrame) -> Styler:
    return (
        df.style.set_table_styles(
            [
                {"selector": "th", "props": [("background-color", "#0f172a"), ("color", "#f8fbff"), ("border", "1px solid rgba(148, 163, 184, 0.18)")]},
                {"selector": "td", "props": [("background-color", "#0b1628"), ("color", "#f8fbff"), ("border", "1px solid rgba(148, 163, 184, 0.12)")]},
                {"selector": "table", "props": [("border-collapse", "separate"), ("border-spacing", "0")]},
            ]
        )
        .set_properties(**{"color": "#f8fbff", "background-color": "#0b1628"})
    )