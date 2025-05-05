import streamlit as st
import pandas as pd
import os
from datetime import date
import uuid

# Set page config
st.set_page_config(page_title="Coca-Cola Dashboard", layout="wide")

# Create upload directory if it doesn't exist
UPLOAD_DIR = "images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("📸 Daily Machine Counter Upload System")

# Plant and Line Selection
plant = st.selectbox("Select Plant", ["Plant 1", "Plant 2", "Plant 3"])
line = st.selectbox("Select Line", ["Line 1", "Line 2", "Line 3"])

# Date Selection using Calendar Input
selected_date = st.date_input("Select Date", value=date.today(),
                              min_value=date(2023, 1, 1), max_value=date(2025, 12, 31))

# Image Uploader
uploaded_image = st.file_uploader("Upload Machine Counter Image", type=["jpg", "jpeg", "png"])

# Submit button
if st.button("Save Entry"):
    if uploaded_image is not None:
        # Ensure valid file extension
        ext = os.path.splitext(uploaded_image.name)[1].lower()
        # Generate unique and safe filename
        unique_filename = f"{plant}_{line}_{selected_date.strftime('%Y-%m-%d')}_{uuid.uuid4().hex}{ext}"
        image_path = os.path.join(UPLOAD_DIR, unique_filename)

        # Save file
        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

        st.success(f"✅ Image saved successfully: {unique_filename}")
    else:
        st.warning("⚠️ Please upload an image before saving.")

# Optional: Display uploaded images (for confirmation)
if st.checkbox("Show Uploaded Images"):
    images = os.listdir(UPLOAD_DIR)
    if images:
        for img_file in sorted(images, reverse=True):
            st.image(os.path.join(UPLOAD_DIR, img_file), caption=img_file, use_column_width=True)
    else:
        st.info("No images uploaded yet.")
