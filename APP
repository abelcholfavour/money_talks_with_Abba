import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="K-CEWS | Kenya Cholera Early Warning System",
    page_icon="🌍",
    layout="wide"
)

# --- CSS FOR WHO BRANDING (Blue & Clean) ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/c2/WHO_logo.png", width=100) # Placeholder for professional feel
    st.title("Navigation")
    app_mode = st.radio("Go to:", ["Executive Summary", "Regional Risk Map", "14-Day Forecast", "Data Engineering Insights"])
    
    st.divider()
    st.info("**Project Note:** This system utilizes NASA IMERG satellite data and KNBS census weights to predict outbreaks 14 days in advance.")

# --- MAIN HEADER ---
st.title("🇰🇪 K-CEWS: Kenya Cholera Early Warning System")
st.subheader("AI-Driven Predictive Surveillance for Sub-County Intervention")

# --- PLACEHOLDER FOR THE MVP ---
if app_mode == "Executive Summary":
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="High Risk Sub-Counties", value="4", delta="2 since last week", delta_color="inverse")
    
    with col2:
        st.metric(label="System Accuracy (MAE)", value="1.42", delta="Improved 5%")
        
    with col3:
        st.metric(label="Forecast Window", value="14 Days", delta="Fixed Lead Time")

    st.info("💡 **Lead's Insight:** Current weather patterns in the Lake Victoria Basin indicate a 70% probability of surge in Nyatike and Nyakach by May 22, 2026.")
