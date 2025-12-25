"""
Signal Generator & Output Formatter
Main orchestrator for generating trading signals with comprehensive output
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from .data_fetcher import DataFetcher
from .technical_indicators import TechnicalIndicators
from .market_regime import MarketRegimeDetector
from .strategy_logic import StrategyLogic
from .risk_manager import RiskManager
from .news_sentiment import NewsAndSentiment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Main signal generation engine"""
    
    def __init__(self, account_balance: float = 10000):
        self.data_fetcher = DataFetcher()
        self.risk_manager = RiskManager(account_balance=account_balance)
        
    def analyze_asset(self, symbol: str, asset_type: str = 'crypto') -> Dict:
        """
        Complete analysis of a single asset
        
        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
            asset_type: 'crypto' or 'stock'
            
        Returns:
            Dict with complete analysis and signal
        """
        logger.info(f"Analyzing {symbol}...")
        
        # ========== DATA FETCHING ==========
        timeframes_data = self.data_fetcher.fetch_multiple_timeframes(symbol, asset_type)
        
        if not timeframes_data or '1h' not in timeframes_data or len(timeframes_data['1h']) < 100:
            logger.warning(f"Insufficient data for {symbol}")
            return self._create_no_trade_response(symbol, "Insufficient historical data")
        
        # ========== CALCULATE INDICATORS ==========
        df_1h = timeframes_data['1h'].copy()
        df_4h = timeframes_data.get('4h', df_1h).copy()
        df_1d = timeframes_data.get('1d', df_1h).copy()
        
        for df in [df_1h, df_4h, df_1d]:
            TechnicalIndicators.calculate_all_indicators(df)
        
        # ========== MARKET SESSION & REGIME ==========
        session_info = self.data_fetcher.get_market_session_info()
        liquidity_info = MarketRegimeDetector.check_market_hours_liquidity(session_info)
        
        regime_info = MarketRegimeDetector.detect_regime(df_1h)
        regime_rules = MarketRegimeDetector.get_regime_trading_rules(regime_info['regime'])
        
        valid_conditions, condition_msg = MarketRegimeDetector.validate_trading_conditions(
            regime_info, liquidity_info, df_1h
        )
        
        # ========== MULTI-TIMEFRAME CONFIRMATION ==========
        # Higher timeframe (4h) defines primary trend
        trend_4h, trend_conf_4h = StrategyLogic.evaluate_trend(df_4h)
        
        # Lower timeframe (1h) for entry
        trend_1h, trend_conf_1h = StrategyLogic.evaluate_trend(df_1h)
        
        # Check timeframe conflict
        timeframe_conflict = self._check_timeframe_conflict(trend_4h, trend_1h)
        
        # ========== STRATEGY SIGNALS ==========
        trend_signal = StrategyLogic.evaluate_trend(df_1h)
        momentum_signal = StrategyLogic.evaluate_momentum(df_1h)
        volume_signal = StrategyLogic.evaluate_volume(df_1h)
        volatility_signal = StrategyLogic.evaluate_volatility_suitability(df_1h, regime_info['regime'])
        
        # Generate composite signal
        composite_signal = StrategyLogic.generate_composite_signal(
            trend_signal, momentum_signal, volume_signal, volatility_signal, regime_info['regime']
        )
        
        # ========== NEWS & SENTIMENT ==========
        sentiment_data = NewsAndSentiment.evaluate_news_and_sentiment(symbol)
        
        # Adjust confidence based on sentiment
        final_confidence = composite_signal['confidence'] + sentiment_data['confidence_adjustment']
        final_confidence = max(0, min(100, final_confidence))
        
        # ========== RISK MANAGEMENT ==========
        current_price = df_1h['close'].iloc[-1]
        atr = df_1h['ATR'].iloc[-1]
        
        if composite_signal['signal'] == 'BUY':
            stop_loss = self.risk_manager.calculate_atr_stop_loss(current_price, atr, 'BUY')
            take_profit = current_price + (atr * 4)  # 4x ATR for reward
        elif composite_signal['signal'] == 'SELL':
            stop_loss = self.risk_manager.calculate_atr_stop_loss(current_price, atr, 'SELL')
            take_profit = current_price - (atr * 4)
        else:
            stop_loss = 0
            take_profit = 0
        
        # Validate risk-reward
        rr_valid = True
        rr_ratio = 0
        if composite_signal['signal'] != 'NEUTRAL':
            rr_valid, rr_ratio, rr_msg = self.risk_manager.validate_risk_reward(
                current_price, stop_loss, take_profit
            )
        
        # Check liquidity
        liquidity_ok, liquidity_msg = self.risk_manager.check_liquidity_conditions(df_1h)
        
        # Check ADX
        adx_ok, adx_msg = self.risk_manager.check_adx_strength(regime_info['adx'])
        
        # Position sizing
        position_size = self.risk_manager.calculate_position_size(current_price, stop_loss) if composite_signal['signal'] != 'NEUTRAL' else 0
        position_reduction_mult, position_reduction_msg = self.risk_manager.should_reduce_risk_after_losses()
        
        # ========== FINAL SIGNAL DETERMINATION ==========
        # Apply all filters
        final_signal = composite_signal['signal']
        
        # Timeframe conflict overrides
        if timeframe_conflict:
            final_signal = 'NEUTRAL'
            logger.warning(f"Timeframe conflict: 4H {trend_4h} vs 1H {trend_1h}")
        
        # Risk conditions filter
        if not valid_conditions:
            final_signal = 'NEUTRAL'
        
        if not liquidity_ok:
            final_signal = 'NEUTRAL'
        
        if not adx_ok and final_signal != 'NEUTRAL':
            final_signal = 'NEUTRAL'
        
        if not rr_valid and final_signal != 'NEUTRAL':
            final_signal = 'NEUTRAL'
        
        # Negative sentiment adjustment
        if sentiment_data['overall_sentiment'] == 'NEGATIVE':
            final_confidence *= 0.7  # Reduce confidence
        
        # High-impact event uncertainty
        if sentiment_data['high_impact_event_detected']:
            final_signal = 'NEUTRAL'
            logger.info(f"High-impact event detected: {sentiment_data['high_impact_events']}")
        
        # ========== COMPILE RESULTS ==========
        return {
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'signal': final_signal,
            'confidence': min(100, max(0, final_confidence)),
            'grade': self._determine_signal_grade(final_signal, final_confidence),
            
            # Pricing & Setup
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': stop_loss if final_signal != 'NEUTRAL' else 0,
            'take_profit': take_profit if final_signal != 'NEUTRAL' else 0,
            'risk_reward_ratio': rr_ratio if final_signal != 'NEUTRAL' else 0,
            'position_size': position_size * position_reduction_mult if final_signal != 'NEUTRAL' else 0,
            
            # Technical Analysis
            'technical_indicators': {
                'current_price': current_price,
                'SMA_10': df_1h['SMA_10'].iloc[-1],
                'SMA_20': df_1h['SMA_20'].iloc[-1],
                'EMA_10': df_1h['EMA_10'].iloc[-1],
                'RSI': df_1h['RSI'].iloc[-1],
                'MACD': df_1h['MACD'].iloc[-1],
                'ADX': regime_info['adx'],
                'ATR': atr,
                'Bollinger_Bands': {
                    'upper': df_1h['BB_Upper'].iloc[-1],
                    'middle': df_1h['BB_Middle'].iloc[-1],
                    'lower': df_1h['BB_Lower'].iloc[-1]
                }
            },
            
            # Alignment Summary
            'indicator_alignment': {
                'trend': f"{trend_signal[0]} (confidence: {trend_signal[1]:.0f}%)",
                'momentum': f"{momentum_signal[0]} (confidence: {momentum_signal[1]:.0f}%)",
                'volume': f"{volume_signal[0]} (confidence: {volume_signal[1]:.0f}%)",
                'volatility': f"{volatility_signal[0]} (confidence: {volatility_signal[1]:.0f}%)"
            },
            
            # Market Context
            'market_regime': regime_info['regime'],
            'regime_confidence': regime_info['confidence'],
            'trading_strategy': regime_rules['strategy'],
            'market_session': liquidity_info['active_sessions'],
            'liquidity_level': liquidity_info['liquidity_level'],
            
            # Timeframe Analysis
            'timeframe_analysis': {
                '4H_trend': trend_4h,
                '1H_trend': trend_1h,
                'timeframe_conflict': timeframe_conflict
            },
            
            # Support & Resistance
            'key_levels': self._extract_key_levels(df_1h),
            'fibonacci_levels': TechnicalIndicators.calculate_fibonacci_levels(
                df_1h['high'].max(), df_1h['low'].min()
            ),
            
            # News & Sentiment
            'news_sentiment': {
                'overall_sentiment': sentiment_data['overall_sentiment'],
                'sentiment_strength': sentiment_data['sentiment_strength'],
                'high_impact_event': sentiment_data['high_impact_event_detected'],
                'impact_events': sentiment_data['high_impact_events'],
                'recommendation': sentiment_data['recommendation']
            },
            
            # Risk Notes
            'risk_notes': RiskManager.get_risk_notes(
                {
                    'signal': final_signal,
                    'adx': regime_info['adx'],
                    'confidence': final_confidence,
                    'news_impact': sentiment_data['overall_sentiment']
                },
                {
                    'consecutive_losses': self.risk_manager.consecutive_losses,
                    'position_size_multiplier': position_reduction_mult,
                    'liquidity_ok': liquidity_ok
                }
            ),
            
            # Validation Messages
            'validation_messages': [
                condition_msg if not valid_conditions else "✓ Market conditions suitable",
                liquidity_msg,
                adx_msg,
                rr_msg if final_signal != 'NEUTRAL' else "",
                sentiment_data['recommendation']
            ]
        }
    
    @staticmethod
    def _check_timeframe_conflict(trend_4h: str, trend_1h: str) -> bool:
        """Check if higher and lower timeframes conflict"""
        if trend_4h == 'NEUTRAL' or trend_1h == 'NEUTRAL':
            return False
        
        bullish_4h = 'BULLISH' in trend_4h
        bullish_1h = 'BULLISH' in trend_1h
        
        return bullish_4h != bullish_1h
    
    @staticmethod
    def _extract_key_levels(df: pd.DataFrame) -> Dict:
        """Extract support, resistance, and key MAs"""
        sma_50 = df.get('SMA_50', pd.Series([0]*len(df))).iloc[-1] if 'SMA_50' in df.columns else 0
        sma_200 = df.get('SMA_200', pd.Series([0]*len(df))).iloc[-1] if 'SMA_200' in df.columns else 0
        
        return {
            '24h_high': df['high'].tail(24).max(),
            '24h_low': df['low'].tail(24).min(),
            'key_resistance': df['high'].tail(50).max(),
            'key_support': df['low'].tail(50).min(),
            'SMA_50_level': sma_50,
            'SMA_200_level': sma_200
        }
    
    @staticmethod
    def _determine_signal_grade(signal: str, confidence: float) -> str:
        """Determine signal quality grade"""
        if signal == 'NEUTRAL':
            return 'No-Trade'
        elif confidence > 85:
            return 'A+'
        elif confidence > 70:
            return 'B'
        else:
            return 'No-Trade'
    
    @staticmethod
    def _create_no_trade_response(symbol: str, reason: str) -> Dict:
        """Create NO TRADE response"""
        return {
            'symbol': symbol,
            'signal': 'NEUTRAL',
            'confidence': 0,
            'grade': 'No-Trade',
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        }


