import streamlit as st
import pandas as pd
import json, os
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Coca-Cola Dashboard", layout="wide")
DATA_FILE = 'production_data.json'

# ---------- DATA LOADING ----------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE,'r') as f:
        all_data = json.load(f)
else:
    all_data = {}  # structure: all_data[year][plant][line][month]

# utility to ensure nested dicts
from collections import defaultdict

def get_data():
    # ensure structure for current years
    return defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {m:0 for m in months})))

# ---------- CONSTANTS ----------
plants = ['A','B','C','D','E','F']
lines  = [1,2,3,4,5]
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
current_year = datetime.now().year

# fill missing structure
if not all_data:
    for y in range(2023, current_year+1):
        all_data[str(y)] = {}
        for p in plants:
            all_data[str(y)][p] = {}
            for l in lines:
                all_data[str(y)][p][str(l)] = {m:0 for m in months}

# ---------- UI ----------
st.title("🥤 Coca-Cola Production Dashboard")

# Year filter
year = st.selectbox("Select Year", [str(y) for y in range(2023, current_year+1)])
# Month filter (multi)
selected_months = st.multiselect("Select Month(s)", months, default=months)

# ---------- Monthly Edit Section ----------
st.header("✏️ Edit Monthly Production")
col1, col2, col3 = st.columns(3)
with col1:
    plant = st.selectbox("Plant", plants)
with col2:
    line = st.selectbox("Line", lines)
with col3:
    month = st.selectbox("Month", months)

# current value
current_val = all_data[year][plant][str(line)][month]
new_val = st.number_input(f"Production for {plant} Line {line} {month} {year}", value=current_val, min_value=0)
if st.button("💾 Save", key="save_monthly"):
    all_data[year][plant][str(line)][month] = new_val
    with open(DATA_FILE,'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("Saved!")

# ---------- Graph for selected line ----------
st.subheader(f"📈 Monthly Trend: {plant} Line {line} {year}")
df_line = pd.DataFrame({m: all_data[year][plant][str(line)][m] for m in months}, index=[0]).T
fig = px.line(df_line.reset_index(), x='index', y=0, markers=True,
              labels={'index':'Month',0:'Production'})
st.plotly_chart(fig, use_container_width=True)

# ---------- Plant-level Overview ----------
st.header("🌱 Plant-Level Total Production")
plant_totals = []
for p in plants:
    total = sum(sum(all_data[year][p][str(l)].values()) for l in lines)
    plant_totals.append({'Plant':p,'Total':total})
df_plants = pd.DataFrame(plant_totals)
st.dataframe(df_plants)

# ---------- Line-level Breakdown ----------
st.header("📊 Line-Level Breakdown (25 lines)")
line_records = []
for p in plants:
    for l in lines:
        total = sum(all_data[year][p][str(l)].values())
        line_records.append({'Plant':p,'Line':l,'Total':total})
df_lines = pd.DataFrame(line_records)
st.dataframe(df_lines)
