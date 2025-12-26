import streamlit as st

st.set_page_config(page_title="Signals Bot", layout="wide")

st.write("TEST - App is loading")
st.title("Signals Bot")
st.write("If you see this, Streamlit is working!")

st.markdown("---")
st.subheader("Status Check")

# Test 1: Can we import sys?
try:
    import sys
    st.write("OK - sys imported")
except Exception as e:
    st.error(f"FAIL - sys import: {e}")

# Test 2: Can we add to path?
try:
    from pathlib import Path
    import os
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    st.write("OK - Path updated")
except Exception as e:
    st.error(f"FAIL - Path update: {e}")

# Test 3: Can we find config.json?
try:
    config_exists = os.path.exists('config.json')
    st.write(f"config.json exists: {config_exists}")
    st.write(f"Current directory: {os.getcwd()}")
    files = os.listdir('.')
    st.write(f"Files in directory ({len(files)} total): {files[:10]}")
except Exception as e:
    st.error(f"FAIL - Config check: {e}")

# Test 4: Can we import bot?
try:
    from src.bot_engine import BotOrchestrator
    st.write("OK - BotOrchestrator imported")
    
    # Try to load bot
    if os.path.exists('config.json'):
        bot = BotOrchestrator('config.json')
        st.success("OK - Bot loaded successfully!")
        
        # Show simple UI
        st.markdown("---")
        st.subheader("Trading Analysis")
        
        symbol = st.text_input("Enter symbol", "BTC/USDT")
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
        
        if st.button("Analyze"):
            with st.spinner("Analyzing..."):
                try:
                    result = bot.engine.analyze_single_asset(
                        symbol=symbol,
                        asset_type="crypto",
                        timeframe=timeframe,
                        backtest=False
                    )
                    st.success("Analysis complete!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
    else:
        st.warning("config.json not found - bot features unavailable")
        
except Exception as e:
    st.error(f"FAIL - Bot import: {e}")
    import traceback
    st.write(traceback.format_exc())
