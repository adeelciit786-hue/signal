"""
Enhanced Signal Engine with Strict Multi-Confirmation Rules
BUY/SELL/NEUTRAL logic with mandatory confirmations
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalQuality(Enum):
    """Signal quality grades"""
    STRONG = "STRONG (A+)"
    GOOD = "GOOD (B)"
    WEAK = "WEAK (C)"
    NEUTRAL = "NEUTRAL (No-Trade)"


class EnhancedSignalEngine:
    """
    Multi-confirmation signal generator
    Strict IF-THEN rules with mandatory filters
    """
    
    @staticmethod
    def evaluate_trend_strength(df: pd.DataFrame) -> Dict:
        """
        Comprehensive trend evaluation
        """
        latest = df.iloc[-1]
        close = latest['close']
        
        # Basic MAs
        ema_10 = latest.get('EMA_10', close)
        ema_20 = latest.get('EMA_20', close)
        ema_50 = latest.get('EMA_50', close)
        sma_200 = latest.get('SMA_200', close)
        
        # ADX trend strength
        adx = latest.get('ADX', 0)
        
        # Supertrend
        st_trend = latest.get('Supertrend_Trend', 0)
        
        # Aroon trend
        aroon_up = latest.get('Aroon_Up', 50)
        aroon_down = latest.get('Aroon_Down', 50)
        
        # Count bullish signals
        bullish_signals = 0
        bullish_reasons = []
        
        if ema_10 > ema_20:
            bullish_signals += 1
            bullish_reasons.append("EMA 10 > EMA 20")
        
        if ema_20 > ema_50:
            bullish_signals += 1
            bullish_reasons.append("EMA 20 > EMA 50")
        
        if close > sma_200:
            bullish_signals += 1
            bullish_reasons.append("Price > SMA 200")
        
        if adx > 25:
            bullish_signals += 1
            bullish_reasons.append("Strong Trend (ADX > 25)")
        
        if st_trend == 1:
            bullish_signals += 1
            bullish_reasons.append("Supertrend Bullish")
        
        if aroon_up > aroon_down:
            bullish_signals += 1
            bullish_reasons.append("Aroon Bullish")
        
        # Bearish signals
        bearish_signals = 6 - bullish_signals
        bearish_reasons = [
            r.replace("Bullish", "Bearish").replace(">", "<") for r in bullish_reasons
        ]
        
        if bullish_signals > bearish_signals:
            trend = "BULLISH"
            confidence = (bullish_signals / 6) * 100
        elif bearish_signals > bullish_signals:
            trend = "BEARISH"
            confidence = (bearish_signals / 6) * 100
        else:
            trend = "NEUTRAL"
            confidence = 50
        
        return {
            'trend': trend,
            'confidence': min(100, confidence),
            'bullish_signals': bullish_signals,
            'reasons': bullish_reasons if trend == "BULLISH" else bearish_reasons,
            'adx': adx,
            'supertrend': st_trend
        }
    
    @staticmethod
    def evaluate_momentum_confirmation(df: pd.DataFrame) -> Dict:
        """
        Momentum confirmation with multiple indicators
        """
        latest = df.iloc[-1]
        
        rsi = latest.get('RSI', 50)
        macd_hist = latest.get('MACD_Histogram', 0)
        roc = latest.get('ROC', 0)
        williams_r = latest.get('Williams_R', -50)
        mfi = latest.get('MFI', 50)
        
        confirmation_score = 0
        bullish_indicators = []
        
        # RSI analysis
        if 40 < rsi < 70:
            confirmation_score += 1
            bullish_indicators.append("RSI Healthy Bullish")
        elif rsi > 70:
            confirmation_score += 0.5
            bullish_indicators.append("RSI Overbought (caution)")
        
        # MACD
        if macd_hist > 0 and len(df) > 1:
            prev_hist = df.iloc[-2].get('MACD_Histogram', 0)
            if macd_hist > prev_hist:
                confirmation_score += 1
                bullish_indicators.append("MACD Increasing Bullish")
            else:
                confirmation_score += 0.5
                bullish_indicators.append("MACD Positive but Weakening")
        
        # ROC (Rate of Change)
        if roc > 0:
            confirmation_score += 1
            bullish_indicators.append(f"ROC Positive ({roc:.2f}%)")
        
        # Williams %R
        if -80 < williams_r < -20:
            confirmation_score += 1
            bullish_indicators.append("Williams %R Healthy")
        
        # MFI
        if 40 < mfi < 80:
            confirmation_score += 1
            bullish_indicators.append("MFI Healthy")
        elif mfi > 80:
            confirmation_score += 0.5
            bullish_indicators.append("MFI Overbought")
        
        max_score = 5
        confidence = (confirmation_score / max_score) * 100
        
        return {
            'confirmed': confirmation_score >= 3,
            'confidence': min(100, confidence),
            'score': confirmation_score,
            'indicators': bullish_indicators,
            'rsi': rsi,
            'mfi': mfi
        }
    
    @staticmethod
    def evaluate_volume_confirmation(df: pd.DataFrame) -> Dict:
        """
        Volume validation - must confirm price movement
        """
        latest = df.iloc[-1]
        
        current_volume = latest['volume']
        volume_ma = latest.get('Volume_MA', current_volume)
        obv = latest.get('OBV', 0)
        cmf = latest.get('CMF', 0)
        
        confirmation = False
        reason = "No Volume Confirmation"
        
        # Volume check
        if current_volume > volume_ma * 1.3:
            confirmation = True
            reason = "Strong Volume Confirmation"
        elif current_volume > volume_ma * 1.0:
            confirmation = True
            reason = "Adequate Volume"
        else:
            confirmation = False
            reason = "Low Volume - Risky"
        
        # OBV check
        obv_bullish = False
        if len(df) > 1:
            prev_obv = df.iloc[-2].get('OBV', obv)
            if obv > prev_obv:
                obv_bullish = True
        
        # CMF check
        cmf_bullish = cmf > 0
        
        combined_score = 0
        if confirmation:
            combined_score += 1
        if obv_bullish:
            combined_score += 1
        if cmf_bullish:
            combined_score += 1
        
        return {
            'confirmed': combined_score >= 2,
            'confidence': (combined_score / 3) * 100,
            'volume_check': confirmation,
            'obv_bullish': obv_bullish,
            'cmf_bullish': cmf_bullish,
            'reason': reason,
            'current_volume': current_volume,
            'volume_ma': volume_ma,
            'cmf': cmf
        }
    
    @staticmethod
    def evaluate_volatility_condition(df: pd.DataFrame) -> Dict:
        """
        Volatility suitability for trading
        """
        latest = df.iloc[-1]
        
        atr = latest.get('ATR', 0)
        natr = latest.get('NATR', 0)
        bb_width = latest.get('BB_Width', 0)
        historical_vol = latest.get('Historical_Vol', 0)
        
        # Calculate relative volatility
        mean_atr = df['ATR'].tail(20).mean() if 'ATR' in df.columns else atr
        volatility_ratio = atr / mean_atr if mean_atr > 0 else 1
        
        acceptable = True
        reason = "Volatility Acceptable"
        
        # Check for extreme volatility
        if natr > 8:  # Very high volatility
            acceptable = False
            reason = "HIGH VOLATILITY - Too Risky"
        elif natr > 5:  # Moderate-high
            acceptable = True
            reason = "Elevated Volatility - Use Tighter Stops"
        elif natr < 1:  # Very low volatility
            acceptable = False
            reason = "TOO LOW VOLATILITY - Breakout Setup"
        else:
            acceptable = True
            reason = "Volatility Normal"
        
        return {
            'acceptable': acceptable,
            'reason': reason,
            'volatility_ratio': volatility_ratio,
            'natr': natr,
            'historical_vol': historical_vol,
            'atr': atr
        }
    
    @staticmethod
    def apply_strict_signal_rules(df: pd.DataFrame) -> Dict:
        """
        STRICT IF-THEN RULES for signal generation
        
        IF trend is BULLISH
        AND momentum confirms
        AND volume confirms
        AND volatility acceptable
        AND risk rules pass
        → BUY
        ELSE → NEUTRAL
        """
        
        logger.info("Applying Strict Multi-Confirmation Rules...")
        
        # Get all confirmations
        trend_eval = EnhancedSignalEngine.evaluate_trend_strength(df)
        momentum_eval = EnhancedSignalEngine.evaluate_momentum_confirmation(df)
        volume_eval = EnhancedSignalEngine.evaluate_volume_confirmation(df)
        volatility_eval = EnhancedSignalEngine.evaluate_volatility_condition(df)
        
        # Initialize signal
        signal = "NEUTRAL"
        confidence = 50
        quality = SignalQuality.NEUTRAL.value
        all_checks = {
            'trend': trend_eval,
            'momentum': momentum_eval,
            'volume': volume_eval,
            'volatility': volatility_eval
        }
        
        # ========== STRICT RULE LOGIC ==========
        
        if trend_eval['trend'] == "BULLISH":
            # Trend is bullish, check other conditions
            
            if momentum_eval['confirmed']:
                # Momentum confirms
                
                if volume_eval['confirmed']:
                    # Volume confirms
                    
                    if volatility_eval['acceptable']:
                        # All conditions met → BUY
                        signal = "BUY"
                        confidence = min(
                            trend_eval['confidence'],
                            momentum_eval['confidence'],
                            volume_eval['confidence']
                        )
                        
                        # Grade the signal
                        if confidence > 85:
                            quality = SignalQuality.STRONG.value
                        elif confidence > 70:
                            quality = SignalQuality.GOOD.value
                        else:
                            quality = SignalQuality.WEAK.value
                    else:
                        # Volatility issue
                        signal = "NEUTRAL"
                        confidence = 40
                        quality = SignalQuality.NEUTRAL.value
                else:
                    # Volume doesn't confirm
                    signal = "NEUTRAL"
                    confidence = 45
                    quality = SignalQuality.NEUTRAL.value
            else:
                # Momentum doesn't confirm
                signal = "NEUTRAL"
                confidence = 50
                quality = SignalQuality.NEUTRAL.value
        
        elif trend_eval['trend'] == "BEARISH":
            # Repeat for SELL signals
            
            if momentum_eval['confirmed']:
                if volume_eval['confirmed']:
                    if volatility_eval['acceptable']:
                        signal = "SELL"
                        confidence = min(
                            trend_eval['confidence'],
                            momentum_eval['confidence'],
                            volume_eval['confidence']
                        )
                        
                        if confidence > 85:
                            quality = SignalQuality.STRONG.value
                        elif confidence > 70:
                            quality = SignalQuality.GOOD.value
                        else:
                            quality = SignalQuality.WEAK.value
                    else:
                        signal = "NEUTRAL"
                        confidence = 40
                        quality = SignalQuality.NEUTRAL.value
                else:
                    signal = "NEUTRAL"
                    confidence = 45
                    quality = SignalQuality.NEUTRAL.value
            else:
                signal = "NEUTRAL"
                confidence = 50
                quality = SignalQuality.NEUTRAL.value
        
        else:
            # No clear trend
            signal = "NEUTRAL"
            confidence = 50
            quality = SignalQuality.NEUTRAL.value
        
        # ========== CALCULATE SETUP (Entry, SL, TP) ==========
        latest = df.iloc[-1]
        current_price = latest['close']
        atr = latest.get('ATR', current_price * 0.02)
        
        setup = {
            'entry': current_price,
            'stop_loss': 0,
            'take_profit': 0,
            'rr_ratio': 0,
            'position_size': 0,
            'atr': atr
        }
        
        if signal == 'BUY':
            setup['stop_loss'] = current_price - (atr * 2.0)  # 2x ATR below entry
            setup['take_profit'] = current_price + (atr * 4.0)  # 4x ATR above entry
            setup['rr_ratio'] = (setup['take_profit'] - setup['entry']) / (setup['entry'] - setup['stop_loss'])
            
        elif signal == 'SELL':
            setup['stop_loss'] = current_price + (atr * 2.0)  # 2x ATR above entry
            setup['take_profit'] = current_price - (atr * 4.0)  # 4x ATR below entry
            setup['rr_ratio'] = (setup['entry'] - setup['take_profit']) / (setup['stop_loss'] - setup['entry'])
        
        return {
            'signal': signal,
            'confidence': confidence,
            'quality': quality,
            'setup': setup,
            'confirmations': {
                'trend': trend_eval['trend'],
                'trend_strength': f"{trend_eval['confidence']:.1f}%",
                'momentum_confirmed': momentum_eval['confirmed'],
                'momentum_strength': f"{momentum_eval['confidence']:.1f}%",
                'volume_confirmed': volume_eval['confirmed'],
                'volatility_acceptable': volatility_eval['acceptable'],
                'volatility_reason': volatility_eval['reason']
            },
            'detailed_analysis': all_checks,
            'reasons': {
                'bullish_reasons': trend_eval.get('reasons', []),
                'momentum_indicators': momentum_eval.get('indicators', []),
                'volume_status': volume_eval.get('reason', ''),
                'volatility_status': volatility_eval.get('reason', '')
            }
        }
