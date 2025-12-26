"""
ENHANCED SIGNALS BOT - Professional Trading Signal Analyzer
Displays charts with BUY/SELL markers, detailed technical analysis, and risk assessment
Works in all environments with full indicator visualization
"""

import streamlit as st
import sys
import os
import logging
from pathlib import Path

# Configure Streamlit
st.set_page_config(
    page_title="Professional Trading Signals",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for better styling
st.markdown("""
    <style>
        .signal-buy {
            background-color: rgba(0, 200, 0, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #00CC00;
        }
        .signal-sell {
            background-color: rgba(255, 50, 50, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF3333;
        }
        .signal-neutral {
            background-color: rgba(255, 184, 28, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FFB81C;
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("📈 Professional Trading Signal Analyzer")
st.markdown("*Accurate BUY/SELL signals with technical analysis, charts, and risk management*")

# Initialize session state
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None


# ========== SIDEBAR CONFIGURATION ==========
st.sidebar.markdown("## ⚙️ Configuration")

asset_type = st.sidebar.selectbox(
    "Asset Type",
    ["Crypto", "Stock", "Forex"],
    help="Select the type of asset to analyze"
)

# Symbol selection based on asset type
symbols = {
    "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"],
    "Stock": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META"],
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "NZD/USD"]
}

symbol = st.sidebar.selectbox(
    "Symbol",
    symbols[asset_type],
    help="Select the trading symbol"
)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["15m", "30m", "1h", "4h", "1d", "1w"],
    help="Candlestick timeframe for analysis"
)

# Risk settings
st.sidebar.markdown("---")
st.sidebar.markdown("## 🛡️ Risk Settings")

max_risk_percent = st.sidebar.slider(
    "Max Risk per Trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="Maximum percentage of account to risk per trade"
)

min_confidence = st.sidebar.slider(
    "Minimum Signal Confidence (%)",
    min_value=50,
    max_value=90,
    value=65,
    help="Only show signals above this confidence level"
)

# Additional options
st.sidebar.markdown("---")
show_indicators = st.sidebar.checkbox("Show Detailed Indicators", value=True)
show_reasoning = st.sidebar.checkbox("Show Signal Reasoning", value=True)


# ========== LOAD BOT ENGINE ==========
try:
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from bot_engine import BotOrchestrator
    from chart_visualizer import ChartVisualizer, display_trading_analysis
    
    if not os.path.exists('config.json'):
        st.error("❌ config.json not found! Please ensure the configuration file exists.")
        st.stop()
    
    bot = BotOrchestrator('config.json')
    logger.info("✓ Bot engine loaded successfully")
    
except Exception as e:
    st.error(f"❌ Failed to load bot engine: {str(e)}")
    logger.error(f"Bot loading error: {e}")
    st.stop()


# ========== MAIN ANALYSIS SECTION ==========
st.markdown("---")

# Generate signal button
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    analyze_button = st.button(
        "🔍 Analyze and Generate Signal",
        type="primary",
        use_container_width=True,
        help="Click to analyze the selected symbol and generate a trading signal"
    )

with col2:
    refresh_button = st.button("🔄 Refresh", use_container_width=True)

with col3:
    clear_button = st.button("🗑️ Clear", use_container_width=True)

if clear_button:
    st.session_state.analysis_result = None
    st.rerun()


# ========== SIGNAL ANALYSIS ==========
if analyze_button or st.session_state.analysis_result:
    
    if analyze_button:
        # Show spinner while analyzing
        with st.spinner(f"🔄 Analyzing {symbol} on {timeframe} timeframe..."):
            try:
                # Perform analysis
                analysis = bot.engine.analyze_single_asset(
                    symbol=symbol,
                    asset_type=asset_type.lower(),
                    timeframe=timeframe,
                    backtest=False
                )
                
                # Store in session state
                st.session_state.analysis_result = {
                    'analysis': analysis,
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'asset_type': asset_type
                }
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                logger.error(f"Analysis error: {e}")
                st.stop()
    
    # Display stored result
    if st.session_state.analysis_result:
        result = st.session_state.analysis_result
        analysis = result['analysis']
        symbol = result['symbol']
        timeframe = result['timeframe']
        
        signal = analysis.get('signal', 'NEUTRAL')
        confidence = analysis.get('confidence', 0)
        setup = analysis.get('setup', {})
        confirmations = analysis.get('confirmations', {})
        risk_validation = analysis.get('risk_validation', {})
        quality = analysis.get('quality', 'NEUTRAL')
        
        # ========== SIGNAL HEADER ==========
        st.markdown("---")
        
        if signal == 'BUY' and confidence >= min_confidence:
            st.markdown("""
                <div class="signal-buy">
                    <h2 style="color: #00CC00; margin: 0;">🟢 BUY SIGNAL</h2>
                    <h3 style="color: #00CC00; margin: 0;">Confidence: {:.1f}%</h3>
                    <p style="margin: 0;">Quality: <strong>{}</strong></p>
                </div>
            """.format(confidence, quality), unsafe_allow_html=True)
            
        elif signal == 'SELL' and confidence >= min_confidence:
            st.markdown("""
                <div class="signal-sell">
                    <h2 style="color: #FF3333; margin: 0;">🔴 SELL SIGNAL</h2>
                    <h3 style="color: #FF3333; margin: 0;">Confidence: {:.1f}%</h3>
                    <p style="margin: 0;">Quality: <strong>{}</strong></p>
                </div>
            """.format(confidence, quality), unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="signal-neutral">
                    <h2 style="color: #FFB81C; margin: 0;">🟡 NEUTRAL / INSUFFICIENT SIGNAL</h2>
                    <h3 style="color: #FFB81C; margin: 0;">Confidence: {:.1f}%</h3>
                    <p style="margin: 0;">⚠️ Signal below minimum confidence threshold or data insufficient</p>
                </div>
            """.format(confidence), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ========== CHART DISPLAY ==========
        if 'dataframe' in analysis and analysis['dataframe'] is not None:
            try:
                st.subheader("📊 Price Chart with Signal Markers")
                
                fig_chart = ChartVisualizer.create_signal_chart(
                    analysis['dataframe'],
                    signal,
                    confidence,
                    symbol,
                    timeframe,
                    setup
                )
                st.plotly_chart(fig_chart, use_container_width=True)
                
            except Exception as e:
                st.warning(f"Could not display main chart: {e}")
        
        # ========== TRADE SETUP ==========
        st.subheader("💰 Trade Setup Details")
        
        setup_col1, setup_col2, setup_col3, setup_col4 = st.columns(4)
        
        with setup_col1:
            entry = setup.get('entry', 0)
            st.metric(
                "Entry Price",
                f"${entry:.4f}" if entry > 0 else "N/A",
                help="Entry point for the trade"
            )
        
        with setup_col2:
            sl = setup.get('stop_loss', 0)
            st.metric(
                "Stop Loss",
                f"${sl:.4f}" if sl > 0 else "N/A",
                help="Risk management - price at which to exit with loss"
            )
        
        with setup_col3:
            tp = setup.get('take_profit', 0)
            st.metric(
                "Take Profit",
                f"${tp:.4f}" if tp > 0 else "N/A",
                help="Target profit - price at which to take profit"
            )
        
        with setup_col4:
            rr = setup.get('rr_ratio', 0)
            st.metric(
                "Risk:Reward Ratio",
                f"{rr:.2f}:1" if rr > 0 else "N/A",
                help="Profit potential vs risk (higher is better, min 1.5:1 recommended)"
            )
        
        st.markdown("---")
        
        # ========== TECHNICAL CONFIRMATIONS ==========
        st.subheader("✓ Technical Confirmations")
        
        conf_col1, conf_col2, conf_col3 = st.columns(3)
        
        with conf_col1:
            trend = confirmations.get('trend', 'N/A')
            trend_strength = confirmations.get('trend_strength', '0%')
            
            if 'BULLISH' in str(trend):
                st.success(f"**Trend:** {trend}")
            elif 'BEARISH' in str(trend):
                st.error(f"**Trend:** {trend}")
            else:
                st.info(f"**Trend:** {trend}")
            
            st.caption(f"Strength: {trend_strength}")
        
        with conf_col2:
            momentum_ok = confirmations.get('momentum_confirmed', False)
            momentum_strength = confirmations.get('momentum_strength', '0%')
            
            if momentum_ok:
                st.success("**Momentum:** Confirmed ✓")
            else:
                st.warning("**Momentum:** Not Confirmed ✗")
            
            st.caption(f"Strength: {momentum_strength}")
        
        with conf_col3:
            volume_ok = confirmations.get('volume_confirmed', False)
            volatility_ok = confirmations.get('volatility_acceptable', False)
            
            if volume_ok:
                st.success("**Volume:** Confirmed ✓")
            else:
                st.info("**Volume:** Low (⚠️ but OK)")
            
            if volatility_ok:
                st.caption("Volatility: Acceptable ✓")
            else:
                st.caption("Volatility: High ⚠️")
        
        # Add explanation of signal logic
        st.markdown("---")
        with st.expander("📖 How Signals Are Generated (Click to expand)", expanded=False):
            st.markdown("""
            ### Signal Generation Logic
            
            **PRIMARY REQUIREMENTS (MUST have both):**
            1. ✓ **Trend**: BULLISH (>45% confidence) OR BEARISH (>45% confidence)
            2. ✓ **Momentum**: Confirmed by indicators (>45% confidence)
            
            **SECONDARY FACTORS (Enhance signal quality):**
            - 📊 **Volume**: Confirmed = bonus +5% confidence
            - 🌊 **Volatility**: Acceptable range = no penalty
            
            **SIGNAL TYPES:**
            - 🟢 **BUY**: Bullish trend + Momentum confirmed
            - 🔴 **SELL**: Bearish trend + Momentum confirmed  
            - 🟡 **NEUTRAL**: No clear trend OR momentum not confirmed
            
            **Why you might see signals with low volume?**
            - In range-bound markets, volume is naturally lower
            - Momentum indicators still confirm the trend
            - Modern algorithms trade off momentum alone
            - Low volume doesn't invalidate the signal
            
            **Confidence Scoring:**
            - Base: (Trend% + Momentum%) / 2
            - Bonus: +5% if volume also confirms
            - Maximum: 95% (leave 5% margin for uncertainty)
            """)
        
        st.markdown("---")
        
        # ========== DETAILED INDICATORS (Optional) ==========
        if show_indicators:
            st.subheader("📈 Detailed Technical Indicators")
            
            try:
                fig_indicators = ChartVisualizer.create_indicator_panel(
                    analysis['dataframe'],
                    symbol
                )
                st.plotly_chart(fig_indicators, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not display indicator panel: {e}")
        
        # ========== SIGNAL REASONING (Optional) ==========
        if show_reasoning:
            st.subheader("💭 Signal Analysis Reasoning")
            
            reasons = analysis.get('reasons', {})
            
            with st.expander("Why this signal?", expanded=True):
                bullish = reasons.get('bullish_reasons', [])
                momentum = reasons.get('momentum_indicators', [])
                volume_status = reasons.get('volume_status', 'No data')
                volatility_status = reasons.get('volatility_status', 'No data')
                
                if bullish:
                    st.markdown("**Bullish Signals:**")
                    for reason in bullish[:5]:
                        st.markdown(f"• {reason}")
                
                if momentum:
                    st.markdown("**Momentum Confirmations:**")
                    for ind in momentum[:5]:
                        st.markdown(f"• {ind}")
                
                if volume_status != 'No data':
                    st.markdown(f"**Volume:** {volume_status}")
                
                if volatility_status != 'No data':
                    st.markdown(f"**Volatility:** {volatility_status}")
        
        # ========== RISK ASSESSMENT ==========
        st.subheader("⚠️ Risk Assessment")
        
        is_allowed = risk_validation.get('allowed', False)
        
        if is_allowed and signal != 'NEUTRAL':
            st.success("✓ RISK APPROVED - Trade meets all risk criteria")
        elif signal == 'NEUTRAL':
            st.warning("⚠️ No signal generated - wait for clearer market conditions")
        else:
            st.error("✗ RISK REJECTED - Trade does not meet risk criteria")
        
        # Risk checks
        with st.expander("Risk Check Details"):
            checks = risk_validation.get('checks', {})
            
            for check_name, check_result in checks.items():
                if isinstance(check_result, dict):
                    is_valid = check_result.get('valid', False)
                    reason = check_result.get('reason', 'No details')
                    
                    if is_valid:
                        st.info(f"✓ {check_name}: {reason}")
                    else:
                        st.warning(f"⚠️ {check_name}: {reason}")
        
        st.markdown("---")
        
        # ========== DISCLAIMER ==========
        st.info(
            "⚠️ **DISCLAIMER**: This is for educational purposes only. "
            "Always perform your own due diligence and risk assessment before trading. "
            "Past performance does not guarantee future results."
        )

else:
    st.info("👈 Configure options in the sidebar and click 'Analyze and Generate Signal' to begin")


