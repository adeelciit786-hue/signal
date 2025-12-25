"""
Strategy Logic Module
Multi-confirmation trading strategy with weighted scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Literal
from enum import Enum


class SignalConfidence(Enum):
    """Signal quality grades"""
    A_PLUS = "A+"
    B = "B"
    NO_TRADE = "No-Trade"


class StrategyLogic:
    """Multi-confirmation strategy with weighted scoring"""
    
    @staticmethod
    def evaluate_trend(df: pd.DataFrame, short_ema: pd.Series = None, long_ema: pd.Series = None) -> Tuple[str, float]:
        """
        Evaluate trend using EMA, SMA, and price structure
        
        Returns:
            (direction, confidence_score)
        """
        if len(df) < 50:
            return 'NEUTRAL', 0
        
        latest = df.iloc[-1]
        close = latest['close']
        
        # Check EMA alignment
        ema_10 = latest.get('EMA_10', close)
        ema_20 = latest.get('EMA_20', close)
        ema_50 = latest.get('EMA_50', close)
        sma_100 = latest.get('SMA_100', close)
        sma_200 = latest.get('SMA_200', close)
        
        bullish_ema_alignment = ema_10 > ema_20 > ema_50 > sma_100 > sma_200
        bearish_ema_alignment = ema_10 < ema_20 < ema_50 < sma_100 < sma_200
        
        # Check price structure
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        
        price_above_key_mas = close > ema_20 and close > ema_50
        price_below_key_mas = close < ema_20 and close < ema_50
        
        # Price making higher highs and higher lows
        trend_up = (df['high'].tail(10) > df['high'].tail(10).shift(1)).sum() > 5
        trend_down = (df['low'].tail(10) < df['low'].tail(10).shift(1)).sum() > 5
        
        confidence = 0
        
        if bullish_ema_alignment and price_above_key_mas and trend_up:
            return 'BULLISH', 90
        elif bullish_ema_alignment and price_above_key_mas:
            return 'BULLISH', 70
        elif bearish_ema_alignment and price_below_key_mas and trend_down:
            return 'BEARISH', 90
        elif bearish_ema_alignment and price_below_key_mas:
            return 'BEARISH', 70
        elif price_above_key_mas:
            return 'SLIGHTLY_BULLISH', 50
        elif price_below_key_mas:
            return 'SLIGHTLY_BEARISH', 50
        else:
            return 'NEUTRAL', 30
    
    @staticmethod
    def evaluate_momentum(df: pd.DataFrame) -> Tuple[str, float]:
        """
        Evaluate momentum using RSI, MACD, and Stochastic
        
        Returns:
            (momentum, confidence_score)
        """
        latest = df.iloc[-1]
        
        rsi = latest.get('RSI', 50)
        macd = latest.get('MACD', 0)
        macd_signal = latest.get('MACD_Signal', 0)
        macd_hist = latest.get('MACD_Histogram', 0)
        stoch_k = latest.get('Stoch_RSI_K', 50)
        stoch_d = latest.get('Stoch_RSI_D', 50)
        
        bullish_signals = 0
        bearish_signals = 0
        confidence = 0
        
        # RSI analysis
        if rsi > 50 and rsi < 70:
            bullish_signals += 1
        elif rsi > 70:
            bullish_signals += 0.5  # Overbought warning
        elif rsi < 50 and rsi > 30:
            bearish_signals += 1
        elif rsi < 30:
            bearish_signals += 0.5  # Oversold
        
        # MACD analysis
        if macd > macd_signal and macd_hist > 0:
            bullish_signals += 2
        elif macd < macd_signal and macd_hist < 0:
            bearish_signals += 2
        
        # MACD histogram increasing/decreasing
        if len(df) > 1:
            prev_hist = df.iloc[-2].get('MACD_Histogram', 0)
            if macd_hist > prev_hist and macd_hist > 0:
                bullish_signals += 1
            elif macd_hist < prev_hist and macd_hist < 0:
                bearish_signals += 1
        
        # Stochastic RSI
        if stoch_k > 50 and stoch_k < 80:
            bullish_signals += 1
        if stoch_d > 50:
            bullish_signals += 0.5
        
        if stoch_k < 50 and stoch_k > 20:
            bearish_signals += 1
        if stoch_d < 50:
            bearish_signals += 0.5
        
        total_signals = bullish_signals + bearish_signals
        
        if bullish_signals > bearish_signals:
            confidence = min(100, (bullish_signals / max(total_signals, 1)) * 100)
            return 'BULLISH', confidence
        elif bearish_signals > bullish_signals:
            confidence = min(100, (bearish_signals / max(total_signals, 1)) * 100)
            return 'BEARISH', confidence
        else:
            return 'NEUTRAL', 50
    
    @staticmethod
    def evaluate_volume(df: pd.DataFrame) -> Tuple[str, float]:
        """
        Evaluate volume and institutional flow
        
        Returns:
            (volume_signal, confidence_score)
        """
        latest = df.iloc[-1]
        
        recent_volume = df['volume'].tail(5).mean()
        volume_ma = latest.get('Volume_MA', recent_volume)
        obv = latest.get('OBV', 0)
        vwap = latest.get('VWAP', latest['close'])
        close = latest['close']
        
        confidence = 0
        
        # Volume confirmation
        if recent_volume > volume_ma * 1.5:
            volume_signal = "STRONG_CONFIRMATION"
            confidence = 80
        elif recent_volume > volume_ma:
            volume_signal = "GOOD_CONFIRMATION"
            confidence = 60
        elif recent_volume < volume_ma * 0.7:
            volume_signal = "WEAK_SIGNAL"
            confidence = 30
        else:
            volume_signal = "NEUTRAL"
            confidence = 50
        
        # OBV trend
        if len(df) > 1:
            obv_trend = obv > df.iloc[-2].get('OBV', obv)
            if obv_trend:
                confidence += 10
            else:
                confidence -= 10
        
        # VWAP alignment
        if close > vwap:
            confidence += 10
        elif close < vwap:
            confidence -= 10
        
        confidence = min(100, max(0, confidence))
        
        return volume_signal, confidence
    
    @staticmethod
    def evaluate_volatility_suitability(df: pd.DataFrame, regime: str) -> Tuple[str, float]:
        """
        Check if volatility is suitable for current regime
        
        Returns:
            (suitability, confidence_score)
        """
        latest = df.iloc[-1]
        
        atr = latest.get('ATR', 0)
        mean_atr = df['ATR'].tail(20).mean()
        volatility_ratio = atr / mean_atr if mean_atr > 0 else 1
        
        if regime in ['STRONG_TREND', 'MODERATE_TREND']:
            # Trends need reasonable volatility
            if 0.8 < volatility_ratio < 1.5:
                return "SUITABLE", 80
            elif 0.5 < volatility_ratio < 2.0:
                return "ACCEPTABLE", 60
            else:
                return "UNSUITABLE", 30
        
        elif regime == 'RANGE_BOUND':
            # Range need moderate, not extreme volatility
            if 0.7 < volatility_ratio < 1.3:
                return "SUITABLE", 80
            else:
                return "UNSUITABLE", 40
        
        elif regime in ['HIGH_VOLATILITY', 'COMPRESSION']:
            return "UNSUITABLE", 20
        
        else:
            return "UNCERTAIN", 50
    
    @staticmethod
    def evaluate_market_structure(df: pd.DataFrame) -> Tuple[str, float]:
        """
        Evaluate support/resistance and price structure
        
        Returns:
            (structure_signal, confidence_score)
        """
        if len(df) < 20:
            return "INSUFFICIENT_DATA", 0
        
        latest = df.iloc[-1]
        close = latest['close']
        
        # Get recent support and resistance
        recent_high = df['high'].tail(20).max()
        recent_low = df['low'].tail(20).min()
        recent_mid = (recent_high + recent_low) / 2
        
        # Fibonacci levels
        high = df['high'].max()
        low = df['low'].min()
        fib_levels = {
            '38.2': low + (high - low) * 0.382,
            '50': low + (high - low) * 0.5,
            '61.8': low + (high - low) * 0.618,
        }
        
        # Check proximity to key levels
        distance_to_resistance = recent_high - close
        distance_to_support = close - recent_low
        
        # Better structure at key levels
        if distance_to_support > distance_to_resistance:
            return "SUPPORT_BOUNCE", 70  # Price near support
        elif distance_to_resistance > distance_to_support:
            return "RESISTANCE_REJECTION", 70  # Price near resistance
        else:
            return "MID_RANGE", 50
    
    @staticmethod
    def generate_composite_signal(trend_signal: Tuple[str, float],
                                 momentum_signal: Tuple[str, float],
                                 volume_signal: Tuple[str, float],
                                 volatility_signal: Tuple[str, float],
                                 regime: str) -> Dict:
        """
        Combine all signals using weighted scoring
        
        Returns:
            Dict with final signal and metrics
        """
        trend_dir, trend_conf = trend_signal
        momentum_dir, momentum_conf = momentum_signal
        vol_type, vol_conf = volume_signal
        volatility_suit, volatility_conf = volatility_signal
        
        # Weights (total = 100)
        weights = {
            'trend': 0.35,
            'momentum': 0.25,
            'volume': 0.20,
            'volatility': 0.20
        }
        
        # Direction alignment
        bullish_alignment = 0
        bearish_alignment = 0
        
        if 'BULLISH' in trend_dir:
            bullish_alignment += weights['trend'] * trend_conf
        elif 'BEARISH' in trend_dir:
            bearish_alignment += weights['trend'] * trend_conf
        
        if 'BULLISH' in momentum_dir:
            bullish_alignment += weights['momentum'] * momentum_conf
        elif 'BEARISH' in momentum_dir:
            bearish_alignment += weights['momentum'] * momentum_conf
        
        if vol_type in ['STRONG_CONFIRMATION', 'GOOD_CONFIRMATION']:
            bullish_alignment += weights['volume'] * vol_conf if 'BULLISH' in trend_dir else 0
            bearish_alignment += weights['volume'] * vol_conf if 'BEARISH' in trend_dir else 0
        
        if volatility_suit == "SUITABLE":
            bullish_alignment += weights['volatility'] * volatility_conf
            bearish_alignment += weights['volatility'] * volatility_conf
        elif volatility_suit == "UNSUITABLE":
            bullish_alignment *= 0.5
            bearish_alignment *= 0.5
        
        # Final decision
        total_alignment = bullish_alignment + bearish_alignment
        
        if bullish_alignment > bearish_alignment + 20:
            final_signal = 'BUY'
            confidence = min(100, bullish_alignment)
        elif bearish_alignment > bullish_alignment + 20:
            final_signal = 'SELL'
            confidence = min(100, bearish_alignment)
        else:
            final_signal = 'NEUTRAL'
            confidence = 50
        
        # Grade the signal
        if confidence > 85 and final_signal != 'NEUTRAL':
            grade = SignalConfidence.A_PLUS.value
        elif confidence > 70 and final_signal != 'NEUTRAL':
            grade = SignalConfidence.B.value
        else:
            grade = SignalConfidence.NO_TRADE.value
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'grade': grade,
            'trend_alignment': trend_conf,
            'momentum_alignment': momentum_conf,
            'volume_alignment': vol_conf,
            'volatility_alignment': volatility_conf,
            'regime_compatibility': regime not in ['HIGH_VOLATILITY', 'COMPRESSION']
        }
