import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "Production Dashboard Data"  # Update if needed

# Define scopes for Google Sheets and Drive access
scope = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Load credentials from Streamlit secrets.
# Make sure your secrets.toml (or Streamlit Cloud secrets) has a [gcp_service_account] section.
creds_info = st.secrets["gcp_service_account"]

# Create credentials using the service account info and scopes
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# -------------------------------------------------------------------
# AUTO-REFRESH SETUP
# -------------------------------------------------------------------
# Automatically refresh the app every 60 seconds (60000 ms)
st_autorefresh(interval=60000, limit=100, key="datarefresh")

# -------------------------------------------------------------------
# DATA LOADING WITH CACHING (Refreshes every 30 seconds)
# -------------------------------------------------------------------
@st.cache_data(ttl=30)
def load_data():
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

df = load_data()

# -------------------------------------------------------------------
# INTERACTIVE FILTERS IN THE SIDEBAR
# -------------------------------------------------------------------
st.sidebar.header("Filters")
if "Plant" in df.columns:
    selected_plants = st.sidebar.multiselect(
        "Select Plants", options=df["Plant"].unique(), default=df["Plant"].unique()
    )
    filtered_df = df[df["Plant"].isin(selected_plants)]
else:
    filtered_df = df

# -------------------------------------------------------------------
# ENHANCED UI: KPIs, CHARTS, AND DATA TABLE
# -------------------------------------------------------------------
st.title("Production Dashboard")

# Display KPIs in columns if the columns exist
col1, col2 = st.columns(2)
if "Production" in filtered_df.columns:
    total_production = filtered_df["Production"].sum()
    average_production = round(filtered_df["Production"].mean(), 2)
    col1.metric("Total Production", total_production)
    col2.metric("Average Production", average_production)
else:
    col1.write("No Production column found")
    col2.write("No Production column found")

# Visualize data with an Altair bar chart (if the expected columns exist)
if "Plant" in filtered_df.columns and "Production" in filtered_df.columns:
    chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('Plant:N', title="Plant"),
        y=alt.Y('Production:Q', title="Production"),
        tooltip=['Plant', 'Production']
    ).properties(title="Production by Plant")
    st.altair_chart(chart, use_container_width=True)

# Display the filtered data table
st.subheader("Production Data")
st.dataframe(filtered_df)

# A manual refresh button (optional)
if st.button("Refresh Data"):
    st.experimental_rerun()
