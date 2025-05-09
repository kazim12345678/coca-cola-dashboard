import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Set your Google Sheet name
SPREADSHEET_NAME = "Production Dashboard Data"

# Define the required scopes for accessing Google Sheets and Google Drive
scope = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Load the service account details from Streamlit secrets.
# Ensure that your secrets.toml file has a [gcp_service_account] section containing your JSON credentials.
creds_info = st.secrets["gcp_service_account"]

# Create credentials using the service account information and the defined scopes.
creds = Credentials.from_service_account_info(creds_info, scopes=scope)

# Authorize the gspread client using these credentials.
client = gspread.authorize(creds)

try:
    # Open your spreadsheet and select the first worksheet.
    sheet = client.open(SPREADSHEET_NAME).sheet1
    # Fetch all records from the sheet.
    data = sheet.get_all_records()
    # Convert the data into a Pandas DataFrame for easier display and manipulation.
    df = pd.DataFrame(data)
    
    # Build the Streamlit UI.
    st.title("Production Dashboard")
    st.write("Data fetched from Google Sheets:")
    st.dataframe(df)
    
    # Optional: A refresh button to manually reload the app.
    if st.button("Refresh Data"):
        st.experimental_rerun()

except Exception as e:
    # Display any error that occurs in the app.
    st.error(f"Error fetching data: {e}")
