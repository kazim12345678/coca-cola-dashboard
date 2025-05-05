import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# --- Ensure data file exists ---
DATA_FILE = "data.csv"
UPLOAD_DIR = "uploads"

if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Plant", "Line", "Date", "Production"])
    df_init.to_csv(DATA_FILE, index=False)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- Load data ---
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()

# --- Title ---
st.title("📊 Coca-Cola Daily Production Tracker")

# --- Inputs ---
plant = st.selectbox("Select Plant", ["Plant A", "Plant B", "Plant C"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3"])

# Date selector: year, month, day
year = st.selectbox("Year", list(range(2023, 2026)))
month = st.selectbox("Month", list(range(1, 13)))
day = st.selectbox("Day", list(range(1, 32)))

# Validate and build date
try:
    selected_date = datetime(year, month, day)
except ValueError:
    st.error("Invalid date. Please select a valid combination of year, month, and day.")
    st.stop()

production = st.number_input("Enter Daily Production", min_value=0)

# Upload machine counter image
uploaded_image = st.file_uploader("Upload Machine Counter Image", type=["jpg", "png", "jpeg"])

# --- Save data ---
if st.button("💾 Save Entry"):
    # Save data row
    new_data = pd.DataFrame([{
        "Plant": plant,
        "Line": line,
        "Date": selected_date.strftime("%Y-%m-%d"),
        "Production": production
    }])
    new_data.to_csv(DATA_FILE, mode="a", header=not os.path.exists(DATA_FILE), index=False)

    # Save image
    if uploaded_image:
        filename = f"{UPLOAD_DIR}/{plant}_{line}_{selected_date.strftime('%Y-%m-%d')}_{uploaded_image.name}"
        with open(filename, "wb") as f:
            f.write(uploaded_image.getbuffer())

    st.success("✅ Data and image saved successfully!")

# --- View entries ---
st.subheader("📁 Uploaded Records")
if not df.empty:
    st.dataframe(df)

# Optional: Display uploaded images
with st.expander("🖼 View Uploaded Images"):
    for file in os.listdir(UPLOAD_DIR):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            st.image(os.path.join(UPLOAD_DIR, file), caption=file, use_column_width=True)
