"""
Streamlit App Entry Point for Signals Bot
This is the main entry file for Streamlit deployment
"""

import sys
import os
import streamlit as st
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Signals Bot - Trading Signal Generator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.bot_engine import BotOrchestrator
    from src.bot_config import BotConfig
    from src.bot_interface import BotInterface
except ImportError as e:
    st.error(f"Import Error: {str(e)}")
    st.stop()

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Run the Streamlit application"""
    
    # Header
    st.title("🤖 Signals Bot - Professional Trading Signal Generator")
    st.markdown("Multi-Confirmation Strategy | Risk-Managed Trading")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Asset selection
        asset_type = st.selectbox(
            "Asset Type",
            ["crypto", "stock", "forex"],
            help="Select the type of asset to analyze"
        )
        
        # Symbol input
        symbol = st.text_input(
            "Symbol",
            placeholder="BTC/USDT or AAPL or EUR/USD",
            help="Enter the trading symbol"
        )
        
        # Timeframe
        timeframe = st.selectbox(
            "Timeframe",
            ["1h", "4h", "1d", "1w"],
            help="Select analysis timeframe"
        )
        
        # Risk settings
        st.subheader("💰 Risk Settings")
        account_balance = st.number_input(
            "Account Balance ($)",
            min_value=100,
            value=10000,
            step=100
        )
        
        risk_percent = st.slider(
            "Risk per Trade (%)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        
        min_rr_ratio = st.slider(
            "Min R:R Ratio",
            min_value=1.0,
            max_value=5.0,
            value=2.0,
            step=0.5
        )
        
        # Backtest option
        backtest = st.checkbox("Run Backtest", value=True)
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Symbol", use_container_width=True)
    
    # Main content
    if analyze_button and symbol:
        st.info(f"Analyzing {symbol.upper()} on {timeframe} timeframe...")
        
        try:
            # Create config
            config = BotConfig()
            config.set('account_balance', account_balance)
            config.set('risk_percent', risk_percent)
            config.set('min_rr_ratio', min_rr_ratio)
            
            # Create orchestrator
            bot = BotOrchestrator(config)
            
            # Analyze
            result = bot.analyze_single_asset(
                symbol=symbol,
                asset_type=asset_type,
                timeframe=timeframe,
                backtest=backtest
            )
            
            if result:
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    signal = result.get('signal', 'NEUTRAL')
                    signal_color = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "🟡")
                    st.metric("Signal", f"{signal_color} {signal}")
                
                with col2:
                    confidence = result.get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.1f}%")
                
                with col3:
                    quality = result.get('quality', 'NEUTRAL')
                    st.metric("Quality", quality)
                
                with col4:
                    win_rate = result.get('backtest', {}).get('win_rate', 0) if backtest else 0
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                st.divider()
                
                # Confirmations
                st.subheader("📊 Confirmations")
                confirmations = result.get('confirmations', {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    trend = confirmations.get('trend', 'N/A')
                    st.write(f"**Trend:** {trend}")
                
                with col2:
                    momentum = "✓ YES" if confirmations.get('momentum_confirmed') else "✗ NO"
                    st.write(f"**Momentum:** {momentum}")
                
                with col3:
                    volume = "✓ YES" if confirmations.get('volume_confirmed') else "✗ NO"
                    st.write(f"**Volume:** {volume}")
                
                with col4:
                    volatility = "✓ OK" if confirmations.get('volatility_acceptable') else "✗ RISKY"
                    st.write(f"**Volatility:** {volatility}")
                
                st.divider()
                
                # Setup Details
                st.subheader("🎯 Setup Details")
                setup = result.get('setup', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                
                with col2:
                    st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
                
                with col3:
                    st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
                
                rr_ratio = setup.get('rr_ratio', 0)
                st.metric("R:R Ratio", f"{rr_ratio:.2f}:1")
                
                st.divider()
                
                # Risk Validation
                st.subheader("✓ Risk Validation")
                risk_check = result.get('risk_check', {})
                allowed = risk_check.get('allowed', False)
                
                if allowed:
                    st.success("✓ Trade APPROVED - Passes all risk checks")
                else:
                    st.error("✗ Trade REJECTED - Fails risk checks")
                
                reasons = risk_check.get('reasons', [])
                for reason in reasons:
                    st.write(f"• {reason}")
                
                # Backtest Results (if enabled)
                if backtest:
                    st.divider()
                    st.subheader("📈 Backtest Results")
                    backtest_results = result.get('backtest', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Trades", backtest_results.get('total_trades', 0))
                    with col2:
                        st.metric("Win Rate", f"{backtest_results.get('win_rate', 0):.1f}%")
                    with col3:
                        st.metric("Max Drawdown", f"{backtest_results.get('max_drawdown', 0):.2f}%")
                    with col4:
                        pnl = backtest_results.get('total_pnl', 0)
                        pnl_pct = backtest_results.get('total_pnl_percent', 0)
                        st.metric("Total P&L", f"${pnl:.2f} ({pnl_pct:.2f}%)")
                
                # Analysis Details
                st.divider()
                st.subheader("🔬 Analysis Details")
                
                with st.expander("Show Raw Data"):
                    st.json(result)
            
            else:
                st.warning("No analysis results returned. Please check symbol and try again.")
        
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            with st.expander("Show Error Details"):
                st.code(str(e))
                import traceback
                st.code(traceback.format_exc())
    
    elif analyze_button:
        st.warning("Please enter a symbol to analyze")
    
    else:
        # Welcome message
        st.info("""
        ### Welcome to Signals Bot! 🚀
        
        This is a professional trading signal generator with:
        - **Multi-Confirmation Strategy**: Trend + Momentum + Volume + Volatility checks
        - **Risk Management**: Mandatory SL/TP validation and risk per trade calculations
        - **Backtesting**: Historical performance validation
        - **Professional Analysis**: Technical + Fundamental + Sentiment analysis
        
        **How to use:**
        1. Select asset type (Crypto, Stock, Forex)
        2. Enter the trading symbol
        3. Configure risk settings
        4. Click "Analyze Symbol"
        5. Review the signal and validation results
        
        ⚠️ **Disclaimer**: This tool is for educational purposes only. Always do your own research before trading.
        """)

if __name__ == "__main__":
    main()
else:
    main()

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Run the Streamlit application"""
    
    # Header
    st.title("🤖 Signals Bot - Professional Trading Signal Generator")
    st.markdown("Multi-Confirmation Strategy | Risk-Managed Trading")
    st.divider()
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Asset selection
        asset_type = st.selectbox(
            "Asset Type",
            ["crypto", "stock", "forex"],
            help="Select the type of asset to analyze"
        )
        
        # Symbol input
        symbol = st.text_input(
            "Symbol",
            placeholder="BTC/USDT or AAPL or EUR/USD",
            help="Enter the trading symbol"
        )
        
        # Timeframe
        timeframe = st.selectbox(
            "Timeframe",
            ["1h", "4h", "1d", "1w"],
            help="Select analysis timeframe"
        )
        
        # Risk settings
        st.subheader("Risk Settings")
        account_balance = st.number_input(
            "Account Balance ($)",
            min_value=100,
            value=10000,
            step=100
        )
        
        risk_percent = st.slider(
            "Risk per Trade (%)",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1
        )
        
        min_rr_ratio = st.slider(
            "Min R:R Ratio",
            min_value=1.0,
            max_value=5.0,
            value=2.0,
            step=0.5
        )
        
        # Backtest option
        backtest = st.checkbox("Run Backtest", value=True)
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Symbol", use_container_width=True)
    
    # Main content
    if analyze_button and symbol:
        st.info(f"Analyzing {symbol.upper()} on {timeframe} timeframe...")
        
        try:
            # Create config
            config = BotConfig()
            config.set('account_balance', account_balance)
            config.set('risk_percent', risk_percent)
            config.set('min_rr_ratio', min_rr_ratio)
            
            # Create orchestrator
            bot = BotOrchestrator(config)
            
            # Analyze
            result = bot.analyze_single_asset(
                symbol=symbol,
                asset_type=asset_type,
                timeframe=timeframe,
                backtest=backtest
            )
            
            if result:
                # Display results
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    signal = result.get('signal', 'NEUTRAL')
                    signal_color = "🟢" if signal == "BUY" else ("🔴" if signal == "SELL" else "🟡")
                    st.metric("Signal", f"{signal_color} {signal}")
                
                with col2:
                    confidence = result.get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.1f}%")
                
                with col3:
                    quality = result.get('quality', 'NEUTRAL')
                    st.metric("Quality", quality)
                
                with col4:
                    win_rate = result.get('backtest', {}).get('win_rate', 0) if backtest else 0
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                
                st.divider()
                
                # Confirmations
                st.subheader("📊 Confirmations")
                confirmations = result.get('confirmations', {})
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    trend = confirmations.get('trend', 'N/A')
                    st.write(f"**Trend:** {trend}")
                
                with col2:
                    momentum = "✓ YES" if confirmations.get('momentum_confirmed') else "✗ NO"
                    st.write(f"**Momentum:** {momentum}")
                
                with col3:
                    volume = "✓ YES" if confirmations.get('volume_confirmed') else "✗ NO"
                    st.write(f"**Volume:** {volume}")
                
                with col4:
                    volatility = "✓ OK" if confirmations.get('volatility_acceptable') else "✗ RISKY"
                    st.write(f"**Volatility:** {volatility}")
                
                st.divider()
                
                # Setup Details
                st.subheader("🎯 Setup Details")
                setup = result.get('setup', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Entry", f"${setup.get('entry', 0):.2f}")
                
                with col2:
                    st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
                
                with col3:
                    st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
                
                rr_ratio = setup.get('rr_ratio', 0)
                st.metric("R:R Ratio", f"{rr_ratio:.2f}:1")
                
                st.divider()
                
                # Risk Validation
                st.subheader("✓ Risk Validation")
                risk_check = result.get('risk_check', {})
                allowed = risk_check.get('allowed', False)
                
                if allowed:
                    st.success("✓ Trade APPROVED - Passes all risk checks")
                else:
                    st.error("✗ Trade REJECTED - Fails risk checks")
                
                reasons = risk_check.get('reasons', [])
                for reason in reasons:
                    st.write(f"• {reason}")
                
                # Backtest Results (if enabled)
                if backtest:
                    st.divider()
                    st.subheader("📈 Backtest Results")
                    backtest_results = result.get('backtest', {})
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Trades", backtest_results.get('total_trades', 0))
                    with col2:
                        st.metric("Win Rate", f"{backtest_results.get('win_rate', 0):.1f}%")
                    with col3:
                        st.metric("Max Drawdown", f"{backtest_results.get('max_drawdown', 0):.2f}%")
                    with col4:
                        pnl = backtest_results.get('total_pnl', 0)
                        pnl_pct = backtest_results.get('total_pnl_percent', 0)
                        st.metric("Total P&L", f"${pnl:.2f} ({pnl_pct:.2f}%)")
                
                # Analysis Details
                st.divider()
                st.subheader("🔬 Analysis Details")
                
                with st.expander("Show Raw Data"):
                    st.json(result)
            
            else:
                st.warning("No analysis results returned. Please check symbol and try again.")
        
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            with st.expander("Show Error Details"):
                st.code(str(e))
    
    elif analyze_button:
        st.warning("Please enter a symbol to analyze")
    
    else:
        # Welcome message
        st.info("""
        ### Welcome to Signals Bot! 🚀
        
        This is a professional trading signal generator with:
        - **Multi-Confirmation Strategy**: Trend + Momentum + Volume + Volatility checks
        - **Risk Management**: Mandatory SL/TP validation and risk per trade calculations
        - **Backtesting**: Historical performance validation
        - **Professional Analysis**: Technical + Fundamental + Sentiment analysis
        
        **How to use:**
        1. Select asset type (Crypto, Stock, Forex)
        2. Enter the trading symbol
        3. Configure risk settings
        4. Click "Analyze Symbol"
        5. Review the signal and validation results
        
        ⚠️ **Disclaimer**: This tool is for educational purposes only. Always do your own research before trading.
        """)

if __name__ == "__main__":
    main()
else:
    main()

