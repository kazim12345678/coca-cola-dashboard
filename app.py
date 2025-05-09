import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import altair as alt
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------------
SPREADSHEET_NAME = "Production Dashboard Data"  # Your Google Sheet name

# Define scopes with write permissions to allow updates.
scope = [
    "https://www.googleapis.com/auth/spreadsheets",  # Full access to spreadsheets
    "https://www.googleapis.com/auth/drive.readonly"
]

# Load credentials from Streamlit secrets.
# Ensure your Streamlit Cloud secrets (secrets.toml) has a [gcp_service_account] entry.
creds_info = st.secrets["gcp_service_account"]

# Create credentials and authorize the gspread client.
creds = Credentials.from_service_account_info(creds_info, scopes=scope)
client = gspread.authorize(creds)

# -------------------------------------------------------------------
# AUTO-REFRESH SETUP (Refreshes every 60 seconds)
# -------------------------------------------------------------------
st_autorefresh(interval=60000, limit=100, key="datarefresh")

# -------------------------------------------------------------------
# DATA LOADING WITH CACHING (Cached for 30 seconds)
# -------------------------------------------------------------------
@st.cache_data(ttl=30)
def load_data():
    sheet = client.open(SPREADSHEET_NAME).sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

df = load_data()

# -------------------------------------------------------------------
# FUNCTION TO UPDATE GOOGLE SHEET WITH CSV DATA
# -------------------------------------------------------------------
def update_sheet_with_csv(new_df):
    sheet = client.open(SPREADSHEET_NAME).sheet1
    sheet.clear()  # Clear existing data
    # Prepare data: header row followed by the data rows.
    data_to_update = [new_df.columns.tolist()] + new_df.values.tolist()
    sheet.update("A1", data_to_update)

# -------------------------------------------------------------------
# SIDEBAR: CSV UPLOADER to Update the Google Sheet
# -------------------------------------------------------------------
st.sidebar.header("Update Google Sheet with CSV")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type="csv")
if uploaded_file is not None:
    try:
        df_csv = pd.read_csv(uploaded_file)
        st.sidebar.write("Preview of CSV Data:")
        st.sidebar.dataframe(df_csv.head())
        if st.sidebar.button("Update Google Sheet"):
            update_sheet_with_csv(df_csv)
            st.sidebar.success("Google Sheet updated!")
            # Rerun the app to load new data.
            st.experimental_rerun()
    except Exception as e:
        st.sidebar.error(f"Error processing CSV: {e}")

# -------------------------------------------------------------------
# SIDEBAR: Data Viewing Filters
# -------------------------------------------------------------------
st.sidebar.header("View Filters")
if "Plant" in df.columns:
    selected_plants = st.sidebar.multiselect(
        "Select Plants", options=df["Plant"].unique(), default=df["Plant"].unique()
    )
    filtered_df = df[df["Plant"].isin(selected_plants)]
else:
    filtered_df = df

# -------------------------------------------------------------------
# MAIN DASHBOARD: KPIs, Charts, and Data Table
# -------------------------------------------------------------------
st.title("Production Dashboard")

# Display KPIs in two columns (if column exists)
col1, col2 = st.columns(2)
if "Production" in filtered_df.columns:
    total_production = filtered_df["Production"].sum()
    average_production = round(filtered_df["Production"].mean(), 2)
    col1.metric("Total Production", total_production)
    col2.metric("Average Production", average_production)
else:
    col1.write("No Production column found")
    col2.write("No Production column found")

# Altair bar chart demonstration (if needed columns are available)
if "Plant" in filtered_df.columns and "Production" in filtered_df.columns:
    chart = alt.Chart(filtered_df).mark_bar().encode(
        x=alt.X('Plant:N', title="Plant"),
        y=alt.Y('Production:Q', title="Production"),
        tooltip=['Plant', 'Production']
    ).properties(title="Production by Plant")
    st.altair_chart(chart, use_container_width=True)

# Display the DataFrame
st.subheader("Production Data")
st.dataframe(filtered_df)

# Optional manual refresh button
if st.button("Refresh Data"):
    st.experimental_rerun()
