import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# File to store data
DATA_FILE = 'production_data.json'

# Load existing data if file exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        all_data = json.load(f)
else:
    all_data = {}

# --- UI SECTION ---
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# Coca-Cola logo (optional: place a valid image path or URL here)
st.image("https://1000logos.net/wp-content/uploads/2017/05/Coca-Cola-Logo-500x281.png", width=200)

st.title("Coca-Cola Plant Production Dashboard 🎯")
st.markdown("Manage and visualize production data by line and plant.")

# Input: plant and line
plant_name = st.selectbox("Select Plant Name", ["Plant A", "Plant B", "Plant C"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"])

# Unique key for saving data
key = f"{plant_name}_{line}"

# Initialize or load monthly data
if key in all_data:
    monthly_data = all_data[key]
else:
    monthly_data = {month: 0 for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}

# Show input fields for each month
st.subheader("Enter Monthly Production Data (in units)")
cols = st.columns(6)
months = list(monthly_data.keys())
for i, month in enumerate(months):
    monthly_data[month] = cols[i % 6].number_input(
        f"{month}", min_value=0, value=monthly_data[month], step=1)

# Save button
if st.button("💾 Save Data"):
    all_data[key] = monthly_data
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("Data saved successfully!")

# Create and show graph
df = pd.DataFrame({
    "Month": list(monthly_data.keys()),
    "Production": list(monthly_data.values())
})

st.subheader(f"📊 Production Trend for {plant_name} - {line}")
fig = px.bar(df, x="Month", y="Production", title=f"{plant_name} - {line} Production",
             color="Production", color_continuous_scale='reds')
st.plotly_chart(fig, use_container_width=True)
