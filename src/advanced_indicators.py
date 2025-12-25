"""
Advanced Technical Indicators Engine
Extended indicators for comprehensive market analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedIndicators:
    """Advanced technical indicators beyond the basics"""
    
    # ========== TREND INDICATORS ==========
    @staticmethod
    def calculate_ichimoku(high: pd.Series, low: pd.Series, close: pd.Series) -> Dict:
        """
        Ichimoku Cloud - Complete trend system
        """
        # Tenkan-sen (Conversion Line)
        tenkan_high = high.rolling(window=9).max()
        tenkan_low = low.rolling(window=9).min()
        tenkan = (tenkan_high + tenkan_low) / 2
        
        # Kijun-sen (Base Line)
        kijun_high = high.rolling(window=26).max()
        kijun_low = low.rolling(window=26).min()
        kijun = (kijun_high + kijun_low) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_a = ((tenkan + kijun) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        senkou_b_high = high.rolling(window=52).max()
        senkou_b_low = low.rolling(window=52).min()
        senkou_b = ((senkou_b_high + senkou_b_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        chikou = close.shift(-26)
        
        return {
            'tenkan': tenkan.iloc[-1],
            'kijun': kijun.iloc[-1],
            'senkou_a': senkou_a.iloc[-1],
            'senkou_b': senkou_b.iloc[-1],
            'chikou': chikou.iloc[-1],
            'price': close.iloc[-1]
        }
    
    @staticmethod
    def calculate_keltner_channels(high: pd.Series, low: pd.Series, close: pd.Series, 
                                  period: int = 20) -> Tuple[float, float, float]:
        """
        Keltner Channels - ATR-based channels
        """
        # Middle line (EMA)
        ema = close.ewm(span=period).mean()
        
        # Calculate ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        upper = ema.iloc[-1] + (atr.iloc[-1] * 2)
        middle = ema.iloc[-1]
        lower = ema.iloc[-1] - (atr.iloc[-1] * 2)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
                           period: int = 10, multiplier: float = 3.0) -> Dict:
        """
        Supertrend - Trend direction with stops
        """
        hl2 = (high + low) / 2
        
        # Calculate basic bands
        atr_period = period
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=atr_period).mean()
        
        basic_upper = hl2 + (multiplier * atr)
        basic_lower = hl2 - (multiplier * atr)
        
        # Final bands
        final_upper = basic_upper.copy()
        final_lower = basic_lower.copy()
        
        for i in range(1, len(final_upper)):
            final_upper.iloc[i] = min(basic_upper.iloc[i], final_upper.iloc[i-1]) if close.iloc[i] < final_upper.iloc[i-1] else basic_upper.iloc[i]
            final_lower.iloc[i] = max(basic_lower.iloc[i], final_lower.iloc[i-1]) if close.iloc[i] > final_lower.iloc[i-1] else basic_lower.iloc[i]
        
        # Determine trend
        trend = []
        for i in range(len(close)):
            if i == 0:
                trend.append(1 if close.iloc[i] <= final_upper.iloc[i] else -1)
            else:
                if trend[-1] == 1:
                    trend.append(1 if close.iloc[i] > final_lower.iloc[i] else -1)
                else:
                    trend.append(-1 if close.iloc[i] < final_upper.iloc[i] else 1)
        
        return {
            'trend': trend[-1],  # 1 = uptrend, -1 = downtrend
            'upper': final_upper.iloc[-1],
            'lower': final_lower.iloc[-1],
            'atr': atr.iloc[-1]
        }
    
    # ========== MOMENTUM INDICATORS ==========
    @staticmethod
    def calculate_williams_r(high: pd.Series, low: pd.Series, close: pd.Series, 
                            period: int = 14) -> float:
        """
        Williams %R - Momentum oscillator
        Range: 0 to -100 (overbought -20, oversold -80)
        """
        highest = high.rolling(window=period).max()
        lowest = low.rolling(window=period).min()
        
        wr = ((highest - close) / (highest - lowest)) * -100
        return wr.iloc[-1]
    
    @staticmethod
    def calculate_mfi(high: pd.Series, low: pd.Series, close: pd.Series, 
                     volume: pd.Series, period: int = 14) -> float:
        """
        Money Flow Index - Volume + RSI
        Range: 0-100 (overbought >80, oversold <20)
        """
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = pd.Series(0.0, index=close.index)
        negative_flow = pd.Series(0.0, index=close.index)
        
        for i in range(1, len(close)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi_ratio = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + mfi_ratio))
        
        return mfi.iloc[-1]
    
    @staticmethod
    def calculate_roc(close: pd.Series, period: int = 12) -> float:
        """
        Rate of Change - Momentum indicator
        """
        roc = ((close - close.shift(period)) / close.shift(period)) * 100
        return roc.iloc[-1]
    
    @staticmethod
    def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series, 
                     period: int = 20) -> float:
        """
        Commodity Channel Index - Trend indicator
        Range: usually -100 to +100
        """
        typical_price = (high + low + close) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        
        cci = (typical_price - sma) / (0.015 * mad)
        return cci.iloc[-1]
    
    # ========== VOLATILITY INDICATORS ==========
    @staticmethod
    def calculate_natr(high: pd.Series, low: pd.Series, close: pd.Series, 
                      period: int = 14) -> float:
        """
        Normalized ATR - ATR as % of close price
        Useful for comparing volatility across different price levels
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        natr = (atr / close) * 100
        return natr.iloc[-1]
    
    @staticmethod
    def calculate_historical_volatility(close: pd.Series, period: int = 20) -> float:
        """
        Historical Volatility - Standard deviation of returns
        """
        returns = close.pct_change().dropna()
        hv = returns.rolling(window=period).std() * np.sqrt(252)
        return hv.iloc[-1] * 100
    
    @staticmethod
    def calculate_average_directional_movement_index(high: pd.Series, low: pd.Series, 
                                                      period: int = 14) -> Dict:
        """
        DMI+ and DMI- (Directional Movement)
        Complements ADX
        """
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = pd.Series(0.0, index=close.index)
        minus_dm = pd.Series(0.0, index=close.index)
        
        for i in range(len(close)):
            if up_move.iloc[i] > down_move.iloc[i] and up_move.iloc[i] > 0:
                plus_dm.iloc[i] = up_move.iloc[i]
            if down_move.iloc[i] > up_move.iloc[i] and down_move.iloc[i] > 0:
                minus_dm.iloc[i] = down_move.iloc[i]
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        tr_sum = tr.rolling(window=period).sum()
        
        plus_di = 100 * (plus_dm.rolling(window=period).sum() / tr_sum)
        minus_di = 100 * (minus_dm.rolling(window=period).sum() / tr_sum)
        
        return {
            'plus_di': plus_di.iloc[-1],
            'minus_di': minus_di.iloc[-1]
        }
    
    # ========== VOLUME INDICATORS ==========
    @staticmethod
    def calculate_accumulation_distribution_line(high: pd.Series, low: pd.Series, 
                                                 close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Accumulation/Distribution Line - Money flow
        """
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0)  # Handle division by zero
        ad_line = (clv * volume).cumsum()
        return ad_line
    
    @staticmethod
    def calculate_cmf(high: pd.Series, low: pd.Series, close: pd.Series, 
                     volume: pd.Series, period: int = 20) -> float:
        """
        Chaikin Money Flow - Volume-weighted price momentum
        Range: -1 to 1 (positive = accumulation, negative = distribution)
        """
        clv = ((close - low) - (high - close)) / (high - low)
        clv = clv.fillna(0)
        cmf = (clv * volume).rolling(window=period).sum() / volume.rolling(window=period).sum()
        return cmf.iloc[-1]
    
    @staticmethod
    def calculate_ease_of_movement(high: pd.Series, low: pd.Series, volume: pd.Series,
                                   scale: int = 14000, period: int = 14) -> float:
        """
        Ease of Movement - Volume efficiency
        """
        em = (high.diff() + low.diff()) / (scale * volume / (high - low))
        ease_of_mov = em.rolling(window=period).mean()
        return ease_of_mov.iloc[-1]
    
    # ========== COMPOSITE INDICATORS ==========
    @staticmethod
    def calculate_qstick(open_: pd.Series, close: pd.Series, period: int = 10) -> float:
        """
        QStick - Momentum from closing above/below open
        """
        qstick = (close - open_).rolling(window=period).mean()
        return qstick.iloc[-1]
    
    @staticmethod
    def calculate_aroon(high: pd.Series, low: pd.Series, period: int = 25) -> Dict:
        """
        Aroon Indicator - Trend identification
        """
        aroon_up = ((period - high.rolling(window=period).apply(lambda x: period - 1 - np.argmax(x))) / period) * 100
        aroon_down = ((period - low.rolling(window=period).apply(lambda x: period - 1 - np.argmin(x))) / period) * 100
        
        return {
            'aroon_up': aroon_up.iloc[-1],
            'aroon_down': aroon_down.iloc[-1],
            'oscillator': aroon_up.iloc[-1] - aroon_down.iloc[-1]
        }
    
    @staticmethod
    def calculate_linear_regression(close: pd.Series, period: int = 20) -> Dict:
        """
        Linear Regression - Trend slope and channel
        """
        if len(close) < period:
            return {'slope': 0, 'intercept': 0, 'r_squared': 0}
        
        x = np.arange(period)
        y = close.tail(period).values
        
        coeffs = np.polyfit(x, y, 1)
        slope = coeffs[0]
        intercept = coeffs[1]
        
        # R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'trend_strength': abs(slope)
        }
    
    @staticmethod
    def calculate_mass_index(high: pd.Series, low: pd.Series, period: int = 25, 
                            sum_period: int = 9) -> float:
        """
        Mass Index - Reversal detection
        High readings (>27) indicate potential reversal
        """
        hl_ratio = high / low
        ema1 = hl_ratio.ewm(span=period).mean()
        ema2 = ema1.ewm(span=period).mean()
        ratio = ema1 / ema2
        mi = ratio.rolling(window=sum_period).sum()
        return mi.iloc[-1]
    
    # ========== ALL INDICATORS COMBINED ==========
    @staticmethod
    def calculate_all_advanced_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all advanced indicators
        """
        try:
            # Ichimoku
            ichimoku = AdvancedIndicators.calculate_ichimoku(df['high'], df['low'], df['close'])
            df['Ichimoku_Tenkan'] = ichimoku['tenkan']
            df['Ichimoku_Kijun'] = ichimoku['kijun']
            df['Ichimoku_A'] = ichimoku['senkou_a']
            df['Ichimoku_B'] = ichimoku['senkou_b']
            
            # Keltner Channels
            upper, middle, lower = AdvancedIndicators.calculate_keltner_channels(
                df['high'], df['low'], df['close']
            )
            df['Keltner_Upper'] = upper
            df['Keltner_Middle'] = middle
            df['Keltner_Lower'] = lower
            
            # Supertrend
            st = AdvancedIndicators.calculate_supertrend(df['high'], df['low'], df['close'])
            df['Supertrend_Trend'] = st['trend']
            df['Supertrend_Upper'] = st['upper']
            df['Supertrend_Lower'] = st['lower']
            
            # Williams R
            df['Williams_R'] = AdvancedIndicators.calculate_williams_r(df['high'], df['low'], df['close'])
            
            # MFI
            df['MFI'] = AdvancedIndicators.calculate_mfi(df['high'], df['low'], df['close'], df['volume'])
            
            # ROC
            df['ROC'] = AdvancedIndicators.calculate_roc(df['close'])
            
            # CCI
            df['CCI'] = AdvancedIndicators.calculate_cci(df['high'], df['low'], df['close'])
            
            # NATR
            df['NATR'] = AdvancedIndicators.calculate_natr(df['high'], df['low'], df['close'])
            
            # Historical Volatility
            df['Historical_Vol'] = AdvancedIndicators.calculate_historical_volatility(df['close'])
            
            # CMF
            df['CMF'] = AdvancedIndicators.calculate_cmf(df['high'], df['low'], df['close'], df['volume'])
            
            # Linear Regression
            lr = AdvancedIndicators.calculate_linear_regression(df['close'])
            df['LR_Slope'] = lr['slope']
            df['LR_RSq'] = lr['r_squared']
            
            # Aroon
            aroon = AdvancedIndicators.calculate_aroon(df['high'], df['low'])
            df['Aroon_Up'] = aroon['aroon_up']
            df['Aroon_Down'] = aroon['aroon_down']
            
            # Mass Index
            df['Mass_Index'] = AdvancedIndicators.calculate_mass_index(df['high'], df['low'])
            
            logger.info(f"Calculated {15} advanced indicators")
            
        except Exception as e:
            logger.error(f"Error calculating advanced indicators: {str(e)}")
        
        return df
