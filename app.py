import streamlit as st
import pandas as pd
import os
import uuid
import calendar
import plotly.express as px
from datetime import datetime, date

# Constants
DATA_FILE = "data.csv"
IMAGE_FOLDER = "images"
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]

# Ensure image directory exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

st.set_page_config(page_title="Coca-Cola Dashboard", layout="wide")
st.title("📊 Coca-Cola Production Dashboard & 📸 Daily Uploads")

# Load CSV data if available
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df.dropna(subset=["Date"])
    return pd.DataFrame(columns=["Date", "Plant", "Line", "Production"])

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("📅 Filter by Date")

today = date.today()
year = st.sidebar.selectbox("Select Year", list(range(2023, today.year + 1)), index=len(range(2023, today.year + 1)) - 1)
month = st.sidebar.selectbox("Select Month", list(calendar.month_name)[1:], index=today.month - 1)

# Filter data by year and month
df_filtered = df[(df["Date"].dt.year == year) & (df["Date"].dt.month == list(calendar.month_name).index(month))]

# --- Graph Section ---
if not df_filtered.empty:
    st.subheader(f"📈 Production Trend for {month} {year}")
    fig = px.line(df_filtered, x="Date", y="Production", color="Line", markers=True, title="Daily Production")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No production data available for selected month and year.")

# --- Image Upload Section ---
st.markdown("---")
st.header("📸 Upload Daily Machine Counter")

plant = st.selectbox("Select Plant", ["Plant 1", "Plant 2", "Plant 3"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3"])
selected_date = st.date_input("Select Date", value=today)
uploaded_image = st.file_uploader("Upload Counter Image", type=["jpg", "jpeg", "png"])

if st.button("Upload Image"):
    if uploaded_image is not None:
        try:
            ext = os.path.splitext(uploaded_image.name)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                st.error("❌ Invalid file type. Only .jpg, .jpeg, and .png are allowed.")
            else:
                unique_name = f"{plant}_{line}_{selected_date.strftime('%Y-%m-%d')}_{uuid.uuid4().hex}{ext}"
                image_path = os.path.join(IMAGE_FOLDER, unique_name)

                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())

                st.success(f"✅ Image saved: {unique_name}")
        except Exception as e:
            st.error(f"🚫 Upload failed: {e}")
    else:
        st.warning("⚠️ Please upload a file before submitting.")

# --- View Uploaded Images ---
with st.expander("📁 View Uploaded Images"):
    image_files = sorted(os.listdir(IMAGE_FOLDER), reverse=True)
    if image_files:
        for img in image_files:
            st.image(os.path.join(IMAGE_FOLDER, img), caption=img, use_column_width=True)
    else:
        st.info("No images uploaded yet.")
