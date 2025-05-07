import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from PIL import Image

# Setup Page Config
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load & Display Company Logo
try:
    logo = Image.open("coca_cola_logo.png")  # Ensure this file exists
    st.image(logo, width=200)
except:
    st.warning("⚠️ Logo not found! Ensure 'coca_cola_logo.png' is in the same directory.")

st.markdown("<h1 style='color: #E00000;'>Coca-Cola Production & Maintenance Dashboard</h1>", unsafe_allow_html=True)

# Sidebar Navigation
tab = st.sidebar.radio("📌 Select Tab", ["Production", "Maintenance", "Reports"])

# Dark Mode Toggle
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
theme_color = "#E00000" if not dark_mode else "#FFFFFF"
bg_color = "#FFFFFF" if not dark_mode else "#333333"
st.markdown(f"<style>body {{ background-color: {bg_color}; }}</style>", unsafe_allow_html=True)

# Year, Month, Date Selection
year = st.sidebar.selectbox("📅 Select Year", list(range(2020, 2031)))
month = st.sidebar.selectbox("🗓 Select Month",
                             ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
date = st.sidebar.date_input("📆 Select Date")

# Plant & Line Selection
plants = ["A", "B", "C", "D", "E"]
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]

plant = st.sidebar.selectbox("🏭 Select Plant", plants)
line = st.sidebar.selectbox("🔧 Select Line", lines)

# Create a local JSON database file for saving production data
DATA_FILE = "production_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}  # Handle corrupted JSON file
    return {}

def save_data(data):
    try:
        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4, default=str)  # Fix JSON serialization
    except TypeError as e:
        st.error(f"⚠️ Error saving data: {e}")

# Load production data
data_store = load_data()
plant_data = data_store.get(plant, {}).get(line, {})  # Load data for selected plant/line
days = list(range(1, 32))
data = pd.DataFrame({"Date": days, "Production": [plant_data.get(str(day), 0) for day in days]})

# Editable Production Table
st.subheader(f"📊 Production Data Entry for {plant}, {line}")
edited_data = st.data_editor(data, key="production_entry")

# Save Production Data
if st.button("💾 Save Production Data"):
    if plant not in data_store:
        data_store[plant] = {}
    data_store[plant][line] = {str(day): int(edited_data.iloc[day-1]["Production"]) for day in days}
    save_data(data_store)
    st.success("✅ Data saved successfully!")

# Low Production Alert
if edited_data["Production"].mean() < 1000:
    st.error(f"⚠️ Low Production Alert! Avg. daily production: {edited_data['Production'].mean()} units")

# Monthly Production Graph (Animated)
st.subheader("📈 Monthly Production Trends")
fig = px.line(edited_data, x="Date", y="Production", title=f"Production Trends for {line} in {month}", markers=True)
fig.update_layout(transition_duration=500)
st.plotly_chart(fig, use_container_width=True)

# Accurate Plant-Wise Production Summary
st.subheader("🏭 Total Production Summary")
summary_data = pd.DataFrame({"Plant": plants, "Total Production": [
    sum(data_store.get(p, {}).get(l, {}).values()) for p in plants for l in lines]})
st.table(summary_data)

# Export Reports (Excel Only)
st.sidebar.subheader("📜 Download Reports")
if st.sidebar.button("Download Excel Report"):
    summary_data.to_excel("production_report.xlsx", index=False)
    st.success("✅ Excel report generated!")

st.write("🚀 Future Enhancements: Google Sheets Integration, IoT Data Sync, AI Predictions")
