import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json, os, calendar, re
from datetime import datetime

DATA_FILE = 'production_data.json'

# ─── Load or initialize data ─────────────────────────────────────────────
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        all_data = json.load(f)
else:
    all_data = {}

st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# ─── Branding ─────────────────────────────────────────────────────────────
col1, col2 = st.columns([1,4])
with col1:
    st.image("https://1000logos.net/wp-content/uploads/2017/05/Coca-Cola-Logo-500x281.png", width=150)
with col2:
    st.title("Coca-Cola Production Dashboard")
    st.markdown("📅 Daily edit → Monthly aggregates → Interactive charts")

# ─── Select Plant & Line ─────────────────────────────────────────────────
plants = ["Plant A","Plant B","Plant C"]
lines  = ["Line 1","Line 2","Line 3","Line 4","Line 5"]
plant = st.selectbox("Plant", plants)
line  = st.selectbox("Line",  lines)
key   = f"{plant}_{line}"

# ─── Daily Data Entry ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("1️⃣ Daily Production Entry")

year  = st.selectbox("Year",  [2023,2024,2025], key="year")
month = st.selectbox("Month", list(range(1,13)), key="month")
ndays = calendar.monthrange(year, month)[1]
day   = st.selectbox("Day",   list(range(1, ndays+1)), key="day")

if key not in all_data:
    all_data[key] = {}

daily_data = all_data[key]
date_str   = f"{year:04d}-{month:02d}-{day:02d}"
current    = daily_data.get(date_str, 0)

new_val = st.number_input(f"Production on {date_str}", min_value=0, value=current, step=1)
if st.button("💾 Save Daily"):
    daily_data[date_str] = new_val
    all_data[key] = daily_data
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success(f"Saved {new_val} units on {date_str}")

# ─── Aggregate to Monthly Totals ──────────────────────────────────────────
# Prepare valid daily entries
entries = [(d,val) for d,val in daily_data.items() if re.match(r"^\d{4}-\d{2}-\d{2}$", d)]
if entries:
    df_daily = pd.DataFrame(entries, columns=["Date","Prod"])
    df_daily["Date"] = pd.to_datetime(df_daily["Date"], errors="coerce")
    df_daily = df_daily.dropna(subset=["Date"])
else:
    df_daily = pd.DataFrame(columns=["Date","Prod"])

# Filter by selected year and sum by month
df_year    = df_daily[df_daily["Date"].dt.year == year]
df_monthly = df_year.groupby(df_year["Date"].dt.month)["Prod"].sum()
months_abbr = list(calendar.month_abbr)[1:]
monthly_totals = [int(df_monthly.get(m,0)) for m in range(1,13)]

# ─── Show Monthly Table & Charts ──────────────────────────────────────────
st.markdown("---")
st.subheader("2️⃣ Monthly Production (Summed)")

table = pd.DataFrame({
    "Month": months_abbr,
    "Production": monthly_totals
})
st.dataframe(table)

tab1, tab2 = st.tabs(["📊 Bar Chart","📈 Line Chart"])
with tab1:
    fig = px.bar(table, x="Month", y="Production",
                 color="Production", title=f"{plant} {line} Monthly Totals")
    st.plotly_chart(fig, use_container_width=True)
with tab2:
    fig = px.line(table, x="Month", y="Production", markers=True,
                  title=f"{plant} {line} Monthly Trend")
    st.plotly_chart(fig, use_container_width=True)

# ─── Combined Analysis Tab ────────────────────────────────────────────────
tab3 = st.expander("🔗 Combined Analysis", expanded=False)
with tab3:
    fig_comb = make_subplots(specs=[[{"secondary_y": True}]])
    fig_comb.add_trace(
        go.Bar(x=table["Month"], y=table["Production"],
               name="Monthly Production", marker_color='crimson'),
        secondary_y=False)
    fig_comb.add_trace(
        go.Scatter(x=table["Month"], y=pd.Series(monthly_totals).cumsum(),
                   name="Cumulative Production", mode='lines+markers',
                   line=dict(color='orange')),
        secondary_y=True)
    fig_comb.update_xaxes(title_text="Month")
    fig_comb.update_yaxes(title_text="Monthly Production", secondary_y=False)
    fig_comb.update_yaxes(title_text="Cumulative Production", secondary_y=True)
    fig_comb.update_layout(title_text=f"{plant} {line} Combined View")
    st.plotly_chart(fig_comb, use_container_width=True)
