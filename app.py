import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "Machine Counter Details"  # Google Sheets file name

# Define authentication scopes (including write permissions)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit secrets
creds_info = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# Open the spreadsheet and both sheets
spreadsheet = client.open(SPREADSHEET_NAME)
sheet1 = spreadsheet.worksheet("Sheet1")
sheet2 = spreadsheet.worksheet("Sheet2")

# -------------------------------------------------------------------
# AUTO-REFRESH FUNCTIONALITY
# -------------------------------------------------------------------
st_autorefresh(interval=60000, limit=100, key="datarefresh")  # Refresh every 60 seconds

# -------------------------------------------------------------------
# STREAMLIT FORM TO ENTER MACHINE COUNTER DATA (Sheet1)
# -------------------------------------------------------------------
st.title("Submit Data to Sheet1")

date = st.date_input("Select Date")
date_str = date.strftime("%Y-%m-%d")  # Convert date to string
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
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for Sheet1
    new_row_sheet1 = [timestamp, date_str, blowing_counter, filler_counter, labeller_counter, tra_counter,
                      kister_counter, palatizer_counter, actual_transfer, difference, comments]
    
    # Prepare data for Sheet2
    OEE = actual_transfer / 79992  # Calculate OEE
    new_row_sheet2 = [date_str, actual_transfer, OEE]
    
    try:
        # Append data to Sheet1
        sheet1.append_row(new_row_sheet1)
        # Append corresponding data to Sheet2
        sheet2.append_row(new_row_sheet2)
        
        st.success("✅ Data submitted successfully! (Sheet1 and Sheet2 updated)")
    
    except Exception as e:
        st.error(f"❌ Error saving data: {e}")

# -------------------------------------------------------------------
# DISPLAY LIVE DATA FROM BOTH SHEETS
# -------------------------------------------------------------------
st.subheader("Live Data from Sheet1")

@st.cache_data(ttl=30)
def load_data(sheet):
    try:
        data = sheet.get_all_records()
        if not data:
            return pd.DataFrame(columns=["Timestamp", "Date", "Blowing Counter", "Filler Counter",
                                         "Labeller Counter", "TRA Counter", "Kister Counter",
                                         "Palatizer Counter", "Actual Production Transfer",
                                         "Difference", "Comments"])
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

df_sheet1 = load_data(sheet1)
st.dataframe(df_sheet1)

st.subheader("Live Data from Sheet2")

df_sheet2 = load_data(sheet2)
st.dataframe(df_sheet2)

# -------------------------------------------------------------------
# MANUAL REFRESH BUTTON (OPTIONAL)
# -------------------------------------------------------------------
if st.button("Refresh Data"):
    st.experimental_rerun()
