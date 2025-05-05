import streamlit as st
import pandas as pd
import os
import calendar
from datetime import datetime
from PIL import Image
import re

# ------------------------
# Configuration
# ------------------------

DATA_FILE = "data.csv"
UPLOAD_DIR = "uploads"

# ------------------------
# Initial Setup
# ------------------------

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Ensure data file exists
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Plant", "Line", "Date", "Production"])
    df_init.to_csv(DATA_FILE, index=False)

# ------------------------
# Load data function
# ------------------------

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

# ------------------------
# UI
# ------------------------

st.title("🥤 Coca-Cola Daily Production Tracker")

st.header("📋 Daily Entry Form")

plant = st.selectbox("Select Plant", ["Plant A", "Plant B", "Plant C"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3"])

# Date selection
year = st.selectbox("Select Year", list(range(2023, 2026)))
month_name = st.selectbox("Select Month", list(calendar.month_name)[1:])
month = list(calendar.month_name).index(month_name)

days_in_month = calendar.monthrange(year, month)[1]
day = st.selectbox("Select Day", list(range(1, days_in_month + 1)))

# Final selected date
try:
    selected_date = datetime(year, month, day)
except ValueError:
    st.error("Invalid date selected!")
    st.stop()

# Production value
production = st.number_input("Enter Production (Units)", min_value=0)

# Image uploader
uploaded_image = st.file_uploader("📸 Upload Machine Counter Image", type=["jpg", "jpeg", "png"])

# ------------------------
# Save Button
# ------------------------

if st.button("💾 Save Entry"):
    # Save to CSV
    df_new = pd.DataFrame([{
        "Plant": plant,
        "Line": line,
        "Date": selected_date.strftime("%Y-%m-%d"),
        "Production": production
    }])
    df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)

    # Save image
    if uploaded_image:
        clean_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", uploaded_image.name.lower())
        folder_date = selected_date.strftime("%Y-%m-%d")
        image_filename = f"{plant}_{line}_{folder_date}_{clean_filename}"
        image_path = os.path.join(UPLOAD_DIR, image_filename)
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

    st.success("✅ Entry saved successfully!")

# ------------------------
# Display Records
# ------------------------

st.header("📈 Daily Production Records")
df_display = load_data()

if df_display.empty:
    st.info("No records found.")
else:
    st.dataframe(df_display)

# ------------------------
# Display Uploaded Images
# ------------------------

with st.expander("🖼 View Uploaded Images"):
    files = os.listdir(UPLOAD_DIR)
    image_files = [f for f in files if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if image_files:
        for image_name in sorted(image_files, reverse=True):
            st.image(os.path.join(UPLOAD_DIR, image_name), caption=image_name, use_column_width=True)
    else:
        st.write("No images uploaded yet.")
