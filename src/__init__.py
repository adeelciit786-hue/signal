"""
Signals Bot - Professional Trading Signal Generator
Complete analysis with technical indicators, market regimes, risk management
"""

# Original modules
from .data_fetcher import DataFetcher
from .technical_indicators import TechnicalIndicators
from .market_regime import MarketRegimeDetector
from .strategy_logic import StrategyLogic
from .risk_manager import RiskManager
from .news_sentiment import NewsAndSentiment
from .signal_generator import SignalGenerator, OutputFormatter

# Enhanced modules
from .advanced_indicators import AdvancedIndicators
from .enhanced_signal_engine import EnhancedSignalEngine, SignalQuality
from .enhanced_risk_manager import EnhancedRiskManager
from .backtest_engine import BacktestEngine

# New modules
from .bot_config import BotConfig
from .bot_interface import BotInterface
from .bot_engine import SignalsBotEngine, BotOrchestrator

__version__ = "2.0.0"
__author__ = "Signals Bot Team"

__all__ = [
    # Original
    'DataFetcher',
    'TechnicalIndicators',
    'MarketRegimeDetector',
    'StrategyLogic',
    'RiskManager',
    'NewsAndSentiment',
    'SignalGenerator',
    'OutputFormatter',
    # Enhanced
    'AdvancedIndicators',
    'EnhancedSignalEngine',
    'SignalQuality',
    'EnhancedRiskManager',
    'BacktestEngine',
    # New
    'BotConfig',
    'BotInterface',
    'SignalsBotEngine',
    'BotOrchestrator'
]
