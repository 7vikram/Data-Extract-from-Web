import streamlit as st
import pandas as pd
from io import BytesIO
from st_aggrid import AgGrid



# Set page config to full screen
st.set_page_config(layout="wide")

# Load data from backend (cached to avoid re-reading)
@st.cache_data
def load_data_from_backend(file_path):
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
        
        df = load_data_from_backend(dataset_info["file_path"])

        if df is not None:
            st.write("### Data Preview")
            st.dataframe(df.head())

            # Filtering UI
            st.write("### Filter Data")
            filters = {}
            filter_columns = dataset_info["filter_columns"]
            cols = st.columns(len(filter_columns))

            for i, col in enumerate(filter_columns):
                if col in df.columns:
                    options = [""] + df[col].astype(str).unique().tolist()
                    filters[col] = cols[i].selectbox(f"{col}", options, key=f"{col}_{idx}")

            filtered_df = filter_data(df, filters)

            # Apply year filter only for AllData (Dataset 1)
            if dataset_info["apply_year_filter"]:
                year_columns = [col for col in df.columns if col.isdigit()]
                start_year, end_year = st.select_slider(
                    "Select Year Range:",
                    options=sorted(map(int, year_columns)),
                    value=(int(year_columns[0]), int(year_columns[-1])),
                )
                filtered_df = filter_by_year(filtered_df, start_year, end_year)

            st.write("### Filtered Data")
            #if st.button("Apply Filters"):
            st.dataframe(filtered_df.head(100))
            #AgGrid(filtered_df, height=400, fit_columns_on_grid_load=True)
            
            # Button to download filtered data
            excel_data = to_excel(filtered_df)
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"{dataset_name}_filtered_data.xlsx",
                mime="application/vnd.ms-excel"
            )
        else:
            st.error("Error loading data from backend.")
