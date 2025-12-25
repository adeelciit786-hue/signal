"""
Market Regime Detection Module
Classifies market conditions into: Strong Trend, Range-Bound, High-Volatility, Low-Volatility Compression
"""

import pandas as pd
import numpy as np
from typing import Dict, Literal, Tuple


class MarketRegimeDetector:
    """Detect and classify market regimes"""
    
    @staticmethod
    def detect_regime(df: pd.DataFrame) -> Dict:
        """
        Classify market regime based on multiple factors:
        - Trend strength (ADX)
        - Volatility (ATR, Bollinger Bands width)
        - Range behavior
        
        Returns:
            Dict with regime classification and metrics
        """
        if len(df) < 50:
            return {'regime': 'INSUFFICIENT_DATA', 'confidence': 0}
        
        latest = df.iloc[-1]
        adx = latest.get('ADX', 0)
        atr = latest.get('ATR', 0)
        close = latest['close']
        
        # Calculate volatility metrics
        returns = df['close'].pct_change().tail(20)
        volatility = returns.std()
        mean_atr = df['ATR'].tail(20).mean()
        
        # Calculate Bollinger Band width (in percentage)
        bb_upper = latest.get('BB_Upper', close)
        bb_lower = latest.get('BB_Lower', close)
        bb_width = ((bb_upper - bb_lower) / close) * 100 if close > 0 else 0
        
        # Determine regime
        regime = MarketRegimeDetector._classify_regime(
            adx, volatility, bb_width, atr, mean_atr
        )
        
        confidence = MarketRegimeDetector._calculate_confidence(
            adx, volatility, bb_width
        )
        
        return {
            'regime': regime,
            'confidence': confidence,
            'adx': adx,
            'volatility': volatility,
            'bb_width': bb_width,
            'atr_ratio': atr / mean_atr if mean_atr > 0 else 0
        }
    
    @staticmethod
    def _classify_regime(adx: float, volatility: float, bb_width: float, atr: float, mean_atr: float) -> str:
        """
        Classify market regime
        """
        volatility_threshold_high = 0.05  # 5%
        volatility_threshold_low = 0.015  # 1.5%
        
        # High Volatility / Panic
        if volatility > volatility_threshold_high:
            return 'HIGH_VOLATILITY'
        
        # Low Volatility Compression
        if volatility < volatility_threshold_low and bb_width < 3:
            return 'COMPRESSION'
        
        # Strong Trend (ADX > 25 is very strong)
        if adx > 25:
            return 'STRONG_TREND'
        
        # Moderate Trend (ADX 20-25)
        if adx > 20:
            return 'MODERATE_TREND'
        
        # Range-Bound (ADX < 20 and stable volatility)
        if bb_width > 1 and bb_width < 4:
            return 'RANGE_BOUND'
        
        return 'CHOPPY'
    
    @staticmethod
    def _calculate_confidence(adx: float, volatility: float, bb_width: float) -> float:
        """
        Calculate confidence score (0-100) for regime classification
        """
        score = 50  # Base score
        
        # ADX strength adds confidence
        if adx > 25:
            score += 30
        elif adx > 20:
            score += 15
        elif adx < 15:
            score -= 10
        
        # Volatility consistency
        if 0.02 < volatility < 0.05:
            score += 15
        
        # Bollinger Band width consistency
        if 2 < bb_width < 5:
            score += 10
        
        return min(100, max(0, score))
    
    @staticmethod
    def get_regime_trading_rules(regime: str) -> Dict:
        """
        Get trading rules based on market regime
        """
        rules = {
            'STRONG_TREND': {
                'strategy': 'TREND_FOLLOWING',
                'entry': 'Breakout or pullback in trend direction',
                'mean_reversion': False,
                'risk_level': 'Medium-High',
                'signal_confidence_threshold': 70
            },
            'MODERATE_TREND': {
                'strategy': 'TREND_FOLLOWING',
                'entry': 'Confirmed trendline break',
                'mean_reversion': False,
                'risk_level': 'Medium',
                'signal_confidence_threshold': 75
            },
            'RANGE_BOUND': {
                'strategy': 'MEAN_REVERSION',
                'entry': 'Support/Resistance bounce',
                'mean_reversion': True,
                'risk_level': 'Low-Medium',
                'signal_confidence_threshold': 75
            },
            'CHOPPY': {
                'strategy': 'NEUTRAL',
                'entry': 'Avoid trading or use tight stops',
                'mean_reversion': False,
                'risk_level': 'Very High',
                'signal_confidence_threshold': 85
            },
            'HIGH_VOLATILITY': {
                'strategy': 'CAUTION',
                'entry': 'Only with high confirmation (90%+)',
                'mean_reversion': False,
                'risk_level': 'Very High',
                'signal_confidence_threshold': 90
            },
            'COMPRESSION': {
                'strategy': 'BREAKOUT_WAITING',
                'entry': 'Prepare for breakout outside bands',
                'mean_reversion': False,
                'risk_level': 'Low initially, High on breakout',
                'signal_confidence_threshold': 80
            },
            'INSUFFICIENT_DATA': {
                'strategy': 'NO_TRADE',
                'entry': 'Wait for more data',
                'mean_reversion': False,
                'risk_level': 'Undefined',
                'signal_confidence_threshold': 100
            }
        }
        
        return rules.get(regime, rules['CHOPPY'])
    
    @staticmethod
    def check_market_hours_liquidity(session_info: Dict) -> Dict:
        """
        Check liquidity based on market session
        """
        sessions = session_info.get('sessions', {})
        
        liquidity_levels = {
            'Asia': sessions.get('Asia', {}).get('active', False),
            'London': sessions.get('London', {}).get('active', False),
            'New York': sessions.get('New York', {}).get('active', False)
        }
        
        # Overlaps have higher liquidity
        london_ny_overlap = liquidity_levels['London'] and liquidity_levels['New York']
        
        return {
            'active_sessions': [s for s, active in liquidity_levels.items() if active],
            'liquidity_level': 'HIGH' if london_ny_overlap else ('MEDIUM' if sum(liquidity_levels.values()) > 1 else 'LOW'),
            'session_details': liquidity_levels,
            'overlap': london_ny_overlap
        }
    
    @staticmethod
    def validate_trading_conditions(regime_info: Dict, liquidity_info: Dict, market_data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Validate if current market conditions are suitable for trading
        """
        regime = regime_info.get('regime')
        
        # Check regime suitability
        if regime in ['INSUFFICIENT_DATA', 'HIGH_VOLATILITY']:
            return False, f"Unsuitable regime: {regime}"
        
        if regime == 'COMPRESSION':
            return False, "Market in compression - awaiting breakout"
        
        # Check liquidity
        if liquidity_info['liquidity_level'] == 'LOW':
            return False, "Low liquidity session"
        
        # Check for wide spreads (implied by low volume)
        if len(market_data) > 0:
            recent_volume = market_data['volume'].tail(5).mean()
            volume_ma = market_data['Volume_MA'].iloc[-1] if 'Volume_MA' in market_data.columns else recent_volume
            
            if recent_volume < volume_ma * 0.5:
                return False, "Very low volume - wide spreads likely"
        
        return True, "Market conditions suitable for trading"
