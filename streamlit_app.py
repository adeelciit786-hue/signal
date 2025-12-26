"""
Signals Bot - Streamlit Web Application
Professional Trading Signal Generator
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Page configuration MUST be first
st.set_page_config(
    page_title="Signals Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Show something immediately
st.write("Loading Signals Bot...")

# Add src to path
try:
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from src.bot_engine import BotOrchestrator
    bot_available = True
except Exception as e:
    st.error(f"Bot import failed: {e}")
    bot_available = False

# Main UI
st.title("📈 Signals Bot")
st.markdown("Professional Multi-Confirmation Trading Strategy")

if bot_available:
    # Load bot
    @st.cache_resource
    def load_bot():
        try:
            config_path = 'config.json'
            if not os.path.exists(config_path):
                return None
            return BotOrchestrator(config_path)
        except Exception as e:
            st.error(f"Bot load error: {e}")
            return None
    
    bot = load_bot()
    
    if bot:
        # Sidebar
        st.sidebar.header("Configuration")
        
        asset_type = st.sidebar.selectbox("Asset Type", ["Crypto", "Stock", "Forex"])
        
        if asset_type == "Crypto":
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT"]
        elif asset_type == "Stock":
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]
        else:
            symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD"]
        
        symbol = st.sidebar.selectbox("Symbol", symbols)
        timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
        
        st.sidebar.markdown("---")
        
        # Main content
        st.write(f"Selected: **{symbol}** | Timeframe: **{timeframe}**")
        
        if st.button("Analyze", type="primary", use_container_width=True):
            try:
                with st.spinner(f"Analyzing {symbol}..."):
                    analysis = bot.engine.analyze_single_asset(
                        symbol=symbol,
                        asset_type=asset_type.lower(),
                        timeframe=timeframe,
                        backtest=False
                    )
                
                if analysis:
                    # Signal
                    signal = analysis.get('signal', 'NEUTRAL')
                    confidence = analysis.get('confidence', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if signal == 'BUY':
                            st.success(f"## {signal}")
                        elif signal == 'SELL':
                            st.error(f"## {signal}")
                        else:
                            st.warning(f"## {signal}")
                    with col2:
                        st.metric("Confidence", f"{confidence:.1f}%")
                    with col3:
                        st.metric("Quality", analysis.get('quality', 'N/A'))
                    
                    # Tabs
                    tab1, tab2, tab3 = st.tabs(["Confirmations", "Setup", "Risk"])
                    
                    with tab1:
                        confirmations = analysis.get('confirmations', {})
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.metric("Trend", confirmations.get('trend', 'N/A'))
                        with c2:
                            st.metric("Momentum", "Yes" if confirmations.get('momentum_confirmed') else "No")
                        with c3:
                            st.metric("Volume", "Yes" if confirmations.get('volume_confirmed') else "No")
                        with c4:
                            st.metric("Volatility", "OK" if confirmations.get('volatility_acceptable') else "High")
                    
                    with tab2:
                        setup = analysis.get('setup', {})
                        s1, s2, s3 = st.columns(3)
                        with s1:
                            st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                        with s2:
                            st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
                        with s3:
                            st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
                    
                    with tab3:
                        risk = analysis.get('risk_validation', {})
                        if risk.get('allowed'):
                            st.success("Risk Rules APPROVED")
                        else:
                            st.error("Risk Rules REJECTED")
                else:
                    st.error("No analysis results")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("config.json not found - demo mode")
        st.info("""
        To enable full functionality:
        1. Ensure config.json exists in project root
        2. Check bot engine initialization
        """)
else:
    st.error("Bot engine not available")