class OutputFormatter:
    """Format signal output for display"""
    
    @staticmethod
    def format_signal_report(analysis: Dict) -> str:
        """
        Format analysis into readable report
        """
        symbol = analysis.get('symbol', 'N/A')
        signal = analysis.get('signal', 'NEUTRAL')
        confidence = analysis.get('confidence', 0)
        grade = analysis.get('grade', 'No-Trade')
        
        report = f"""
{'='*70}
TRADING SIGNAL ANALYSIS
{'='*70}

ASSET: {symbol}
TIME: {analysis.get('timestamp', 'N/A')}

{'─'*70}
SIGNAL
{'─'*70}

Signal: {signal} | Confidence: {confidence:.0f}% | Grade: {grade}

{'─'*70}
SETUP DETAILS
{'─'*70}

Current Price:        ${analysis.get('current_price', 0):.2f}
Entry Price:          ${analysis.get('entry_price', 0):.2f}
Stop Loss:            ${analysis.get('stop_loss', 0):.2f}
Take Profit:          ${analysis.get('take_profit', 0):.2f}
Risk-Reward Ratio:    {analysis.get('risk_reward_ratio', 0):.2f}:1
Position Size:        {analysis.get('position_size', 0):.4f} units

{'─'*70}
INDICATOR ALIGNMENT
{'─'*70}

"""
        for indicator, alignment in analysis.get('indicator_alignment', {}).items():
            report += f"{indicator.replace('_', ' ').title():<20} {alignment}\n"
        
        report += f"""
{'─'*70}
MARKET CONTEXT
{'─'*70}

Regime:               {analysis.get('market_regime', 'N/A')} (conf: {analysis.get('regime_confidence', 0):.0f}%)
Strategy:             {analysis.get('trading_strategy', 'N/A')}
Liquidity Level:      {analysis.get('liquidity_level', 'N/A')}
Active Sessions:      {', '.join(analysis.get('market_session', []))}

{'─'*70}
KEY LEVELS
{'─'*70}

"""
        for level, value in analysis.get('key_levels', {}).items():
            report += f"{level.replace('_', ' ').title():<25} ${value:.2f}\n"
        
        # Fibonacci levels
        report += "\nFibonacci Levels:\n"
        for level, value in analysis.get('fibonacci_levels', {}).items():
            report += f"  {level:<8} ${value:.2f}\n"
        
        report += f"""
{'─'*70}
NEWS & SENTIMENT
{'─'*70}

Sentiment:            {analysis.get('news_sentiment', {}).get('overall_sentiment', 'N/A')}
Impact Events:        {', '.join(analysis.get('news_sentiment', {}).get('impact_events', ['None']))}
Recommendation:       {analysis.get('news_sentiment', {}).get('recommendation', 'N/A')}

{'─'*70}
RISK NOTES
{'─'*70}

{analysis.get('risk_notes', 'No specific risk notes')}

{'─'*70}
VALIDATION
{'─'*70}

"""
        for msg in analysis.get('validation_messages', []):
            if msg:
                report += f"* {msg}\n"
        
        report += f"\n{'='*70}\n"
        
        return report
    
    @staticmethod
    def format_csv_output(analyses: List[Dict]) -> str:
        """Format multiple analyses as CSV"""
        import csv
        import io
        
        output = io.StringIO()
        if not analyses:
            return ""
        
        fieldnames = ['Symbol', 'Signal', 'Confidence', 'Grade', 'Regime', 'Liquidity', 'Price', 'Stop Loss', 'Take Profit', 'RR Ratio']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        for analysis in analyses:
            writer.writerow({
                'Symbol': analysis.get('symbol'),
                'Signal': analysis.get('signal'),
                'Confidence': f"{analysis.get('confidence', 0):.0f}%",
                'Grade': analysis.get('grade'),
                'Regime': analysis.get('market_regime'),
                'Liquidity': analysis.get('liquidity_level'),
                'Price': f"${analysis.get('current_price', 0):.2f}",
                'Stop Loss': f"${analysis.get('stop_loss', 0):.2f}",
                'Take Profit': f"${analysis.get('take_profit', 0):.2f}",
                'RR Ratio': f"{analysis.get('risk_reward_ratio', 0):.2f}"
            })
        
        return output.getvalue()
