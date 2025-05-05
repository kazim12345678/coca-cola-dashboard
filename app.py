import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide")

# ------------------ Simulated Data ------------------
data = {
    'Date': pd.date_range(start='2023-01-01', periods=365, freq='D'),
    'Production': [int(x) for x in abs(1000 + 500 * pd.Series(range(365)).apply(lambda x: x % 10).astype(int))],
    'Plant': ['Plant A'] * 365,
    'Line': ['Line 1'] * 365
}
df_daily = pd.DataFrame(data)
df_daily["Date"] = pd.to_datetime(df_daily["Date"])

# ------------------ Sidebar Filters ------------------
st.sidebar.header("Filters")
plant = st.sidebar.selectbox("Select Plant", df_daily['Plant'].unique())
line = st.sidebar.selectbox("Select Line", df_daily['Line'].unique())
year = st.sidebar.selectbox("Select Year", list(range(2023, 2026)))

# ------------------ Filter Data ------------------
df_filtered = df_daily[(df_daily['Plant'] == plant) & (df_daily['Line'] == line)]
df_year = df_filtered[df_filtered["Date"].dt.year == year]
df_month = df_year.copy()
df_month["Month"] = df_month["Date"].dt.strftime("%B")

# ------------------ Monthly Aggregation ------------------
df_summary = df_month.groupby("Month")["Production"].sum().reindex(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"]
).reset_index()

# ------------------ Tabs ------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Monthly View", "🗓 Daily Entry", "📁 Upload Photo", "📈 Combined"])

# ------------------ Tab 1: Monthly View ------------------
with tab1:
    st.subheader(f"Monthly Production Summary - {plant} - {line} - {year}")
    st.bar_chart(data=df_summary, x="Month", y="Production")

# ------------------ Tab 2: Daily Entry ------------------
with tab2:
    st.subheader("Daily Production Entry")
    selected_month = st.selectbox("Month", df_month["Month"].unique())
    selected_day = st.selectbox("Day", range(1, 32))
    try:
        date_str = f"{year}-{datetime.strptime(selected_month, '%B').month:02d}-{selected_day:02d}"
        selected_date = pd.to_datetime(date_str)
    except ValueError:
        st.error("Invalid date")
        selected_date = None

    if selected_date:
        production_input = st.number_input("Enter Production", min_value=0, step=10)
        if st.button("Save Daily"):
            if selected_date in df_daily["Date"].values:
                df_daily.loc[df_daily["Date"] == selected_date, "Production"] = production_input
                st.success(f"Updated production for {selected_date.date()} to {production_input}")
            else:
                new_entry = pd.DataFrame({
                    "Date": [selected_date],
                    "Production": [production_input],
                    "Plant": [plant],
                    "Line": [line]
                })
                df_daily = pd.concat([df_daily, new_entry], ignore_index=True)
                st.success(f"Added production entry for {selected_date.date()}")

# ------------------ Tab 3: Photo Upload ------------------
with tab3:
    st.subheader("📷 Upload Machine Counter Photo")

    base_folder = "uploads"
    plant_folder = os.path.join(base_folder, plant.replace(" ", "_"))
    line_folder  = os.path.join(plant_folder, line.replace(" ", "_"))
    date_folder  = os.path.join(line_folder, date_str)

    os.makedirs(date_folder, exist_ok=True)

    uploaded_file = st.file_uploader("Choose an image file (PNG/JPG)", type=["png", "jpg", "jpeg"], key="uploader")

    if uploaded_file:
        save_path = os.path.join(date_folder, uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"Saved image to {save_path}")

    st.markdown(f"**Photos for {date_str}:**")
    if os.path.isdir(date_folder):
        imgs = os.listdir(date_folder)
        if imgs:
            cols = st.columns(3)
            for i, img_name in enumerate(imgs):
                img_path = os.path.join(date_folder, img_name)
                with cols[i % 3]:
                    st.image(img_path, use_column_width=True, caption=img_name)
        else:
            st.info("No photos uploaded for this date yet.")

# ------------------ Tab 4: Combined Analysis ------------------
with tab4:
    st.subheader(f"Combined Analysis for {plant} – {line}")
    fig_combined = make_subplots(
        specs=[[{"secondary_y": True}]],
        subplot_titles=[f"{plant} - {line} Comprehensive View"]
    )

    fig_combined.add_trace(
        go.Bar(
            x=df_summary["Month"],
            y=df_summary["Production"],
            name="Monthly Production",
            marker_color='crimson'
        ),
        secondary_y=False,
    )

    fig_combined.add_trace(
        go.Scatter(
            x=df_summary["Month"],
            y=df_summary["Production"].cumsum(),
            name="Cumulative Production",
            mode='lines+markers',
            line=dict(color='orange')
        ),
        secondary_y=True,
    )

    fig_combined.update_xaxes(title_text="Month")
    fig_combined.update_yaxes(title_text="Monthly Production", secondary_y=False)
    fig_combined.update_yaxes(title_text="Cumulative Production", secondary_y=True)

    fig_combined.update_layout(
        title_text=f"{plant} - {line} Comprehensive View",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig_combined, use_container_width=True)
