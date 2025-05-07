import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ---------- SETUP GOOGLE SHEET ----------
creds_dict = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open("Production Dashboard Data").sheet1

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Coca-Cola Dashboard", layout="wide")
st.title("🥤 A. One Production Dashboard")

# ---------- CONSTANTS ----------
plants = ['Lahore', 'B', 'C', 'D', 'E', 'F']
lines = [1, 2, 3, 4, 5]
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
current_year = datetime.now().year
years = [str(y) for y in range(2023, current_year + 1)]

# ---------- LOAD DATA FROM SHEET ----------
@st.cache_data
def load_data():
    records = sheet.get_all_records()
    return pd.DataFrame(records)

df = load_data()

# ---------- FILTERING ----------
year = st.selectbox("Select Year", years)
st.markdown(f"**Editing data for year {year}**")

st.subheader("✏️ Edit Monthly Production")
col1, col2, col3 = st.columns(3)
with col1:
    plant = st.selectbox("Plant", plants)
with col2:
    line = st.selectbox("Line", lines)
with col3:
    month = st.selectbox("Month", months)

# Get current value from DataFrame
mask = (
    (df['Year'] == int(year)) &
    (df['Plant'] == plant) &
    (df['Line'] == int(line)) &
    (df['Month'] == month)
)
existing_rows = df[mask]
current_val = int(existing_rows['Production'].values[0]) if not existing_rows.empty else 0

# Input new value
new_val = st.number_input(
    f"Production for {plant} Line {line} in {month} {year}",
    min_value=0, value=current_val, step=1
)

# ---------- SAVE ----------
if st.button("💾 Save"):
    if not existing_rows.empty:
        # Update existing row
        cell = sheet.find(str(year))
        for i in range(cell.row, sheet.row_count + 1):
            row = sheet.row_values(i)
            if row and row[0] == str(year) and row[1] == plant and row[2] == str(line) and row[3] == month:
                sheet.update_cell(i, 5, str(new_val))
                st.success("✅ Data updated successfully!")
                st.cache_data.clear()
                st.rerun()
                break
    else:
        # Insert new row
        sheet.append_row([year, plant, line, month, new_val])
        st.success("✅ New data saved successfully!")
        st.cache_data.clear()
        st.rerun()

# ---------- PLOTS ----------
df_filtered = df[df['Year'] == int(year)]

# Line-level trend
st.subheader(f"📈 {plant} Line {line} - Monthly Trend")
line_data = df_filtered[(df_filtered['Plant'] == plant) & (df_filtered['Line'] == int(line))]
line_data = line_data.set_index('Month').reindex(months).reset_index()
line_data['Production'] = line_data['Production'].fillna(0)
fig_line = px.line(line_data, x="Month", y="Production", markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# Plant-level total
st.header("🌱 Plant-Level Total Production")
plant_totals = df_filtered.groupby("Plant")["Production"].sum().reset_index()
st.bar_chart(plant_totals.set_index("Plant"))

# Line-level breakdown
st.header("📊 Line-Level Breakdown")
line_totals = df_filtered.groupby(["Plant", "Line"])["Production"].sum().reset_index()
st.dataframe(line_totals)
