import streamlit as st
import pandas as pd
from io import BytesIO

# Set page config to full screen
st.set_page_config(layout="wide")

# Function to load data for preview (only first 1000 rows to avoid huge data loads)
@st.cache_data
def load_data_preview(file_path):
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path, nrows=1000)  # Only load a preview of 1000 rows
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, nrows=1000)  # Only load a preview of 1000 rows
    else:
        return None
    return df

# Function to load full data (for applying filters)
@st.cache_data
def load_full_data(file_path):
    if file_path.endswith('.xlsx'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        return None
    return df

# Function to filter data
def filter_data(df, filters):
    for col, value in filters.items():
        if value and col in df.columns:
            df = df[df[col].astype(str).str.contains(value, case=False, na=False)]
    return df

# Function to filter based on year range (specific to Dataset 1)
def filter_by_year(df, start_year, end_year):
    year_columns = [col for col in df.columns if col.isdigit()]
    year_columns = sorted(year_columns, key=int)
    selected_years = [year for year in year_columns if start_year <= int(year) <= end_year]
    return df[['Model', 'Scenario', 'Region', 'Variable', 'Unit'] + selected_years]

# Function to convert DataFrame to Excel for download
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    return processed_data

# Streamlit UI
st.title("Data Viewer and Exporter")

# Define tabs for multiple data sources
tabs = st.tabs(["AllData", "Dataset 2", "Dataset 3", "Dataset 4"])

# File paths and filter columns for different datasets
datasets_info = {
    "AllData": {
        "file_path": "C1-3_summary_2050_variable.csv",
        "filter_columns": ["Category", "Model", "Scenario", "Region", "Variable", "Unit"],
        "apply_year_filter": True
    },
    "Dataset 2": {
        "file_path": "AllData.csv",
        "filter_columns": ["Model", "Scenario", "Region", "Variable"],
        "apply_year_filter": False
    },
    "Dataset 3": {
        "file_path": "AllData3.csv",
        "filter_columns": ["Model", "Scenario", "Region"],
        "apply_year_filter": False
    },
    "Dataset 4": {
        "file_path": "AllData4.csv",
        "filter_columns": ["Model", "Scenario"],
        "apply_year_filter": False
    }
}

# Iterate over each tab and display corresponding data
for idx, tab in enumerate(tabs):
    dataset_name = list(datasets_info.keys())[idx]
    dataset_info = datasets_info[dataset_name]

    with tab:
        st.subheader(f"View and Filter {dataset_name}")
        
        # Load data preview (first 1000 rows only)
        file_path = dataset_info["file_path"]
        df_preview = load_data_preview(file_path)

        if df_preview is not None:
            st.write("### Data Preview")
            st.dataframe(df_preview.head())

            # Load full data for filtering purposes (without limiting to preview rows)
            df_full = load_full_data(file_path)

            # Filtering UI based on the full data columns (not preview)
            st.write("### Filter Data")
            filters = {}
            filter_columns = dataset_info["filter_columns"]
            cols = st.columns(len(filter_columns))

            for i, col in enumerate(filter_columns):
                if col in df_full.columns:
                    options = [""] + df_full[col].astype(str).unique().tolist()
                    filters[col] = cols[i].selectbox(f"{col}", options, key=f"{col}_{idx}")

            # Add year range filters for 'AllData' dataset or any dataset requiring year filtering
            if dataset_info["apply_year_filter"]:
                # Get list of years from the dataset
                year_columns = [col for col in df_full.columns if col.isdigit()]
                year_columns = sorted(year_columns, key=int)  # Sort years in ascending order

                # Dropdown for Start Year
                start_year = st.selectbox(
                    "Select Start Year:",
                    options=year_columns,
                    index=0,  # Default to the first year
                    key=f"start_year_{dataset_name}_{idx}"
                )

                # Dropdown for End Year
                end_year = st.selectbox(
                    "Select End Year:",
                    options=year_columns,
                    index=len(year_columns)-1,  # Default to the last year
                    key=f"end_year_{dataset_name}_{idx}"
                )

                # Ensure end year is greater than or equal to start year
                if int(end_year) < int(start_year):
                    st.error("End Year must be greater than or equal to Start Year.")
                    end_year = start_year

                # Filter data based on selected year range
                df_preview = filter_by_year(df_preview, int(start_year), int(end_year))

            # Button to load full data and apply filters
            if st.button("Apply Filters", key=f"apply_filters_{dataset_name}_{idx}"):
                # Apply year filter only for AllData (Dataset 1)
                filtered_df = filter_data(df_full, filters)

                # Apply year filter only for 'AllData'
                if dataset_info["apply_year_filter"]:
                    filtered_df = filter_by_year(filtered_df, int(start_year), int(end_year))

                # Show filtered data
                st.write("### Filtered Data")
                st.dataframe(filtered_df.head(100))

                # Button to download filtered data
                excel_data = to_excel(filtered_df)
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"{dataset_name}_filtered_data.xlsx",
                    mime="application/vnd.ms-excel",
                    key=f"download_button_{dataset_name}_{idx}"  # Ensure unique key for download button
                )
        else:
            st.error("Error loading data preview.")