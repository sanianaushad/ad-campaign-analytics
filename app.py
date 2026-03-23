import streamlit as st
import pandas as pd
import os
from backend.forecast_model import run_forecast_pipeline

st.set_page_config(layout="wide")
st.title("📊 Ad Campaign Platform")

# ---------------- SESSION STATE INIT ----------------
if "data" not in st.session_state:
    st.session_state["data"] = None

if "forecast" not in st.session_state:
    st.session_state["forecast"] = None

if "accuracy" not in st.session_state:
    st.session_state["accuracy"] = None

# ---------------- FILE UPLOAD ----------------
file = st.file_uploader("Upload Campaign CSV", type=["csv"])

if file is not None:
    df = pd.read_csv(file)

    st.session_state["data"] = df

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/uploaded.csv", index=False)

    st.success("CSV uploaded successfully!")

# ---------------- MAIN LOGIC ----------------
if file is not None:
    df = st.session_state["data"]

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # ---------------- RUN MODEL ----------------
    if st.button("🚀 Run Forecast Model"):
        try:
            forecast_df, accuracy_df = run_forecast_pipeline(df)

            # Save in session
            st.session_state["forecast"] = forecast_df
            st.session_state["accuracy"] = accuracy_df

            # Save to files
            forecast_df.to_csv("data/forecast.csv", index=False)
            accuracy_df.to_csv("data/accuracy.csv", index=False)

            st.success("Model executed successfully!")

        except Exception as e:
            st.error(f"Error running model: {e}")

    # ---------------- SHOW RESULTS ----------------
    if st.session_state["forecast"] is not None:
        st.subheader("Forecast Sample")
        st.dataframe(st.session_state["forecast"].head())

    if st.session_state["accuracy"] is not None:
        st.subheader("Model Accuracy")
        st.dataframe(st.session_state["accuracy"])

else:
    st.info("Please upload a CSV file to continue.")

st.write("➡️ Use sidebar to open Analyzer or Prediction pages.")