"""
Data Fetching Module for Real-time and Historical Market Data
Supports: Crypto (Binance, Coinbase), Forex/Stocks (Yahoo Finance)
"""

import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Unified data fetching from multiple sources"""
    
    def __init__(self):
        self.binance = ccxt.binance()
        self.coinbase = ccxt.coinbase()
        
    def fetch_crypto_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> pd.DataFrame:
        """
        Fetch OHLCV data from Binance for crypto pairs
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ohlcv = self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_stock_ohlcv(self, symbol: str, period: str = '1y', interval: str = '1h') -> pd.DataFrame:
        """
        Fetch OHLCV data from Yahoo Finance for stocks/forex
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'EURUSD=X')
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y'
            interval: '1m', '5m', '15m', '30m', '60m', '1d'
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            # Handle different column structures from yfinance
            if 'Adj Close' in df.columns:
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_multiple_timeframes(self, symbol: str, asset_type: str = 'crypto') -> dict:
        """
        Fetch data for multiple timeframes (1h, 4h, 1d)
        
        Args:
            symbol: Trading pair/ticker
            asset_type: 'crypto' or 'stock'
            
        Returns:
            Dict with data for each timeframe
        """
        timeframes_data = {}
        
        if asset_type == 'crypto':
            for tf in ['1h', '4h', '1d']:
                try:
                    timeframes_data[tf] = self.fetch_crypto_ohlcv(symbol, tf)
                except Exception as e:
                    logger.warning(f"Failed to fetch {tf} for {symbol}: {str(e)}")
        else:
            intervals = {'1h': '1h', '4h': '4h', '1d': '1d'}
            for name, interval in intervals.items():
                try:
                    timeframes_data[name] = self.fetch_stock_ohlcv(symbol, interval=interval)
                except Exception as e:
                    logger.warning(f"Failed to fetch {interval} for {symbol}: {str(e)}")
        
        return timeframes_data
    
    def fetch_data(self, symbol: str, asset_type: str = 'crypto', timeframe: str = '1h', lookback_days: int = 30) -> pd.DataFrame:
        """
        Unified fetch_data method for compatibility
        
        Args:
            symbol: Trading pair/ticker
            asset_type: 'crypto', 'forex', or 'stock'
            timeframe: '1h', '4h', '1d', '1w'
            lookback_days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if asset_type == 'crypto':
                return self.fetch_crypto_ohlcv(symbol, timeframe, limit=500)
            else:  # stock or forex
                # Map timeframe to yfinance interval
                period = f"{lookback_days}d"
                return self.fetch_stock_ohlcv(symbol, period=period, interval=timeframe)
        except Exception as e:
            logger.error(f"Error fetching {symbol} ({asset_type}, {timeframe}): {str(e)}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str, asset_type: str = 'crypto') -> float:
        """Get current price for a symbol"""
        try:
            if asset_type == 'crypto':
                ticker = self.binance.fetch_ticker(symbol)
                return ticker['last']
            else:
                data = yf.download(symbol, period='1d', interval='1h', progress=False)
                return data['Close'].iloc[-1]
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None
    
    def get_market_session_info(self) -> dict:
        """Get current market session information (UTC-based)"""
        now = datetime.utcnow()
        hour = now.hour
        
        sessions = {
            'Asia': {'open': 0, 'close': 8, 'active': 0 <= hour < 8},
            'London': {'open': 8, 'close': 16, 'active': 8 <= hour < 16},
            'New York': {'open': 13, 'close': 21, 'active': 13 <= hour < 21}
        }
        
        return {'current_utc_hour': hour, 'sessions': sessions}
