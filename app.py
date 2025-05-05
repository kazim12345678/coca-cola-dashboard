import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Production Dashboard", layout="wide")

st.title("📊 Coca-Cola Production Dashboard with Image Upload")

# Create folders if not exist
if not os.path.exists("images"):
    os.makedirs("images")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
    df.dropna(subset=["Date"], inplace=True)
    return df

df = load_data()

# --- Sidebar Selections ---
st.sidebar.header("Filters")
all_plants = df["Plant"].unique()
selected_plant = st.sidebar.selectbox("Select Plant", all_plants)

filtered_plant = df[df["Plant"] == selected_plant]
all_lines = filtered_plant["Line"].unique()
selected_line = st.sidebar.selectbox("Select Line", all_lines)

selected_year = st.sidebar.selectbox("Select Year", [2023, 2024, 2025])
selected_month = st.sidebar.selectbox("Select Month", list(range(1, 13)))

# --- Date Range Selection ---
days_in_month = 31 if selected_month in [1, 3, 5, 7, 8, 10, 12] else (29 if selected_month == 2 and selected_year % 4 == 0 else 30)
selected_day = st.sidebar.selectbox("Select Day", list(range(1, days_in_month + 1)))

selected_date = datetime(selected_year, selected_month, selected_day)

# --- Production Data Entry ---
st.subheader("🔧 Daily Production Entry")
new_production = st.number_input(f"Enter Production for {selected_date.date()} on Line {selected_line}", min_value=0)

if st.button("Update Production"):
    # Update or append production
    new_row = pd.DataFrame({
        "Plant": [selected_plant],
        "Line": [selected_line],
        "Date": [selected_date],
        "Production": [new_production]
    })

    df = df[df["Date"] != selected_date]  # Remove old record
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv("data.csv", index=False)
    st.success("✅ Production updated.")

# --- Image Upload ---
st.subheader("📷 Upload Machine Counter Image")
image_filename = f"{selected_plant}_{selected_line}_{selected_date.strftime('%Y-%m-%d')}.jpg"
uploaded_image = st.file_uploader("Upload Image (jpg, png only)", type=["jpg", "jpeg", "png"], key=image_filename)

if uploaded_image is not None:
    image_path = os.path.join("images", image_filename)
    with open(image_path, "wb") as f:
        f.write(uploaded_image.getbuffer())
    st.success(f"✅ Image saved for {selected_date.date()}.")
    st.image(image_path, caption="Uploaded Image", use_column_width=True)

# --- Display Table ---
st.subheader("📅 Monthly Production Overview")
df_filtered = df[(df["Plant"] == selected_plant) & (df["Line"] == selected_line)]
df_month = df_filtered[(df_filtered["Date"].dt.year == selected_year) & (df_filtered["Date"].dt.month == selected_month)]
st.dataframe(df_month.sort_values("Date"))
