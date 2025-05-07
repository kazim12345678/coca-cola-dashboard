import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import datetime
from PIL import Image

# ---------------------------
# Page Setup & Branding
# ---------------------------
st.set_page_config(page_title="Coca-Cola Production & Maintenance Dashboard", layout="wide")
st.markdown("<h1 style='color: #E00000;'>Coca-Cola Production & Maintenance Dashboard</h1>", unsafe_allow_html=True)

# Display Company Logo
try:
    logo = Image.open("coca_cola_logo.png")
    st.image(logo, width=200)
except Exception:
    st.warning("⚠️ Logo not found! Please ensure 'coca_cola_logo.png' is in the working directory.")

# ---------------------------
# Sidebar: Module Selection & Settings
# ---------------------------
module = st.sidebar.radio("Select Module", ["Production", "Maintenance"])

# Common selections for both modules
plants = ["A", "B", "C", "D", "E"]
lines = ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"]
plant = st.sidebar.selectbox("Select Plant", plants)
line = st.sidebar.selectbox("Select Line", lines)

# ---------------------------
# JSON File Paths & Utility Functions
# ---------------------------
PROD_FILE = "production_data.json"
MAINT_FILE = "maintenance_data.json"

def load_json(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_json(data, file_path):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4, default=str)

# ---------------------------
# Production Module
# ---------------------------
if module == "Production":
    st.subheader(f"Production Data Entry for Plant {plant}, {line}")
    
    # Load existing production data
    prod_data = load_json(PROD_FILE)
    plant_data = prod_data.get(plant, {}).get(line, {})
    dates = list(range(1, 32))
    production_values = [plant_data.get(str(d), 0) for d in dates]
    
    prod_df = pd.DataFrame({
        "Date": dates,
        "Production": production_values
    })
    
    # Editable production table (using Streamlit’s data_editor)
    edited_prod = st.data_editor(prod_df, key="prod_editor")
    
    if st.button("💾 Save Production Data"):
        if plant not in prod_data:
            prod_data[plant] = {}
        prod_data[plant][line] = {str(d): int(edited_prod.iloc[d-1]["Production"]) for d in dates}
        save_json(prod_data, PROD_FILE)
        st.success("✅ Production data saved successfully!")
    
    # Alert if average production is below threshold (example: 1000 units)
    avg_prod = edited_prod["Production"].mean()
    if avg_prod < 1000:
        st.error(f"⚠️ Low Production Alert: Average daily production = {avg_prod:.2f} units")
    
    # Production Trend Graph
    fig_prod = px.line(edited_prod, x="Date", y="Production", 
                         title=f"Production Trend for {line}")
    fig_prod.update_layout(transition_duration=500)
    st.plotly_chart(fig_prod, use_container_width=True)
    
    # Export Production Report
    if st.sidebar.button("Download Production Excel Report"):
        export_df = prod_df.copy()
        export_df.to_excel("production_report.xlsx", index=False)
        st.success("✅ Production Excel report generated!")

