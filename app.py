import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from PIL import Image

# ---------------------------
# Page Setup & Branding
# ---------------------------
st.set_page_config(page_title="Coca-Cola Advanced Maintenance Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load & Display Company Logo (Ensure 'coca_cola_logo.png' exists)
try:
    logo = Image.open("coca_cola_logo.png")
    st.image(logo, width=200)
except Exception:
    st.warning("⚠️ Logo not found! Please ensure 'coca_cola_logo.png' is in the working directory.")

st.markdown("<h1 style='color: #E00000;'>Coca-Cola Advanced Maintenance Dashboard</h1>", unsafe_allow_html=True)

# ---------------------------
# Sidebar - Selection Filters
# ---------------------------
st.sidebar.title("Settings")
year = st.sidebar.selectbox("Select Year", list(range(2020, 2031)))
month = st.sidebar.selectbox("Select Month", 
                             ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
plants = ["A", "B", "C", "D", "E"]
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
plant = st.sidebar.selectbox("Select Plant", plants)
line = st.sidebar.selectbox("Select Line", lines)

# ---------------------------
# Maintenance Data File
# ---------------------------
MAINTENANCE_DATA_FILE = "maintenance_data.json"

def load_data():
    """Load maintenance data from a JSON file."""
    if os.path.exists(MAINTENANCE_DATA_FILE):
        try:
            with open(MAINTENANCE_DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(data):
    """Save maintenance data to a JSON file."""
    try:
        with open(MAINTENANCE_DATA_FILE, "w") as f:
            json.dump(data, f, indent=4, default=str)
    except Exception as e:
        st.error(f"Error saving maintenance data: {e}")

# Load maintenance data
data_store = load_data()
plant_maintenance = data_store.get(plant, {}).get(line, [])

st.subheader(f"Maintenance Records for Plant {plant} – {line}")

# ---------------------------
# Maintenance Record Form
# ---------------------------
with st.form("new_maintenance_record", clear_on_submit=True):
    st.write("### Add New Maintenance Record")
    equipment_options = [
        "KHS", "Krones", "Sidel", "Stretch Blowing", 
        "Filler", "Labeler", "Packer", "Palletizer",
        "Air Compressor", "Chiller", "DG", "Boiler"
    ]
    equipment = st.selectbox("Equipment Type", equipment_options)
    fault_code = st.text_input("Fault Code (Optional)")
    last_maintenance_date = st.date_input("Last Maintenance Date")
    status = st.selectbox("Status", ["Operational", "Needs Maintenance", "Urgent"])
    downtime = st.number_input("Downtime (in hours)", min_value=0.0, step=0.1, format="%.1f")
    notes = st.text_area("Maintenance Notes")
    next_maintenance_date = st.date_input("Next Scheduled Maintenance Date")
    maintenance_cost = st.number_input("Repair Cost ($)", min_value=0.0, step=0.1, format="%.2f")

    # Image Upload for Faulty Parts
    uploaded_file = st.file_uploader("Upload Faulty Part Image (Optional)", type=["jpg", "png"])

    submitted = st.form_submit_button("Add Maintenance Record")
    if submitted:
        new_record = {
            "Equipment": equipment,
            "FaultCode": fault_code,
            "LastMaintenanceDate": str(last_maintenance_date),
            "Status": status,
            "Downtime": downtime,
            "MaintenanceNotes": notes,
            "NextScheduledMaintenance": str(next_maintenance_date),
            "RepairCost": maintenance_cost,
            "ImageUploaded": uploaded_file.name if uploaded_file else None
        }
        if plant not in data_store:
            data_store[plant] = {}
        if line not in data_store[plant]:
            data_store[plant][line] = []
        data_store[plant][line].append(new_record)
        save_data(data_store)
        st.success("✅ Maintenance record added successfully!")
        # Refresh records
        plant_maintenance = data_store[plant][line]

# ---------------------------
# Maintenance Dashboard & Summary Charts
# ---------------------------
st.write("### Existing Maintenance Records")
if plant_maintenance:
    df = pd.DataFrame(plant_maintenance)
    st.dataframe(df)

    # Fault Code Overview
    if "FaultCode" in df.columns:
        fault_summary = df["FaultCode"].value_counts().reset_index()
        fault_summary.columns = ["Fault Code", "Occurrences"]
        st.subheader("Fault Code Analysis")
        fig_faults = px.bar(fault_summary, x="Fault Code", y="Occurrences", title="Most Frequent Fault Codes")
        st.plotly_chart(fig_faults, use_container_width=True)

    # Status Overview Pie Chart
    status_counts = df["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    st.subheader("Equipment Status Overview")
    fig_status = px.pie(status_counts, names="Status", values="Count", title="Maintenance Status Distribution")
    st.plotly_chart(fig_status, use_container_width=True)

    # Downtime Analysis Bar Chart
    downtime_summary = df.groupby("Equipment")["Downtime"].sum().reset_index()
    st.subheader("Total Downtime Analysis (hrs)")
    fig_downtime = px.bar(downtime_summary, x="Equipment", y="Downtime", title="Total Downtime per Equipment Type")
    st.plotly_chart(fig_downtime, use_container_width=True)

else:
    st.info("No maintenance records available for this plant and line.")

# ---------------------------
# Export to Excel
# ---------------------------
st.sidebar.subheader("Export Maintenance Report")
if st.sidebar.button("Download Excel Maintenance Report"):
    if plant_maintenance:
        export_df = pd.DataFrame(plant_maintenance)
        export_df["Plant"] = plant
        export_df["Line"] = line
        export_df.to_excel("maintenance_report.xlsx", index=False)
        st.success("✅ Excel maintenance report generated!")
    else:
        st.info("No maintenance records to export.")

st.write("🚀 Future Enhancements: IoT Integration, Predictive Failure Analysis, Spare Parts Inventory.")
