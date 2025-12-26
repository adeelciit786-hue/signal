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

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Title
st.title("📈 Signals Bot - Trading Analysis")
st.markdown("Professional Multi-Confirmation Trading Strategy")

# Load bot engine
@st.cache_resource
def load_bot():
    try:
        from src.bot_engine import BotOrchestrator
        
        # Try to load config
        config_path = 'config.json'
        if not os.path.exists(config_path):
            st.error(f"Config.json not found at {config_path}")
            return None
        
        bot = BotOrchestrator(config_path)
        return bot
    except Exception as e:
        st.error(f"Failed to load bot: {str(e)}")
        return None

# Sidebar configuration
st.sidebar.header("Configuration")

# Asset and symbol selection
asset_type = st.sidebar.selectbox(
    "Asset Type",
    ["Crypto", "Stock", "Forex"]
)

symbol_map = {
    "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT"],
    "Stock": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"],
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD"]
}

symbol = st.sidebar.selectbox("Symbol", symbol_map[asset_type])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])

st.sidebar.markdown("---")

# Load bot
bot = load_bot()

if bot:
    st.sidebar.success("Bot Ready")
    
    # Analyze button
    if st.sidebar.button("Analyze", type="primary", use_container_width=True):
        try:
            with st.spinner(f"Analyzing {symbol}..."):
                analysis = bot.engine.analyze_single_asset(
                    symbol=symbol,
                    asset_type=asset_type.lower(),
                    timeframe=timeframe,
                    backtest=False
                )
            
            if analysis:
                # Create tabs
                tab1, tab2, tab3, tab4 = st.tabs(["Signal", "Confirmations", "Setup", "Risk"])
                
                # Tab 1: Signal
                with tab1:
                    signal = analysis.get('signal', 'NEUTRAL')
                    confidence = analysis.get('confidence', 0)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if signal == 'BUY':
                            st.success(f"### {signal}")
                        elif signal == 'SELL':
                            st.error(f"### {signal}")
                        else:
                            st.warning(f"### {signal}")
                    with col2:
                        st.metric("Confidence", f"{confidence:.1f}%")
                    with col3:
                        st.metric("Quality", analysis.get('quality', 'N/A'))
                    
                    st.markdown("---")
                    reasons = analysis.get('reasons', {})
                    if reasons.get('bullish_reasons'):
                        st.write("**Analysis Reasons:**")
                        for reason in reasons.get('bullish_reasons', [])[:3]:
                            st.write(f"• {reason}")
                
                # Tab 2: Confirmations
                with tab2:
                    confirmations = analysis.get('confirmations', {})
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Trend", confirmations.get('trend', 'N/A'))
                    with col2:
                        momentum = "Yes" if confirmations.get('momentum_confirmed') else "No"
                        st.metric("Momentum", momentum)
                    with col3:
                        volume = "Yes" if confirmations.get('volume_confirmed') else "No"
                        st.metric("Volume", volume)
                    with col4:
                        volatility = "OK" if confirmations.get('volatility_acceptable') else "High"
                        st.metric("Volatility", volatility)
                
                # Tab 3: Setup
                with tab3:
                    setup = analysis.get('setup', {})
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                    with col2:
                        st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
                    with col3:
                        st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
                    
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("R:R Ratio", f"{setup.get('rr_ratio', 0):.2f}:1")
                    with col2:
                        st.metric("Position Size", f"{setup.get('position_size', 0):.4f}")
                
                # Tab 4: Risk
                with tab4:
                    risk_validation = analysis.get('risk_validation', {})
                    
                    if risk_validation.get('allowed'):
                        st.success("Risk Rules APPROVED")
                    else:
                        st.error("Risk Rules REJECTED")
                    
                    st.markdown("---")
                    reasons_list = risk_validation.get('reasons', [])
                    if reasons_list:
                        st.write("**Risk Checks:**")
                        for reason in reasons_list[:5]:
                            st.write(f"• {reason}")
            else:
                st.error("Analysis returned no data")
        
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
else:
    st.warning("Bot engine not available")
    st.info("""
    ### Setup Required
    
    Make sure:
    1. config.json exists in the root directory
    2. All dependencies are installed
    3. Bot engine modules are in src/ folder
    """)