# ---------------------------
# Maintenance Module
# ---------------------------
elif module == "Maintenance":
    st.subheader(f"Maintenance Tracker for Plant {plant}, {line}")
    maint_data = load_json(MAINT_FILE)
    
    # Use tabs for Weekly and Monthly maintenance trackers
    tab_weekly, tab_monthly = st.tabs(["Weekly Maintenance Tracker", "Monthly Maintenance Tracker"])
    
    # --- Weekly Maintenance Tracker ---
    with tab_weekly:
        st.markdown("### Weekly Maintenance Tracker")
        # Sample weekly maintenance tasks (customize as needed)
        weekly_tasks = [
            {"No": 1, "Location": "Preform Hopper", "Activity": "Clean & apply grease for cam & bearing", 
             "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
            {"No": 2, "Location": "Preform Hopper", "Activity": "Check chain & sprocket condition and apply grease", 
             "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
            {"No": 3, "Location": "Roller", "Activity": "Check roller condition", 
             "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
            {"No": 4, "Location": "Preform return conveyor", "Activity": "Check belt condition", 
             "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
            {"No": 5, "Location": "Chiller Filters", "Activity": "Clean & Check", 
             "Week1": False, "Week2": False, "Week3": False, "Week4": False, "Week5": False},
        ]
        df_weekly = pd.DataFrame(weekly_tasks)
        # Use data_editor for weekly tasks so users can check off completed tasks
        edited_weekly = st.data_editor(df_weekly, key="weekly_editor")
        
        if st.button("💾 Save Weekly Maintenance", key="save_weekly"):
            if plant not in maint_data:
                maint_data[plant] = {}
            if line not in maint_data[plant]:
                maint_data[plant][line] = {}
            maint_data[plant][line]["weekly"] = edited_weekly.to_dict(orient="records")
            save_json(maint_data, MAINT_FILE)
            st.success("✅ Weekly Maintenance data saved!")
        
        st.dataframe(edited_weekly)
        
        # Calculate weekly completion percentage and display a progress bar
        # Convert the weekly checkbox columns to numeric (True=1, False=0)
        weekly_numeric = edited_weekly.loc[:, "Week1":"Week5"].astype(int)
        weekly_completed = weekly_numeric.sum(axis=1).mean() / 5 * 100
        st.write(f"**Weekly Completion:** {weekly_completed:.1f}%")
        st.progress(int(weekly_completed))
        
    # --- Monthly Maintenance Tracker ---
    with tab_monthly:
        st.markdown("### Monthly Maintenance Tracker")
        # Sample monthly maintenance tasks (customize as needed)
        monthly_tasks = [
            {"No": 1, "Location": "Oven reflector", "Activity": "Clean & inspect", "Completed": False, "Remark": ""},
            {"No": 2, "Location": "Mandrel cam & roller", "Activity": "Check Wear/Tear", "Completed": False, "Remark": ""},
            {"No": 3, "Location": "Hopper belt", "Activity": "Check Wear/Tear", "Completed": False, "Remark": ""},
            {"No": 4, "Location": "Elevator Belt", "Activity": "Check Wear/Tear", "Completed": False, "Remark": ""},
            {"No": 5, "Location": "Head wheel / Blow wheel", "Activity": "Check zero setting", "Completed": False, "Remark": ""},
        ]
        df_monthly = pd.DataFrame(monthly_tasks)
        # Editable table for monthly maintenance
        edited_monthly = st.data_editor(df_monthly, key="monthly_editor")
        
        if st.button("💾 Save Monthly Maintenance", key="save_monthly"):
            if plant not in maint_data:
                maint_data[plant] = {}
            if line not in maint_data[plant]:
                maint_data[plant][line] = {}
            maint_data[plant][line]["monthly"] = edited_monthly.to_dict(orient="records")
            save_json(maint_data, MAINT_FILE)
            st.success("✅ Monthly Maintenance data saved!")
        
        st.dataframe(edited_monthly)
        
        # Calculate monthly completion percentage (assuming 'Completed' column is boolean)
        monthly_numeric = edited_monthly["Completed"].astype(int)
        monthly_completed = monthly_numeric.mean() * 100
        st.write(f"**Monthly Completion:** {monthly_completed:.1f}%")
        st.progress(int(monthly_completed))
    
    # ---------------------------
    # Spare Parts Inventory Section
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
    for idx, row in df_inventory.iterrows():
        if row["Stock"] < row["Reorder Level"]:
            st.warning(f"⚠️ Low stock alert for {row['Part']}! Consider reordering.")
    
    # ---------------------------
    # Export Maintenance Reports
    # ---------------------------
    if st.sidebar.button("Download Maintenance Excel Report"):
        weekly_export = pd.DataFrame(maint_data.get(plant, {}).get(line, {}).get("weekly", []))
        monthly_export = pd.DataFrame(maint_data.get(plant, {}).get(line, {}).get("monthly", []))
        inventory_export = pd.DataFrame(spare_parts)
        with pd.ExcelWriter("Maintenance_Report.xlsx") as writer:
            weekly_export.to_excel(writer, sheet_name="Weekly Tracker", index=False)
            monthly_export.to_excel(writer, sheet_name="Monthly Tracker", index=False)
            inventory_export.to_excel(writer, sheet_name="Spare Parts Inventory", index=False)
        st.success("✅ Maintenance Excel report generated!")

st.write("🚀 Future Enhancements: Predictive AI Maintenance, IoT Sensor Integration, Spare Parts Inventory Management, and more.")
