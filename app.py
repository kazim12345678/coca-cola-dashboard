import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime
from io import BytesIO

# ---------- CONFIG ----------
st.set_page_config(page_title="Coca-Cola Production Dashboard", layout="wide")

DATA_FILE = 'production_data.json'

# ---------- LOAD EXISTING DATA ----------
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        all_data = json.load(f)
else:
    all_data = {}

# ---------- HEADER ----------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://1000logos.net/wp-content/uploads/2017/05/Coca-Cola-Logo-500x281.png", width=150)
with col2:
    st.title("Coca-Cola Plant Production Dashboard 🎯")
    st.markdown("Manage and visualize production data by line and plant.")

# ---------- INPUT SECTION ----------
plant_name = st.selectbox("Select Plant Name", ["Plant A", "Plant B", "Plant C"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3", "Line 4", "Line 5"])
key = f"{plant_name}_{line}"

# Initialize or load monthly data
if key in all_data:
    monthly_data = all_data[key]["data"]
else:
    monthly_data = {month: 0 for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}

# Monthly input fields
st.subheader("📅 Enter Monthly Production Data")
cols = st.columns(6)
months = list(monthly_data.keys())
for i, month in enumerate(months):
    monthly_data[month] = cols[i % 6].number_input(
        f"{month}", min_value=0, value=monthly_data[month], step=1
    )

# ---------- OPTIONAL IMAGE UPLOAD ----------
st.subheader("🖼️ Optional: Upload Image (e.g. line snapshot or report)")
uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])

# ---------- SAVE BUTTON ----------
if st.button("💾 Save Data"):
    all_data[key] = {
        "data": monthly_data,
        "image": uploaded_image.name if uploaded_image else None
    }
    with open(DATA_FILE, 'w') as f:
        json.dump(all_data, f, indent=4)
    st.success("✅ Data saved successfully!")

# ---------- VISUALIZATION ----------
df = pd.DataFrame({
    "Month": list(monthly_data.keys()),
    "Production": list(monthly_data.values())
})

tab1, tab2, tab3, tab4 = st.tabs(["📊 Bar Chart", "📈 Line Chart", "📉 Area Chart", "📌 Combined View"])

with tab1:
    st.subheader(f"Bar Chart - {plant_name} - {line}")
    fig = px.bar(df, x="Month", y="Production", color="Production", color_continuous_scale='reds')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Line Chart")
    fig = px.line(df, x="Month", y="Production", markers=True)
    fig.update_traces(line=dict(color='red', width=3))
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Area Chart")
    fig = px.area(df, x="Month", y="Production", color_discrete_sequence=['#FF0000'])
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Combined View")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=df["Month"], y=df["Production"], name="Monthly Production"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Month"], y=df["Production"].cumsum(), name="Cumulative", line=dict(color='red')), secondary_y=True)
    fig.update_layout(title_text=f"{plant_name} - {line} Combined View")
    fig.update_yaxes(title_text="Monthly", secondary_y=False)
    fig.update_yaxes(title_text="Cumulative", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

# ---------- METRICS ----------
st.divider()
st.subheader("🚀 Performance Metrics")
total = df["Production"].sum()
avg = df["Production"].mean()
peak_month = df.loc[df["Production"].idxmax(), "Month"]
peak_value = df["Production"].max()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Production", f"{total:,} units")
col2.metric("Monthly Average", f"{avg:,.0f} units")
col3.metric("Peak Month", f"{peak_month} ({peak_value:,})")
col4.metric("Efficiency", f"{(avg/df['Production'].max()*100):.1f}%" if df["Production"].max() else "0%")

# ---------- EXPORT ----------
st.subheader("📤 Export Data")
export_format = st.selectbox("Select export format", ["CSV", "Excel", "JSON"])
if st.button(f"Export as {export_format}"):
    filename = f"{plant_name}_{line}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if export_format == "CSV":
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name=f"{filename}.csv", mime="text/csv")
    elif export_format == "Excel":
        buffer = BytesIO()
        with pd.ExcelWriter(buffer) as writer:
            df.to_excel(writer, index=False)
        st.download_button("Download Excel", data=buffer.getvalue(), file_name=f"{filename}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        json_data = json.dumps({key: monthly_data}, indent=4)
        st.download_button("Download JSON", data=json_data, file_name=f"{filename}.json", mime="application/json")

# ---------- COMPARISON ----------
st.subheader("🔍 Compare with Another Line")
compare_key = st.selectbox("Select another Plant-Line to compare", [k for k in all_data.keys() if k != key])

if compare_key:
    comp_data = all_data[compare_key]["data"]
    compare_df = pd.DataFrame({
        "Month": list(comp_data.keys()),
        "Production": list(comp_data.values()),
        "Source": compare_key
    })
    df["Source"] = key
    combined_df = pd.concat([df, compare_df])
    
    fig = px.line(combined_df, x="Month", y="Production", color="Source",
                  title="Line Comparison", color_discrete_sequence=['red', 'blue'])
    st.plotly_chart(fig, use_container_width=True)

# ---------- IMAGE DISPLAY ----------
if key in all_data and all_data[key].get("image") and uploaded_image:
    st.subheader("📷 Uploaded Image Preview")
    st.image(uploaded_image, use_column_width=True)
