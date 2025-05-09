import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Configure your parameters
SPREADSHEET_NAME = "Production Dashboard Data"
CREDS_FILE = r"C:\Users\Lenovo\Documents\google_sheets_project\credentials.json"

# Set up authentication scopes
scope = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Authenticate and create a client
creds = Credentials.from_service_account_file(CREDS_FILE, scopes=scope)
client = gspread.authorize(creds)

try:
    # Fetch data from your Google Sheet
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # Display the data in a Streamlit app
    st.title("Production Dashboard")
    st.write("Data fetched from Google Sheets:")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error fetching data: {e}")
