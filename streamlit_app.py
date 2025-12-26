"""
Streamlit App for Signals Bot
"""
import streamlit as st

# Test if Streamlit is working
st.write("Testing Streamlit...")
st.title("🤖 Signals Bot")
st.write("If you see this, Streamlit is working!")
st.divider()

# Show that we're attempting to load
st.write("Loading modules...")

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    import bot_config
    import bot_engine
    
    st.success("✅ Modules imported successfully!")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.write("Asset Type: Crypto")
        st.write("Symbol: BTC/USDT")
        st.write("Status: Ready to analyze")
    
    # Main area
    st.subheader("📊 Ready to Analyze")
    st.write("Click the button below to test signal generation")
    
    if st.button("🔍 Test Analysis"):
        st.info("Analysis would start here...")
        st.write("App is working correctly!")
    
except Exception as e:
    st.error(f"❌ Error: {str(e)}")
    import traceback
    st.error(traceback.format_exc())
