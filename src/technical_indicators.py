"""
Technical Indicators Module
Implements all required indicators: EMA, SMA, RSI, MACD, Bollinger Bands, ATR, ADX, Fibonacci, etc.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict


class TechnicalIndicators:
    """Calculate all technical indicators"""
    
    # ========== MOVING AVERAGES ==========
    @staticmethod
    def calculate_sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    # ========== MOMENTUM INDICATORS ==========
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index
        Overbought > 70, Oversold < 30
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_stochastic_rsi(rsi: pd.Series, period: int = 14, smooth_k: int = 3, smooth_d: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic RSI (Oscillator RSI)
        Combines RSI with Stochastic formula
        """
        lowest_rsi = rsi.rolling(window=period).min()
        highest_rsi = rsi.rolling(window=period).max()
        
        stoch_rsi = (rsi - lowest_rsi) / (highest_rsi - lowest_rsi) * 100
        stoch_rsi_k = stoch_rsi.rolling(window=smooth_k).mean()
        stoch_rsi_d = stoch_rsi_k.rolling(window=smooth_d).mean()
        
        return stoch_rsi_k, stoch_rsi_d
    
    @staticmethod
    def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence)
        Returns: MACD line, Signal line, Histogram
        """
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_rsi_macd_divergence(close: pd.Series, rsi: pd.Series, macd_line: pd.Series) -> Dict[str, bool]:
        """
        Detect RSI and MACD divergence
        Bullish divergence: Price lower, RSI/MACD higher
        Bearish divergence: Price higher, RSI/MACD lower
        """
        # Simple divergence detection (last 20 candles)
        window = 20
        if len(close) < window:
            return {'bullish': False, 'bearish': False}
        
        close_recent = close.iloc[-window:]
        rsi_recent = rsi.iloc[-window:]
        macd_recent = macd_line.iloc[-window:]
        
        close_trend = close_recent.iloc[-1] < close_recent.iloc[0]  # Lower
        rsi_trend = rsi_recent.iloc[-1] > rsi_recent.iloc[0]  # Higher
        macd_trend = macd_recent.iloc[-1] > macd_recent.iloc[0]  # Higher
        
        bullish_div = close_trend and (rsi_trend or macd_trend)
        bearish_div = (not close_trend) and (not rsi_trend or not macd_trend)
        
        return {'bullish': bullish_div, 'bearish': bearish_div}
    
    # ========== VOLATILITY INDICATORS ==========
    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        Returns: Middle band (SMA), Upper band, Lower band
        """
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return sma, upper_band, lower_band
    
    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """
        Average True Range
        Measures volatility
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Average Directional Index (ADX)
        Measures trend strength (20+ = strong trend)
        Returns: ADX, +DI, -DI
        """
        plus_dm = high.diff()
        minus_dm = low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr.rolling(window=period).mean())
        
        di_diff = abs(plus_di - minus_di)
        di_sum = plus_di + minus_di
        
        dx = 100 * (di_diff / di_sum)
        adx = dx.rolling(window=period).mean()
        
        return adx, plus_di, minus_di
    
    # ========== VOLUME INDICATORS ==========
    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = pd.Series(index=close.index, dtype='float64')
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    @staticmethod
    def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).rolling(window=20).sum() / volume.rolling(window=20).sum()
        return vwap
    
    @staticmethod
    def calculate_volume_ma(volume: pd.Series, period: int = 20) -> pd.Series:
        """Moving average of volume for comparison"""
        return volume.rolling(window=period).mean()
    
    # ========== SUPPORT & RESISTANCE ==========
    @staticmethod
    def calculate_fibonacci_levels(high: float, low: float) -> Dict[str, float]:
        """
        Calculate Fibonacci retracement levels
        Returns key levels: 0%, 23.6%, 38.2%, 50%, 61.8%, 100%
        """
        diff = high - low
        levels = {
            '0%': low,
            '23.6%': low + (diff * 0.236),
            '38.2%': low + (diff * 0.382),
            '50%': low + (diff * 0.5),
            '61.8%': low + (diff * 0.618),
            '100%': high
        }
        return levels
    
    @staticmethod
    def calculate_support_resistance(data: pd.Series, lookback: int = 20) -> Tuple[list, list]:
        """
        Identify support and resistance levels
        """
        supports = []
        resistances = []
        
        for i in range(lookback, len(data) - lookback):
            # Local minimum (support)
            if data.iloc[i] < data.iloc[i-lookback:i].min() and data.iloc[i] < data.iloc[i+1:i+lookback+1].min():
                supports.append(data.iloc[i])
            
            # Local maximum (resistance)
            if data.iloc[i] > data.iloc[i-lookback:i].max() and data.iloc[i] > data.iloc[i+1:i+lookback+1].max():
                resistances.append(data.iloc[i])
        
        return supports, resistances
    
    @staticmethod
    def detect_trendline(data: pd.Series, window: int = 20) -> Tuple[float, float]:
        """
        Detect trendline using linear regression
        Returns: slope, intercept
        """
        if len(data) < window:
            return 0, 0
        
        x = np.arange(window)
        y = data.iloc[-window:].values
        
        slope = np.polyfit(x, y, 1)[0]
        intercept = np.polyfit(x, y, 1)[1]
        
        return slope, intercept
    
    # ========== COMPOSITE ANALYSIS ==========
    @staticmethod
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators for a given OHLCV dataframe
        """
        # Moving Averages
        df['SMA_10'] = TechnicalIndicators.calculate_sma(df['close'], 10)
        df['SMA_20'] = TechnicalIndicators.calculate_sma(df['close'], 20)
        df['SMA_50'] = TechnicalIndicators.calculate_sma(df['close'], 50)
        df['SMA_100'] = TechnicalIndicators.calculate_sma(df['close'], 100)
        df['SMA_200'] = TechnicalIndicators.calculate_sma(df['close'], 200)
        
        df['EMA_10'] = TechnicalIndicators.calculate_ema(df['close'], 10)
        df['EMA_20'] = TechnicalIndicators.calculate_ema(df['close'], 20)
        df['EMA_50'] = TechnicalIndicators.calculate_ema(df['close'], 50)
        
        # Momentum
        df['RSI'] = TechnicalIndicators.calculate_rsi(df['close'], 14)
        stoch_k, stoch_d = TechnicalIndicators.calculate_stochastic_rsi(df['RSI'])
        df['Stoch_RSI_K'] = stoch_k
        df['Stoch_RSI_D'] = stoch_d
        
        macd, signal, hist = TechnicalIndicators.calculate_macd(df['close'])
        df['MACD'] = macd
        df['MACD_Signal'] = signal
        df['MACD_Histogram'] = hist
        
        # Volatility
        sma, upper, lower = TechnicalIndicators.calculate_bollinger_bands(df['close'])
        df['BB_Middle'] = sma
        df['BB_Upper'] = upper
        df['BB_Lower'] = lower
        
        df['ATR'] = TechnicalIndicators.calculate_atr(df['high'], df['low'], df['close'])
        
        adx, plus_di, minus_di = TechnicalIndicators.calculate_adx(df['high'], df['low'], df['close'])
        df['ADX'] = adx
        df['Plus_DI'] = plus_di
        df['Minus_DI'] = minus_di
        
        # Volume
        df['OBV'] = TechnicalIndicators.calculate_obv(df['close'], df['volume'])
        df['VWAP'] = TechnicalIndicators.calculate_vwap(df['high'], df['low'], df['close'], df['volume'])
        df['Volume_MA'] = TechnicalIndicators.calculate_volume_ma(df['volume'])
        
        return df
