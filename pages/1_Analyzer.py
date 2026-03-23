import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")
st.title("📊 Performance Analyzer")

# ---------------- LOAD DATA ----------------
if "data" in st.session_state and st.session_state["data"] is not None:
    df = st.session_state["data"]
elif os.path.exists("data/uploaded.csv"):
    df = pd.read_csv("data/uploaded.csv")
    st.session_state["data"] = df
else:
    st.warning("Please upload data from App page first.")
    st.stop()

# ---------------- CLEAN ----------------
df.columns = df.columns.str.strip()

# ---------------- METRICS ----------------
total_spend = df["Spend"].sum()
total_clicks = df["Clicks"].sum()
total_conversions = df["Conversions"].sum()
total_revenue = df["Revenue"].sum()

roas = total_revenue / total_spend if total_spend != 0 else 0
ctr = total_clicks / df["Impressions"].sum() if "Impressions" in df else 0
cpa = total_spend / total_conversions if total_conversions != 0 else 0

# ---------------- DISPLAY ----------------
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric("Total Spend", f"{total_spend:,.0f}")
col2.metric("Total Conversions", f"{total_conversions:,.0f}")
col3.metric("Total Clicks", f"{total_clicks:,.0f}")
col4.metric("Total Revenue", f"{total_revenue:,.0f}")
col5.metric("ROAS", f"{roas:.2f}")
col6.metric("CTR", f"{ctr:.2%}")
col7.metric("CPA", f"{cpa:.2f}")

st.divider()

# ---------------- GRAPHS (SIDE BY SIDE) ----------------
c1, c2 = st.columns(2)

platform_data = df.groupby("Platform")[["Spend", "Revenue"]].sum().reset_index()

fig1 = px.bar(platform_data, x="Platform", y="Revenue", title="Revenue by Platform")
c1.plotly_chart(fig1, use_container_width=True)

daily = df.groupby("Date")[["Spend", "Revenue"]].sum().reset_index()

fig2 = px.line(daily, x="Date", y=["Spend", "Revenue"], title="Spend vs Revenue")
c2.plotly_chart(fig2, use_container_width=True)