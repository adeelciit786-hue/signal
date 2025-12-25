"""
Risk Management Module
Handles position sizing, stop-loss placement, and risk-reward validation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class RiskManager:
    """Manages all risk aspects of trading"""
    
    def __init__(self, account_balance: float = 10000, risk_per_trade: float = 0.01):
        """
        Initialize risk manager
        
        Args:
            account_balance: Starting account balance
            risk_per_trade: Risk per trade as % of account (default 1%)
        """
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.max_risk_per_trade = account_balance * risk_per_trade
        self.cumulative_losses = 0
        self.max_drawdown_threshold = 0.10  # 10% max drawdown
        self.consecutive_losses = 0
        self.max_consecutive_losses = 3
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk per trade
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Number of units/contracts to trade
        """
        risk_amount = self.max_risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk <= 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size
    
    def calculate_atr_stop_loss(self, current_price: float, atr: float, direction: str = 'BUY') -> float:
        """
        Calculate ATR-based dynamic stop loss
        
        Args:
            current_price: Current price
            atr: Average True Range
            direction: 'BUY' or 'SELL'
            
        Returns:
            Stop loss price
        """
        if direction == 'BUY':
            return current_price - (atr * 2)  # 2x ATR below entry
        else:  # SELL
            return current_price + (atr * 2)  # 2x ATR above entry
    
    def validate_risk_reward(self, entry: float, stop_loss: float, take_profit: float, 
                           min_ratio: float = 2.0) -> Tuple[bool, float, str]:
        """
        Validate risk-reward ratio (minimum 1:2)
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            min_ratio: Minimum risk-reward ratio (default 2:1)
            
        Returns:
            (is_valid, ratio, message)
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk <= 0:
            return False, 0, "Invalid stop loss"
        
        ratio = reward / risk
        
        if ratio < min_ratio:
            return False, ratio, f"Risk-reward ratio {ratio:.2f}:1 below minimum {min_ratio}:1"
        
        return True, ratio, f"Good risk-reward ratio: {ratio:.2f}:1"
    
    def check_liquidity_conditions(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if liquidity conditions are acceptable
        - Minimum volume
        - Not too wide spread (inferred from price action)
        
        Returns:
            (is_liquid, message)
        """
        if len(df) < 5:
            return False, "Insufficient data for liquidity check"
        
        recent_volume = df['volume'].tail(5).mean()
        volume_ma = df['volume'].tail(20).mean()
        
        # Volume should be at least 50% of average
        if recent_volume < volume_ma * 0.5:
            return False, f"Low volume: {recent_volume:.0f} < {volume_ma * 0.5:.0f}"
        
        # Check for price stability (not extreme wicks)
        tail_data = df.tail(5)
        avg_range = (tail_data['high'] - tail_data['low']).mean()
        recent_range = tail_data['high'].iloc[-1] - tail_data['low'].iloc[-1]
        
        if recent_range > avg_range * 1.5:
            return False, f"Wide spread detected in recent candle"
        
        return True, "Adequate liquidity"
    
    def check_adx_strength(self, adx: float, min_adx: float = 20) -> Tuple[bool, str]:
        """
        Check if trend is strong enough (ADX > 20)
        
        Returns:
            (is_strong, message)
        """
        if adx < 15:
            return False, f"ADX {adx:.1f} - Choppy market, avoid trading"
        elif adx < min_adx:
            return False, f"ADX {adx:.1f} - Weak trend"
        else:
            return True, f"ADX {adx:.1f} - Strong trend"
    
    def should_reduce_risk_after_losses(self) -> Tuple[float, str]:
        """
        Reduce position size after consecutive losses
        
        Returns:
            (position_size_multiplier, message)
        """
        if self.consecutive_losses == 0:
            return 1.0, "Normal position size"
        elif self.consecutive_losses == 1:
            return 0.75, "1 loss - reduce to 75% size"
        elif self.consecutive_losses == 2:
            return 0.5, "2 losses - reduce to 50% size"
        elif self.consecutive_losses >= 3:
            return 0.0, f"{self.consecutive_losses} consecutive losses - PAUSE TRADING"
        
        return 1.0, "Unknown state"
    
    def update_drawdown(self, current_balance: float) -> Tuple[float, bool]:
        """
        Update and check drawdown
        
        Args:
            current_balance: Current account balance
            
        Returns:
            (drawdown_percent, is_max_exceeded)
        """
        drawdown = (self.account_balance - current_balance) / self.account_balance
        is_exceeded = drawdown > self.max_drawdown_threshold
        
        return drawdown, is_exceeded
    
    def record_loss(self, loss_amount: float):
        """Record a losing trade"""
        self.cumulative_losses += loss_amount
        self.consecutive_losses += 1
    
    def record_win(self):
        """Reset consecutive losses counter on winning trade"""
        self.consecutive_losses = 0
    
    def get_risk_summary(self) -> Dict:
        """Get current risk status summary"""
        reduction_multiplier, reduction_msg = self.should_reduce_risk_after_losses()
        
        return {
            'risk_per_trade': self.max_risk_per_trade,
            'consecutive_losses': self.consecutive_losses,
            'position_size_multiplier': reduction_multiplier,
            'position_reduction_reason': reduction_msg,
            'cumulative_losses': self.cumulative_losses,
            'max_drawdown_threshold': self.max_drawdown_threshold,
            'trading_paused': self.consecutive_losses >= self.max_consecutive_losses,
            'min_adx_requirement': 20,
            'min_risk_reward_ratio': 2.0
        }
    
    @staticmethod
    def get_risk_notes(trade_decision: Dict, risk_info: Dict) -> str:
        """
        Generate risk notes explaining why a trade is safe or avoided
        """
        notes = []
        
        # Check position size
        if risk_info['consecutive_losses'] > 0:
            notes.append(f"⚠️ {risk_info['consecutive_losses']} loss(es) - position size at {risk_info['position_size_multiplier']*100:.0f}%")
        
        if trade_decision.get('signal') == 'NEUTRAL':
            notes.append("🛑 NEUTRAL signal - avoiding trade")
        
        if trade_decision.get('adx', 0) < 20:
            notes.append(f"⚠️ ADX {trade_decision.get('adx', 0):.1f} < 20 - weak trend, higher risk")
        
        if not risk_info.get('liquidity_ok', True):
            notes.append("⚠️ Low liquidity - may face slippage")
        
        if trade_decision.get('news_impact') == 'NEGATIVE':
            notes.append("📰 Negative sentiment detected - reduce size or avoid")
        
        if trade_decision.get('confidence', 0) < 70:
            notes.append(f"⚠️ Low confidence ({trade_decision.get('confidence', 0):.0f}%) - wait for better setup")
        
        if len(notes) == 0:
            notes.append("✓ Risk parameters acceptable for trade")
        
        return "\n".join(notes)
