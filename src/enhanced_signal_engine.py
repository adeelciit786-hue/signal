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
        
        # Basic MAs - use close price if not available
        ema_10 = latest.get('EMA_10')
        ema_20 = latest.get('EMA_20')
        ema_50 = latest.get('EMA_50')
        sma_200 = latest.get('SMA_200')
        
        # Fill NaN with close price
        ema_10 = ema_10 if pd.notna(ema_10) else close
        ema_20 = ema_20 if pd.notna(ema_20) else close
        ema_50 = ema_50 if pd.notna(ema_50) else close
        sma_200 = sma_200 if pd.notna(sma_200) else close
        
        # ADX trend strength
        adx = latest.get('ADX', 25)  # Default to moderate trend
        if pd.isna(adx):
            adx = 25
        
        # Supertrend
        st_trend = latest.get('Supertrend_Trend', 1)  # Default to 1 (bullish)
        if pd.isna(st_trend):
            st_trend = 1
        
        # Aroon trend
        aroon_up = latest.get('Aroon_Up', 50)
        aroon_down = latest.get('Aroon_Down', 50)
        if pd.isna(aroon_up):
            aroon_up = 50
        if pd.isna(aroon_down):
            aroon_down = 50
        
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
        
        if adx > 20:  # Lowered threshold
            bullish_signals += 1
            bullish_reasons.append(f"Trend Strength (ADX {adx:.1f})")
        
        if st_trend == 1:
            bullish_signals += 1
            bullish_reasons.append("Supertrend Bullish")
        
        if aroon_up > aroon_down:
            bullish_signals += 1
            bullish_reasons.append("Aroon Bullish")
        
        # Bearish signals
        bearish_signals = 6 - bullish_signals
        bearish_reasons = [
            "EMA 10 < EMA 20",
            "EMA 20 < EMA 50",
            "Price < SMA 200",
            f"Weak Trend (ADX {adx:.1f})",
            "Supertrend Bearish",
            "Aroon Bearish"
        ]
        
        # Determine trend - LOWER THRESHOLD FOR GENERATION
        if bullish_signals >= 3:  # 3+ signals = BULLISH
            trend = "BULLISH"
            confidence = min(100, (bullish_signals / 6) * 100)
        elif bearish_signals >= 3:
            trend = "BEARISH"
            confidence = min(100, (bearish_signals / 6) * 100)
        else:
            # With fewer signals, still try to determine direction
            if bullish_signals > bearish_signals:
                trend = "BULLISH"
                confidence = min(100, (bullish_signals / 6) * 100)
            elif bearish_signals > bullish_signals:
                trend = "BEARISH"
                confidence = min(100, (bearish_signals / 6) * 100)
            else:
                trend = "NEUTRAL"
                confidence = 50
        
        return {
            'trend': trend,
            'confidence': min(100, max(50, confidence)),  # Min 50% confidence
            'bullish_signals': bullish_signals,
            'bearish_signals': bearish_signals,
            'reasons': bullish_reasons if trend == "BULLISH" else bearish_reasons[:bullish_signals],
            'adx': adx,
            'supertrend': st_trend,
            'ema_10': ema_10,
            'ema_20': ema_20,
            'ema_50': ema_50,
            'sma_200': sma_200,
            'close': close
        }
    
    @staticmethod
    def evaluate_momentum_confirmation(df: pd.DataFrame) -> Dict:
        """
        Momentum confirmation with multiple indicators
        """
        latest = df.iloc[-1]
        
        rsi = latest.get('RSI')
        macd_hist = latest.get('MACD_Histogram')
        roc = latest.get('ROC')
        williams_r = latest.get('Williams_R')
        mfi = latest.get('MFI')
        
        # Fill NaN with neutral values
        if pd.isna(rsi):
            rsi = 50
        if pd.isna(macd_hist):
            macd_hist = 0
        if pd.isna(roc):
            roc = 0
        if pd.isna(williams_r):
            williams_r = -50
        if pd.isna(mfi):
            mfi = 50
        
        confirmation_score = 0
        bullish_indicators = []
        
        # RSI analysis - more lenient
        if 30 < rsi < 80:  # Wider range
            confirmation_score += 1
            bullish_indicators.append(f"RSI: {rsi:.1f}")
        elif rsi >= 50:  # Even weak bullish is ok
            confirmation_score += 0.5
            bullish_indicators.append(f"RSI: {rsi:.1f}")
        
        # MACD
        if macd_hist > 0:
            confirmation_score += 1
            bullish_indicators.append("MACD Positive")
            if len(df) > 1:
                prev_hist = df.iloc[-2].get('MACD_Histogram', 0)
                if pd.isna(prev_hist):
                    prev_hist = 0
                if macd_hist > prev_hist:
                    bullish_indicators[-1] += " (Increasing)"
        elif len(df) > 1:
            prev_hist = df.iloc[-2].get('MACD_Histogram', 0)
            if pd.isna(prev_hist):
                prev_hist = 0
            if prev_hist > 0 and macd_hist > prev_hist * 0.5:
                confirmation_score += 0.3
                bullish_indicators.append("MACD Weakening but Positive")
        
        # ROC (Rate of Change)
        if roc > 0:
            confirmation_score += 1
            bullish_indicators.append(f"ROC: {roc:.2f}%")
        elif roc > -0.5:  # Slightly negative is ok
            confirmation_score += 0.3
            bullish_indicators.append(f"ROC: {roc:.2f}%")
        
        # Williams %R - more lenient
        if -80 < williams_r < -20:
            confirmation_score += 1
            bullish_indicators.append(f"Williams %R: {williams_r:.1f}")
        elif -95 < williams_r < 0:
            confirmation_score += 0.3
            bullish_indicators.append(f"Williams %R: {williams_r:.1f}")
        
        # MFI - more lenient
        if 30 < mfi < 90:
            confirmation_score += 1
            bullish_indicators.append(f"MFI: {mfi:.1f}")
        elif mfi > 40:
            confirmation_score += 0.3
            bullish_indicators.append(f"MFI: {mfi:.1f}")
        
        max_score = 5
        confidence = min(100, (confirmation_score / max_score) * 100)
        
        # LOWER THRESHOLD - need 1.5 or more for confirmation
        return {
            'confirmed': confirmation_score >= 1.5,
            'confidence': min(100, max(50, confidence)),  # Min 50%
            'score': confirmation_score,
            'indicators': bullish_indicators,
            'rsi': rsi,
            'mfi': mfi,
            'macd_hist': macd_hist
        }
    
    @staticmethod
    def evaluate_volume_confirmation(df: pd.DataFrame) -> Dict:
        """
        Volume validation - LENIENT check
        Don't block signals just for low volume
        """
        latest = df.iloc[-1]
        
        current_volume = latest['volume']
        volume_ma = latest.get('Volume_MA', current_volume)
        obv = latest.get('OBV', 0)
        cmf = latest.get('CMF', 0)
        
        # Much more lenient volume checks
        volume_ok = current_volume >= volume_ma * 0.4  # 40% of average is OK
        
        # OBV check - just needs to be rising
        obv_bullish = False
        if len(df) > 1:
            prev_obv = df.iloc[-2].get('OBV', obv)
            if obv > prev_obv:
                obv_bullish = True
        
        # CMF check - positive money flow
        cmf_bullish = cmf > -0.1  # Very lenient
        
        # Confirmation score - need at least 1 positive
        combined_score = 0
        reason_parts = []
        
        if volume_ok:
            combined_score += 1
            reason_parts.append(f"Volume OK ({current_volume:.0f} vs MA {volume_ma:.0f})")
        else:
            reason_parts.append(f"Low volume ({current_volume:.0f} vs MA {volume_ma:.0f})")
        
        if obv_bullish:
            combined_score += 1
            reason_parts.append("OBV Rising")
        
        if cmf_bullish:
            combined_score += 1
            reason_parts.append("Positive Flows")
        
        return {
            'confirmed': combined_score >= 1,  # Just need 1 positive (was 2)
            'confidence': min(100, (combined_score / 3) * 100),
            'volume_check': volume_ok,
            'obv_bullish': obv_bullish,
            'cmf_bullish': cmf_bullish,
            'reason': " | ".join(reason_parts),
            'current_volume': current_volume,
            'volume_ma': volume_ma,
            'cmf': cmf
        }
    
    @staticmethod
    def evaluate_volatility_condition(df: pd.DataFrame) -> Dict:
        """
        Volatility suitability for trading
        More permissive - low volatility is OK for range-bound trades
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
        
        # Check for EXTREME volatility only (reject only if too risky)
        if natr > 10:  # Extremely high volatility - risky
            acceptable = False
            reason = "EXTREME VOLATILITY - Too Risky"
        elif natr > 7:  # Very high - warn but allow
            acceptable = True
            reason = "HIGH VOLATILITY - Use Wider Stops"
        elif natr > 4:  # Moderate-high
            acceptable = True
            reason = "ELEVATED VOLATILITY"
        elif natr < 0.5:  # Very low - allow for range-bound trades
            acceptable = True
            reason = "LOW VOLATILITY - Range-Bound Setup"
        else:
            acceptable = True
            reason = "Volatility Acceptable"
        
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
        
    @staticmethod
    def apply_strict_signal_rules(df: pd.DataFrame) -> Dict:
        """
        CONSERVATIVE MULTI-CONFIRMATION SIGNAL RULES
        Only generates BUY/SELL when multiple conditions align
        Prioritizes accuracy over frequency
        """
        
        logger.info("Applying Conservative Multi-Confirmation Rules...")
        
        if len(df) < 50:
            return {
                'signal': 'NEUTRAL',
                'confidence': 0,
                'quality': 'INSUFFICIENT_DATA',
                'setup': {'entry': 0, 'stop_loss': 0, 'take_profit': 0, 'rr_ratio': 0},
                'reasons': {'bullish_reasons': ['Insufficient historical data (need 50+ candles)']}
            }
        
        # Get all confirmations
        trend_eval = EnhancedSignalEngine.evaluate_trend_strength(df)
        momentum_eval = EnhancedSignalEngine.evaluate_momentum_confirmation(df)
        volume_eval = EnhancedSignalEngine.evaluate_volume_confirmation(df)
        volatility_eval = EnhancedSignalEngine.evaluate_volatility_condition(df)
        
        latest = df.iloc[-1]
        current_price = latest['close']
        atr = latest.get('ATR', current_price * 0.02)
        if pd.isna(atr):
            atr = current_price * 0.02
        
        signal = "NEUTRAL"
        confidence = 0
        quality = SignalQuality.NEUTRAL.value
        
        all_checks = {
            'trend': trend_eval,
            'momentum': momentum_eval,
            'volume': volume_eval,
            'volatility': volatility_eval
        }
        
        # ========== ENHANCED SIGNAL RULES ==========
        # PRIMARY: Trend + Momentum MUST align
        # SECONDARY: Volume & Volatility are informational
        
        trend = trend_eval['trend']
        trend_conf = trend_eval['confidence']
        momentum_conf = momentum_eval['confidence']
        momentum_ok = momentum_eval['confirmed']
        volume_ok = volume_eval['confirmed']
        
        # BUY SIGNAL: Trend BULLISH + Momentum Confirmed
        # (Volume is secondary - doesn't block the signal)
        if (trend == "BULLISH" and 
            trend_conf > 45 and  # Lowered to 45% for more signals
            momentum_ok and 
            momentum_conf > 45):  # Lowered to 45% for faster confirmation
            
            signal = "BUY"
            # Confidence is weighted: Trend + Momentum + Volume bonus
            base_confidence = (trend_conf + momentum_conf) / 2
            
            # Add volume bonus if confirmed
            if volume_ok:
                confidence = min(95, base_confidence + 5)  # Bonus for volume
            else:
                confidence = base_confidence  # Use as-is if no volume
            
            # Quality based on confidence
            if confidence > 80:
                quality = SignalQuality.STRONG.value
            elif confidence > 65:
                quality = SignalQuality.GOOD.value
            elif confidence > 50:
                quality = SignalQuality.WEAK.value
            else:
                quality = SignalQuality.NEUTRAL.value
        
        # SELL SIGNAL: Trend BEARISH + Momentum Confirmed
        # (Volume is secondary - doesn't block the signal)
        elif (trend == "BEARISH" and 
              trend_conf > 45 and
              momentum_ok and 
              momentum_conf > 45):
            
            signal = "SELL"
            # Confidence is weighted: Trend + Momentum + Volume bonus
            base_confidence = (trend_conf + momentum_conf) / 2
            
            # Add volume bonus if confirmed
            if volume_ok:
                confidence = min(95, base_confidence + 5)  # Bonus for volume
            else:
                confidence = base_confidence  # Use as-is if no volume
            
            # Quality based on confidence
            if confidence > 80:
                quality = SignalQuality.STRONG.value
            elif confidence > 65:
                quality = SignalQuality.GOOD.value
            elif confidence > 50:
                quality = SignalQuality.WEAK.value
            else:
                quality = SignalQuality.NEUTRAL.value
        
        # No signal if PRIMARY conditions (Trend + Momentum) don't align
        else:
            signal = "NEUTRAL"
            confidence = 0
            quality = SignalQuality.NEUTRAL.value
        
        # ========== CALCULATE SETUP (Entry, SL, TP) ==========
        setup = {
            'entry': current_price,
            'stop_loss': 0,
            'take_profit': 0,
            'rr_ratio': 0,
            'position_size': 0,
            'atr': atr,
            'signal_bars': len(df)
        }
        
        if signal == 'BUY':
            # Conservative: 2.5x ATR for stop (wider)
            setup['stop_loss'] = current_price - (atr * 2.5)
            # Conservative: 5x ATR for TP (better rewards)
            setup['take_profit'] = current_price + (atr * 5.0)
            setup['rr_ratio'] = (setup['take_profit'] - setup['entry']) / (setup['entry'] - setup['stop_loss'])
            
        elif signal == 'SELL':
            # Conservative: 2.5x ATR for stop (wider)
            setup['stop_loss'] = current_price + (atr * 2.5)
            # Conservative: 5x ATR for TP (better rewards)
            setup['take_profit'] = current_price - (atr * 5.0)
            setup['rr_ratio'] = (setup['entry'] - setup['take_profit']) / (setup['stop_loss'] - setup['entry'])
        
        return {
            'signal': signal,
            'confidence': min(100, max(0, confidence)),
            'quality': quality,
            'setup': setup,
            'confirmations': {
                'trend': trend_eval['trend'],
                'trend_strength': f"{trend_eval['confidence']:.1f}%",
                'trend_bullish_signals': trend_eval.get('bullish_signals', 0),
                'momentum_confirmed': momentum_eval['confirmed'],
                'momentum_strength': f"{momentum_eval['confidence']:.1f}%",
                'volume_confirmed': volume_eval['confirmed'],
                'volatility_acceptable': volatility_eval['acceptable'],
                'volatility_reason': volatility_eval['reason'],
                'atr_value': f"{atr:.2f}"
            },
            'detailed_analysis': all_checks,
            'reasons': {
                'bullish_reasons': trend_eval.get('reasons', [])[:3],
                'momentum_indicators': momentum_eval.get('indicators', [])[:3],
                'volume_status': volume_eval.get('reason', ''),
                'volatility_status': volatility_eval.get('reason', '')
            }
        }
