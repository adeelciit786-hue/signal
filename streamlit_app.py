"""
Signals Bot - Streamlit Web Application
Professional Trading Signal Generator with Multi-Confirmation Strategy
"""

import streamlit as st
import sys
from pathlib import Path
import logging
import os

# Configure logging first
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Page configuration FIRST
st.set_page_config(
    page_title="Signals Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Display title first
st.title("📈 Signals Bot - Professional Trading Analysis")
st.markdown("Multi-Confirmation Strategy | Risk-Managed Trading")

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Try to import bot engine
try:
    from src.bot_engine import BotOrchestrator
    bot_import_success = True
except Exception as e:
    st.error(f"⚠️ Failed to import bot engine: {e}")
    bot_import_success = False

# Load bot with caching
@st.cache_resource
def load_bot():
    """Load bot engine once"""
    try:
        if not bot_import_success:
            return None
        
        config_path = 'config.json'
        if not os.path.exists(config_path):
            st.error(f"Config file not found: {config_path}")
            return None
            
        return BotOrchestrator(config_path)
    except Exception as e:
        st.error(f"Failed to load bot: {e}")
        logger.error(f"Bot load error: {e}", exc_info=True)
        return None

# Main app
def main():
    try:
        # Sidebar
        st.sidebar.header("⚙️ Configuration")
        
        # Load bot
        bot = load_bot()
        
        if not bot:
            st.warning("⚠️ Bot engine not available. Showing demo mode.")
            show_welcome()
            return
        
        # Asset selection
        asset_type = st.sidebar.selectbox(
            "Asset Type",
            ["Crypto", "Stock", "Forex"],
            help="Select the type of asset to analyze"
        )
        
        asset_type_map = {
            "Crypto": "crypto",
            "Stock": "stock",
            "Forex": "forex"
        }
        asset_type_val = asset_type_map[asset_type]
        
        # Symbol selection
        if asset_type == "Crypto":
            symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", 
                      "DOGE/USDT", "DOT/USDT", "LINK/USDT"]
        elif asset_type == "Stock":
            symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "AMD", "IBM", "JPM"]
        else:
            symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "USD/CHF"]
        
        symbol = st.sidebar.selectbox("Select Symbol", symbols)
        
        # Timeframe
        timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
        
        # Risk settings
        st.sidebar.markdown("---")
        st.sidebar.subheader("Risk Management")
        
        account_balance = st.sidebar.number_input(
            "Account Balance ($)",
            min_value=100,
            value=10000,
            step=100
        )
        
        risk_percent = st.sidebar.slider(
            "Risk per Trade (%)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        
        # Analyze button
        st.sidebar.markdown("---")
        analyze_button = st.sidebar.button(
            "🔍 Analyze",
            use_container_width=True,
            type="primary"
        )
        
        # Main content
        if analyze_button:
            with st.spinner(f"Analyzing {symbol}..."):
                try:
                    analysis = bot.engine.analyze_single_asset(
                        symbol=symbol,
                        asset_type=asset_type_val,
                        timeframe=timeframe,
                        backtest=False
                    )
                    
                    if analysis:
                        display_analysis(analysis, symbol)
                    else:
                        st.error("Analysis returned no results")
                        
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
                    logger.error(f"Analysis error: {e}", exc_info=True)
        else:
            show_welcome()
    
    except Exception as e:
        st.error(f"App error: {str(e)}")
        logger.error(f"Main error: {e}", exc_info=True)

def show_welcome():
    """Show welcome information"""
    st.markdown("---")
    st.info("""
    ### Welcome to Signals Bot! 📊
    
    This professional trading analysis tool provides:
    
    **Multi-Confirmation Strategy:**
    - Trend Analysis (ADX, EMA, SMA)
    - Momentum Confirmation (RSI, MACD, ROC)
    - Volume Validation
    - Volatility Assessment
    
    **Risk Management:**
    - Position Sizing
    - Stop Loss Calculation
    - Take Profit Levels
    - Risk-to-Reward Ratio
    
    **Supported Assets:**
    - 8 Cryptocurrencies
    - 10 Stocks
    - 7 Forex Pairs
    
    **How to Use:**
    1. Select asset type and symbol from sidebar
    2. Choose timeframe for analysis
    3. Configure risk parameters
    4. Click "Analyze" button to generate signals
    
    **Important:** Always validate signals before trading!
    """)

def display_analysis(analysis, symbol):
    """Display analysis results"""
    
    # Tabs
    tabs = st.tabs(["Signal", "Confirmations", "Setup", "Risk Analysis"])
    
    # Tab 1: Signal
    with tabs[0]:
        signal = analysis.get('signal', 'NEUTRAL')
        confidence = analysis.get('confidence', 0)
        quality = analysis.get('quality', 'NEUTRAL')
        
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
            st.metric("Quality", quality)
        
        st.markdown("---")
        reasons = analysis.get('reasons', {})
        if reasons.get('bullish_reasons'):
            st.write("**Why This Signal:**")
            for reason in reasons['bullish_reasons'][:5]:
                st.write(f"• {reason}")
    
    # Tab 2: Confirmations
    with tabs[1]:
        confirmations = analysis.get('confirmations', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Trend", confirmations.get('trend', 'N/A'), 
                     confirmations.get('trend_strength', 'N/A'))
        with col2:
            momentum = "✓ YES" if confirmations.get('momentum_confirmed') else "✗ NO"
            st.metric("Momentum", momentum)
        with col3:
            volume = "✓ YES" if confirmations.get('volume_confirmed') else "✗ NO"
            st.metric("Volume", volume)
        with col4:
            volatility = "✓ OK" if confirmations.get('volatility_acceptable') else "✗ RISKY"
            st.metric("Volatility", volatility)
    
    # Tab 3: Setup
    with tabs[2]:
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
    
    # Tab 4: Risk Analysis
    with tabs[3]:
        risk_valid = analysis.get('risk_validation', {})
        
        if risk_valid.get('allowed'):
            st.success("✓ Risk rules APPROVED")
        else:
            st.error("✗ Risk rules REJECTED")
        
        st.markdown("---")
        reasons = risk_valid.get('reasons', [])
        if reasons:
            st.write("**Risk Checks:**")
            for reason in reasons[:5]:
                st.write(f"• {reason}")

if __name__ == "__main__":
    main()
