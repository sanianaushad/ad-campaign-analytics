import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


def run_forecast_pipeline(df):

    # =========================
    # CLEAN DATA
    # =========================
    df.columns = df.columns.str.strip()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    numeric_cols = ["Clicks", "Spend", "Conversions", "Revenue"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Date"])
    df = df.fillna(0)

    if "Spend" in df.columns:
        df = df[df["Spend"] > 0]

    # =========================
    # SORT
    # =========================
    df = df.sort_values("Date")

    # =========================
    # FEATURE ENGINEERING
    # =========================
    df["Day"] = df["Date"].dt.day
    df["Month"] = df["Date"].dt.month
    df["Weekday"] = df["Date"].dt.weekday

    df["Clicks_lag1"] = df["Clicks"].shift(1)
    df["Clicks_lag2"] = df["Clicks"].shift(2)

    df = df.fillna(0)

    # =========================
    # MODEL PER PLATFORM
    # =========================
    FORECAST_DAYS = 30
    forecast_list = []
    accuracy_list = []

    for platform in df["Platform"].unique():

        temp = df[df["Platform"] == platform].copy()

        if len(temp) < 20:
            continue

        features = [
            "Spend", "Day", "Month", "Weekday",
            "Clicks_lag1", "Clicks_lag2"
        ]

        X = temp[features]
        y = temp["Clicks"]

        split = int(len(temp) * 0.8)

        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]

        model = RandomForestRegressor(
            n_estimators=150,
            max_depth=8,
            random_state=42
        )

        model.fit(X_train, y_train)

        # =========================
        # ACCURACY
        # =========================
        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1))) * 100

        accuracy_list.append({
            "Platform": platform,
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "MAPE (%)": round(mape, 2)
        })

        # =========================
        # FUTURE FORECAST
        # =========================
        last_date = temp["Date"].max()

        last_clicks = temp["Clicks"].iloc[-1]
        last_clicks_2 = temp["Clicks"].iloc[-2]

        future_rows = []

        for i in range(1, FORECAST_DAYS + 1):

            future_date = last_date + pd.Timedelta(days=i)

            row = {
                "Spend": temp["Spend"].mean(),
                "Day": future_date.day,
                "Month": future_date.month,
                "Weekday": future_date.weekday(),
                "Clicks_lag1": last_clicks,
                "Clicks_lag2": last_clicks_2
            }

            pred_clicks = model.predict(pd.DataFrame([row]))[0]

            last_clicks_2 = last_clicks
            last_clicks = pred_clicks

            future_rows.append({
                "Date": future_date,
                "Platform": platform,
                "Clicks": pred_clicks
            })

        future_df = pd.DataFrame(future_rows)
        forecast_list.append(future_df)

    # =========================
    # COMBINE FORECASTS
    # =========================
    forecast_df = pd.concat(forecast_list, ignore_index=True)

    # =========================
    # BUSINESS METRICS 
    # =========================
    conv_rate = df["Conversions"].sum() / df["Clicks"].sum()
    rev_per_conv = df["Revenue"].sum() / df["Conversions"].sum()
    avg_spend = df["Spend"].mean()

    # NO RANDOMNESS
    forecast_df["Conversion_Rate"] = conv_rate
    forecast_df["Revenue_per_Conversion"] = rev_per_conv
    forecast_df["Spend"] = avg_spend

    forecast_df["Conversions"] = forecast_df["Clicks"] * forecast_df["Conversion_Rate"]
    forecast_df["Revenue"] = forecast_df["Conversions"] * forecast_df["Revenue_per_Conversion"]

    forecast_df["ROAS"] = forecast_df["Revenue"] / forecast_df["Spend"]
    forecast_df["CPA"] = forecast_df["Spend"] / forecast_df["Conversions"]

    forecast_df = forecast_df.replace([np.inf, -np.inf], 0).fillna(0).round(2)

    forecast_df = forecast_df[[
        "Date", "Platform", "Clicks", "Conversions",
        "Revenue", "Spend", "ROAS", "CPA"
    ]]

    accuracy_df = pd.DataFrame(accuracy_list)

    # =========================
    # SAVE
    # =========================
    forecast_df.to_csv("data/forecast.csv", index=False)
    accuracy_df.to_csv("data/accuracy.csv", index=False)

    return forecast_df, accuracy_df