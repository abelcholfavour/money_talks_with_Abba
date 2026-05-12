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

# --- PAGE 2: REGIONAL RISK MAP (Phase 2 Upgrade) ---
elif page == "Regional Risk Map":
    st.subheader("📍 High-Frequency Surveillance Command Center")
    
    if os.path.exists(geo_path) and df is not None:
        # A. TOP METRICS (Alert Bar)
        latest_risk = df.sort_values('Date').groupby('Sub_County').tail(1)
        high_risk_count = len(latest_risk[latest_risk['Risk_Score'] >= 9])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Sub-Counties with Data", len(latest_risk))
        m2.metric("Critical Alerts (🔴)", high_risk_count)
        m3.metric("System Status", "Live / Predictive")
        
        st.divider()

        # B. TWO-COLUMN LAYOUT
        col_map, col_intel = st.columns([2, 1]) # Map takes 2/3, Intel takes 1/3

        with col_map:
            st.markdown("### Regional Risk Map")
            # --- MAP LOGIC ---
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
            
            st_folium(m, width=700, height=500)

        with col_intel:
            st.markdown("### 🔍 Intelligence Panel")
            # Selector for the user to pick which focus area to "monitor"
            focus_area = st.selectbox("Select Area to Monitor:", latest_risk['Sub_County'].unique())
            
            # Get specific data for the focus area
            area_data = latest_risk[latest_risk['Sub_County'] == focus_area].iloc[0]
            
            # Weather Monitor Cards
            st.write(f"**Current Environmental Status: {focus_area}**")
            st.info(f"📅 Last Satellite Sync: {area_data['Date']}")
            
            st.metric("14-Day Rainfall Lag", f"{area_data['rainfall_lag_14']} mm")
            st.metric("Current Humidity", f"{area_data['RH2M']}%")
            
            # Call to Action Logic
            st.divider()
            if area_data['Risk_Score'] >= 9:
                st.error(f"⚠️ **URGENT ACTION REQUIRED**\n\nHigh risk score of {area_data['Risk_Score']} detected. Triggering 14-day intervention window for {focus_area}.")
                st.button(f"Generate Report for {focus_area}")
            else:
                st.success(f"✅ **ROUTINE SURVEILLANCE**\n\nNo immediate outbreak threat for {focus_area}. Continue standard WASH monitoring.")

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