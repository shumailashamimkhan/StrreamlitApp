# Imports
# Imports
from io import BytesIO
import streamlit as st
import pandas as pd
import openpyxl
import os

# Setup our App
st.set_page_config(page_title="📀 Data Sweeper", layout="wide")
st.title("📀 Data Sweeper")
st.write("Transform your file between CSV and Excel formats with built-in data cleaning and visualization!")

# File upload
upload_files = st.file_uploader("Upload your files (CSV or Excel):", type=['csv', 'xlsx'], accept_multiple_files=True)

df = None  # Initialize df before the loop

if upload_files:
    for file in upload_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        if file_ext == '.csv':
            df = pd.read_csv(file)
        elif file_ext == '.xlsx':
            df = pd.read_excel(file, engine="openpyxl") 
        else:
            st.error(f"Unsupported file type: {file_ext}")
            continue

        # ✅ Ensure df is not empty
        if df is None or df.empty:
            st.warning(f"The uploaded file {file.name} is empty or could not be read.")
            continue  # Skip to the next file

        # Display file info
        st.write(f"**File Name:** {file.name}")
        st.write(f"**File Size:** {round(file.size / 1024, 2)} KB")

        # Show the first 5 rows of df
        st.write("Preview the Head of the DataFrame")
        st.dataframe(df)

        # Option for Data Cleaning
        st.subheader("Data Cleaning Options")
        if st.checkbox(f"Clean data for {file.name}"):
            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"Remove Duplicates for {file.name}"):
                    df.drop_duplicates(inplace=True)
                    st.write("Duplicates Removed!")

            with col2:
                if st.button(f"Fill Missing Values for {file.name}"):
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    st.write("Missing Values have been filled!")

        # Choose the specific Columns to keep or Convert 
        st.header("Select the Columns to Convert")
        columns = st.multiselect(f"Choose Columns for {file.name}", df.columns, default=df.columns)
        df = df[columns]

        # Create Some Visualization
        st.subheader("📊 Data Visualization")
        if st.checkbox(f"Show Visualization for {file.name}"):
            st.bar_chart(df.select_dtypes(include="number").iloc[:, :2])

        # Convert the file CSV to Excel
        st.subheader("OptiConvert Options")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=file.name)

        if st.button(f"Convert {file.name}"):
            buffer = BytesIO()
            if conversion_type == "CSV":
                df.to_csv(buffer, index=False)
                file_name = file.name.replace(file_ext, ".csv")
                mime_type = "text/csv"

            elif conversion_type == "Excel":
                df.to_excel(buffer, index=False, engine="openpyxl")
                file_name = file.name.replace(file_ext, ".xlsx")
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            buffer.seek(0)

            # ✅ Download Button (inside button block)
            st.download_button(
                label=f"⏬ Download {file.name} as {conversion_type}",
                data=buffer,
                file_name=file_name,
                mime=mime_type
            )

    # ✅ Corrected success message
    st.success("🎉 All Files Processed")