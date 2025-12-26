import streamlit as st

# MUST be first
st.set_page_config(page_title="Signals Bot", layout="wide")

# Immediate output - if nothing shows, something is very wrong
st.write("=== SIGNALS BOT IS RUNNING ===")
st.title("Trading Signal Analyzer")

# Show something to prove app works
st.success("✓ Streamlit is working!")

st.markdown("---")

# Try to load bot
st.write("Attempting to load bot engine...")

import sys, os
from pathlib import Path

try:
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from src.bot_engine import BotOrchestrator
    
    if os.path.exists('config.json'):
        bot = BotOrchestrator('config.json')
        st.write("✓ Bot loaded successfully")
        
        # UI
        asset = st.selectbox("Select Asset Type", ["Crypto", "Stock", "Forex"])
        
        symbols = {
            "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
            "Stock": ["AAPL", "GOOGL", "MSFT"],
            "Forex": ["EUR/USD", "GBP/USD", "USD/JPY"]
        }
        
        symbol = st.selectbox("Select Symbol", symbols[asset])
        timeframe = st.selectbox("Select Timeframe", ["1h", "4h", "1d", "1w"])
        
        if st.button("Generate Signal", type="primary"):
            with st.spinner("Analyzing..."):
                try:
                    analysis = bot.engine.analyze_single_asset(
                        symbol=symbol,
                        asset_type=asset.lower(),
                        timeframe=timeframe,
                        backtest=False
                    )
                    
                    # Display signal
                    signal = analysis.get('signal', 'NEUTRAL')
                    if signal == 'BUY':
                        st.success(f"## BUY SIGNAL - {analysis.get('confidence', 0):.1f}% confidence")
                    elif signal == 'SELL':
                        st.error(f"## SELL SIGNAL - {analysis.get('confidence', 0):.1f}% confidence")
                    else:
                        st.warning(f"## {signal} - {analysis.get('confidence', 0):.1f}% confidence")
                    
                    # Tabs
                    t1, t2, t3 = st.tabs(["Details", "Confirmations", "Risk"])
                    
                    with t1:
                        setup = analysis.get('setup', {})
                        st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                        st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
                        st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
                    
                    with t2:
                        conf = analysis.get('confirmations', {})
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Trend", conf.get('trend', 'N/A'))
                        c2.metric("Momentum", "Yes" if conf.get('momentum_confirmed') else "No")
                        c3.metric("Volume", "Yes" if conf.get('volume_confirmed') else "No")
                    
                    with t3:
                        risk = analysis.get('risk_validation', {})
                        if risk.get('allowed'):
                            st.success("Risk APPROVED")
                        else:
                            st.error("Risk REJECTED")
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.error("config.json not found")
        
except Exception as e:
    st.error(f"Error: {str(e)}")


