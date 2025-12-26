"""
Signals Bot - Streamlit Web Application
Professional Trading Signal Generator with Multi-Confirmation Strategy
"""

import streamlit as st
import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.bot_engine import BotOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Signals Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .main {
            padding: 0rem 1rem;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_bot():
    """Load bot engine once"""
    try:
        return BotOrchestrator('config.json')
    except Exception as e:
        st.error(f"Failed to load bot: {e}")
        return None

def main():
    # Header
    st.title("📈 Signals Bot - Professional Trading Analysis")
    st.markdown("Multi-Confirmation Strategy | Risk-Managed Trading")
    
    # Sidebar
    st.sidebar.header("⚙️ Configuration")
    
    # Load bot
    bot = load_bot()
    if not bot:
        st.error("Failed to initialize bot engine. Check configuration.")
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
    
    # Symbol selection based on asset type
    if asset_type == "Crypto":
        symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", 
                   "DOGE/USDT", "DOT/USDT", "LINK/USDT"]
    elif asset_type == "Stock":
        symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "AMD", "IBM", "JPM"]
    else:  # Forex
        symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "USD/CHF"]
    
    symbol = st.sidebar.selectbox(
        "Select Symbol",
        symbols,
        help=f"Choose a {asset_type} symbol to analyze"
    )
    
    # Timeframe selection
    timeframe = st.sidebar.selectbox(
        "Timeframe",
        ["1h", "4h", "1d", "1w"],
        help="Select the timeframe for technical analysis"
    )
    
    # Risk settings
    st.sidebar.markdown("---")
    st.sidebar.subheader("Risk Management")
    
    account_balance = st.sidebar.number_input(
        "Account Balance ($)",
        min_value=100,
        value=10000,
        step=100,
        help="Your trading account balance"
    )
    
    risk_percent = st.sidebar.slider(
        "Risk per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Maximum percentage of account to risk per trade"
    )
    
    min_rr_ratio = st.sidebar.slider(
        "Minimum R:R Ratio",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="Minimum risk-to-reward ratio"
    )
    
    # Analysis button
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
                # Run analysis
                analysis = bot.engine.analyze_single_asset(
                    symbol=symbol,
                    asset_type=asset_type_val,
                    timeframe=timeframe,
                    backtest=False
                )
                
                if not analysis:
                    st.error("Analysis failed. Please try again.")
                    return
                
                # Display results in tabs
                tabs = st.tabs(["Signal", "Confirmations", "Setup", "Risk Analysis", "Market Analysis"])
                
                # Tab 1: Signal
                with tabs[0]:
                    col1, col2, col3 = st.columns(3)
                    
                    signal = analysis.get('signal', 'NEUTRAL')
                    confidence = analysis.get('confidence', 0)
                    quality = analysis.get('quality', 'NEUTRAL')
                    
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
                        st.metric("Quality", quality)
                    
                    st.markdown("---")
                    
                    # Reasons
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
                        trend = confirmations.get('trend', 'N/A')
                        st.metric("Trend", trend, confirmations.get('trend_strength', 'N/A'))
                    
                    with col2:
                        momentum = "✓ YES" if confirmations.get('momentum_confirmed') else "✗ NO"
                        st.metric("Momentum", momentum, confirmations.get('momentum_strength', 'N/A'))
                    
                    with col3:
                        volume = "✓ YES" if confirmations.get('volume_confirmed') else "✗ NO"
                        st.metric("Volume", volume)
                    
                    with col4:
                        volatility = "✓ OK" if confirmations.get('volatility_acceptable') else "✗ RISKY"
                        st.metric("Volatility", volatility)
                    
                    st.markdown("---")
                    st.write("**Multi-Confirmation Analysis:**")
                    
                    detailed = analysis.get('detailed_analysis', {})
                    if detailed:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            trend_det = detailed.get('trend', {})
                            st.write(f"**Trend Details:**")
                            st.write(f"- ADX: {trend_det.get('adx', 'N/A')}")
                            st.write(f"- Confidence: {trend_det.get('confidence', 'N/A')}%")
                        
                        with col2:
                            momentum_det = detailed.get('momentum', {})
                            st.write(f"**Momentum Details:**")
                            st.write(f"- RSI: {momentum_det.get('rsi', 'N/A')}")
                            st.write(f"- MFI: {momentum_det.get('mfi', 'N/A')}")
                
                # Tab 3: Setup
                with tabs[2]:
                    setup = analysis.get('setup', {})
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Entry Price", f"${setup.get('entry', 0):.2f}")
                    
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
                    st.write("**Risk Validation Results:**")
                    
                    risk_valid = analysis.get('risk_validation', {})
                    if risk_valid.get('allowed'):
                        st.success("✓ Risk rules APPROVED - Safe to trade")
                    else:
                        st.error("✗ Risk rules REJECTED - Do not trade")
                    
                    st.markdown("---")
                    
                    reasons = risk_valid.get('reasons', [])
                    if reasons:
                        st.write("**Risk Checks:**")
                        for reason in reasons:
                            if "✓" in reason or "Approved" in reason or "passed" in reason:
                                st.success(reason)
                            elif "✗" in reason or "Rejected" in reason or "failed" in reason:
                                st.error(reason)
                            else:
                                st.info(reason)
                
                # Tab 5: Market Analysis
                with tabs[4]:
                    detailed = analysis.get('detailed_analysis', {})
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Market Regime:**")
                        regime = analysis.get('market_regime', 'UNKNOWN')
                        st.info(regime)
                    
                    with col2:
                        st.write("**Sentiment:**")
                        sentiment = analysis.get('sentiment', 'NEUTRAL')
                        if sentiment == 'POSITIVE':
                            st.success(sentiment)
                        elif sentiment == 'NEGATIVE':
                            st.error(sentiment)
                        else:
                            st.warning(sentiment)
                    
                    st.markdown("---")
                    
                    vol_det = detailed.get('volatility', {})
                    if vol_det:
                        st.write(f"**Volatility Info:**")
                        st.write(f"- Status: {vol_det.get('reason', 'N/A')}")
                        st.write(f"- ATR: {vol_det.get('atr', 'N/A')}")
                
            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {e}", exc_info=True)
    else:
        # Welcome message
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
        - 8 Cryptocurrencies (BTC, ETH, SOL, XRP, ADA, DOGE, DOT, LINK)
        - 10 Stocks (AAPL, GOOGL, MSFT, TSLA, AMZN, META, NVDA, AMD, IBM, JPM)
        - 7 Forex Pairs (EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, EUR/GBP, USD/CHF)
        
        **How to Use:**
        1. Select asset type and symbol from sidebar
        2. Choose timeframe for analysis
        3. Configure risk parameters
        4. Click "Analyze" button to generate signals
        
        **Important:** Always validate signals before trading. Capital preservation is key.
        """)

if __name__ == "__main__":
    main()
