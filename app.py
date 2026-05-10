import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
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

# --- DATA LOADING LOGIC (Points to your 'csv' folder) ---
@st.cache_data
def load_project_data():
    # Adjust filenames if they are different in your folder
    main_data_path = os.path.join("csv", "full_geotemporal_dataset.csv")
    geojson_path = os.path.join("csv", "ken_admin2.geojson")
    
    df = pd.read_csv(main_data_path) if os.path.exists(main_data_path) else pd.DataFrame()
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
    st.success(f"✅ Data Loaded: {len(df):,} records found.")

# --- MAIN HEADER ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("Developed for Public Health Surveillance & Early Intervention")

# --- 1. EXECUTIVE SUMMARY MODE ---
if app_mode == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    col1, col2, col3 = st.columns(3)
    
    # Dynamic Metrics based on your real CSV
    with col1:
        st.metric(label="Sub-Counties Monitored", value=df['Sub_County'].nunique() if not df.empty else "0")
    
    with col2:
        # We will update this value once Marcus finishes the ML Model
        st.metric(label="Model Confidence (Current)", value="84%", delta="Targeting 90%+")
        
    with col3:
        st.metric(label="Warning Lead Time", value="14 Days", delta="Biological Constant")

    st.write("---")
    
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown("#### **Recent Surveillance Snapshot**")
        if not df.empty:
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.warning("Main dataset not found in /csv folder.")
            
    with col_right:
        st.info("💡 **Lead's Strategic Note:** This MVP focuses on the intersection of NASA Precipitation lags and Socio-demographic vulnerability. By Monday EOD, this dashboard will visualize live ML predictions.")

# --- 2. REGIONAL RISK MAP MODE ---
elif app_mode == "Regional Risk Map":
    st.header("📍 Geospatial Vulnerability Map")
    
    if os.path.exists(geo_path):
        # Center of Kenya coordinates
        m = folium.Map(location=[0.0236, 37.9062], zoom_start=6, tiles="CartoDB positron")
        
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
        
        folium_static(m, width=1200, height=600)
    else:
        st.error(f"GeoJSON file not found at: {geo_path}")

# --- 3. DATA ENGINEERING INSIGHTS ---
elif app_mode == "Data Engineering Insights":
    st.header("⚙️ The Engineering Pipeline")
    st.write("This section documents the transformation process executed by the team.")
    
    if not df.empty:
        st.write("### Data Quality Check")
        st.write(df.describe())
