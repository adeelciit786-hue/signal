"""
Streamlit App for Signals Bot - Professional Trading Signal Generator
"""
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Page config
st.set_page_config(
    page_title="Signals Bot - Trading Signals",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("🤖 Signals Bot - Trading Signal Generator")
st.markdown("Professional Multi-Asset Analysis | BUY/SELL Signals with Risk Assessment")
st.divider()

# Load modules
try:
    import bot_config
    import bot_engine
    BotConfig = bot_config.BotConfig
    BotOrchestrator = bot_engine.BotOrchestrator
except Exception as e:
    st.error(f"❌ Error loading modules: {str(e)}")
    st.stop()

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Analysis Configuration")
    
    # Asset Type Selection
    asset_type = st.selectbox(
        "Select Asset Type",
        ["crypto", "forex", "stock"],
        help="Choose between Cryptocurrency, Forex, or Stocks"
    )
    
    # Symbol Selection based on Asset Type
    if asset_type == "crypto":
        symbols = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "SOL/USDT", "DOGE/USDT", "DOT/USDT"]
        symbol = st.selectbox("Select Cryptocurrency", symbols)
    elif asset_type == "forex":
        symbols = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "NZD/USD", "CAD/USD"]
        symbol = st.selectbox("Select Forex Pair", symbols)
    else:  # stock
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "BAC", "GS"]
        symbol = st.selectbox("Select Stock", symbols)
    
    # Timeframe Selection
    timeframe = st.selectbox(
        "Select Timeframe",
        ["1h", "4h", "1d", "1w"],
        help="Analysis timeframe for the signal"
    )
    
    st.divider()
    
    # Risk Settings
    st.subheader("💰 Risk Management")
    account_balance = st.number_input(
        "Account Balance ($)",
        min_value=100,
        value=10000,
        step=1000,
        help="Your trading account balance"
    )
    
    risk_percent = st.slider(
        "Risk per Trade (%)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        help="Percentage of account to risk on each trade"
    )
    
    min_rr_ratio = st.slider(
        "Minimum R:R Ratio",
        min_value=1.0,
        max_value=5.0,
        value=2.0,
        step=0.5,
        help="Risk to Reward ratio (must be at least this to trade)"
    )
    
    # Backtest toggle
    backtest_enabled = st.checkbox(
        "Run Backtest",
        value=True,
        help="Validate signal with historical data"
    )
    
    st.divider()
    
    # Analyze Button
    analyze_btn = st.button(
        "🔍 Analyze & Generate Signal",
        use_container_width=True,
        type="primary"
    )

