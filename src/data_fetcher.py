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
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFetcher:
    """Unified data fetching from multiple sources with failover"""
    
    def __init__(self):
        try:
            self.binance = ccxt.binance({'enableRateLimit': True})
            logger.info("Binance CCXT initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Binance: {e}")
            self.binance = None
        
        try:
            self.coinbase = ccxt.coinbase({'enableRateLimit': True})
            logger.info("Coinbase CCXT initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Coinbase: {e}")
            self.coinbase = None
        
    def fetch_crypto_ohlcv(self, symbol: str, timeframe: str = '1h', limit: int = 500) -> pd.DataFrame:
        """
        Fetch OHLCV data from Binance for crypto pairs with retry logic
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        # Try multiple times with exponential backoff
        for attempt in range(3):
            try:
                if self.binance is None:
                    raise Exception("Binance not initialized")
                
                logger.info(f"Fetching {symbol} from Binance (attempt {attempt + 1}/3)...")
                ohlcv = self.binance.fetch_ohlcv(symbol, timeframe, limit=limit)
                
                if not ohlcv or len(ohlcv) == 0:
                    raise Exception(f"No data returned for {symbol}")
                
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                df.set_index('timestamp', inplace=True)
                
                # Ensure data quality
                df = df.dropna()
                
                if len(df) > 50:
                    logger.info(f"Successfully fetched {len(df)} candles for {symbol} from Binance")
                    return df
                else:
                    logger.warning(f"Only {len(df)} candles returned for {symbol}, need 50+")
                    raise Exception(f"Insufficient data: only {len(df)} candles")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {str(e)}")
                if attempt < 2:
                    wait_time = 2 ** attempt
                    logger.info(f"Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
        
        # Fallback: Try to fetch from Yahoo Finance
        logger.warning(f"Binance fetch failed after 3 attempts, trying Yahoo Finance fallback for {symbol}")
        return self._fetch_crypto_yfinance_fallback(symbol, timeframe)
    
    def _fetch_crypto_yfinance_fallback(self, symbol: str, timeframe: str = '1h') -> pd.DataFrame:
        """Fallback crypto fetch using Yahoo Finance"""
        try:
            # Convert CCXT symbol to Yahoo Finance format
            # BTC/USDT -> BTCUSDT (no dash for crypto on Yahoo)
            yf_symbol = symbol.replace('/', '')
            
            period_map = {'1m': '7d', '5m': '60d', '15m': '60d', '1h': '90d', '4h': '360d', '1d': '5y'}
            period = period_map.get(timeframe, '90d')
            
            logger.info(f"Fetching {symbol} from Yahoo Finance as {yf_symbol}")
            df = yf.download(yf_symbol, period=period, interval=timeframe, progress=False)
            
            if df is None or len(df) == 0:
                raise Exception("Yahoo Finance returned no data")
            
            # Standardize columns
            if 'Adj Close' in df.columns:
                df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            df = df.dropna()
            
            if len(df) > 50:
                logger.info(f"Successfully fetched {len(df)} candles for {symbol} from Yahoo Finance fallback")
                return df
            else:
                logger.warning(f"Insufficient data from Yahoo: {len(df)} candles")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Yahoo Finance fallback also failed for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    def fetch_stock_ohlcv(self, symbol: str, period: str = '90d', interval: str = '1h') -> pd.DataFrame:
        """
        Fetch OHLCV data from Yahoo Finance for stocks/forex with validation
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL', 'EURUSD=X')
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y'
            interval: '1m', '5m', '15m', '30m', '60m', '1d'
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Validate period format
            if not period.endswith(('d', 'mo', 'y')):
                period = '90d'
            
            logger.info(f"Fetching {symbol} with period={period}, interval={interval}")
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            
            if df is None or len(df) == 0:
                raise Exception(f"No data returned for {symbol}")
            
            # Handle different column structures from yfinance
            if isinstance(df, pd.Series):
                # Single column, likely only Close prices
                logger.warning(f"Only close prices available for {symbol}")
                df = df.to_frame()
                df.columns = ['close']
                df['open'] = df['close']
                df['high'] = df['close']
                df['low'] = df['close']
                df['volume'] = 0
            else:
                # Normalize column names - handle MultiIndex columns (when multiple symbols)
                if isinstance(df.columns, pd.MultiIndex):
                    df = df.iloc[:, :5]  # Take first 5 columns
                
                # Rename columns to standard format
                col_mapping = {
                    'Open': 'open', 'open': 'open',
                    'High': 'high', 'high': 'high',
                    'Low': 'low', 'low': 'low',
                    'Close': 'close', 'Adj Close': 'close', 'close': 'close',
                    'Volume': 'volume', 'volume': 'volume'
                }
                
                # Create new column mapping
                new_cols = {}
                for old_col in df.columns:
                    new_col = col_mapping.get(str(old_col), None)
                    if new_col:
                        new_cols[old_col] = new_col
                
                if new_cols:
                    df = df.rename(columns=new_cols)
                else:
                    # Fallback: rename by position
                    df.columns = ['open', 'high', 'low', 'close', 'volume'][:len(df.columns)]
            
            # Ensure we have the required columns in the right order
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = df.get('close', 0)
            
            df = df[['open', 'high', 'low', 'close', 'volume']]
            df = df.dropna(subset=['close'])  # Drop rows where close is NaN
            
            # Ensure numeric columns
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna()
            
            if len(df) < 50:
                raise Exception(f"Insufficient data: only {len(df)} candles")
            
            logger.info(f"Successfully fetched {len(df)} candles for {symbol} from Yahoo Finance")
            return df
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def fetch_multiple_timeframes(self, symbol: str, asset_type: str = 'crypto') -> dict:
        """
        Fetch data for multiple timeframes (1h, 4h, 1d)
        
        Args:
            symbol: Trading pair/ticker
            asset_type: 'crypto', 'stock', or 'forex'
            
        Returns:
            Dict with data for each timeframe
        """
        timeframes_data = {}
        
        if asset_type == 'crypto':
            for tf in ['1h', '4h', '1d']:
                try:
                    data = self.fetch_crypto_ohlcv(symbol, tf)
                    if len(data) > 50:
                        timeframes_data[tf] = data
                except Exception as e:
                    logger.warning(f"Failed to fetch {tf} for {symbol}: {str(e)}")
        else:  # stock or forex
            intervals = {'1h': '1h', '4h': '4h', '1d': '1d'}
            for name, interval in intervals.items():
                try:
                    data = self.fetch_stock_ohlcv(symbol, period='360d', interval=interval)
                    if len(data) > 50:
                        timeframes_data[name] = data
                except Exception as e:
                    logger.warning(f"Failed to fetch {interval} for {symbol}: {str(e)}")
        
        return timeframes_data
    
    def fetch_data(self, symbol: str, asset_type: str = 'crypto', timeframe: str = '1h', lookback_days: int = 30) -> pd.DataFrame:
        """
        Unified fetch_data method for compatibility
        
        Args:
            symbol: Trading pair/ticker
            asset_type: 'crypto', 'forex', or 'stock'
            timeframe: '1m', '5m', '15m', '30m', '1h', '4h', '1d'
            lookback_days: Number of days of historical data (1-365)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Clamp lookback days
        lookback_days = max(1, min(365, lookback_days))
        
        try:
            if asset_type == 'crypto':
                # For crypto, use CCXT with fallback to Yahoo
                return self.fetch_crypto_ohlcv(symbol, timeframe, limit=500)
            elif asset_type == 'forex':
                # Convert forex symbol format: AUD/USD -> AUDUSD=X
                forex_symbol = symbol.replace('/', '') + '=X'
                logger.info(f"Fetching Forex: {symbol} as {forex_symbol} with {lookback_days} days")
                return self.fetch_stock_ohlcv(forex_symbol, period=f"{lookback_days}d", interval=timeframe)
            else:  # stock
                logger.info(f"Fetching Stock: {symbol} with {lookback_days} days")
                return self.fetch_stock_ohlcv(symbol, period=f"{lookback_days}d", interval=timeframe)
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
