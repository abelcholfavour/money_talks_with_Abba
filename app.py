import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import json

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="K-CEWS | Kenya Cholera Early Warning", 
    page_icon="🇰🇪",
    layout="wide"
)

# --- 2. DYNAMIC PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Points to the NEW AI-generated predictions
csv_path = os.path.join(BASE_DIR, "csv", "kcews_live_predictions.csv")
geo_path = os.path.join(BASE_DIR, "csv", "ken_admin2.geojson")
comparison_path = os.path.join(BASE_DIR, "csv", "model_performance_comparison.csv")

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
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
        st.success(f"✅ AI Engine Active")
        st.caption(f"Surveillance Rows: {len(df):,}")
    else:
        st.error("❌ AI Data Not Found")
    
    st.info("**Lead's Note:** System powered by Optimized XGBoost with 100% Outbreak Recall.")

# --- 5. MAIN INTERFACE ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("AI-Driven Predictive Surveillance for Sub-County Intervention")

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    c1, c2, c3 = st.columns(3)
    
    sub_counties = df['Sub_County'].nunique() if df is not None else 0
    c1.metric("Sub-Counties Tracked", sub_counties)
    # Reflecting the new Model Accuracy
    c2.metric("Outbreak Sensitivity", "100%", delta="Recall Score")
    c3.metric("Forecast Window", "14 Days", delta="Lead Time")
    
    st.divider()
    if df is not None:
        st.write("### AI Forecast Snapshot")
        # Showing the new AI columns
        display_cols = ['Date', 'Sub_County', 'AI_Risk_Score', 'AI_Risk_Level', 'IMERG_PRECTOT']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)
    else:
        st.warning("Please ensure 'kcews_live_predictions.csv' is in the /csv folder.")

# --- PAGE 2: REGIONAL RISK MAP (AI-POWERED) ---
elif page == "Regional Risk Map":
    st.subheader("📍 AI Surveillance Command Center")
    
    if os.path.exists(geo_path) and df is not None:
        latest_risk = df.sort_values('Date').groupby('Sub_County').tail(1)
        
        # 1. TOP METRICS
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Sites", len(latest_risk))
        m2.metric("Critical Risk (🔴)", len(latest_risk[latest_risk['AI_Risk_Level'] == 'High Risk']))
        m3.metric("Moderate Risk (🟡)", len(latest_risk[latest_risk['AI_Risk_Level'] == 'Moderate']))
        
        st.divider()

        col_map, col_intel = st.columns([2.2, 1]) 

        with col_map:
            st.markdown("### 🗺️ Live Risk Map")
            m = folium.Map(location=[0.02, 37.9], zoom_start=6, tiles="CartoDB positron")
            
            with open(geo_path) as f:
                kenya_geojson = json.load(f)

            for feature in kenya_geojson['features']:
                geo_name = feature['properties']['adm2_name'].upper().strip()
                match = latest_risk[latest_risk['Sub_County'] == geo_name]
                
                if not match.empty:
                    # Logic using our new AI Risk Score
                    score = match.iloc[0]['AI_Risk_Score']
                    if score >= 2.0: fill_color = "#e74c3c" # Red (Threshold 0.20)
                    elif score >= 1.0: fill_color = "#f1c40f" # Yellow
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
                    tooltip=f"<b>{geo_name}</b><br>AI Score: {match.iloc[0]['AI_Risk_Score'] if not match.empty else 'N/A'}"
                ).add_to(m)
            
            st_folium(m, width=700, height=550)

        with col_intel:
            st.markdown("### 🔍 Intelligence Panel")
            focus_area = st.selectbox("Monitor Sub-County:", latest_risk['Sub_County'].unique())
            area_info = latest_risk[latest_risk['Sub_County'] == focus_area].iloc[0]
            
            st.write(f"**Surveillance Data: {focus_area}**")
            st.info(f"📅 **Sync Date:** {area_info['Date']}")
            
            # AI Weather Monitor
            st.metric("Rainfall (14d Lag)", f"{area_info['rainfall_lag_14']} mm")
            st.metric("AI Risk Probability", f"{area_info['AI_Risk_Score'] * 10}%")
            
            st.divider()
            
            # AI-DRIVEN TEXT REPORT
            report_text = f"""
            K-CEWS AI INTERVENTION MEMO
            ----------------------------------
            Location: {focus_area}
            Prediction Date: {area_info['Date']}
            AI Risk Level: {area_info['AI_Risk_Level'].upper()}
            Confidence Score: {area_info['AI_Risk_Score']}/10
            
            ENVIRONMENTAL ANALYSIS:
            - 14-Day Lagged Rainfall: {area_info['rainfall_lag_14']} mm
            - Relative Humidity: {area_info['RH2M']}%
            
            RECOMMENDED PROTOCOL:
            {'1. URGENT: Deploy mobile health teams immediately.' if area_info['AI_Risk_Level'] == 'High Risk' else '1. Maintain routine environmental monitoring.'}
            2. Alert WASH coordinators in {focus_area}.
            3. Review 14-day rainfall lag trends.
            """

            if area_info['AI_Risk_Level'] == 'High Risk':
                st.error(f"🚨 **HIGH RISK ALERT**")
                st.download_button("📥 Download AI Memo", report_text, f"KCEWS_AI_{focus_area}.txt", use_container_width=True)
            else:
                st.success(f"✅ **STABLE CONDITIONS**")
                st.download_button("📥 Download Update", report_text, f"KCEWS_AI_{focus_area}.txt", use_container_width=True)

# --- PAGE 3: DATA ENGINEERING ---
elif page == "Data Engineering":
    st.subheader("⚙️ AI Model Performance & Training")
    
    # Show the Tournament Results
    if os.path.exists(comparison_path):
        st.write("### 🏆 Model Tournament Results")
        comp_df = pd.read_csv(comparison_path)
        st.dataframe(comp_df, use_container_width=True)
        st.success("Selected Engine: XGBoost (Sensitivity Optimized)")
    
    st.divider()
    
    if df is not None:
        st.write("### Environmental Variable Distribution")
        st.write(df.describe())
    else:
        st.error("Data source not found.")