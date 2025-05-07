import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from PIL import Image

# ---------------------------
# Page Setup & Branding
# ---------------------------
st.set_page_config(page_title="Coca-Cola Maintenance Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load & display company logo (ensure 'coca_cola_logo.png' is present)
try:
    logo = Image.open("coca_cola_logo.png")
    st.image(logo, width=200)
except Exception:
    st.warning("⚠️ Logo not found! Please ensure 'coca_cola_logo.png' is in the working directory.")

st.markdown("<h1 style='color: #E00000;'>Coca-Cola Maintenance Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------
# Sidebar - Global Selections
# ---------------------------
st.sidebar.title("Settings")
# Although Maintenance records are not date–specific, we include them for consistency
year = st.sidebar.selectbox("Select Year", list(range(2020, 2031)))
month = st.sidebar.selectbox("Select Month", 
                             ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
_ = st.sidebar.date_input("Select Date")
plants = ["A", "B", "C", "D", "E"]
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
plant = st.sidebar.selectbox("Select Plant", plants)
line = st.sidebar.selectbox("Select Line", lines)

# ---------------------------
# File for Maintenance Data Storage
# ---------------------------
MAINTENANCE_DATA_FILE = "maintenance_data.json"

def load_maintenance_data():
    """Load maintenance data from a JSON file."""
    if os.path.exists(MAINTENANCE_DATA_FILE):
        try:
            with open(MAINTENANCE_DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_maintenance_data(data):
    """Save maintenance data to a JSON file."""
    try:
        with open(MAINTENANCE_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4, default=str)
    except Exception as e:
        st.error(f"Error saving maintenance data: {e}")

# Load existing maintenance data
maint_data = load_maintenance_data()
# Get records for the selected plant & line (if any)
plant_maint_records = maint_data.get(plant, {}).get(line, [])

st.subheader(f"Maintenance Records for Plant {plant} – {line}")

# ---------------------------
# Form for Adding a New Maintenance Record
# ---------------------------
with st.form("new_maintenance_record", clear_on_submit=True):
    st.write("### Add New Maintenance Record")
    # Equipment options (production line equipment and utilities)
    equipment_options = [
        "KHS", "Krones", "Sidel", "Stretch Blowing", 
        "Filler", "Labeler", "Packer", "Palletizer",
        "Air Compressor", "Chiller", "DG", "Boiler"
    ]
    equipment = st.selectbox("Equipment", equipment_options)
    last_maintenance_date = st.date_input("Last Maintenance Date")
    status = st.selectbox("Status", ["Operational", "Needs Maintenance", "Urgent"])
    notes = st.text_area("Maintenance Notes")
    next_maintenance_date = st.date_input("Next Scheduled Maintenance Date")
    downtime = st.number_input("Downtime (in hours)", min_value=0.0, step=0.1, format="%.1f")
    submitted = st.form_submit_button("Add Maintenance Record")
    
    if submitted:
        new_record = {
            "Equipment": equipment,
            "LastMaintenanceDate": str(last_maintenance_date),
            "Status": status,
            "MaintenanceNotes": notes,
            "NextScheduledMaintenance": str(next_maintenance_date),
            "Downtime": downtime
        }
        if plant not in maint_data:
            maint_data[plant] = {}
        if line not in maint_data[plant]:
            maint_data[plant][line] = []
        maint_data[plant][line].append(new_record)
        save_maintenance_data(maint_data)
        st.success("✅ Maintenance record added successfully!")
        # Refresh current records list
        plant_maint_records = maint_data[plant][line]

# ---------------------------
# Display Existing Maintenance Records
# ---------------------------
st.write("### Existing Maintenance Records")
if plant_maint_records:
    maint_df = pd.DataFrame(plant_maint_records)
    st.dataframe(maint_df)
    
    # Summary chart: Count of records per equipment type
    summary_counts = maint_df["Equipment"].value_counts().reset_index()
    summary_counts.columns = ["Equipment", "Count"]
    st.subheader("Maintenance Records Summary by Equipment")
    fig = px.bar(summary_counts, x="Equipment", y="Count", title="Maintenance Records Count")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No maintenance records available for this plant and line.")

# ---------------------------
# Export Functionality
# ---------------------------
st.sidebar.subheader("Export Maintenance Report")
if st.sidebar.button("Download Excel Maintenance Report"):
    if plant_maint_records:
        export_df = pd.DataFrame(plant_maint_records)
        export_df["Plant"] = plant
        export_df["Line"] = line
        export_df.to_excel("maintenance_report.xlsx", index=False)
        st.success("✅ Excel maintenance report generated!")
    else:
        st.info("No maintenance records to export.")

st.write("🚀 Future enhancements: Add fault codes, upload images, integrate IoT sensor data, track spare parts inventory, and more.")
