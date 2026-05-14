import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import json
import altair as alt

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="K-CEWS | ProMax Command Center", 
    page_icon="🇰🇪",
    layout="wide"
)

# --- CUSTOM UI FIXES ---
st.markdown("""
    <style>
        div[data-baseweb="select"], div[role="button"], .stSelectbox div {
            cursor: pointer !important;
        }
        div[data-baseweb="select"]:hover {
            border-color: #e74c3c !important;
        }
        .stMetric { background-color: #ffffff; padding: 10px; border-radius: 5px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DYNAMIC PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "csv", "kcews_live_predictions.csv")
geo_path = os.path.join(BASE_DIR, "csv", "ken_admin2.geojson")
comparison_path = os.path.join(BASE_DIR, "csv", "model_performance_comparison.csv")
factors_path = os.path.join(BASE_DIR, "csv", "subcounty_risk_factors.csv")

# --- 3. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df['Sub_County'] = df['Sub_County'].str.upper().str.strip()
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    return None

@st.cache_data
def load_risk_factors():
    if os.path.exists(factors_path):
        rf = pd.read_csv(factors_path)
        rf['Sub_County'] = rf['Sub_County'].str.upper().str.strip()
        return rf
    return None

df = load_data()
risk_factors = load_risk_factors()

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c2/WHO_logo.png", width=100)
    st.title("K-CEWS ProMax")
    page = st.selectbox("Select View:", ["Executive Summary", "Regional Risk Map", "Data Engineering"])
    
    st.divider()
    
    st.subheader("⚠️ Historical Burden")
    if df is not None:
        hotspots = df[df['Outbreak'] == 1.0]['Sub_County'].unique()
        if len(hotspots) > 0:
            st.warning(f"Monitoring {len(hotspots)} high-priority zones:")
            for area in hotspots[:10]: # Limiting for UI cleanliness
                st.write(f"- 🔴 {area}")
    
    st.divider()
    if df is not None:
        st.success(f"✅ AI Engine Active")
        st.caption(f"Surveillance Rows: {len(df):,}")
    
    st.info("**Lead's Note:** System powered by Optimized XGBoost with 100% Outbreak Recall.")

# --- 5. MAIN INTERFACE ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.caption("PROMAX Edition: AI-Driven Predictive Surveillance & Logistics Command")

# --- PAGE 1: EXECUTIVE SUMMARY ---
if page == "Executive Summary":
    st.subheader("📊 System Critical Metrics")
    c1, c2, c3 = st.columns(3)
    
    sub_counties = df['Sub_County'].nunique() if df is not None else 0
    c1.metric("Sub-Counties Tracked", sub_counties)
    c2.metric("Outbreak Sensitivity", "100%", delta="Recall Score")
    c3.metric("Forecast Window", "14 Days", delta="Lead Time")
    
    st.divider()
    if df is not None:
        st.write("### AI Forecast Snapshot")
        display_cols = ['Date', 'Sub_County', 'AI_Risk_Score', 'AI_Risk_Level', 'IMERG_PRECTOT']
        st.dataframe(df[display_cols].tail(10), use_container_width=True)

# --- PAGE 2: REGIONAL RISK MAP (PROMAX) ---
elif page == "Regional Risk Map":
    st.subheader("📍 AI Surveillance Command Center")
    
    if os.path.exists(geo_path) and df is not None:
        latest_risk = df.sort_values('Date').groupby('Sub_County').tail(1)
        history_list = df[df['Outbreak'] == 1.0]['Sub_County'].unique()
        
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
                    score = match.iloc[0]['AI_Risk_Score']
                    if geo_name in history_list and score >= 2.0: fill_color = "#922b21"
                    elif score >= 2.0: fill_color = "#e74c3c"
                    elif score >= 1.0: fill_color = "#f1c40f"
                    else: fill_color = "#2ecc71"
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
            st.markdown("### 🔍 Intelligence & Logistics")
            focus_area = st.selectbox("Monitor Sub-County:", latest_risk['Sub_County'].unique())
            area_info = latest_risk[latest_risk['Sub_County'] == focus_area].iloc[0]
            
            st.info(f"📅 **Sync Date:** {area_info['Date'].date()}")
            
            # --- MEDICAL LOGISTICS ESTIMATOR (NEW PROMAX FEATURE) ---
            baseline_score = 8
            if risk_factors is not None:
                rf_match = risk_factors[risk_factors['Sub_County'] == focus_area]
                if not rf_match.empty:
                    baseline_score = rf_match.iloc[0]['Risk_Score']
            
            # Logic: Higher baseline risk + higher AI score = more supplies
            pop_proxy = baseline_score * 5000 
            chlorine = round((pop_proxy * area_info['AI_Risk_Score'] * 0.02), 1)
            ors = int(pop_proxy * area_info['AI_Risk_Score'] * 0.5)

            li1, li2 = st.columns(2)
            li1.metric("Chlorine Needed", f"{chlorine}L")
            li2.metric("ORS Kits", f"{ors} Units")
            
            # --- 14-DAY SIGNATURE TREND (NEW PROMAX FEATURE) ---
            st.markdown("#### 🌧️ 14-Day Rainfall Trend")
            area_history = df[df['Sub_County'] == focus_area].tail(14)
            st.line_chart(area_history.set_index('Date')['IMERG_PRECTOT'])
            
            st.divider()
            
            # AI-DRIVEN TEXT REPORT (RETAINED)
            is_hotspot = "YES" if focus_area in history_list else "NO"
            report_text = f"K-CEWS AI MEMO\nLoc: {focus_area}\nRisk: {area_info['AI_Risk_Level']}\nLogistics: Chlorine {chlorine}L, ORS {ors}"

            if area_info['AI_Risk_Level'] == 'High Risk':
                st.error(f"🚨 **HIGH RISK ALERT**")
                st.download_button("📥 Download AI Memo", report_text, f"KCEWS_{focus_area}.txt", use_container_width=True)
            else:
                st.success(f"✅ **STABLE CONDITIONS**")
                st.download_button("📥 Download Update", report_text, f"KCEWS_{focus_area}.txt", use_container_width=True)

# --- PAGE 3: DATA ENGINEERING (RETAINED FULLY) ---
elif page == "Data Engineering":
    st.subheader("⚙️ AI Model Performance & Training")
    
    if os.path.exists(comparison_path):
        st.write("### 🏆 Model Tournament Results")
        comp_df = pd.read_csv(comparison_path)
        st.dataframe(comp_df, use_container_width=True)
        st.success("Selected Engine: XGBoost (Sensitivity Optimized for 100% Recall)")
    
    st.divider()
    
    if df is not None:
        st.write("### Environmental Variable Distribution (Surveillance Insights)")
        st.write(df.describe())
    else:
        st.error("Data source not found.")