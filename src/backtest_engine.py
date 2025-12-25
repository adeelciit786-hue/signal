"""
Backtesting Engine
Test signals against historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Complete backtesting system
    Tests strategy on historical data
    """
    
    def __init__(self, starting_balance: float = 10000, risk_per_trade: float = 1.0):
        """
        Initialize backtest
        
        Args:
            starting_balance: Initial account balance
            risk_per_trade: Risk per trade in percent
        """
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.risk_per_trade = risk_per_trade / 100
        self.max_risk_amount = starting_balance * self.risk_per_trade
        
        # Results tracking
        self.trades = []
        self.equity_curve = [starting_balance]
        self.peak_equity = starting_balance
        self.trough_equity = starting_balance
    
    def backtest_signal(self, df: pd.DataFrame, signal_func, 
                       params: Dict = None) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            df: Historical OHLCV data
            signal_func: Function that generates signals
            params: Strategy parameters
            
        Returns:
            Backtest results
        """
        logger.info(f"Starting backtest with {len(df)} candles...")
        
        trades = []
        in_trade = False
        entry_price = 0
        entry_index = 0
        
        # Run through each candle
        for i in range(100, len(df)):  # Need 100 candles for indicators
            current_df = df.iloc[:i+1].copy()
            latest = current_df.iloc[-1]
            current_price = latest['close']
            current_bar = i
            
            # Generate signal
            try:
                signal_result = signal_func(current_df)
                signal = signal_result.get('signal', 'NEUTRAL')
            except Exception as e:
                logger.error(f"Error generating signal at bar {i}: {str(e)}")
                continue
            
            # Entry logic
            if not in_trade:
                if signal in ['BUY', 'SELL']:
                    # Calculate position
                    atr = latest.get('ATR', current_price * 0.02)
                    stop_loss = current_price - (atr * 2) if signal == 'BUY' else current_price + (atr * 2)
                    take_profit = current_price + (atr * 4) if signal == 'BUY' else current_price - (atr * 4)
                    
                    # Position size
                    risk_amount = self.current_balance * self.risk_per_trade
                    risk_distance = abs(current_price - stop_loss)
                    position_size = risk_amount / risk_distance if risk_distance > 0 else 0
                    
                    if position_size > 0:
                        in_trade = True
                        entry_price = current_price
                        entry_index = current_bar
                        entry_signal = signal
                        entry_atr = atr
            
            # Exit logic
            elif in_trade:
                # Check stop loss or take profit
                trade_result = None
                
                if entry_signal == 'BUY':
                    if current_price <= stop_loss:
                        trade_result = 'STOP_LOSS'
                        exit_price = stop_loss
                    elif current_price >= take_profit:
                        trade_result = 'TAKE_PROFIT'
                        exit_price = take_profit
                
                elif entry_signal == 'SELL':
                    if current_price >= stop_loss:
                        trade_result = 'STOP_LOSS'
                        exit_price = stop_loss
                    elif current_price <= take_profit:
                        trade_result = 'TAKE_PROFIT'
                        exit_price = take_profit
                
                # Record trade
                if trade_result:
                    pnl = (exit_price - entry_price) * position_size if entry_signal == 'BUY' else (entry_price - exit_price) * position_size
                    pnl_percent = (pnl / (entry_price * position_size)) * 100 if entry_price > 0 else 0
                    
                    trade_record = {
                        'entry_bar': entry_index,
                        'exit_bar': current_bar,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'direction': entry_signal,
                        'position_size': position_size,
                        'pnl': pnl,
                        'pnl_percent': pnl_percent,
                        'exit_reason': trade_result,
                        'bars_held': current_bar - entry_index
                    }
                    
                    trades.append(trade_record)
                    
                    # Update balance
                    self.current_balance += pnl
                    self.equity_curve.append(self.current_balance)
                    
                    # Track peak and trough
                    if self.current_balance > self.peak_equity:
                        self.peak_equity = self.current_balance
                    if self.current_balance < self.trough_equity:
                        self.trough_equity = self.current_balance
                    
                    in_trade = False
        
        self.trades = trades
        return self._calculate_backtest_metrics()
    
    def _calculate_backtest_metrics(self) -> Dict:
        """Calculate comprehensive backtest metrics"""
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'message': 'No trades generated'
            }
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit metrics
        total_pnl = trades_df['pnl'].sum()
        total_pnl_percent = ((self.current_balance - self.starting_balance) / self.starting_balance) * 100
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['pnl'] < 0]['pnl'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        max_consecutive_losses = self._calculate_max_consecutive_losses(trades_df)
        max_drawdown = ((self.trough_equity - self.peak_equity) / self.peak_equity * 100) if self.peak_equity > 0 else 0
        
        # Duration metrics
        avg_bars_held = trades_df['bars_held'].mean() if total_trades > 0 else 0
        
        # Profit factor
        total_wins = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        total_losses = abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl': total_pnl,
            'total_pnl_percent': total_pnl_percent,
            'final_balance': self.current_balance,
            'peak_equity': self.peak_equity,
            'trough_equity': self.trough_equity,
            'max_drawdown': max_drawdown,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_bars_held': avg_bars_held,
            'starting_balance': self.starting_balance,
            'equity_curve': self.equity_curve
        }
    
    def _calculate_max_consecutive_losses(self, trades_df: pd.DataFrame) -> int:
        """Calculate maximum consecutive losing trades"""
        consecutive = 0
        max_consecutive = 0
        
        for pnl in trades_df['pnl']:
            if pnl < 0:
                consecutive += 1
                max_consecutive = max(max_consecutive, consecutive)
            else:
                consecutive = 0
        
        return max_consecutive
    
    def print_backtest_report(self, backtest_results: Dict):
        """Print formatted backtest report"""
        print("\n" + "="*70)
        print("BACKTEST RESULTS")
        print("="*70)
        print(f"\nTrade Statistics:")
        print(f"  Total Trades:        {backtest_results.get('total_trades', 0)}")
        print(f"  Winning Trades:      {backtest_results.get('winning_trades', 0)}")
        print(f"  Losing Trades:       {backtest_results.get('losing_trades', 0)}")
        print(f"  Win Rate:            {backtest_results.get('win_rate', 0):.2f}%")
        
        print(f"\nProfit/Loss:")
        print(f"  Total P&L:           ${backtest_results.get('total_pnl', 0):,.2f}")
        print(f"  P&L Percent:         {backtest_results.get('total_pnl_percent', 0):.2f}%")
        print(f"  Final Balance:       ${backtest_results.get('final_balance', 0):,.2f}")
        
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown:        {backtest_results.get('max_drawdown', 0):.2f}%")
        print(f"  Avg Bars Held:       {backtest_results.get('avg_bars_held', 0):.0f}")
        print(f"  Profit Factor:       {backtest_results.get('profit_factor', 0):.2f}")
        print(f"  Max Consecutive Losses: {backtest_results.get('max_consecutive_losses', 0)}")
        
        print("\n" + "="*70)
    
    def get_equity_curve_data(self) -> List[float]:
        """Return equity curve for plotting"""
        return self.equity_curve
