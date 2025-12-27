"""
Alternative Crypto Data Fetcher
Uses multiple sources to ensure crypto data availability
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class AlternativeCryptoFetcher:
    """Fetch crypto data from alternative sources"""
    
    @staticmethod
    def fetch_from_coingecko(symbol: str, days: int = 90) -> pd.DataFrame:
        """
        Fetch crypto data from CoinGecko API (free, no auth required)
        
        Args:
            symbol: e.g., 'BTC/USDT' or 'BTC'
            days: Number of days of history to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Map symbol to CoinGecko ID
            symbol_clean = symbol.replace('/USDT', '').replace('/USD', '').upper()
            
            coingecko_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'SOL': 'solana',
                'LINK': 'chainlink',
                'MATIC': 'matic-network',
                'AVAX': 'avalanche-2',
                'AAVE': 'aave',
                'UNI': 'uniswap',
                'DOGE': 'dogecoin',
                'ADA': 'cardano',
                'XRP': 'ripple',
                'LTC': 'litecoin',
                'NEAR': 'near',
                'ARB': 'arbitrum',
                'OP': 'optimism',
            }
            
            coin_id = coingecko_map.get(symbol_clean)
            if not coin_id:
                logger.warning(f"No CoinGecko mapping for {symbol_clean}")
                return pd.DataFrame()
            
            # CoinGecko API endpoint
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': min(days, 90),  # CoinGecko free tier max
                'interval': 'daily'
            }
            
            logger.info(f"Fetching {symbol} from CoinGecko...")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'prices' not in data:
                logger.error(f"CoinGecko data missing prices for {symbol}")
                return pd.DataFrame()
            
            # Convert to daily OHLCV (CoinGecko only provides daily close)
            prices = data['prices']
            volumes = data.get('volumes', [[0, 0]] * len(prices))
            market_caps = data.get('market_caps', [[0, 0]] * len(prices))
            
            df_data = []
            for i, (timestamp_ms, price) in enumerate(prices):
                timestamp = pd.to_datetime(timestamp_ms, unit='ms')
                volume = volumes[i][1] if i < len(volumes) else 0
                
                # CoinGecko only has close prices, use as OHLC
                df_data.append({
                    'timestamp': timestamp,
                    'open': price,
                    'high': price,
                    'low': price,
                    'close': price,
                    'volume': volume
                })
            
            df = pd.DataFrame(df_data)
            df.set_index('timestamp', inplace=True)
            
            logger.info(f"Successfully fetched {len(df)} daily candles for {symbol} from CoinGecko")
            return df
        
        except Exception as e:
            logger.error(f"CoinGecko fetch failed for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_from_yahoo_crypto(symbol: str, timeframe: str = '1h', days: int = 90) -> pd.DataFrame:
        """
        Fetch crypto data from Yahoo Finance
        
        Args:
            symbol: e.g., 'BTC/USDT'
            timeframe: '1m', '5m', '15m', '30m', '1h', '4h', '1d'
            days: Number of days of history
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Convert to Yahoo Finance format
            symbol_clean = symbol.replace('/', '')  # BTC/USDT -> BTCUSDT
            yf_symbol = symbol_clean  # Yahoo might have these
            
            period_map = {
                '1m': '7d', '5m': '60d', '15m': '60d', 
                '30m': '60d', '1h': '90d', '4h': '360d', '1d': '5y'
            }
            period = period_map.get(timeframe, '90d')
            
            logger.info(f"Fetching {symbol} from Yahoo Finance (symbol={yf_symbol})...")
            
            df = yf.download(yf_symbol, period=period, interval=timeframe, progress=False)
            
            if df.empty or df is None:
                logger.warning(f"No data from Yahoo Finance for {yf_symbol}")
                return pd.DataFrame()
            
            # Standardize columns
            df.columns = [col.lower() for col in df.columns]
            
            if 'adj close' in df.columns:
                df = df[['open', 'high', 'low', 'adj close', 'volume']].copy()
                df.columns = ['open', 'high', 'low', 'close', 'volume']
            elif 'close' in df.columns:
                df = df[['open', 'high', 'low', 'close', 'volume']].copy()
            
            df = df.dropna()
            
            if len(df) > 50:
                logger.info(f"Successfully fetched {len(df)} candles for {symbol} from Yahoo Finance")
                return df
            else:
                logger.warning(f"Insufficient Yahoo Finance data: {len(df)} candles")
                return pd.DataFrame()
        
        except Exception as e:
            logger.error(f"Yahoo Finance fetch failed for {symbol}: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def fetch_crypto_data(symbol: str, timeframe: str = '1h', days: int = 90) -> pd.DataFrame:
        """
        Fetch crypto data from multiple sources with fallback
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candlestick timeframe
            days: Number of days of history
            
        Returns:
            DataFrame with OHLCV data
        """
        
        # Strategy 1: Try Yahoo Finance first (fastest for intraday)
        if timeframe in ['15m', '30m', '1h', '4h']:
            logger.info(f"Attempting fetch via Yahoo Finance (intraday)...")
            df = AlternativeCryptoFetcher.fetch_from_yahoo_crypto(symbol, timeframe, days)
            if not df.empty and len(df) > 50:
                return df
        
        # Strategy 2: Try CoinGecko for daily data
        if timeframe == '1d':
            logger.info(f"Attempting fetch via CoinGecko (daily)...")
            df = AlternativeCryptoFetcher.fetch_from_coingecko(symbol, days)
            if not df.empty and len(df) > 50:
                return df
        
        # Strategy 3: Fallback to Yahoo Finance if CoinGecko fails
        logger.info(f"Fallback: Attempting Yahoo Finance...")
        df = AlternativeCryptoFetcher.fetch_from_yahoo_crypto(symbol, timeframe, days)
        if not df.empty and len(df) > 50:
            return df
        
        # All sources failed
        logger.error(f"All crypto data sources failed for {symbol}")
        return pd.DataFrame()
