import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load Company Logo
try:
    logo = Image.open("coca_cola_logo.png")  # Ensure this file exists in the same folder!
    st.image(logo, width=200)
except:
    st.warning("⚠️ Logo not found! Ensure 'coca_cola_logo.png' is in the same directory.")

# Title & Theme Styling
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

# Editable Production Entry
st.subheader(f"📊 Production Data Entry for {plant}, {line}")
days = list(range(1, 32))
data = pd.DataFrame({"Date": days, "Production": [0]*31})  # Default values

# Make table editable
edited_data = st.data_editor(data, key="production_entry")

# Alerts for Low Production
if edited_data["Production"].mean() < 1000:  # Example threshold
    st.error(f"⚠️ Low Production Alert! Avg. daily production: {edited_data['Production'].mean()} units")

# Save Button (Google Sheets integration later)
if st.button("💾 Save Production Data"):
    st.success("✅ Data saved successfully! (Placeholder)")

# Production Graph (Animated)
st.subheader("📈 Monthly Production Trends")
fig = px.line(edited_data, x="Date", y="Production", title=f"Production Trends for {line} in {month}", markers=True)
fig.update_layout(transition_duration=500)
st.plotly_chart(fig, use_container_width=True)

# Production Summary Table
st.subheader("🏭 Total Production Summary")
summary_data = pd.DataFrame({"Plant": plants, "Total Production": [5000, 8000, 6000, 7000, 9000]})  # Placeholder
st.table(summary_data)

# Export Options
st.sidebar.subheader("📜 Download Reports")
report_type = st.sidebar.radio("Select Report Format", ["Excel", "PDF"])
if st.sidebar.button("Download Report"):
    st.success(f"✅ {report_type} report generated! (Placeholder)")

st.write("🚀 Future Enhancements: Google Sheets Integration, IoT Data Sync, AI Predictions")
