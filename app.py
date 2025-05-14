import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "AIR COMPRESSOR MONTHLY CHECK LIST"  # Correct file name

# Define authentication scopes (including write permissions)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
creds_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# Open the spreadsheet
spreadsheet = client.open(SPREADSHEET_NAME)
sheet = spreadsheet.sheet1  # Ensure this is the correct sheet tab

# -------------------------------------------------------------------
# AUTO-REFRESH FUNCTIONALITY
# -------------------------------------------------------------------
st_autorefresh(interval=60000, limit=100, key="datarefresh")  # Refresh every 60 seconds

# -------------------------------------------------------------------
# STREAMLIT FORM TO ENTER COMPRESSOR MAINTENANCE DATA
# -------------------------------------------------------------------
st.title(f"Submit Air Compressor Maintenance Data")

date = st.date_input("Select Date")
date_str = date.strftime("%Y-%m-%d")  # Convert date to string
task = st.selectbox("Select Task", ["DISMANTLE, CHECK AND CLEAN VALVES",
                                    "CLEAN AIR GOVERNOR",
                                    "CHECK ALL BOLTS AND NUTS",
                                    "CHECK UNLOADED PISTON OPERATION"])
month = st.selectbox("Select Month", ["JAN", "FEB", "MAR", "APR", "MAY", "JUNE",
                                      "JULY", "AUG", "SEPT", "OCT", "NOV", "DEC"])
operator_signature = st.text_input("Operator Signature")
shift_engineer_signature = st.text_input("Shift Engineer Signature")
comments = st.text_area("Additional Comments (Optional)")

# Submit Button
if st.button("Submit Data"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [timestamp, date_str, task, month, operator_signature, shift_engineer_signature, comments]
    try:
        sheet.append_row(new_row)
        st.success(f"✅ Data submitted successfully to {SPREADSHEET_NAME}!")
    except Exception as e:
        st.error(f"❌ Error saving data: {e}")

# -------------------------------------------------------------------
# DISPLAY LIVE DATA FROM GOOGLE SHEETS
# -------------------------------------------------------------------
st.subheader(f"Live Maintenance Data from {SPREADSHEET_NAME}")

@st.cache_data(ttl=30)
def load_data(sheet):
    try:
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Timestamp", "Date", "Task", "Month",
                                         "Operator Signature", "Shift Engineer Signature",
                                         "Comments"])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

df = load_data(sheet)
st.dataframe(df)

# -------------------------------------------------------------------
# MANUAL REFRESH BUTTON (OPTIONAL)
# -------------------------------------------------------------------
if st.button("Refresh Data"):
    st.experimental_rerun()
