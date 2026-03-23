import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.markdown("""
<style>
[data-testid="metric-container"] {
    background-color: #f2f2f2;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
st.title("📊 Performance Analyzer")

file = st.file_uploader("Upload CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna().fillna(0)

    # ========= KPI ROW =========
    spend = df["Spend"].sum()
    conv = df["Conversions"].sum()
    clicks = df["Clicks"].sum()
    revenue = df["Revenue"].sum()
    impr = df["Impressions"].sum()

    roas = revenue/spend if spend else 0
    ctr = clicks/impr if impr else 0
    cpa = spend/conv if conv else 0

    k1,k2,k3,k4,k5,k6,k7 = st.columns(7)

    k1.metric("Total Spend", f"{spend:,.0f}")
    k2.metric("Total Conversions", f"{conv:,.0f}")
    k3.metric("Total Clicks", f"{clicks:,.0f}")
    k4.metric("Total Revenue", f"{revenue:,.0f}")
    k5.metric("ROAS", f"{roas:.2f}")
    k6.metric("CTR", f"{ctr:.2%}")
    k7.metric("CPA", f"{cpa:.2f}")

    st.divider()

    # ========= ROW 2 =========

    # Platform Filter
    platforms = st.multiselect("Platform", df["Platform"].unique(),
                               default=df["Platform"].unique())
    df = df[df["Platform"].isin(platforms)]

    c2,c3,c4 = st.columns([2,2,2])

    # Revenue by Platform
    plat = df.groupby("Platform")["Revenue"].sum().reset_index()
    fig1 = px.bar(plat, x="Platform", y="Revenue", title="Revenue by Platform")
    c2.plotly_chart(fig1, use_container_width=True)

    # Platform Table
    plat_tbl = df.groupby("Platform").agg(
        CTR=("Clicks","sum"),
        CPA=("Spend","sum"),
        Revenue=("Revenue","sum"),
        Clicks=("Clicks","sum")
    )
    c3.dataframe(plat_tbl)

    # Spend vs Revenue
    daily = df.groupby("Date")[["Spend","Revenue"]].sum().reset_index()
    fig2 = px.line(daily, x="Date", y=["Spend","Revenue"],
                   title="Spend vs Revenue")
    c4.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ========= ROW 3 =========

    r1,r2,r3 = st.columns(3)

    # Campaign Revenue
    camp = df.groupby("Campaign")["Revenue"].sum().nlargest(10).reset_index()
    fig3 = px.bar(camp, x="Campaign", y="Revenue",
                  title="Total Revenue by Campaign")
    r1.plotly_chart(fig3, use_container_width=True)

    # Revenue Trend
    monthly = df.groupby(df["Date"].dt.month)["Revenue"].sum().reset_index()
    fig4 = px.line(monthly, x="Date", y="Revenue",
                   title="Total Revenue by Month")
    r2.plotly_chart(fig4, use_container_width=True)

    # Conversion Trend
    conv_month = df.groupby(df["Date"].dt.month)["Conversions"].sum().reset_index()
    fig5 = px.line(conv_month, x="Date", y="Conversions",
                   title="Total Conversions by Month")
    r3.plotly_chart(fig5, use_container_width=True)
