import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json, os
from datetime import datetime
import calendar

DATA_FILE = 'production_data.json'

# Load existing data
if os.path.exists(DATA_FILE):
    with open(DATA_FILE) as f:
        all_data = json.load(f)
else:
    all_data = {}

st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# Branding
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://1000logos.net/wp-content/uploads/2017/05/Coca-Cola-Logo-500x281.png", width=150)
with col2:
    st.title("Coca-Cola Production Dashboard")
    st.markdown("📅 Now with Daily-edit & Monthly-aggregate")

# Plant & Line selectors
plants = ["Plant A", "Plant B", "Plant C"]
lines  = ["Line 1","Line 2","Line 3","Line 4","Line 5"]
plant = st.selectbox("Plant", plants)
line  = st.selectbox("Line",  lines)
key   = f"{plant}_{line}"

st.markdown("---")
st.subheader("1️⃣ Daily Production Entry")

# Year/Month/Day selectors
year  = st.selectbox("Year",  [2023,2024,2025], key="year")
month = st.selectbox("Month", list(range(1,13)), key="month")
# dynamic day list
ndays = calendar.monthrange(year, month)[1]
day   = st.selectbox("Day",   list(range(1, ndays+1)), key="day")

# Load or init daily_data for this plant/line
if key not in all_data:
    all_data[key] = {}          # will hold daily {"YYYY-MM-DD": value}
daily_data = all_data[key]

# Date string
date_str = f"{year:04d}-{month:02d}-{day:02d}"
current = daily_data.get(date_str, 0)

# Input & Save daily
new_val = st.number_input(f"Production on {date_str}", min_value=0, value=current, step=1)
if st.button("💾 Save Daily", key="save_daily"):
    daily_data[date_str] = new_val
    all_data[key] = daily_data
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success(f"Saved {new_val} units on {date_str}")

# --- build monthly totals from daily_data ---
# aggregate daily values by year-month
df_daily = pd.Series(daily_data).rename_axis("Date").reset_index(name="Prod")
df_daily["Date"] = pd.to_datetime(df_daily["Date"])
# filter by current key and year
df_year = df_daily[df_daily["Date"].dt.year == year]
df_monthly = df_year.groupby(df_year["Date"].dt.month)["Prod"].sum()
# ensure all months 1–12 present
months = list(calendar.month_abbr)[1:]
monthly_totals = [int(df_monthly.get(m, 0)) for m in range(1,13)]

st.markdown("---")
st.subheader("2️⃣ Monthly Production (Summed from Daily)")

# Show table
table = pd.DataFrame({
    "Month": months,
    "Production": monthly_totals
})
st.dataframe(table)

# Plot charts
tab1, tab2 = st.tabs(["Bar Chart","Line Chart"])
with tab1:
    fig = px.bar(table, x="Month", y="Production", color="Production", title=f"{plant} {line} Monthly Totals")
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    fig = px.line(table, x="Month", y="Production", markers=True, title=f"{plant} {line} Monthly Trend")
    st.plotly_chart(fig, use_container_width=True)
