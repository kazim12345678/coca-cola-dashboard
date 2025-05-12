import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "Machine Counter Details"  # Updated Sheet Name

# Define authentication scopes (including write permissions)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
creds_info = st.secrets["gcp_service_account"]

# Create credentials using the service account info
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open(SPREADSHEET_NAME).sheet1

# -------------------------------------------------------------------
# AUTO-REFRESH FUNCTIONALITY
# -------------------------------------------------------------------
st_autorefresh(interval=60000, limit=100, key="datarefresh")  # Refresh every 60 seconds

# -------------------------------------------------------------------
# STREAMLIT FORM TO ENTER DATA
# -------------------------------------------------------------------
st.title("Submit Data to Google Sheets")

# User Input Fields
name = st.text_input("Enter your name:")
plant = st.selectbox("Select plant:", ["Plant A", "Plant B", "Plant C"])
production = st.number_input("Enter production count:", min_value=0)
remarks = st.text_area("Additional remarks (optional):")

# Submit Button
if st.button("Submit Data"):
    # Capture the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare data as a list
    new_row = [timestamp, name, plant, production, remarks]

    try:
        # Append data to Google Sheets
        sheet.append_row(new_row)
        st.success("✅ Data submitted successfully!")

    except Exception as e:
        st.error(f"❌ Error saving data: {e}")

# -------------------------------------------------------------------
# DISPLAY UPDATED DATA
# -------------------------------------------------------------------
st.subheader("Live Data from Google Sheets")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to reduce API calls
def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

df = load_data()
st.dataframe(df)

# -------------------------------------------------------------------
# MANUAL REFRESH BUTTON (OPTIONAL)
# -------------------------------------------------------------------
if st.button("Refresh Data"):
    st.experimental_rerun()
