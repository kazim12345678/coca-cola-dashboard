import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime

# File to store data
DATA_FILE = 'production_data.json'

# Load existing data if file exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        all_data = json.load(f)
else:
    all_data = {}

# --- UI SECTION ---
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

# Coca-Cola branding
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://1000logos.net/wp-content/uploads/2017/05/Coca-Cola-Logo-500x281.png", width=150)
with col2:
    st.title("Coca-Cola Plant Production Dashboard 🎯")
    st.markdown("Manage and visualize production data by line and plant.")

# Input: plant and line
plant_name = st.selectbox("Select Plant Name", ["Plant A", "Plant B", "Plant C"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"])

# Unique key for saving data
key = f"{plant_name}_{line}"

# Initialize or load monthly data
if key in all_data:
    monthly_data = all_data[key]
else:
    monthly_data = {month: 0 for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}

# Show input fields for each month
st.subheader("Enter Monthly Production Data (in units)")
cols = st.columns(6)
months = list(monthly_data.keys())
for i, month in enumerate(months):
    monthly_data[month] = cols[i % 6].number_input(
        f"{month}", min_value=0, value=monthly_data[month], step=1)

# Save button
if st.button("💾 Save Data"):
    all_data[key] = monthly_data
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("Data saved successfully!")

# Create dataframe
df = pd.DataFrame({
    "Month": list(monthly_data.keys()),
    "Production": list(monthly_data.values())
})

# --- NEW VISUALIZATIONS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Chart", "📈 Line Chart", "📉 Area Chart", "📌 Combined View"])

with tab1:
    st.subheader(f"Production Trend for {plant_name} - {line}")
    fig_bar = px.bar(df, x="Month", y="Production", 
                    title=f"{plant_name} - {line} Production",
                    color="Production", 
                    color_continuous_scale='reds')
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.subheader(f"Monthly Trend Line")
    fig_line = px.line(df, x="Month", y="Production", 
                      title=f"Monthly Production Trend",
                      markers=True)
    fig_line.update_traces(line=dict(color='red', width=3))
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    st.subheader(f"Production Area")
    fig_area = px.area(df, x="Month", y="Production",
                      title=f"Production Volume",
                      color_discrete_sequence=['#FF0000'])
    st.plotly_chart(fig_area, use_container_width=True)

with tab4:
    st.subheader(f"Combined Analysis")
    fig_combined = make_subplots(specs=[[{"secondary_y": False}]])
    
    fig_combined.add_trace(
        go.Bar(x=df["Month"], y=df["Production"], name="Monthly Production"),
        secondary_y=False,
    )
    
    fig_combined.add_trace(
        go.Scatter(x=df["Month"], y=df["Production"].cumsum(), 
                  name="Cumulative Production", line=dict(color='red')),
        secondary_y=True,
    )
    
    fig_combined.update_layout(
        title_text=f"{plant_name} - {line} Comprehensive View"
    )
    fig_combined.update_yaxes(title_text="Monthly Production", secondary_y=False)
    fig_combined.update_yaxes(title_text="Cumulative Production", secondary_y=True)
    
    st.plotly_chart(fig_combined, use_container_width=True)

# --- NEW FEATURES ---
st.divider()

# 1. Performance Metrics
st.subheader("🚀 Performance Metrics")
total = df["Production"].sum()
avg = df["Production"].mean()
peak_month = df.loc[df["Production"].idxmax(), "Month"]
peak_value = df["Production"].max()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Production", f"{total:,} units")
col2.metric("Monthly Average", f"{avg:,.0f} units")
col3.metric("Peak Month", f"{peak_month} ({peak_value:,})")
col4.metric("Efficiency", f"{(avg/df['Production'].max()*100):.1f}%")

# 2. Data Export
st.subheader("📤 Export Data")
export_format = st.selectbox("Select format", ["CSV", "Excel", "JSON"])

if st.button(f"Export as {export_format}"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"cocacola_production_{plant_name}_{line}_{timestamp}"
    
    if export_format == "CSV":
        data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=data,
            file_name=f"{filename}.csv",
            mime="text/csv"
        )
    elif export_format == "Excel":
        data = df.to_excel(index=False)
        st.download_button(
            label="Download Excel",
            data=data,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        data = json.dumps({key: monthly_data}, indent=4)
        st.download_button(
            label="Download JSON",
            data=data,
            file_name=f"{filename}.json",
            mime="application/json"
        )

# 3. Comparison View
st.subheader("🔍 Compare Plants/Lines")
compare_key = st.selectbox("Select another line to compare", 
                          [k for k in all_data.keys() if k != key])

if compare_key and compare_key in all_data:
    compare_df = pd.DataFrame({
        "Month": list(all_data[compare_key].keys()),
        "Production": list(all_data[compare_key].values()),
        "Source": compare_key
    })
    
    df["Source"] = key
    combined_df = pd.concat([df, compare_df])
    
    fig_compare = px.line(combined_df, x="Month", y="Production", 
                         color="Source", title="Production Comparison",
                         color_discrete_sequence=['red', 'blue'])
    st.plotly_chart(fig_compare, use_container_width=True)