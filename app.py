import streamlit as st
st.set_page_config(page_title="Signals Bot", layout="wide")
st.write("TEST 1 - App is running")
st.title("Signals Bot")
st.write("TEST 2 - Basic UI working")

import sys
import os
from pathlib import Path

st.write("TEST 3 - Imports successful")

sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from src.bot_engine import BotOrchestrator
    st.write("TEST 4 - Bot engine imported")
    
    if os.path.exists('config.json'):
        st.write("TEST 5 - config.json found")
        bot = BotOrchestrator('config.json')
        st.success("Bot loaded!")
        
        # UI
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            asset = st.selectbox("Asset", ["Crypto", "Stock", "Forex"])
        with col2:
            if asset == "Crypto":
                symbol = st.selectbox("Symbol", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
            elif asset == "Stock":
                symbol = st.selectbox("Symbol", ["AAPL", "GOOGL", "MSFT"])
            else:
                symbol = st.selectbox("Symbol", ["EUR/USD", "GBP/USD", "USD/JPY"])
        with col3:
            tf = st.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
        
        if st.button("Analyze", type="primary"):
            try:
                result = bot.engine.analyze_single_asset(
                    symbol=symbol,
                    asset_type=asset.lower(),
                    timeframe=tf,
                    backtest=False
                )
                
                signal = result.get('signal', 'NEUTRAL')
                confidence = result.get('confidence', 0)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if signal == 'BUY':
                        st.success(f"## BUY")
                    elif signal == 'SELL':
                        st.error(f"## SELL")
                    else:
                        st.warning(f"## NEUTRAL")
                with col2:
                    st.metric("Confidence", f"{confidence:.1f}%")
                with col3:
                    st.metric("Quality", result.get('quality', 'N/A'))
                
                st.json(result)
            except Exception as e:
                st.error(f"Analysis error: {e}")
    else:
        st.error("config.json not found")
except Exception as e:
    st.error(f"Bot import error: {e}")
    import traceback
    st.write(traceback.format_exc())
