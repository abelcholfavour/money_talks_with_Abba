import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import json # New import for GeoJSON handling

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="K-CEWS | Kenya Cholera Early Warning", 
    page_icon="🇰🇪",
    layout="wide"
)

# --- 2. DYNAMIC PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "csv", "full_geotemporal_dataset.csv")
geo_path = os.path.join(BASE_DIR, "csv", "ken_admin2.geojson")

# --- 3. DATA LOADING (Updated with Normalization) ---
@st.cache_data
def load_data():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # --- FIX: UPPERCASE Normalization ---
        df['Sub_County'] = df['Sub_County'].str.upper().str.strip()
        return df
    return None

df = load_data()

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c2/WHO_logo.png", width=100)
    st.title("Navigation")
    page = st.selectbox("Select View:", ["Executive Summary", "Regional Risk Map", "Data Engineering"])
    st.divider()
    
    if df is not None:
        st.success(f"✅ Data Active: {len(df):,} rows")
    else:
        st.error("❌ CSV Not Found in /csv folder")
    st.info("**Lead's Note:** Using NASA IMERG and KNBS census data (14-day lag).")

# --- 5. MAIN INTERFACE ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("AI-Driven Predictive Surveillance for Sub-County Intervention")

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    c1, c2, c3 = st.columns(3)
    
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

# --- PAGE 2: REGIONAL RISK MAP (Upgraded to Red/Yellow/Green) ---


# --- PAGE 2: REGIONAL RISK MAP (PHASE 2 UPGRADE) ---
elif page == "Regional Risk Map":
    st.subheader("📍 High-Frequency Surveillance Command Center")
    
    if os.path.exists(geo_path) and df is not None:
        # 1. TOP METRICS (Quick Glance Alerts)
        latest_risk = df.sort_values('Date').groupby('Sub_County').tail(1)
        critical_alerts = len(latest_risk[latest_risk['Risk_Score'] >= 9])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Surveillance Sites", len(latest_risk))
        m2.metric("Critical Risk Alerts (🔴)", critical_alerts)
        m3.metric("Lead Time Status", "14-Day Window Active")
        
        st.divider()

        # 2. TWO-COLUMN COMMAND LAYOUT
        col_map, col_intel = st.columns([2.2, 1]) # Map is larger, Intel is the sidebar

        with col_map:
            st.markdown("### 🗺️ Regional Risk Map")
            m = folium.Map(location=[0.02, 37.9], zoom_start=6, tiles="CartoDB positron")
            
            with open(geo_path) as f:
                kenya_geojson = json.load(f)

            for feature in kenya_geojson['features']:
                geo_name = feature['properties']['adm2_name'].upper().strip()
                match = latest_risk[latest_risk['Sub_County'] == geo_name]
                
                if not match.empty:
                    score = match.iloc[0]['Risk_Score']
                    fill_color = "#e74c3c" if score >= 9 else ("#f1c40f" if score >= 7 else "#2ecc71")
                    opacity = 0.8
                else:
                    fill_color = "#d3d3d3"
                    opacity = 0.2

                folium.GeoJson(
                    feature,
                    style_function=lambda x, fc=fill_color, op=opacity: {
                        'fillColor': fc, 'color': 'black', 'weight': 0.5, 'fillOpacity': op
                    },
                    tooltip=f"<b>{geo_name}</b>"
                ).add_to(m)
            
            st_folium(m, width=700, height=550)

        with col_intel:
            st.markdown("### 🔍 Intelligence Panel")
            # This selector lets the user "Zoom In" on a specific focus area
            focus_area = st.selectbox("Monitor Sub-County:", latest_risk['Sub_County'].unique())
            
            # Fetch the specific row for the selected area
            area_info = latest_risk[latest_risk['Sub_County'] == focus_area].iloc[0]
            
            # THE WEATHER MONITOR (Your Idea)
            st.write(f"**Surveillance Data for: {focus_area}**")
            
            st.info(f"📅 **Sync Date:** {area_info['Date']}")
            
            # Displaying the NASA IMERG and 14-day lag info
            st.metric("Rainfall (14d Lag)", f"{area_info['rainfall_lag_14']} mm")
            st.metric("Current Humidity", f"{area_info['RH2M']}%")
            
            # CALL TO ACTION LOGIC
            st.divider()
            # Replace the button section in the Intelligence Panel with this:
            if area_info['Risk_Score'] >= 9:
               st.error(f"🚨 **HIGH RISK ALERT** for {focus_area}")
    
              # Create a small dataframe for the report
               report_data = pd.DataFrame([area_info])
               csv_report = report_data.to_csv(index=False).encode('utf-8')

               st.download_button(
                label=f"📥 Download Intervention Report for {focus_area}",
                data=csv_report,
                file_name=f"KCEWS_Report_{focus_area}.csv",
                mime="text/csv",
               )
            else:
                st.success(f"✅ **STABLE**\n\nConditions in {focus_area} are within safe thresholds. Continue routine monitoring.")

    else:
        st.error("❌ Required files (GeoJSON/CSV) not detected.")



# --- PAGE 3: DATA ENGINEERING ---
elif page == "Data Engineering":
    st.subheader("⚙️ Feature Engineering & Statistical Insights")
    if df is not None:
        st.write("### Environmental Predictor Summary")
        st.write(df.describe())
    else:
        st.error("Cannot display statistics. Data source not found.")