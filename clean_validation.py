import pandas as pd
import numpy as np

INPUT_FILE = "user_uploaded.csv"
OUTPUT_FILE = "cleaned_actual.csv"

# ===============================
# 1. COLUMN NAME MAPPING
# ===============================
COLUMN_MAP = {
    # Date
    "day": "Date",
    "date": "Date",
    "reporting start": "Date",

    # Platform
    "platform": "Platform",
    "source": "Platform",

    # Campaign
    "campaign name": "Campaign",
    "campaign": "Campaign",

    # Metrics
    "clicks": "Clicks",
    "cost": "Spend",
    "amount spent": "Spend",
    "spend": "Spend",
    "conversions": "Conversions",
    "results": "Conversions",
    "revenue": "Revenue",
    "value": "Revenue",
    "purchase value": "Revenue"
}

REQUIRED_COLUMNS = [
    "Date",
    "Platform",
    "Campaign",
    "Clicks",
    "Spend",
    "Conversions",
    "Revenue"
]

# ===============================
# 2. LOAD FILE
# ===============================
df = pd.read_csv(INPUT_FILE)
df.columns = df.columns.str.strip().str.lower()

print("Original columns:", df.columns.tolist())

# ===============================
# 3. MAP TO STANDARD SCHEMA
# ===============================
rename_dict = {}

for col in df.columns:
    if col in COLUMN_MAP:
        rename_dict[col] = COLUMN_MAP[col]

df = df.rename(columns=rename_dict)

print("Mapped columns:", df.columns.tolist())

# Add missing columns
for col in REQUIRED_COLUMNS:
    if col not in df.columns:
        print(f"Adding missing column {col} as 0")
        df[col] = 0

df = df[REQUIRED_COLUMNS]

# ===============================
# 4. CLEAN DATA
# ===============================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

df["Platform"] = df["Platform"].fillna("Unknown").str.strip().str.title()
df["Campaign"] = df["Campaign"].fillna("Unknown")

numeric_cols = ["Clicks","Spend","Conversions","Revenue"]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(0)
    df[col] = df[col].clip(lower=0)

df = df.drop_duplicates(subset=["Date","Platform","Campaign"])

df = df.sort_values(["Date","Platform"])

# ===============================
# 5. VALIDATION CHECKS
# ===============================
errors = []

if len(df) < 20:
    errors.append("Dataset too small for forecasting.")

if df["Spend"].sum() == 0:
    errors.append("Total Spend is 0.")

if df["Clicks"].sum() == 0:
    errors.append("Total Clicks is 0.")

date_range = (df["Date"].max() - df["Date"].min()).days
if date_range < 14:
    errors.append("Not enough date range for forecasting.")

if errors:
    print("\n⚠️ DATASET ISSUES:")
    for e in errors:
        print("-", e)
else:
    print("\n✅ Dataset looks good for forecasting.")

# ===============================
# 6. SAVE CLEANED DATA
# ===============================
df.to_csv(OUTPUT_FILE, index=False)
print("\nCleaned data saved as:", OUTPUT_FILE)
print("Rows:", len(df))