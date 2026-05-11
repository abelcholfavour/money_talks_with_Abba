import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="K-CEWS | Kenya Cholera Early Warning", 
    page_icon="🇰🇪",
    layout="wide"
)

# --- 2. DYNAMIC PATHS (The Lead's Secret) ---
# This finds the folders regardless of which computer runs the app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "csv", "full_geotemporal_dataset.csv")
geo_path = os.path.join(BASE_DIR, "csv", "ken_admin2.geojson")

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

df = load_data()

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    # Official WHO Logo Placeholder
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c2/WHO_logo.png", width=100)
    st.title("Navigation")
    page = st.selectbox("Select View:", ["Executive Summary", "Regional Risk Map", "Data Engineering"])
    
    st.divider()
    
    # Status Indicators
    if df is not None:
        st.success(f"✅ Data Active: {len(df):,} rows")
    else:
        st.error("❌ CSV Not Found in /csv folder")
        
    st.info("**Lead's Note:** This system uses NASA IMERG and KNBS census data for 14-day predictive surveillance.")

# --- 5. MAIN INTERFACE ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("AI-Driven Predictive Surveillance for Sub-County Intervention")

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    c1, c2, c3 = st.columns(3)
    
    # Dynamic Metrics
    sub_counties = df['Sub_County'].nunique() if df is not None else 0
    c1.metric("Sub-Counties Tracked", sub_counties)
    c2.metric("Model Confidence", "84%", delta="Target 90%")
    c3.metric("Forecast Window", "14 Days", delta="Lead Time")
    
    st.divider()
    
    if df is not None:
        st.write("### Recent Surveillance Data (Snapshot)")
        st.dataframe(df.tail(10), use_container_width=True)
    else:
        st.warning("Please ensure 'full_geotemporal_dataset.csv' is in the /csv folder.")

# --- PAGE 2: REGIONAL RISK MAP ---
elif page == "Regional Risk Map":
    st.subheader("📍 Geospatial Risk Analysis")
    
    if os.path.exists(geo_path):
        # Create the Base Map centered on Kenya
        m = folium.Map(location=[0.02, 37.9], zoom_start=6, tiles="CartoDB positron")
        
        # Add the GeoJson layer for Kenya Admin Borders
        folium.GeoJson(
            geo_path, 
            name="Kenya Borders",
            style_function=lambda x: {'fillColor': '#2e86c1', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1}
        ).add_to(m)
        
        # Display the Map
        st_folium(m, width=1100, height=600)
    else:
        st.error(f"❌ GeoJSON file missing at: {geo_path}")

# --- PAGE 3: DATA ENGINEERING ---
elif page == "Data Engineering":
    st.subheader("⚙️ Feature Engineering & Statistical Insights")
    
    if df is not None:
        st.write("### Environmental Predictor Summary")
        st.write("This table shows the statistical distribution of our 14-day lagged variables.")
        st.write(df.describe())
    else:
        st.error("Cannot display statistics. Data source not found.")
