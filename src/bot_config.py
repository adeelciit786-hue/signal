"""
Configuration Management for Signals Bot
Flexible, environment-aware settings
"""

import json
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class BotConfig:
    """Manage bot configuration"""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration"""
        self.config_path = config_path or os.path.join(
            Path(__file__).parent.parent, 'config.json'
        )
        self.config = self._load_config()
        self._set_defaults()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    logger.info(f"Configuration loaded from {self.config_path}")
                    return config
            except Exception as e:
                logger.warning(f"Error loading config file: {e}. Using defaults.")
        
        return {}
    
    def _set_defaults(self):
        """Set default values for missing config keys"""
        defaults = {
            # Account settings
            'account_balance': float(os.getenv('ACCOUNT_BALANCE', 10000)),
            'risk_percent': float(os.getenv('RISK_PERCENT', 1.0)),
            'max_consecutive_losses': int(os.getenv('MAX_CONSECUTIVE_LOSSES', 3)),
            'max_daily_loss': float(os.getenv('MAX_DAILY_LOSS', 5.0)),
            
            # Trading parameters
            'min_rr_ratio': float(os.getenv('MIN_RR_RATIO', 2.0)),
            'min_adx': float(os.getenv('MIN_ADX', 20.0)),
            'max_position_size_percent': float(os.getenv('MAX_POSITION_SIZE', 5.0)),
            'max_drawdown': float(os.getenv('MAX_DRAWDOWN', 10.0)),
            
            # Indicator settings
            'fast_ma_period': int(os.getenv('FAST_MA_PERIOD', 10)),
            'slow_ma_period': int(os.getenv('SLOW_MA_PERIOD', 20)),
            'rsi_period': int(os.getenv('RSI_PERIOD', 14)),
            'rsi_overbought': int(os.getenv('RSI_OVERBOUGHT', 70)),
            'rsi_oversold': int(os.getenv('RSI_OVERSOLD', 30)),
            'macd_fast': int(os.getenv('MACD_FAST', 12)),
            'macd_slow': int(os.getenv('MACD_SLOW', 26)),
            'macd_signal': int(os.getenv('MACD_SIGNAL', 9)),
            'bb_period': int(os.getenv('BB_PERIOD', 20)),
            'bb_std_dev': float(os.getenv('BB_STD_DEV', 2.0)),
            'atr_period': int(os.getenv('ATR_PERIOD', 14)),
            'adx_period': int(os.getenv('ADX_PERIOD', 14)),
            
            # Backtest settings
            'backtest_lookback_days': int(os.getenv('BACKTEST_LOOKBACK_DAYS', 30)),
            'min_backtest_trades': int(os.getenv('MIN_BACKTEST_TRADES', 5)),
            'min_win_rate': float(os.getenv('MIN_WIN_RATE', 0.45)),
            'min_profit_factor': float(os.getenv('MIN_PROFIT_FACTOR', 1.2)),
            
            # Data sources
            'crypto_exchange': os.getenv('CRYPTO_EXCHANGE', 'binance'),
            'forex_source': os.getenv('FOREX_SOURCE', 'yfinance'),
            'stock_source': os.getenv('STOCK_SOURCE', 'yfinance'),
            
            # Assets to monitor
            'assets': [
                {'symbol': 'BTC/USDT', 'type': 'crypto', 'timeframe': '1h'},
                {'symbol': 'ETH/USDT', 'type': 'crypto', 'timeframe': '1h'},
                {'symbol': 'AAPL', 'type': 'stock', 'timeframe': '1h'},
            ],
            
            # Signal settings
            'confidence_threshold': float(os.getenv('CONFIDENCE_THRESHOLD', 60.0)),
            'signal_quality_weights': {
                'A+': 1.0,
                'B': 0.75,
                'C': 0.5,
                'NEUTRAL': 0.0
            },
            
            # Notification settings
            'send_notifications': os.getenv('SEND_NOTIFICATIONS', 'true').lower() == 'true',
            'notification_channels': ['console'],  # 'email', 'telegram', 'discord'
            
            # API keys (from environment)
            'binance_api_key': os.getenv('BINANCE_API_KEY', ''),
            'binance_api_secret': os.getenv('BINANCE_API_SECRET', ''),
            'telegram_bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'telegram_chat_id': os.getenv('TELEGRAM_CHAT_ID', ''),
        }
        
        # Merge with loaded config (loaded config takes precedence)
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(Path(self.config_path).parent, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
                logger.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        logger.debug(f"Set config {key} = {value}")
    
    def get_account_settings(self) -> Dict:
        """Get account-related settings"""
        return {
            'balance': self.get('account_balance'),
            'risk_percent': self.get('risk_percent'),
            'max_risk_amount': self.get('account_balance') * self.get('risk_percent') / 100,
            'max_consecutive_losses': self.get('max_consecutive_losses'),
            'max_daily_loss': self.get('max_daily_loss'),
            'max_drawdown': self.get('max_drawdown'),
        }
    
    def get_trading_rules(self) -> Dict:
        """Get trading rule settings"""
        return {
            'min_rr_ratio': self.get('min_rr_ratio'),
            'min_adx': self.get('min_adx'),
            'max_position_size_percent': self.get('max_position_size_percent'),
            'confidence_threshold': self.get('confidence_threshold'),
        }
    
    def get_indicator_settings(self) -> Dict:
        """Get indicator settings"""
        return {
            'fast_ma_period': self.get('fast_ma_period'),
            'slow_ma_period': self.get('slow_ma_period'),
            'rsi_period': self.get('rsi_period'),
            'rsi_overbought': self.get('rsi_overbought'),
            'rsi_oversold': self.get('rsi_oversold'),
            'macd_fast': self.get('macd_fast'),
            'macd_slow': self.get('macd_slow'),
            'macd_signal': self.get('macd_signal'),
            'bb_period': self.get('bb_period'),
            'bb_std_dev': self.get('bb_std_dev'),
            'atr_period': self.get('atr_period'),
            'adx_period': self.get('adx_period'),
        }
    
    def get_backtest_settings(self) -> Dict:
        """Get backtest settings"""
        return {
            'lookback_days': self.get('backtest_lookback_days'),
            'min_trades': self.get('min_backtest_trades'),
            'min_win_rate': self.get('min_win_rate'),
            'min_profit_factor': self.get('min_profit_factor'),
        }
    
    def get_assets(self) -> list:
        """Get assets to monitor"""
        return self.get('assets', [])
    
    def validate_config(self) -> tuple[bool, list]:
        """Validate configuration values"""
        errors = []
        
        # Check account settings
        if self.get('account_balance') <= 0:
            errors.append("Account balance must be positive")
        if not 0 < self.get('risk_percent') <= 10:
            errors.append("Risk percent must be between 0 and 10")
        
        # Check trading rules
        if self.get('min_rr_ratio') < 1.0:
            errors.append("Min R:R ratio must be >= 1.0")
        if self.get('min_adx') < 10:
            errors.append("Min ADX must be >= 10")
        
        # Check indicator periods
        if self.get('rsi_period') < 5:
            errors.append("RSI period must be >= 5")
        if self.get('atr_period') < 1:
            errors.append("ATR period must be >= 1")
        
        # Check backtest settings
        if self.get('backtest_lookback_days') < 7:
            errors.append("Backtest lookback must be >= 7 days")
        if not 0 < self.get('min_win_rate') <= 1:
            errors.append("Min win rate must be between 0 and 1")
        
        return len(errors) == 0, errors
    
    def print_config(self):
        """Print current configuration"""
        print("\n" + "="*70)
        print("CONFIGURATION SETTINGS")
        print("="*70)
        
        # Account
        print("\nACCOUNT:")
        print(f"  Balance:              ${self.get('account_balance'):,.2f}")
        print(f"  Risk per Trade:       {self.get('risk_percent'):.1f}%")
        print(f"  Max Risk Amount:      ${self.get('account_balance') * self.get('risk_percent') / 100:,.2f}")
        
        # Trading Rules
        print("\nTRADING RULES:")
        print(f"  Min R:R Ratio:        {self.get('min_rr_ratio'):.1f}:1")
        print(f"  Min Trend (ADX):      {self.get('min_adx'):.1f}")
        print(f"  Confidence Threshold: {self.get('confidence_threshold'):.1f}%")
        
        # Risk
        print("\nRISK MANAGEMENT:")
        print(f"  Max Consecutive Loss: {self.get('max_consecutive_losses')}")
        print(f"  Max Daily Loss:       {self.get('max_daily_loss'):.1f}%")
        print(f"  Max Drawdown:         {self.get('max_drawdown'):.1f}%")
        
        # Assets
        print("\nASSETS TO MONITOR:")
        for asset in self.get('assets', []):
            print(f"  • {asset['symbol']:<12} ({asset['type']:<6}) {asset['timeframe']}")
        
        print("\n" + "="*70 + "\n")
