"""
Streamlit App for Signals Bot - Professional Trading Signal Generator
"""
import streamlit as st
import sys
import os

# Page config
st.set_page_config(
    page_title="Signals Bot",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("🤖 Signals Bot")
st.markdown("Professional Trading Signal Generator")
st.divider()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import modules
try:
    from bot_config import BotConfig
    from bot_engine import BotOrchestrator
except Exception as e:
    st.error(f"❌ Import Error: {e}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    asset_type = st.selectbox("Asset Type", ["crypto", "stock", "forex"])
    symbol = st.text_input("Symbol", value="BTC/USDT", placeholder="BTC/USDT")
    timeframe = st.selectbox("Timeframe", ["1h", "4h", "1d", "1w"])
    
    st.subheader("💰 Risk Settings")
    account = st.number_input("Account Balance", value=10000, min_value=100)
    risk = st.slider("Risk %", 0.1, 5.0, 1.0)
    rr = st.slider("Min R:R", 1.0, 5.0, 2.0)
    
    backtest = st.checkbox("Backtest", value=True)
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)

# Main
st.subheader("📊 Analysis")

if analyze_btn and symbol:
    with st.spinner("Analyzing..."):
        try:
            config = BotConfig()
            config.set('account_balance', account)
            config.set('risk_percent', risk)
            config.set('min_rr_ratio', rr)
            
            bot = BotOrchestrator(config)
            result = bot.analyze_single_asset(
                symbol=symbol,
                asset_type=asset_type,
                timeframe=timeframe,
                backtest=backtest
            )
            
            if result:
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    signal = result.get('signal', 'NEUTRAL')
                    color = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "🟡")
                    st.metric("Signal", f"{color} {signal}")
                with col2:
                    st.metric("Confidence", f"{result.get('confidence', 0):.1f}%")
                with col3:
                    st.metric("Quality", result.get('quality', 'N/A'))
                with col4:
                    bt = result.get('backtest', {})
                    st.metric("Win Rate", f"{bt.get('win_rate', 0):.1f}%")
                
                st.divider()
                
                # Confirmations
                st.subheader("✓ Confirmations")
                conf = result.get('confirmations', {})
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.write(f"Trend: **{conf.get('trend', 'N/A')}**")
                with col2:
                    st.write(f"Momentum: **{'✓' if conf.get('momentum_confirmed') else '✗'}**")
                with col3:
                    st.write(f"Volume: **{'✓' if conf.get('volume_confirmed') else '✗'}**")
                with col4:
                    st.write(f"Volatility: **{'✓' if conf.get('volatility_acceptable') else '✗'}**")
                
                st.divider()
                
                # Setup
                st.subheader("🎯 Setup")
                setup = result.get('setup', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                with col2:
                    st.metric("SL", f"${setup.get('stop_loss', 0):.2f}")
                with col3:
                    st.metric("TP", f"${setup.get('take_profit', 0):.2f}")
                st.metric("R:R Ratio", f"{setup.get('rr_ratio', 0):.2f}:1")
                
                st.divider()
                
                # Risk
                st.subheader("✓ Risk Check")
                risk_check = result.get('risk_check', {})
                if risk_check.get('allowed'):
                    st.success("✓ APPROVED")
                else:
                    st.error("✗ REJECTED")
                for reason in risk_check.get('reasons', []):
                    st.write(f"• {reason}")
                
                # Backtest
                if backtest and 'backtest' in result:
                    st.divider()
                    st.subheader("📈 Backtest")
                    bt = result.get('backtest', {})
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Trades", bt.get('total_trades', 0))
                    with col2:
                        st.metric("Win Rate", f"{bt.get('win_rate', 0):.1f}%")
                    with col3:
                        st.metric("Drawdown", f"{bt.get('max_drawdown', 0):.2f}%")
                    with col4:
                        st.metric("P&L", f"${bt.get('total_pnl', 0):.2f}")
                
                # Raw data
                with st.expander("Raw Data"):
                    st.json(result)
            else:
                st.warning("No results")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            with st.expander("Details"):
                import traceback
                st.code(traceback.format_exc())

elif analyze_btn:
    st.warning("Enter a symbol")

else:
    st.info("""
    ### Welcome! 👋
    
    **Signals Bot** - Professional Trading Signal Generator
    
    Features:
    - ✅ Multi-Confirmation Strategy
    - ✅ Risk Management
    - ✅ Backtesting
    - ✅ Technical Analysis
    
    **Get Started:**
    1. Configure settings in sidebar
    2. Click "Analyze"
    3. Review results
    
    **Disclaimer:** For educational purposes only.
    """)
