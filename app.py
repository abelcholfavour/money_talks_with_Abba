import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium 
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="K-CEWS | Kenya Cholera Early Warning System",
    page_icon="🌍",
    layout="wide"
)

# --- CSS FOR WHO BRANDING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid #005ea2;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENHANCED PATH LOGIC (Best Practice) ---
# This finds exactly where your app.py is sitting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- DATA LOADING LOGIC ---
@st.cache_data
def load_project_data():
    # Constructing absolute paths to reach inside the 'csv' folder
    main_data_path = os.path.join(BASE_DIR, "csv", "full_geotemporal_dataset.csv")
    geojson_path = os.path.join(BASE_DIR, "csv", "ken_admin2.geojson")
    
    if os.path.exists(main_data_path):
        df = pd.read_csv(main_data_path)
    else:
        df = pd.DataFrame()
        
    return df, geojson_path

df, geo_path = load_project_data()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c2/WHO_logo.png", width=100)
    st.title("Navigation")
    app_mode = st.radio("Go to:", [
        "Executive Summary", 
        "Regional Risk Map", 
        "14-Day Forecast", 
        "Data Engineering Insights"
    ])
    st.divider()
    
    # Connection Status
    if not df.empty:
        st.success(f"✅ Data Loaded: {len(df):,} records")
    else:
        st.error("❌ CSV Folder or Data not found.")
        st.info(f"Checking in: {os.path.join(BASE_DIR, 'csv')}")

# --- MAIN HEADER ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("Developed for Public Health Surveillance & Early Intervention")

# --- 1. EXECUTIVE SUMMARY MODE ---
if app_mode == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Sub-Counties Monitored", value=df['Sub_County'].nunique() if not df.empty else "0")
    
    with col2:
        st.metric(label="Model Confidence", value="84%", delta="Targeting 90%+")
        
    with col3:
        st.metric(label="Warning Lead Time", value="14 Days", delta="Biological Constant")

    st.write("---")
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("#### **Recent Surveillance Snapshot**")
        if not df.empty:
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.warning("Please verify data file location.")
            
    with col_right:
        st.info("💡 **Lead's Strategic Note:** This MVP focuses on the intersection of NASA Precipitation lags and Socio-demographic vulnerability.")

# --- 2. REGIONAL RISK MAP MODE ---
elif app_mode == "Regional Risk Map":
    st.header("📍 Geospatial Vulnerability Map")
    
    if os.path.exists(geo_path):
        # Coordinates centered on Kenya
        m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB positron")
        
        try:
            # Adding the GeoJSON layer
            folium.GeoJson(
                geo_path,
                name="Kenya Sub-Counties",
                style_function=lambda x: {
                    "fillColor": "#005ea2",
                    "color": "black",
                    "weight": 0.5,
                    "fillOpacity": 0.1,
                },
                tooltip=folium.GeoJsonTooltip(fields=['ADM2_EN'], aliases=['Sub-County:'])
            ).add_to(m)
            
            st_folium(m, width=1100, height=600, returned_objects=[])
        except Exception as e:
            st.error("The map engine failed to draw the boundaries.")
            st.code(f"Error detail: {e}")
    else:
        st.error(f"GeoJSON file not found at: {geo_path}")

# --- 3. DATA ENGINEERING INSIGHTS ---
elif app_mode == "Data Engineering Insights":
    st.header("⚙️ The Engineering Pipeline")
    if not df.empty:
        st.write("### Statistical Summary of Features")
        st.write(df.describe())
