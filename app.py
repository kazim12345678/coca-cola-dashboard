import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# ─── Config ────────────────────────────────────────
st.set_page_config(page_title="Core Dashboard", layout="wide")

DATA_FILE = "daily_production.json"
plants    = ['A','B','C','D','E']
lines     = [1,2,3,4,5]

# ─── Load or initialize data ──────────────────────
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        all_data = json.load(f)
else:
    all_data = {}  # keys: "Plant_Line", values: {"YYYY-MM-DD": production}

# ─── UI Selectors ──────────────────────────────────
st.title("📊 Core Production Dashboard")

# Date picker
selected_date = st.date_input(
    "Select Date",
    min_value=datetime(2023,1,1),
    max_value=datetime(2030,12,31),
    value=datetime.today()
)

# Plant & line selectors
plant = st.selectbox("Select Plant", plants)
line  = st.selectbox("Select Line",  lines)
key   = f"{plant}_{line}"

# Current value for this date
date_str = selected_date.strftime("%Y-%m-%d")
current_val = all_data.get(key, {}).get(date_str, 0)

# Daily production input
new_val = st.number_input(
    f"Production on {date_str}", min_value=0, value=current_val, step=1
)

# Save button
if st.button("💾 Save Production"):
    all_data.setdefault(key, {})[date_str] = new_val
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("Saved!")

# ─── Aggregate Monthly Totals ─────────────────────
# Build DataFrame of 12 months for this plant
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
month_sums = []
for i, m in enumerate(months, start=1):
    # Sum all days in that month-year
    total = 0
    for d_str, val in all_data.get(key, {}).items():
        d = datetime.fromisoformat(d_str)
        if d.year == selected_date.year and d.month == i:
            total += val
    month_sums.append(total)

df_month = pd.DataFrame({
    "Month": months,
    "Production": month_sums
})

# Show plant total (12 months)
st.subheader(f"🌱 {plant} Total Production in {selected_date.year}")
st.bar_chart(df_month.set_index("Month"))

# ─── Show Line Summary Across Plants ─────────────
# Build a summary table: each line of this plant vs all plants?
# Actually, show all lines of this same plant:
st.subheader(f"📈 {plant} – Line {line} Monthly Trend")
st.line_chart(df_month.set_index("Month"))

