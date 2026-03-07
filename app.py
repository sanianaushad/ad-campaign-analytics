import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("📊 Ad Campaign Platform")

file = st.file_uploader("Upload Campaign CSV", type=["csv"])

if file:
    df = pd.read_csv(file)

    # Save for other pages
    st.session_state["data"] = df
    df.to_csv("data/uploaded.csv", index=False)

    st.success("CSV Uploaded Successfully!")

st.write("Use sidebar to open Analyzer or Prediction pages.")