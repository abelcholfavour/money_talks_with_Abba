import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium  # Using the modern render engine
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

# --- DATA LOADING LOGIC ---
@st.cache_data
def load_project_data():
    # Ensuring paths are robust for any OS
    main_data_path = os.path.join("csv", "full_geotemporal_dataset.csv")
    geojson_path = os.path.join("csv", "ken_admin2.geojson")
    
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
    if not df.empty:
        st.success(f"✅ Data Loaded: {len(df):,} records")
    else:
        st.error("❌ Data files not found in /csv")

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
            st.warning("Please ensure 'full_geotemporal_dataset.csv' is in the /csv folder.")
            
    with col_right:
        st.info("💡 **Lead's Strategic Note:** This MVP focuses on the intersection of NASA Precipitation lags and Socio-demographic vulnerability. Predictions refresh every 24 hours.")

# --- 2. REGIONAL RISK MAP MODE ---
elif app_mode == "Regional Risk Map":
    st.header("📍 Geospatial Vulnerability Map")
    
    if os.path.exists(geo_path):
        # Coordinates centered on Kenya
        m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB positron")
        
        # Adding the GeoJSON layer
        # NOTE: Ensure your GeoJSON has the property 'ADM2_EN' for the tooltip to work!
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
        
        # Using st_folium for better compatibility with Streamlit 1.57.0+
        st_folium(m, width=1100, height=600, returned_objects=[])
    else:
        st.error(f"GeoJSON file not found at: {geo_path}")
        st.info("Technical Tip: Ensure the file 'ken_admin2.geojson' is inside the 'csv' folder.")

# --- 3. DATA ENGINEERING INSIGHTS ---
elif app_mode == "Data Engineering Insights":
    st.header("⚙️ The Engineering Pipeline")
    if not df.empty:
        st.write("### Statistical Summary of Features")
        st.write(df.describe())
