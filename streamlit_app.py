"""
PROFESSIONAL SIGNALS BOT - Trading Signal Generator
Real-time analysis with BUY/SELL signals, charts, and technical analysis
Production-ready with comprehensive data fetching and signal generation
"""

import streamlit as st
import sys
import os
import logging
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import bot modules
try:
    from src.data_fetcher import DataFetcher
    from src.technical_indicators import TechnicalIndicators
    from src.strategy_logic import StrategyLogic
    from src.signal_generator import SignalGenerator
    logger.info("Successfully imported bot modules")
except Exception as e:
    logger.error(f"Failed to import bot modules: {e}")
    st.error(f"❌ Failed to load bot modules: {e}")
    st.stop()

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Professional Trading Signals Bot",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .signal-buy {
        background: linear-gradient(135deg, rgba(0, 200, 0, 0.15), rgba(0, 150, 0, 0.05));
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00CC00;
        margin: 10px 0;
    }
    .signal-sell {
        background: linear-gradient(135deg, rgba(255, 50, 50, 0.15), rgba(200, 0, 0, 0.05));
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FF3333;
        margin: 10px 0;
    }
    .signal-neutral {
        background: linear-gradient(135deg, rgba(255, 184, 28, 0.15), rgba(255, 150, 0, 0.05));
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFB81C;
        margin: 10px 0;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ==================== MAIN TITLE ====================
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📈 Professional Trading Signal Analyzer")
    st.markdown("*Multi-timeframe technical analysis with BUY/SELL signals | Real-time data from Yahoo Finance & Binance*")

with col2:
    if st.button("🔄 Refresh Data", help="Force refresh market data"):
        st.session_state.last_refresh = pd.Timestamp.now()
        st.rerun()

# ==================== SIDEBAR CONFIGURATION ====================
st.sidebar.markdown("## ⚙️ Configuration")

# Asset type selection
asset_type_map = {"Crypto": "crypto", "Stock": "stock", "Forex": "forex"}
asset_display = st.sidebar.radio(
    "Asset Type",
    ["Crypto", "Stock", "Forex"],
    horizontal=True,
    help="Select the asset class to analyze"
)
asset_type = asset_type_map[asset_display]

# Symbol selection
symbols_dict = {
    "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "BNB/USDT"],
    "Stock": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA"],
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "NZD/USD", "CAD/USD"]
}

symbol = st.sidebar.selectbox(
    "Trading Pair",
    symbols_dict[asset_display],
    help="Select the trading symbol to analyze"
)

# Timeframe selection
timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["15m", "30m", "1h", "4h", "1d"],
    index=2,  # Default to 1h
    help="Candlestick timeframe"
)

# Risk settings
st.sidebar.markdown("---")
st.sidebar.markdown("## 🛡️ Risk Settings")

max_risk = st.sidebar.slider(
    "Max Risk per Trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="Maximum percentage of account to risk per trade"
)

min_confidence = st.sidebar.slider(
    "Minimum Signal Confidence (%)",
    min_value=0,
    max_value=100,
    value=55,
    step=5,
    help="Minimum confidence level to generate signals"
)

# ==================== MAIN ANALYSIS ====================
st.markdown("---")

# Create columns for data fetching status
status_col1, status_col2, status_col3 = st.columns(3)

with st.spinner("🔄 Fetching market data..."):
    try:
        # Fetch data
        fetcher = DataFetcher()
        df = fetcher.fetch_data(symbol, asset_type, timeframe, lookback_days=90)
        
        if df.empty or len(df) < 50:
            st.error(f"❌ Insufficient data for {symbol}. Got {len(df)} candles, need at least 50.")
            st.info("**Troubleshooting:**\n- Check symbol spelling\n- Try different timeframe\n- Ensure market is open")
            st.stop()
        
        # Calculate all technical indicators
        TechnicalIndicators.calculate_all_indicators(df)
        
        status_col1.success(f"✅ Data: {len(df)} candles")
        status_col2.info(f"⏰ Latest: {df.index[-1].strftime('%Y-%m-%d %H:%M')}")
        
        current_price = df['close'].iloc[-1]
        status_col3.metric("Current Price", f"${current_price:.4f}")
        
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        logger.error(f"Data fetch error for {symbol}: {str(e)}")
        st.stop()

# ==================== SIGNAL GENERATION ====================
st.markdown("---")
st.subheader("📊 Signal Analysis")

try:
    # Evaluate trend
    trend_signal, trend_conf = StrategyLogic.evaluate_trend(df)
    
    # Evaluate momentum
    momentum_signal, momentum_conf = StrategyLogic.evaluate_momentum(df)
    
    # Evaluate volume
    volume_signal, volume_conf = StrategyLogic.evaluate_volume(df)
    
    # Evaluate volatility
    volatility_signal, volatility_conf = StrategyLogic.evaluate_volatility_suitability(df, "normal")
    
    # Generate composite signal
    composite = StrategyLogic.generate_composite_signal(
        (trend_signal, trend_conf),
        (momentum_signal, momentum_conf),
        (volume_signal, volume_conf),
        (volatility_signal, volatility_conf),
        "normal"
    )
    
    final_signal = composite['signal']
    final_confidence = composite['confidence']
    
    # Filter by confidence threshold
    if final_confidence < min_confidence and final_signal != 'NEUTRAL':
        final_signal = 'NEUTRAL'
        reason_text = f"Confidence {final_confidence:.0f}% below threshold {min_confidence}%"
    else:
        reason_text = f"Multi-confirmation signal (Trend: {trend_conf:.0f}%, Momentum: {momentum_conf:.0f}%)"
    
    # Display signal
    if final_signal == "BUY":
        st.markdown(f"""
        <div class="signal-buy">
            <h2>🟢 BUY SIGNAL - {final_confidence:.0f}% Confidence</h2>
            <p><strong>{reason_text}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    elif final_signal == "SELL":
        st.markdown(f"""
        <div class="signal-sell">
            <h2>🔴 SELL SIGNAL - {final_confidence:.0f}% Confidence</h2>
            <p><strong>{reason_text}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="signal-neutral">
            <h2>🟡 NEUTRAL / INSUFFICIENT SIGNAL - {final_confidence:.0f}% Confidence</h2>
            <p><strong>Signal below minimum confidence threshold or mixed confirmations</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
except Exception as e:
    st.error(f"❌ Error in signal generation: {str(e)}")
    logger.error(f"Signal generation error: {str(e)}")

# ==================== TECHNICAL INDICATORS ====================
st.markdown("---")
st.subheader("📈 Technical Indicators Summary")

ind_cols = st.columns(4)
with ind_cols[0]:
    st.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}", help="Overbought: >70, Oversold: <30")
