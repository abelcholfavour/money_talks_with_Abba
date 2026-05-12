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
# --- PAGE 2: REGIONAL RISK MAP (HUMAN-READABLE REPORT VERSION) ---
elif page == "Regional Risk Map":
    st.subheader("📍 High-Frequency Surveillance Command Center")
    
    if os.path.exists(geo_path) and df is not None:
        latest_risk = df.sort_values('Date').groupby('Sub_County').tail(1)
        
        # 1. TOP METRICS
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Sites", len(latest_risk))
        m2.metric("High Risk (🔴)", len(latest_risk[latest_risk['Risk_Score'] >= 9]))
        m3.metric("Moderate Risk (🟡)", len(latest_risk[(latest_risk['Risk_Score'] >= 7) & (latest_risk['Risk_Score'] < 9)]))
        
        st.divider()

        col_map, col_intel = st.columns([2.2, 1]) 

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
                    # ADJUSTED COLOR LOGIC: Red (>=9), Yellow (8), Green (<=7)
                    if score >= 9: fill_color = "#e74c3c" # Red
                    elif score == 8: fill_color = "#f1c40f" # Yellow
                    else: fill_color = "#2ecc71" # Green
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
            focus_area = st.selectbox("Monitor Sub-County:", latest_risk['Sub_County'].unique())
            area_info = latest_risk[latest_risk['Sub_County'] == focus_area].iloc[0]
            
            st.write(f"**Surveillance Data: {focus_area}**")
            st.info(f"📅 **Sync Date:** {area_info['Date']}")
            
            # Weather Monitor
            st.metric("Rainfall (14d Lag)", f"{area_info['rainfall_lag_14']} mm")
            st.metric("Humidity", f"{area_info['RH2M']}%")
            
            # --- ACTION TRIGGER & READABLE REPORT ---
            st.divider()
            
            # Create the HUMAN-READABLE TEXT REPORT
            report_text = f"""
            K-CEWS OFFICIAL INTERVENTION PLAN
            ----------------------------------
            Location: {focus_area} Sub-County
            Report Date: {area_info['Date']}
            Risk Level: {'HIGH' if area_info['Risk_Score'] >= 9 else 'STABLE'}
            Risk Score: {area_info['Risk_Score']}/10
            
            ENVIRONMENTAL ANALYSIS:
            - Detected Rainfall (14-day lag): {area_info['rainfall_lag_14']} mm
            - Relative Humidity: {area_info['RH2M']}%
            
            REQUIRED ACTIONS:
            1. Alert local WASH officials in {focus_area}.
            2. Distribute household water treatment (Chlorine) to high-priority zones.
            3. Initiate 14-day intensive clinical surveillance.
            
            Document generated by K-CEWS AI Predictive Engine.
            """

            if area_info['Risk_Score'] >= 9:
                st.error(f"🚨 **HIGH RISK ALERT**")
                st.download_button(
                    label="📥 Download Intervention Memo (Text)",
                    data=report_text,
                    file_name=f"KCEWS_Memo_{focus_area}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.success(f"✅ **STABLE CONDITIONS**")
                st.download_button(
                    label="📥 Download Surveillance Update",
                    data=report_text,
                    file_name=f"KCEWS_Update_{focus_area}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    else:
        st.error("❌ Required files missing.")


# --- PAGE 3: DATA ENGINEERING ---
elif page == "Data Engineering":
    st.subheader("⚙️ Feature Engineering & Statistical Insights")
    if df is not None:
        st.write("### Environmental Predictor Summary")
        st.write(df.describe())
    else:
        st.error("Cannot display statistics. Data source not found.")