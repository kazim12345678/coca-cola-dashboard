import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "Machine Counter Details"  # Ensure correct sheet name

# Define authentication scopes (with write permissions)
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
# STREAMLIT FORM TO ENTER MACHINE COUNTER DATA
# -------------------------------------------------------------------
st.title("Machine Counter Entry Form")

# User Input Fields
date = st.date_input("Select Date")
date_str = date.strftime("%Y-%m-%d")  # Convert date to string before submitting
blowing_counter = st.number_input("Blowing Counter", min_value=0)
filler_counter = st.number_input("Filler Counter", min_value=0)
labeller_counter = st.number_input("Labeller Counter", min_value=0)
tra_counter = st.number_input("TRA Counter", min_value=0)
kister_counter = st.number_input("Kister Counter", min_value=0)
palatizer_counter = st.number_input("Palatizer Counter", min_value=0)
actual_transfer = st.number_input("Actual Production Transfer", min_value=0)
comments = st.text_area("Additional Comments (Optional)")

# Automatically calculate the difference between Palatizer Counter and Actual Transfer
difference = palatizer_counter - actual_transfer

# Submit Button
if st.button("Submit Data"):
    # Capture current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare data as a list
    new_row = [timestamp, date_str, blowing_counter, filler_counter, labeller_counter, tra_counter,
               kister_counter, palatizer_counter, actual_transfer, difference, comments]

    try:
        # Append data to Google Sheets
        sheet.append_row(new_row)
        st.success("✅ Data submitted successfully!")

    except Exception as e:
        st.error(f"❌ Error saving data: {e}")

# -------------------------------------------------------------------
# DISPLAY LIVE DATA FROM GOOGLE SHEETS
# -------------------------------------------------------------------
st.subheader("Live Machine Counter Data")

@st.cache_data(ttl=30)  # Cache data for 30 seconds to reduce API calls
def load_data():
    try:
        data = sheet.get_all_records()
        if not data:  # If Google Sheets is empty, create a default table structure
            return pd.DataFrame(columns=["Timestamp", "Date", "Blowing Counter", "Filler Counter", 
                                         "Labeller Counter", "TRA Counter", "Kister Counter",
                                         "Palatizer Counter", "Actual Production Transfer",
                                         "Difference", "Comments"])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

df = load_data()
st.dataframe(df)

# -------------------------------------------------------------------
# MANUAL REFRESH BUTTON (OPTIONAL)
# -------------------------------------------------------------------
if st.button("Refresh Data"):
    st.experimental_rerun()
