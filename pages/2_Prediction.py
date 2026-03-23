import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📈 Prediction Dashboard")

# ---------------- LOAD FORECAST ----------------
if "forecast" in st.session_state and st.session_state["forecast"] is not None:
    forecast_df = st.session_state["forecast"]
elif os.path.exists("data/forecast.csv"):
    forecast_df = pd.read_csv("data/forecast.csv")
    st.session_state["forecast"] = forecast_df
else:
    st.warning("Run the model from App page first.")
    st.stop()

# ---------------- LOAD ACCURACY ----------------
if "accuracy" in st.session_state and st.session_state["accuracy"] is not None:
    accuracy_df = st.session_state["accuracy"]
elif os.path.exists("data/accuracy.csv"):
    accuracy_df = pd.read_csv("data/accuracy.csv")
    st.session_state["accuracy"] = accuracy_df
else:
    accuracy_df = None

# ---------------- CLEAN ----------------
forecast_df["Date"] = pd.to_datetime(forecast_df["Date"])

# ---------------- METRICS ----------------
total_revenue = forecast_df["Revenue"].sum()
total_clicks = forecast_df["Clicks"].sum()
avg_roas = forecast_df["ROAS"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"{total_revenue:,.0f}")
col2.metric("Total Clicks", f"{total_clicks:,.0f}")
col3.metric("Avg ROAS", f"{avg_roas:.2f}")

st.divider()

# ---------------- ACCURACY ----------------
if accuracy_df is not None:
    st.subheader("Model Accuracy")
    st.dataframe(accuracy_df)

# ---------------- GRAPHS ----------------
st.subheader("Trends")

c1, c2, c3 = st.columns(3)

fig1 = px.line(
    forecast_df,
    x="Date",
    y="Revenue",
    color="Platform",
    title="Revenue Trend"
)
c1.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    forecast_df,
    x="Date",
    y="Clicks",
    color="Platform",
    title="Clicks Trend"
)
c2.plotly_chart(fig2, use_container_width=True)

fig3 = px.line(
    forecast_df,
    x="Date",
    y="ROAS",
    color="Platform",
    title="ROAS Trend"
)
c3.plotly_chart(fig3, use_container_width=True)

st.divider()

# ---------------- TABLE ----------------
st.subheader("Forecast Data")
st.dataframe(forecast_df.sort_values("Date"))