import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="K-CEWS", layout="wide")

# --- 2. PATHS (Absolute) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_folder = os.path.join(BASE_DIR, "csv")
main_data_path = os.path.join(csv_folder, "full_geotemporal_dataset.csv")
geojson_path = os.path.join(csv_folder, "ken_admin2.geojson")

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists(main_data_path):
        return pd.read_csv(main_data_path)
    return pd.DataFrame()

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("Navigation")
    app_mode = st.selectbox("Choose Page:", ["Executive Summary", "Regional Risk Map", "14-Day Forecast", "Data Engineering Insights"])
    st.divider()
    if not df.empty:
        st.success(f"Data Loaded: {len(df)} rows")
    else:
        st.error("CSV Not Found!")
        st.info(f"Checking: {csv_folder}")

# --- 5. PAGE LOGIC ---
st.title("🇰🇪 Kenya Cholera Early Warning System")

if app_mode == "Executive Summary":
    st.subheader("📊 Executive Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Sub-Counties", df['Sub_County'].nunique() if not df.empty else 0)
    col2.metric("Confidence", "84%")
    col3.metric("Window", "14 Days")
    
    if not df.empty:
        st.write("### Data Preview")
        st.dataframe(df.tail(5))

elif app_mode == "Regional Risk Map":
    st.subheader("📍 Regional Risk Map")
    
    if os.path.exists(geojson_path):
        # Center the map properly on Kenya
        m = folium.Map(location=[0.02, 37.9], zoom_start=6)
        
        folium.GeoJson(
            geojson_path,
            name="Kenya_Borders",
            style_function=lambda x: {'fillColor': '#005ea2', 'color': 'black', 'weight': 1}
        ).add_to(m)
        
        # Display the map
        st_folium(m, width=900, height=500)
    else:
        st.error("GeoJSON file is missing from the /csv folder!")

elif app_mode == "Data Engineering Insights":
    st.subheader("⚙️ Data Insights")
    if not df.empty:
        st.write(df.describe())
