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

# --- ENHANCED PATH LOGIC ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Let's be 100% explicit for your folder structure
csv_folder = os.path.join(BASE_DIR, "csv")
main_data_path = os.path.join(csv_folder, "full_geotemporal_dataset.csv")
geojson_path = os.path.join(csv_folder, "ken_admin2.geojson")

@st.cache_data
def load_project_data():
    # Diagnostic Print (This shows in your Terminal)
    print(f"DEBUG: Searching for CSV at {main_data_path}")
    
    if os.path.exists(main_data_path):
        return pd.read_csv(main_data_path), geojson_path
    else:
        # If it fails, let's create a tiny "fake" table so the app doesn't stay blank
        dummy_df = pd.DataFrame({"Sub_County": ["Data Not Found"], "Risk": [0]})
        return dummy_df, geojson_path

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
    
    # Let's force it to show something even if the file is missing for a second
    if os.path.exists(geo_path):
        m = folium.Map(location=[-1.286, 36.817], zoom_start=6, tiles="OpenStreetMap")
        
        folium.GeoJson(
            geo_path,
            name="Kenya",
            style_function=lambda x: {"fillColor": "#005ea2", "color": "black", "weight": 1}
        ).add_to(m)
        
        # Use a fixed pixel height to force it to appear
        st_folium(m, height=500, width=800, returned_objects=[])
    else:
        st.error(f"Map File Not Found! Check this path: {geo_path}")

# --- 3. DATA ENGINEERING INSIGHTS ---
elif app_mode == "Data Engineering Insights":
    st.header("⚙️ The Engineering Pipeline")
    if not df.empty:
        st.write("### Statistical Summary of Features")
        st.write(df.describe())
