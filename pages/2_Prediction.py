import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🔮 Prediction Dashboard")

# =========================
# LOAD FORECAST DATA
# =========================
try:
    forecast = pd.read_csv("data/forecast.csv")
except:
    st.warning("⚠️ Forecast file not found. Run prediction first.")
    st.stop()

# =========================
# BASIC CLEANING
# =========================
forecast["Date"] = pd.to_datetime(forecast["Date"], errors="coerce")
forecast = forecast.dropna().fillna(0)

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

platform_filter = st.sidebar.multiselect(
    "Platform",
    forecast["Platform"].unique(),
    default=forecast["Platform"].unique()
)

campaign_filter = st.sidebar.multiselect(
    "Campaign",
    forecast["Campaign_ID"].unique(),
    default=forecast["Campaign_ID"].unique()
)

forecast = forecast[
    (forecast["Platform"].isin(platform_filter)) &
    (forecast["Campaign_ID"].isin(campaign_filter))
]

# =========================
# KPI ROW
# =========================
total_revenue = forecast["Revenue"].sum()
total_conv = forecast["Conversions"].sum()
total_clicks = forecast["Clicks"].sum()
avg_roas = forecast["ROAS"].mean()
avg_ctr = forecast["CTR"].mean()
avg_cpa = forecast["CPA"].mean()

k1,k2,k3,k4,k5,k6 = st.columns(6)

k1.metric("Predicted Revenue", f"{total_revenue:,.0f}")
k2.metric("Predicted Conversions", f"{total_conv:,.0f}")
k3.metric("Predicted Clicks", f"{total_clicks:,.0f}")
k4.metric("Avg ROAS", f"{avg_roas:.2f}")
k5.metric("Avg CTR", f"{avg_ctr:.2%}")
k6.metric("Avg CPA", f"{avg_cpa:.2f}")

st.divider()

# =========================
# ROW 2 — PLATFORM FORECAST
# =========================
c1,c2 = st.columns(2)

plat_rev = forecast.groupby("Platform")["Revenue"].sum().reset_index()

fig1 = px.bar(
    plat_rev,
    x="Platform",
    y="Revenue",
    title="Predicted Revenue by Platform"
)
c1.plotly_chart(fig1, use_container_width=True)

daily_rev = forecast.groupby("Date")["Revenue"].sum().reset_index()

fig2 = px.line(
    daily_rev,
    x="Date",
    y="Revenue",
    title="Future Revenue Trend"
)
c2.plotly_chart(fig2, use_container_width=True)

st.divider()

# =========================
# ROW 3 — PERFORMANCE TRENDS
# =========================
r1,r2,r3 = st.columns(3)

fig3 = px.line(
    forecast.groupby("Date")["Conversions"].sum().reset_index(),
    x="Date",
    y="Conversions",
    title="Future Conversions Trend"
)
r1.plotly_chart(fig3, use_container_width=True)

fig4 = px.line(
    forecast.groupby("Date")["CTR"].mean().reset_index(),
    x="Date",
    y="CTR",
    title="CTR Trend"
)
r2.plotly_chart(fig4, use_container_width=True)

fig5 = px.line(
    forecast.groupby("Date")["ROAS"].mean().reset_index(),
    x="Date",
    y="ROAS",
    title="ROAS Trend"
)
r3.plotly_chart(fig5, use_container_width=True)

st.divider()

# =========================
# FORECAST TABLE
# =========================
st.subheader("Forecast Data")
st.dataframe(forecast.sort_values("Date"))