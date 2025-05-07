import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ---------------------------
# Page Setup & Branding
# ---------------------------
st.set_page_config(page_title="Blowing Machine Maintenance Tracker", layout="wide")
st.markdown("<h1 style='color: #E00000;'>Blowing Machine Maintenance Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------
# Data File Setup
# ---------------------------
DATA_FILE = "maintenance_schedule.json"

def load_data():
    """Load maintenance data from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data):
    """Save maintenance data to JSON file"""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4, default=str)

# Load maintenance data
data_store = load_data()

# ---------------------------
# Sidebar Filters & Settings
# ---------------------------
st.sidebar.title("Filter Maintenance Tasks")
filter_status = st.sidebar.radio("Show Records:", ["All", "Pending", "Completed", "Urgent"])
filter_priority = st.sidebar.radio("Show Priority:", ["All", "High", "Medium", "Low"])

# ---------------------------
# Weekly Maintenance Tracker
# ---------------------------
st.subheader("🔹 Weekly Maintenance Tracker")

# Sample Weekly Maintenance Data Structure
weekly_tasks = [
    {"No": 1, "Location": "Preform Hopper", "Activity": "Clean & apply grease for cam & bearing", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False, "Priority": "High", "Technician": "John"},
    {"No": 2, "Location": "Roller", "Activity": "Check roller condition", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False, "Priority": "Medium", "Technician": "Mike"},
    {"No": 3, "Location": "Preform return conveyor", "Activity": "Check belt condition", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False, "Priority": "Low", "Technician": "Alex"},
    {"No": 4, "Location": "Chiller Filters", "Activity": "Clean & Check", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False, "Priority": "High", "Technician": "Sam"},
]

# Convert Weekly Maintenance Data to DataFrame
df_weekly = pd.DataFrame(weekly_tasks)

# Convert Task Completion to Checkboxes
df_weekly["Week1"] = st.checkbox("Week 1 ✅", value=False, key="week1")
df_weekly["Week2"] = st.checkbox("Week 2 ✅", value=False, key="week2")
df_weekly["Week3"] = st.checkbox("Week 3 ✅", value=False, key="week3")
df_weekly["Week4"] = st.checkbox("Week 4 ✅", value=False, key="week4")
df_weekly["Week5"] = st.checkbox("Week 5 ✅", value=False, key="week5")

# Save Updated Weekly Maintenance Data
if st.button("💾 Save Weekly Maintenance"):
    data_store["weekly"] = df_weekly.to_dict(orient="records")
    save_data(data_store)
    st.success("✅ Weekly Maintenance Data Saved!")

# Display Weekly Maintenance Table
st.dataframe(df_weekly)

# ---------------------------
# Monthly Maintenance Tracker
# ---------------------------
st.subheader("🔹 Monthly Maintenance Tracker")

# Sample Monthly Maintenance Data Structure
monthly_tasks = [
    {"No": 1, "Location": "Oven reflector", "Activity": "Clean & inspect", "Completed": False, "Priority": "High", "Technician": "John", "Remarks": ""},
    {"No": 2, "Location": "Mandrel cam & roller", "Activity": "Check Wear/Tear", "Completed": False, "Priority": "Medium", "Technician": "Mike", "Remarks": ""},
    {"No": 3, "Location": "Elevator Belt", "Activity": "Check Wear/Tear", "Completed": False, "Priority": "Low", "Technician": "Alex", "Remarks": ""},
]

# Convert Monthly Maintenance Data to DataFrame
df_monthly = pd.DataFrame(monthly_tasks)

# Mark Completion Checkboxes
df_monthly["Completed"] = st.checkbox("Mark as ✅ Completed", value=False)

# Remarks Section
df_monthly["Remarks"] = st.text_area("Add Remarks")

# Save Updated Monthly Maintenance Data
if st.button("💾 Save Monthly Maintenance"):
    data_store["monthly"] = df_monthly.to_dict(orient="records")
    save_data(data_store)
    st.success("✅ Monthly Maintenance Data Saved!")

# Display Monthly Maintenance Table
st.dataframe(df_monthly)

# ---------------------------
# Alerts for Overdue Maintenance
# ---------------------------
st.subheader("🚨 Critical Alerts")

weekly_completed = df_weekly.iloc[:, 3:].sum(axis=1).mean() / 5 * 100
monthly_completed = df_monthly["Completed"].mean() * 100

if weekly_completed < 50:
    st.error("⚠️ Weekly Maintenance Below 50%! Immediate action required.")
if monthly_completed < 50:
    st.error("⚠️ Monthly Maintenance Below 50%! Immediate action required.")

# ---------------------------
# Spare Parts Inventory System
# ---------------------------
st.subheader("🛠 Spare Parts Inventory")

spare_parts = [
    {"Part": "Mandrel Roller", "Stock": 15, "Reorder Level": 5},
    {"Part": "Oven Sensor", "Stock": 8, "Reorder Level": 3},
    {"Part": "Elevator Belt", "Stock": 2, "Reorder Level": 5},
    {"Part": "Blow Wheel", "Stock": 12, "Reorder Level": 4},
]

df_inventory = pd.DataFrame(spare_parts)

st.table(df_inventory)

# Highlight parts below reorder level
for index, row in df_inventory.iterrows():
    if row["Stock"] < row["Reorder Level"]:
        st.warning(f"⚠️ Low stock alert for {row['Part']}! Consider reordering.")

# ---------------------------
# Export Maintenance Reports
# ---------------------------
st.sidebar.subheader("📤 Export Maintenance Report")
if st.sidebar.button("Download Excel Report"):
    weekly_export = pd.DataFrame(data_store.get("weekly", []))
    monthly_export = pd.DataFrame(data_store.get("monthly", []))
    inventory_export = pd.DataFrame(spare_parts)
    
    with pd.ExcelWriter("Maintenance_Report.xlsx") as writer:
        weekly_export.to_excel(writer, sheet_name="Weekly Tracker", index=False)
        monthly_export.to_excel(writer, sheet_name="Monthly Tracker", index=False)
        inventory_export.to_excel(writer, sheet_name="Spare Parts Inventory", index=False)
    
    st.success("✅ Excel maintenance report generated!")

st.write("🚀 Future Enhancements: Predictive AI Maintenance, IoT Sensor Integration.")
