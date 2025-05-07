import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Page Configuration
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# Load and Display Company Logo
try:
    logo = Image.open("coca_cola_logo.png")  # Ensure this file exists!
    st.image(logo, width=200)
except:
    st.warning("⚠️ Logo not found! Ensure 'coca_cola_logo.png' is in the same directory.")

st.title("Coca-Cola Production & Maintenance Dashboard")

# Sidebar Navigation
tab = st.sidebar.radio("📌 Select Tab", ["Production", "Maintenance"])

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

# Editable Table for Daily Production Entry
st.subheader(f"📊 Production Data Entry for {plant}, {line}")
days = list(range(1, 32))
data = pd.DataFrame({"Date": days, "Production": [0]*31})  # Default values

# Make table editable
edited_data = st.data_editor(data, key="production_entry")

# Save Button (To Be Linked with Google Sheets)
if st.button("💾 Save Production Data"):
    st.success("✅ Data saved successfully! (Placeholder)")

# Production Graph
st.subheader("📈 Monthly Production Trends")
fig = px.line(edited_data, x="Date", y="Production", title=f"Production Trends for {line} in {month}")
st.plotly_chart(fig, use_container_width=True)

# Production Summary Table (Per Plant)
st.subheader("🏭 Total Production Summary")
summary_data = pd.DataFrame({"Plant": plants, "Total Production": [0]*5})
st.table(summary_data)

st.write("🚀 Future Enhancements: Google Sheets Integration, Live Alerts, Advanced Analytics")
