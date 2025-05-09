import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configure your parameters
SPREADSHEET_NAME = "Production Dashboard Data"

# Set up authentication scopes for Sheets and Drive.
scope = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Load credentials from Streamlit secrets.
# This assumes your secrets.toml has a [gcp_service_account] section with your JSON credentials.
creds_info = st.secrets["gcp_service_account"]

# Create credentials using the secrets info.
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

try:
    # Fetch data from your Google Sheet.
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Display the data in the Streamlit app.
    st.title("Production Dashboard")
    st.write("Data fetched from Google Sheets:")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error fetching data: {e}")
