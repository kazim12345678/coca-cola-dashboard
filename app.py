import streamlit as st
import pandas as pd
import json
import os

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
# Weekly Maintenance Tracker
# ---------------------------
st.subheader("🔹 Weekly Maintenance Tracker")

# Sample Weekly Maintenance Data Structure
weekly_tasks = [
    {"No": 1, "Location": "Preform Hopper", "Activity": "Clean & apply grease for cam & bearing", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
    {"No": 2, "Location": "Preform Hopper", "Activity": "Check chain & sprocket condition and apply grease", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
    {"No": 3, "Location": "Roller", "Activity": "Check roller condition", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
    {"No": 4, "Location": "Preform return conveyor", "Activity": "Check belt condition", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
    {"No": 5, "Location": "Chiller Filters", "Activity": "Clean & Check", "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
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
    {"No": 1, "Location": "Oven reflector", "Activity": "Clean & inspect", "Completed": False, "Remarks": ""},
    {"No": 2, "Location": "Mandrel cam & roller", "Activity": "Check Wear/Tear", "Completed": False, "Remarks": ""},
    {"No": 3, "Location": "Hopper belt", "Activity": "Check Wear/Tear", "Completed": False, "Remarks": ""},
    {"No": 4, "Location": "Elevator Belt", "Activity": "Check Wear/Tear", "Completed": False, "Remarks": ""},
    {"No": 5, "Location": "Head wheel / Blow wheel", "Activity": "Check zero setting", "Completed": False, "Remarks": ""},
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
# Maintenance Overview & Alerts
# ---------------------------
st.subheader("📊 Maintenance Overview")

# Calculate Completion Percentage
weekly_completed = df_weekly.iloc[:, 3:].sum(axis=1).mean() / 5 * 100
monthly_completed = df_monthly["Completed"].mean() * 100

# Show Maintenance Progress
st.progress(int(weekly_completed), text="✅ Weekly Completion Progress")
st.progress(int(monthly_completed), text="✅ Monthly Completion Progress")

# Alert for Overdue Maintenance
if weekly_completed < 50:
    st.error("⚠️ Weekly Maintenance Below 50%! Urgent action required.")
if monthly_completed < 50:
    st.error("⚠️ Monthly Maintenance Below 50%! Urgent action required.")

# ---------------------------
# Export Maintenance Reports
# ---------------------------
st.sidebar.subheader("Export Maintenance Report")
if st.sidebar.button("Download Excel Report"):
    weekly_export = pd.DataFrame(data_store.get("weekly", []))
    monthly_export = pd.DataFrame(data_store.get("monthly", []))
    with pd.ExcelWriter("Maintenance_Report.xlsx") as writer:
        weekly_export.to_excel(writer, sheet_name="Weekly Tracker", index=False)
        monthly_export.to_excel(writer, sheet_name="Monthly Tracker", index=False)
    st.success("✅ Excel maintenance report generated!")

st.write("🚀 Future Enhancements: Spare Parts Inventory, Predictive AI Maintenance, IoT Data Integration.")
