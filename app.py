import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime

# ---------- CONFIG ----------
st.set_page_config(page_title="Coca-Cola Dashboard", layout="wide")
DATA_FILE = 'production_data.json'

# ---------- LOAD OR INIT DATA ----------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE,'r') as f:
        all_data = json.load(f)
else:
    all_data = {}

# Ensure top‐level years exist
current_year = datetime.now().year
for y in range(2023, current_year+1):
    all_data.setdefault(str(y), {})

plants = ['Lahore','B','C','D','E','F']
lines  = [1,2,3,4,5]
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# Populate missing nested dicts
for year in all_data:
    for p in plants:
        all_data[year].setdefault(p, {})
        for l in lines:
            all_data[year][p].setdefault(str(l), {m: 0 for m in months})

# ---------- UI ----------
st.title("🥤 Coca-Cola Production Dashboard")

# Year & Month Filters
year = st.selectbox("Select Year", [str(y) for y in range(2023, current_year+1)])
st.markdown(f"**Editing data for year {year}**")

# Edit Monthly Data
st.header("✏️ Edit Monthly Production")

col1, col2, col3 = st.columns(3)
with col1:
    plant = st.selectbox("Plant", plants)
with col2:
    line = st.selectbox("Line", lines)
with col3:
    month = st.selectbox("Month", months)

# Read current value safely
current_val = all_data[year][plant][str(line)][month]
new_val = st.number_input(f"Production for {plant} Line {line} in {month} {year}", 
                           min_value=0, value=current_val, step=1)

if st.button("💾 Save"):
    all_data[year][plant][str(line)][month] = new_val
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("Saved!")

# ---------- Visualization for Single Line ----------
st.subheader(f"📈 {plant} Line {line} - Monthly Trend")
df_line = pd.DataFrame({
    "Month": months,
    "Production": [all_data[year][plant][str(line)][m] for m in months]
})
fig_line = px.line(df_line, x="Month", y="Production", markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# ---------- Plant-Level Overview ----------
st.header("🌱 Plant-Level Total Production")
plant_totals = []
for p in plants:
    total = sum(sum(all_data[year][p][str(l)].values()) for l in lines)
    plant_totals.append({"Plant": p, "Total": total})
df_plants = pd.DataFrame(plant_totals).set_index("Plant")
st.bar_chart(df_plants)

# ---------- Line-Level Breakdown ----------
st.header("📊 Line-Level Breakdown")
line_records = []
for p in plants:
    for l in lines:
        total = sum(all_data[year][p][str(l)].values())
        line_records.append({"Plant": p, "Line": l, "Total": total})
df_lines = pd.DataFrame(line_records)
st.dataframe(df_lines)
