import streamlit as st
import pandas as pd
import plotly.express as px

# Page Configurations
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# Company Branding
st.image("coca_cola_logo.png", width=200)
st.title("Coca-Cola Production & Maintenance Dashboard")

# Navigation Tabs
tab = st.sidebar.radio("Select Tab", ["Production", "Maintenance"])

# Year, Month, Date Selection
year = st.sidebar.selectbox("Select Year", list(range(2020, 2031)))
month = st.sidebar.selectbox("Select Month", ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
date = st.sidebar.date_input("Select Date")

# Plant & Line Selection
plants = ["A", "B", "C", "D", "E"]
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]

plant = st.sidebar.selectbox("Select Plant", plants)
line = st.sidebar.selectbox("Select Line", lines)

# Editable Table for Production Entry
st.subheader(f"Production Data Entry for Plant {plant}, {line}")
days = list(range(1, 32))
data = pd.DataFrame({"Date": days, "Production": [0]*31})
edited_data = st.data_editor(data, key="production_entry")

# Save Button (To Be Connected to Google Sheets)
if st.button("Save Production Data"):
    st.success("Data saved successfully! (Placeholder)")

# Monthly Production Graph
st.subheader("Monthly Production Trends")
fig = px.line(edited_data, x="Date", y="Production", title=f"Production Trends for {line} in {month}")
st.plotly_chart(fig, use_container_width=True)

# Production Summary Table
st.subheader("Total Production Summary")
summary_data = pd.DataFrame({"Plant": plants, "Total Production": [0]*5})
st.table(summary_data)

st.write("🚀 Future Enhancements: Google Sheets Integration, Live Alerts, Advanced Analytics")