# Main Content Area
if analyze_btn:
    st.info(f"🔄 Analyzing {symbol} ({timeframe}) on {asset_type}...")
    
    with st.spinner("Running analysis... Please wait"):
        try:
            # Create configuration
            config = BotConfig()
            config.set('account_balance', account_balance)
            config.set('risk_percent', risk_percent)
            config.set('min_rr_ratio', min_rr_ratio)
            
            # Create bot and analyze
            bot = BotOrchestrator(config)
            result = bot.analyze_single_asset(
                symbol=symbol,
                asset_type=asset_type,
                timeframe=timeframe,
                backtest=backtest_enabled
            )
            
            if result:
                # Signal Display - Large and Prominent
                st.divider()
                signal = result.get('signal', 'NEUTRAL')
                confidence = result.get('confidence', 0)
                quality = result.get('quality', 'NEUTRAL')
                
                # Color code the signal
                if signal == 'BUY':
                    signal_color = '🟢'
                    signal_bg = 'background-color: #d4edda; padding: 20px; border-radius: 10px; border-left: 5px solid #28a745;'
                elif signal == 'SELL':
                    signal_color = '🔴'
                    signal_bg = 'background-color: #f8d7da; padding: 20px; border-radius: 10px; border-left: 5px solid #dc3545;'
                else:
                    signal_color = '🟡'
                    signal_bg = 'background-color: #fff3cd; padding: 20px; border-radius: 10px; border-left: 5px solid #ffc107;'
                
                # Main Signal Box
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 SIGNAL", f"{signal_color} {signal}", delta=None)
                with col2:
                    st.metric("📈 Confidence", f"{confidence:.1f}%", delta=None)
                with col3:
                    st.metric("⭐ Quality", quality, delta=None)
                with col4:
                    if backtest_enabled and 'backtest' in result:
                        win_rate = result['backtest'].get('win_rate', 0)
                        st.metric("✓ Win Rate", f"{win_rate:.1f}%", delta=None)
                
                st.divider()
                
                # Confirmations Section
                st.subheader("✓ Multi-Confirmation Analysis")
                st.markdown("**All of these must confirm for a strong signal:**")
                
                confirmations = result.get('confirmations', {})
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    trend = confirmations.get('trend', 'N/A')
                    trend_strength = confirmations.get('trend_strength', 'N/A')
                    if confirmations.get('trend_confirmed'):
                        st.success(f"✅ **Trend:** {trend}\n({trend_strength})")
                    else:
                        st.warning(f"❌ **Trend:** {trend}\n({trend_strength})")
                
                with col2:
                    if confirmations.get('momentum_confirmed'):
                        st.success(f"✅ **Momentum:** Confirmed")
                    else:
                        st.warning(f"❌ **Momentum:** Not confirmed")
                
                with col3:
                    if confirmations.get('volume_confirmed'):
                        st.success(f"✅ **Volume:** Confirmed")
                    else:
                        st.warning(f"❌ **Volume:** Not confirmed")
                
                with col4:
                    if confirmations.get('volatility_acceptable'):
                        st.success(f"✅ **Volatility:** Safe")
                    else:
                        st.warning(f"⚠️ **Volatility:** High Risk")
                
                st.divider()
                
                # Setup Details
                st.subheader("🎯 Trade Setup")
                setup = result.get('setup', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    entry = setup.get('entry', 0)
                    st.metric("📍 Entry Price", f"${entry:.4f}", delta=None)
                
                with col2:
                    sl = setup.get('stop_loss', 0)
                    st.metric("🛑 Stop Loss", f"${sl:.4f}", delta=None)
                
                with col3:
                    tp = setup.get('take_profit', 0)
                    st.metric("🎁 Take Profit", f"${tp:.4f}", delta=None)
                
                rr = setup.get('rr_ratio', 0)
                st.metric("📊 Risk:Reward Ratio", f"{rr:.2f}:1", help="Higher is better")
                
                st.divider()
                
                # Risk Assessment
                st.subheader("⚠️ Risk Assessment")
                risk_check = result.get('risk_check', {})
                allowed = risk_check.get('allowed', False)
                reasons = risk_check.get('reasons', [])
                
                if allowed:
                    st.success(f"✅ **TRADE APPROVED** - All risk checks passed!")
                    st.write("**Why it's safe:**")
                    for reason in reasons:
                        st.write(f"✓ {reason}")
                else:
                    st.error(f"❌ **TRADE REJECTED** - Risk checks failed!")
                    st.write("**Why it's risky:**")
                    for reason in reasons:
                        st.write(f"✗ {reason}")
                
                # Fear/Greed Indicator
                st.divider()
                st.subheader("😨 Fear/Greed Index")
                fear_score = 100 - confidence  # Inverse of confidence
                greed_score = confidence
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("😨 Fear Level", f"{fear_score:.1f}%", help="How scared you should be")
                with col2:
                    st.metric("🤑 Greed Level", f"{greed_score:.1f}%", help="How greedy you should be")
                
                if fear_score > 70:
                    st.warning("⚠️ **HIGH FEAR** - Very cautious, small position or skip trade")
                elif fear_score > 40:
                    st.info("📊 **MODERATE FEAR** - Standard position size")
                else:
                    st.success("😊 **LOW FEAR** - Good confidence, can increase position")
                
                # Backtest Results
                if backtest_enabled and 'backtest' in result:
                    st.divider()
                    st.subheader("📈 Historical Backtest Results")
                    st.markdown("**How this signal performed in the past 30 days:**")
                    
                    backtest = result['backtest']
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Trades", f"{backtest.get('total_trades', 0)}", help="Total signals generated")
                    with col2:
                        st.metric("Win Rate", f"{backtest.get('win_rate', 0):.1f}%", help="% of trades that were profitable")
                    with col3:
                        st.metric("Max Drawdown", f"{backtest.get('max_drawdown', 0):.2f}%", help="Largest losing period")
                    with col4:
                        pnl = backtest.get('total_pnl', 0)
                        pnl_pct = backtest.get('total_pnl_percent', 0)
                        st.metric("Total P&L", f"${pnl:.2f}", f"{pnl_pct:.2f}%")
                
                # Analysis Details
                with st.expander("📋 View Full Analysis Details"):
                    st.json(result)
            
            else:
                st.error("❌ No analysis results. Please try a different symbol or timeframe.")
        
        except Exception as e:
            st.error(f"❌ Analysis Error: {str(e)}")
            with st.expander("📋 Error Details"):
                import traceback
                st.code(traceback.format_exc())

else:
    # Welcome Section
    st.info("""
    ### 👋 Welcome to Signals Bot!
    
    **Professional Trading Signal Generator with Real-Time Analysis**
    
    #### 🎯 Features:
    - **Multi-Confirmation Strategy**: Trend + Momentum + Volume + Volatility checks
    - **BUY/SELL Signals**: Clear entry, stop loss, and take profit levels
    - **Risk Management**: Automatic position sizing and risk assessment
    - **Fear/Greed Index**: Know when to be cautious or confident
    - **Historical Validation**: Backtest signals on past 30 days of data
    - **Multiple Assets**: Crypto, Forex, and Stocks
    
    #### 🚀 How to Use:
    1. **Select Asset Type**: Choose Crypto, Forex, or Stock
    2. **Pick Your Pair**: Select the trading pair you want to analyze
    3. **Choose Timeframe**: 1h, 4h, 1d, or 1w
    4. **Configure Risk**: Set your account size and risk per trade
    5. **Click Analyze**: Generate your signal
    6. **Review Results**: Check the buy/sell signal and risk assessment
    
    #### ✅ What Each Section Means:
    - **SIGNAL**: BUY (green), SELL (red), or NEUTRAL (yellow)
    - **Confidence**: How confident the signal is (0-100%)
    - **Confirmations**: All 4 must be positive for strong signal
    - **Setup**: Entry price, stop loss, take profit
    - **Risk Assessment**: Is it safe to trade?
    - **Fear/Greed**: Your psychological risk indicator
    
    #### ⚠️ Disclaimer:
    This tool is for **educational purposes only**. Not financial advice.
    Always do your own research and use proper risk management.
    
    ---
    
    **👈 Start by selecting your asset type in the sidebar!**
    """)

st.divider()
st.caption("🔐 Signals Bot v2.0 | Multi-Confirmation Trading Strategy | All Rights Reserved")
