import streamlit as st

st.set_page_config(page_title="K-CEWS Test")

# 1. Sidebar Navigation
with st.sidebar:
    st.title("Navigation")
    # Using a selectbox is more stable for testing
    choice = st.selectbox("Switch Page:", ["Home", "Map Test", "Data Test"])

# 2. Page Logic
st.title("K-CEWS Testing Center")

if choice == "Home":
    st.write("### You are on the HOME page.")
    st.info("If you see this, the sidebar is working!")

elif choice == "Map Test":
    st.write("### You are on the MAP page.")
    st.warning("We will put the map here once we fix the paths.")

elif choice == "Data Test":
    st.write("### You are on the DATA page.")
    st.success("This page is for Marcus and Carolyne's work.")
