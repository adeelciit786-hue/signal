"""
CHART VISUALIZER - Professional Trading Chart Display
Displays candlestick charts with BUY/SELL signal markers
Works in all environments (Streamlit, local, etc.)
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ChartVisualizer:
    """Professional chart visualization for trading signals"""
    
    @staticmethod
    def create_signal_chart(
        df: pd.DataFrame,
        signal: str,
        confidence: float,
        symbol: str,
        timeframe: str,
        setup: Dict = None
    ) -> go.Figure:
        """
        Create professional candlestick chart with signal markers and setup levels
        
        Args:
            df: OHLCV data with indicators
            signal: BUY/SELL/NEUTRAL
            confidence: Confidence percentage
            symbol: Trading pair symbol
            timeframe: Timeframe (1h, 4h, 1d, etc)
            setup: Setup dict with entry, SL, TP
        
        Returns:
            Plotly Figure object
        """
        
        if setup is None:
            setup = {'entry': 0, 'stop_loss': 0, 'take_profit': 0}
        
        # Use last 60 candles for better visibility
        display_df = df.tail(60).copy()
        
        # Create figure with secondary y-axis for volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.12,
            row_heights=[0.7, 0.3],
            specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
        )
        
        # ========== CANDLESTICK CHART ==========
        fig.add_trace(
            go.Candlestick(
                x=display_df.index,
                open=display_df['open'],
                high=display_df['high'],
                low=display_df['low'],
                close=display_df['close'],
                name='Price',
                yaxis='y1',
                increasing_line_color='#00CC00',
                decreasing_line_color='#FF3333'
            ),
            row=1, col=1, secondary_y=False
        )
        
        # ========== SIGNAL MARKERS ==========
        if signal == 'BUY':
            last_close = display_df['close'].iloc[-1]
            fig.add_trace(
                go.Scatter(
                    x=[display_df.index[-1]],
                    y=[last_close],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='#00CC00',
                        symbol='triangle-up',
                        line=dict(color='#00AA00', width=2)
                    ),
                    name=f'BUY Signal ({confidence:.1f}%)',
                    text=[f'BUY<br>{confidence:.1f}%'],
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        elif signal == 'SELL':
            last_close = display_df['close'].iloc[-1]
            fig.add_trace(
                go.Scatter(
                    x=[display_df.index[-1]],
                    y=[last_close],
                    mode='markers',
                    marker=dict(
                        size=20,
                        color='#FF3333',
                        symbol='triangle-down',
                        line=dict(color='#CC0000', width=2)
                    ),
                    name=f'SELL Signal ({confidence:.1f}%)',
                    text=[f'SELL<br>{confidence:.1f}%'],
                    hovertemplate='%{text}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        # ========== SETUP LEVELS (Entry, SL, TP) ==========
        if setup.get('entry') and setup.get('entry') > 0:
            entry = setup.get('entry', 0)
            sl = setup.get('stop_loss', 0)
            tp = setup.get('take_profit', 0)
            
            # Entry line
            fig.add_hline(
                y=entry,
                line_dash="solid",
                line_color="blue",
                line_width=2,
                annotation_text=f"Entry: ${entry:.2f}",
                annotation_position="right",
                row=1, col=1,
                secondary_y=False
            )
            
            # Stop Loss line
            if sl > 0:
                fig.add_hline(
                    y=sl,
                    line_dash="dash",
                    line_color="red",
                    line_width=2,
                    annotation_text=f"SL: ${sl:.2f}",
                    annotation_position="right",
                    row=1, col=1,
                    secondary_y=False
                )
            
            # Take Profit line
            if tp > 0:
                fig.add_hline(
                    y=tp,
                    line_dash="dash",
                    line_color="green",
                    line_width=2,
                    annotation_text=f"TP: ${tp:.2f}",
                    annotation_position="right",
                    row=1, col=1,
                    secondary_y=False
                )
        
        # ========== INDICATORS: EMA & BOLLINGER BANDS ==========
        if 'EMA_10' in display_df.columns and display_df['EMA_10'].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['EMA_10'],
                    name='EMA 10',
                    line=dict(color='orange', width=1),
                    hovertemplate='EMA 10: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        if 'EMA_20' in display_df.columns and display_df['EMA_20'].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['EMA_20'],
                    name='EMA 20',
                    line=dict(color='purple', width=1),
                    hovertemplate='EMA 20: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        if 'EMA_50' in display_df.columns and display_df['EMA_50'].notna().any():
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['EMA_50'],
                    name='EMA 50',
                    line=dict(color='red', width=1),
                    hovertemplate='EMA 50: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        # Bollinger Bands
        if 'BB_Upper' in display_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['BB_Upper'],
                    name='BB Upper',
                    line=dict(color='rgba(200,200,200,0.5)', width=1),
                    hovertemplate='BB Upper: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['BB_Lower'],
                    name='BB Lower',
                    line=dict(color='rgba(200,200,200,0.5)', width=1),
                    fill='tonexty',
                    fillcolor='rgba(200,200,200,0.1)',
                    hovertemplate='BB Lower: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1, secondary_y=False
            )
        
        # ========== VOLUME CHART ==========
        colors = ['#FF3333' if close < open_ else '#00CC00' 
                  for close, open_ in zip(display_df['close'], display_df['open'])]
        
        fig.add_trace(
            go.Bar(
                x=display_df.index,
                y=display_df['volume'],
                name='Volume',
                marker_color=colors,
                hovertemplate='Volume: %{y:.0f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # ========== LAYOUT CONFIGURATION ==========
        title_color = '#00CC00' if signal == 'BUY' else '#FF3333' if signal == 'SELL' else '#FFB81C'
        
        fig.update_layout(
            title={
                'text': f"<b>{symbol} {timeframe} - {signal} Signal ({confidence:.1f}% Confidence)</b>",
                'font': {'size': 20, 'color': title_color}
            },
            template='plotly_dark',
            height=800,
            hovermode='x unified',
            margin=dict(l=50, r=50, t=100, b=50),
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(
                orientation='v',
                yanchor='top',
                y=0.99,
                xanchor='left',
                x=0.01,
                bgcolor='rgba(0,0,0,0.3)',
                bordercolor='rgba(255,255,255,0.3)',
                borderwidth=1
            )
        )
        
        # Y-axis labels
        fig.update_yaxes(title_text="Price (USD)", row=1, col=1, secondary_y=False)
        fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    @staticmethod
    def create_indicator_panel(df: pd.DataFrame, symbol: str) -> go.Figure:
        """Create detailed indicator analysis panel"""
        
        display_df = df.tail(60).copy()
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            subplot_titles=('RSI', 'MACD', 'ADX'),
            vertical_spacing=0.1
        )
        
        # ========== RSI ==========
        if 'RSI' in display_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['RSI'],
                    name='RSI',
                    line=dict(color='cyan', width=2),
                    hovertemplate='RSI: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Overbought/Oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
            fig.update_yaxes(title_text="RSI", row=1, col=1)
        
        # ========== MACD ==========
        if 'MACD' in display_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['MACD'],
                    name='MACD Line',
                    line=dict(color='blue', width=2),
                    hovertemplate='MACD: %{y:.4f}<extra></extra>'
                ),
                row=2, col=1
            )
            
            if 'MACD_Signal' in display_df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=display_df.index,
                        y=display_df['MACD_Signal'],
                        name='Signal Line',
                        line=dict(color='red', width=2),
                        hovertemplate='Signal: %{y:.4f}<extra></extra>'
                    ),
                    row=2, col=1
                )
            
            fig.add_hline(y=0, line_dash="solid", line_color="gray", row=2, col=1)
            fig.update_yaxes(title_text="MACD", row=2, col=1)
        
        # ========== ADX ==========
        if 'ADX' in display_df.columns:
            fig.add_trace(
                go.Scatter(
                    x=display_df.index,
                    y=display_df['ADX'],
                    name='ADX',
                    line=dict(color='yellow', width=2),
                    hovertemplate='ADX: %{y:.2f}<extra></extra>'
                ),
                row=3, col=1
            )
            
            fig.add_hline(y=20, line_dash="dash", line_color="orange", row=3, col=1)
            fig.update_yaxes(title_text="ADX", row=3, col=1)
        
        fig.update_layout(
            title=f"<b>{symbol} - Technical Indicators Analysis</b>",
            template='plotly_dark',
            height=900,
            hovermode='x unified',
            xaxis_rangeslider_visible=False,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_confirmations_table(confirmations: Dict) -> pd.DataFrame:
        """Create confirmations display table"""
        
        data = {
            'Indicator': [
                'Trend Direction',
                'Trend Strength',
                'Momentum Confirmed',
                'Momentum Strength',
                'Volume Confirmed',
                'Volatility Status',
                'ATR Value'
            ],
            'Status': [
                confirmations.get('trend', 'N/A'),
                confirmations.get('trend_strength', 'N/A'),
                '✓ YES' if confirmations.get('momentum_confirmed') else '✗ NO',
                confirmations.get('momentum_strength', 'N/A'),
                '✓ YES' if confirmations.get('volume_confirmed') else '✗ NO',
                confirmations.get('volatility_reason', 'N/A'),
                confirmations.get('atr_value', 'N/A')
            ]
        }
        
        return pd.DataFrame(data)


# Helper function for Streamlit integration
def display_trading_analysis(analysis: Dict, symbol: str, timeframe: str):
    """
    Display complete trading analysis with charts in Streamlit
    
    Args:
        analysis: Analysis dict from bot engine
        symbol: Trading pair
        timeframe: Timeframe
    """
    try:
        import streamlit as st
        
        signal = analysis.get('signal', 'NEUTRAL')
        confidence = analysis.get('confidence', 0)
        df = analysis.get('dataframe')
        setup = analysis.get('setup', {})
        confirmations = analysis.get('confirmations', {})
        
        # Signal header with color
        if signal == 'BUY':
            st.success(f"### 🟢 BUY SIGNAL - {confidence:.1f}% Confidence")
        elif signal == 'SELL':
            st.error(f"### 🔴 SELL SIGNAL - {confidence:.1f}% Confidence")
        else:
            st.warning(f"### 🟡 NEUTRAL - {confidence:.1f}% Confidence")
        
        # Main chart
        if df is not None and not df.empty:
            fig_main = ChartVisualizer.create_signal_chart(
                df, signal, confidence, symbol, timeframe, setup
            )
            st.plotly_chart(fig_main, use_container_width=True)
        
        # Setup details
        st.subheader("📊 Trade Setup")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Entry", f"${setup.get('entry', 0):.2f}")
        with col2:
            st.metric("Stop Loss", f"${setup.get('stop_loss', 0):.2f}")
        with col3:
            st.metric("Take Profit", f"${setup.get('take_profit', 0):.2f}")
        with col4:
            st.metric("R:R Ratio", f"{setup.get('rr_ratio', 0):.2f}:1")
        
        # Confirmations table
        st.subheader("✓ Confirmations")
        conf_df = ChartVisualizer.create_confirmations_table(confirmations)
        st.dataframe(conf_df, use_container_width=True, hide_index=True)
        
        # Indicator panel
        if df is not None:
            fig_indicators = ChartVisualizer.create_indicator_panel(df, symbol)
            st.plotly_chart(fig_indicators, use_container_width=True)
        
        # Risk assessment
        st.subheader("⚠️ Risk Assessment")
        risk = analysis.get('risk_validation', {})
        
        if risk.get('allowed'):
            st.success("✓ Risk APPROVED - Trade meets risk criteria")
        else:
            st.error("✗ Risk REJECTED - Trade fails risk criteria")
        
        # Risk details
        if risk.get('checks'):
            for check_name, check_result in risk['checks'].items():
                if check_result.get('valid'):
                    st.info(f"✓ {check_name}: {check_result.get('reason', 'OK')}")
                else:
                    st.warning(f"⚠ {check_name}: {check_result.get('reason', 'Warning')}")
    
    except ImportError:
        logger.info("Streamlit not available - display_trading_analysis skipped")
    except Exception as e:
        logger.error(f"Error displaying analysis: {e}")
