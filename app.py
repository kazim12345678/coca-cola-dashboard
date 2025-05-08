import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------
# Streamlit Page Configuration
# ---------------------------
st.set_page_config(page_title="Production Dashboard (Google Sheets)", layout="wide")
st.markdown("# Production Dashboard (Google Sheets)")

# ---------------------------
# Google Sheets Setup
# ---------------------------
SPREADSHEET_NAME = "Production Dashboard Data"  # Update with your sheet's name
CREDS_FILE = "credentials.json"  # Ensure the credentials file exists

# Define authentication scope and credentials
scope = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scope)
client = gspread.authorize(creds)

# Open the Google Sheet (first worksheet)
try:
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_records()
except Exception as e:
    st.error(f"Unable to open Google Sheet: {e}")
    st.stop()

# Convert data to Pandas DataFrame
df = pd.DataFrame(data)

# ---------------------------
# Data Display & Filtering
# ---------------------------
st.write("### Production Data Table")
st.dataframe(df)

# Filter Production Data by Plant and Line
plant_filter = st.sidebar.selectbox("Filter by Plant", df["Plant"].unique())
line_filter = st.sidebar.selectbox("Filter by Line", df["Line"].unique())

filtered_df = df[(df["Plant"] == plant_filter) & (df["Line"] == line_filter)]
st.write(f"### Filtered Production Data for Plant {plant_filter} - Line {line_filter}")
st.dataframe(filtered_df)

# ---------------------------
# Production Trend Visualization
# ---------------------------
st.write("### Production Trend Analysis")
fig = px.line(filtered_df, x="Date", y="Production", title=f"Production Trend - Plant {plant_filter}, Line {line_filter}")
fig.update_layout(transition_duration=500)
st.plotly_chart(fig, use_container_width=True)

st.write("🚀 Ready for Next Step: Connecting This Data to Our Main Dashboard")
