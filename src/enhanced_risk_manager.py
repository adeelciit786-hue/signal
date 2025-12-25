"""
Enhanced Risk Management Engine
Mandatory Risk Controls with Strict Validation
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedRiskManager:
    """
    Complete risk management system
    Enforces strict risk rules before any trade
    """
    
    def __init__(self, account_balance: float = 10000, max_risk_percent: float = 1.0):
        """
        Initialize risk manager
        
        Args:
            account_balance: Trading account size
            max_risk_percent: Max risk per trade (default 1%)
        """
        self.account_balance = account_balance
        self.max_risk_percent = max_risk_percent
        self.max_risk_amount = account_balance * (max_risk_percent / 100)
        
        # Tracking
        self.trades_log = []
        self.cumulative_loss = 0
        self.consecutive_losses = 0
        self.peak_balance = account_balance
        
        logger.info(f"Risk Manager Initialized - Account: ${account_balance:.2f}, Max Risk: ${self.max_risk_amount:.2f}/trade")
    
    def calculate_position_size_atr(self, entry_price: float, atr: float, 
                                    stop_multiplier: float = 2.0) -> Dict:
        """
        Calculate position size using ATR-based stop loss
        
        Args:
            entry_price: Entry price
            atr: Average True Range value
            stop_multiplier: ATR multiplier for stop (default 2x)
            
        Returns:
            Dict with position sizing details
        """
        if atr <= 0 or entry_price <= 0:
            return {'position_size': 0, 'valid': False, 'reason': 'Invalid price or ATR'}
        
        # Calculate stop loss
        stop_loss = entry_price - (atr * stop_multiplier)
        
        if stop_loss <= 0:
            return {'position_size': 0, 'valid': False, 'reason': 'Stop loss below zero'}
        
        # Risk amount per trade
        risk_per_point = entry_price - stop_loss
        position_size = self.max_risk_amount / risk_per_point
        
        return {
            'position_size': position_size,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'risk_per_trade': self.max_risk_amount,
            'distance_to_stop': risk_per_point,
            'valid': True,
            'reason': 'Valid Position Size'
        }
    
    def validate_risk_reward_ratio(self, entry: float, stop_loss: float, 
                                  take_profit: float, min_ratio: float = 2.0) -> Dict:
        """
        MANDATORY: Validate risk-reward ratio
        Trade only if RR >= 2:1
        
        Args:
            entry: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            min_ratio: Minimum required ratio (default 2:1)
            
        Returns:
            Dict with validation result
        """
        # Calculate risk and reward
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk <= 0:
            return {
                'valid': False,
                'ratio': 0,
                'reason': 'Invalid stop loss',
                'risk': risk,
                'reward': reward
            }
        
        ratio = reward / risk
        
        # Validation
        valid = ratio >= min_ratio
        reason = f"RR Ratio: {ratio:.2f}:1 - {'✓ VALID' if valid else '✗ INVALID (min 2:1)'}"
        
        return {
            'valid': valid,
            'ratio': ratio,
            'reason': reason,
            'risk': risk,
            'reward': reward,
            'entry': entry,
            'stop_loss': stop_loss,
            'take_profit': take_profit
        }
    
    def validate_market_conditions(self, df: pd.DataFrame) -> Dict:
        """
        MANDATORY: Check market conditions before trade
        
        Returns:
            Dict with validation results
        """
        if len(df) < 20:
            return {'valid': False, 'reasons': ['Insufficient data (need 20 candles)']}
        
        latest = df.iloc[-1]
        current_volume = latest['volume']
        volume_ma = latest.get('Volume_MA', current_volume)
        adx = latest.get('ADX', 0)
        
        conditions = {
            'volume_check': current_volume >= volume_ma * 0.5,
            'volume_reason': f"Volume {current_volume:.0f} vs MA {volume_ma:.0f}",
            'adx_check': adx > 20,
            'adx_reason': f"ADX {adx:.1f}",
            'trend_check': 'Supertrend_Trend' in df.columns
        }
        
        reasons = []
        all_valid = True
        
        if not conditions['volume_check']:
            reasons.append(f"✗ Low Volume: {conditions['volume_reason']}")
            all_valid = False
        else:
            reasons.append(f"✓ Volume Check: {conditions['volume_reason']}")
        
        if not conditions['adx_check']:
            reasons.append(f"✗ Weak Trend: {conditions['adx_reason']}")
            all_valid = False
        else:
            reasons.append(f"✓ Strong Trend: {conditions['adx_reason']}")
        
        return {
            'valid': all_valid,
            'reasons': reasons,
            'conditions': conditions
        }
    
    def validate_drawdown(self, current_balance: float, 
                         max_drawdown_percent: float = 10.0) -> Dict:
        """
        Check current drawdown from peak
        
        Args:
            current_balance: Current account balance
            max_drawdown_percent: Max allowed drawdown
            
        Returns:
            Dict with drawdown status
        """
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        drawdown = ((self.peak_balance - current_balance) / self.peak_balance) * 100
        max_allowed = max_drawdown_percent
        
        exceeded = drawdown > max_allowed
        reason = f"Drawdown: {drawdown:.2f}% {'[EXCEEDED]' if exceeded else '[OK]'}"
        
        return {
            'drawdown_percent': drawdown,
            'max_allowed': max_allowed,
            'exceeded': exceeded,
            'reason': reason,
            'peak_balance': self.peak_balance,
            'current_balance': current_balance
        }
    
    def check_stop_loss_validity(self, entry: float, stop_loss: float, 
                                atr: float, min_sl_distance: float = None) -> Dict:
        """
        MANDATORY: Validate stop loss placement
        Stop must be at least X distance from entry
        """
        distance = abs(entry - stop_loss)
        
        if min_sl_distance is None:
            min_sl_distance = atr * 1.0  # At least 1x ATR
        
        valid = distance >= min_sl_distance
        reason = f"SL Distance: {distance:.2f} vs Min: {min_sl_distance:.2f}"
        
        return {
            'valid': valid,
            'distance': distance,
            'min_distance': min_sl_distance,
            'reason': reason,
            'atr_used': atr
        }
    
    def check_take_profit_validity(self, entry: float, take_profit: float, 
                                  atr: float) -> Dict:
        """
        Validate take profit placement
        TP should be reasonable distance from entry
        """
        distance = abs(take_profit - entry)
        max_tp = entry + (atr * 10)  # Don't be too greedy
        
        valid = 0 < distance < max_tp
        reason = f"TP Distance: {distance:.2f} vs ATR-based Max: {max_tp:.2f}"
        
        return {
            'valid': valid,
            'distance': distance,
            'max_distance': max_tp,
            'reason': reason
        }
    
    def enforce_risk_rules(self, trade_decision: Dict, df: pd.DataFrame) -> Dict:
        """
        ENFORCE ALL RISK RULES
        Returns whether trade should execute
        
        Args:
            trade_decision: Signal decision with entry/SL/TP
            df: Market data
            
        Returns:
            Dict with comprehensive validation
        """
        validation_results = {
            'allowed': False,
            'reasons': [],
            'checks': {}
        }
        
        # 1. Check if we even have a signal
        if trade_decision.get('signal') == 'NEUTRAL':
            validation_results['reasons'].append('❌ No Trade Signal (NEUTRAL)')
            return validation_results
        
        entry = trade_decision.get('entry_price')
        stop_loss = trade_decision.get('stop_loss')
        take_profit = trade_decision.get('take_profit')
        atr = trade_decision.get('atr', 0)
        
        # 2. Validate Risk-Reward
        rr_check = self.validate_risk_reward_ratio(entry, stop_loss, take_profit)
        validation_results['checks']['risk_reward'] = rr_check
        
        if not rr_check['valid']:
            validation_results['reasons'].append(f"❌ {rr_check['reason']}")
        else:
            validation_results['reasons'].append(f"✓ {rr_check['reason']}")
        
        # 3. Validate Stop Loss
        sl_check = self.check_stop_loss_validity(entry, stop_loss, atr)
        validation_results['checks']['stop_loss'] = sl_check
        
        if not sl_check['valid']:
            validation_results['reasons'].append(f"❌ Stop Loss Invalid: {sl_check['reason']}")
        else:
            validation_results['reasons'].append(f"✓ Stop Loss Valid: {sl_check['reason']}")
        
        # 4. Validate Take Profit
        tp_check = self.check_take_profit_validity(entry, take_profit, atr)
        validation_results['checks']['take_profit'] = tp_check
        
        if not tp_check['valid']:
            validation_results['reasons'].append(f"❌ Take Profit Invalid: {tp_check['reason']}")
        else:
            validation_results['reasons'].append(f"✓ Take Profit Valid: {tp_check['reason']}")
        
        # 5. Validate Market Conditions
        mkt_check = self.validate_market_conditions(df)
        validation_results['checks']['market_conditions'] = mkt_check
        validation_results['reasons'].extend(mkt_check['reasons'])
        
        # 6. Check Drawdown
        drawdown_check = self.validate_drawdown(self.account_balance)
        validation_results['checks']['drawdown'] = drawdown_check
        
        if drawdown_check['exceeded']:
            validation_results['reasons'].append(f"❌ {drawdown_check['reason']}")
        else:
            validation_results['reasons'].append(f"✓ {drawdown_check['reason']}")
        
        # FINAL DECISION: All checks must pass
        all_passed = (
            rr_check['valid'] and
            sl_check['valid'] and
            tp_check['valid'] and
            mkt_check['valid'] and
            not drawdown_check['exceeded']
        )
        
        validation_results['allowed'] = all_passed
        
        if all_passed:
            validation_results['reasons'].insert(0, "✓ ALL RISK RULES PASSED - TRADE ALLOWED")
        else:
            validation_results['reasons'].insert(0, "❌ RISK RULES FAILED - TRADE REJECTED")
        
        return validation_results
    
    def get_risk_summary(self) -> Dict:
        """Get current risk status"""
        return {
            'account_balance': self.account_balance,
            'max_risk_per_trade': self.max_risk_amount,
            'max_risk_percent': self.max_risk_percent,
            'trades_logged': len(self.trades_log),
            'cumulative_loss': self.cumulative_loss,
            'consecutive_losses': self.consecutive_losses,
            'peak_balance': self.peak_balance
        }
