import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
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
sheet = spreadsheet.sheet1

# -------------------------------------------------------------------
# AUTO-REFRESH FUNCTIONALITY
# -------------------------------------------------------------------
st_autorefresh(interval=60000, limit=100, key="datarefresh")  # Refresh every 60 seconds

# -------------------------------------------------------------------
# STREAMLIT FORM TO UPDATE MAINTENANCE CHECKLIST
# -------------------------------------------------------------------
st.title(f"Update Air Compressor Checklist")

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

# Find the row number for the selected task
task_rows = {
    "DISMANTLE, CHECK AND CLEAN VALVES": 2,
    "CLEAN AIR GOVERNOR": 3,
    "CHECK ALL BOLTS AND NUTS": 4,
    "CHECK UNLOADED PISTON OPERATION": 5
}
row_number = task_rows[task]

# Find the column number for the selected month
month_columns = {
    "JAN": 2, "FEB": 3, "MAR": 4, "APR": 5, "MAY": 6, "JUNE": 7,
    "JULY": 8, "AUG": 9, "SEPT": 10, "OCT": 11, "NOV": 12, "DEC": 13
}
column_number = month_columns[month]

# Submit Button
if st.button("Update Checklist"):
    try:
        # Update the checklist in Google Sheets
        sheet.update_cell(row_number, column_number, f"{operator_signature} | {shift_engineer_signature}")
        st.success(f"✅ Maintenance task updated for {month}!")
    except Exception as e:
        st.error(f"❌ Error updating checklist: {e}")

# -------------------------------------------------------------------
# DISPLAY CHECKLIST FROM GOOGLE SHEETS
# -------------------------------------------------------------------
st.subheader(f"Live Checklist from {SPREADSHEET_NAME}")

data = sheet.get_all_values()
for row in data:
    st.write(row)

# -------------------------------------------------------------------
# MANUAL REFRESH BUTTON (OPTIONAL)
# -------------------------------------------------------------------
if st.button("Refresh Data"):
    st.experimental_rerun()