with ind_cols[1]:
    atr = df['ATR'].iloc[-1] if 'ATR' in df.columns else 0
    st.metric("ATR", f"${atr:.4f}", help="Average True Range - Volatility measure")
with ind_cols[2]:
    macd = df['MACD'].iloc[-1] if 'MACD' in df.columns else 0
    st.metric("MACD", f"{macd:.6f}", help="MACD Line value")
with ind_cols[3]:
    adx = df['ADX'].iloc[-1] if 'ADX' in df.columns else 0
    st.metric("ADX", f"{adx:.1f}", help="Trend Strength (>25 = strong)")

# ==================== CONFIRMATION DETAILS ====================
st.markdown("---")
st.subheader("✅ Signal Confirmations")

conf_cols = st.columns(4)
with conf_cols[0]:
    color = "🟢" if "BULLISH" in trend_signal else "🔴" if "BEARISH" in trend_signal else "🟡"
    st.write(f"{color} **Trend**: {trend_signal}\n{trend_conf:.0f}% confidence")

with conf_cols[1]:
    color = "🟢" if "BULLISH" in momentum_signal else "🔴" if "BEARISH" in momentum_signal else "🟡"
    st.write(f"{color} **Momentum**: {momentum_signal}\n{momentum_conf:.0f}% confidence")

with conf_cols[2]:
    color = "🟢" if "STRONG" in volume_signal else "🟡" if "GOOD" in volume_signal else "🔴"
    st.write(f"{color} **Volume**: {volume_signal}\n{volume_conf:.0f}% confidence")

with conf_cols[3]:
    color = "🟢" if "SUITABLE" in volatility_signal else "🟡"
    st.write(f"{color} **Volatility**: {volatility_signal}\n{volatility_conf:.0f}% confidence")

# ==================== PRICE CHART WITH INDICATORS ====================
st.markdown("---")
st.subheader("💹 Price Chart with Indicators")

try:
    # Prepare chart data
    df_chart = df.tail(100).copy()
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=df_chart.index,
        open=df_chart['open'],
        high=df_chart['high'],
        low=df_chart['low'],
        close=df_chart['close'],
        name='Price',
        yaxis='y1'
    ))
    
    # Add Bollinger Bands
    if 'BB_Upper' in df_chart.columns:
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=df_chart['BB_Upper'],
            name='BB Upper',
            line=dict(color='rgba(200,200,200,0.3)'),
            yaxis='y1'
        ))
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=df_chart['BB_Lower'],
            name='BB Lower',
            line=dict(color='rgba(200,200,200,0.3)'),
            fill='tonexty',
            yaxis='y1'
        ))
    
    # Add EMAs
    if 'EMA_10' in df_chart.columns:
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=df_chart['EMA_10'],
            name='EMA 10',
            line=dict(color='blue', width=1),
            yaxis='y1'
        ))
    if 'EMA_20' in df_chart.columns:
        fig.add_trace(go.Scatter(
            x=df_chart.index,
            y=df_chart['EMA_20'],
            name='EMA 20',
            line=dict(color='orange', width=1),
            yaxis='y1'
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} - {timeframe} Chart",
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        height=500,
        hovermode='x unified',
        template='plotly_dark'
    )
    
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Chart rendering issue: {str(e)}")

# ==================== RISK MANAGEMENT ====================
st.markdown("---")
st.subheader("💼 Risk Management")

if final_signal != 'NEUTRAL' and atr > 0:
    risk_cols = st.columns(2)
    
    with risk_cols[0]:
        if final_signal == 'BUY':
            stop_loss = current_price - (atr * 2)
            take_profit = current_price + (atr * 4)
        else:  # SELL
            stop_loss = current_price + (atr * 2)
            take_profit = current_price - (atr * 4)
        
        st.metric("Entry Price", f"${current_price:.4f}")
        st.metric("Stop Loss", f"${stop_loss:.4f}")
        st.metric("Take Profit", f"${take_profit:.4f}")
    
    with risk_cols[1]:
        risk_amount = abs(current_price - stop_loss)
        reward_amount = abs(take_profit - current_price)
        ratio = reward_amount / risk_amount if risk_amount > 0 else 0
        
        st.metric("Risk per pip", f"${risk_amount:.4f}")
        st.metric("Reward per pip", f"${reward_amount:.4f}")
        st.metric("Risk:Reward Ratio", f"1:{ratio:.2f}")
else:
    st.info("⚠️ No active signal to calculate risk management setup")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888; font-size: 12px;'>
<p>📊 Professional Trading Signal Analyzer | Data Source: Yahoo Finance & Binance API</p>
<p><strong>Disclaimer:</strong> This tool is for analysis only. Not financial advice. Trade at your own risk.</p>
</div>
""", unsafe_allow_html=True)


