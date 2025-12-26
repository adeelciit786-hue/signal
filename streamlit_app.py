"""Signals Bot - Streamlit Web Application"""

import streamlit as st

# FIRST thing - page config must come before any other st commands
st.set_page_config(page_title="Signals Bot", layout="wide")

# SECOND thing - show something immediately so we know app is running
st.write("Starting Signals Bot...")

import sys
from pathlib import Path
import logging
import os

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Try to import bot engine
try:
    from src.bot_engine import BotOrchestrator
    st.write("Bot engine imported successfully")
    bot_import_success = True
except Exception as e:
    st.error(f"Failed to import bot engine: {e}")
    st.stop()
    bot_import_success = False

st.write("Loading bot engine...")

try:
    st.write("Checking for config file...")
    if os.path.exists('config.json'):
        st.write("Config found - initializing bot...")
        bot = BotOrchestrator('config.json')
        st.success("Bot initialized successfully!")
    else:
        st.warning("config.json not found in current directory")
        bot = None
except Exception as e:
    st.error(f"Error initializing bot: {e}")
    st.write(f"Current directory: {os.getcwd()}")
    bot = None

st.write("---")

if bot:
    st.title("Signals Bot - Trading Analysis")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        asset_type = st.selectbox("Asset Type", ["Crypto", "Stock", "Forex"])
    with col2:
        if asset_type == "Crypto":
            symbol = st.selectbox("Symbol", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "ADA/USDT"])
        elif asset_type == "Stock":
            symbol = st.selectbox("Symbol", ["AAPL", "GOOGL", "MSFT", "TSLA"])
        else:
            symbol = st.selectbox("Symbol", ["EUR/USD", "GBP/USD", "USD/JPY"])
    with col3:
        timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
    
    if st.button("Analyze", type="primary"):
        st.write(f"Analyzing {symbol} on {timeframe}...")
        try:
            analysis = bot.engine.analyze_single_asset(
                symbol=symbol,
                asset_type=asset_type.lower(),
                timeframe=timeframe,
                backtest=False
            )
            st.success("Analysis complete!")
            st.json(analysis)
        except Exception as e:
            st.error(f"Analysis error: {e}")
else:
    st.info("Bot not loaded. Check config.json path.")
