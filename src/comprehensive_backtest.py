"""
Comprehensive Backtesting System
Tests trading strategies for Crypto, Stocks, Forex, and Commodities
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: pd.Timestamp
    entry_price: float
    exit_time: Optional[pd.Timestamp]
    exit_price: Optional[float]
    direction: str  # 'BUY' or 'SELL'
    quantity: float
    risk: float
    reward: float
    pnl: float
    pnl_percent: float
    status: str  # 'CLOSED', 'OPEN'


@dataclass
class BacktestResults:
    """Backtesting results summary"""
    symbol: str
    asset_type: str
    timeframe: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    total_pnl_percent: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Trade]
    equity_curve: List[float]


class ComprehensiveBacktester:
    """Advanced backtesting engine for multiple asset types"""
    
    def __init__(self, starting_balance: float = 10000.0, risk_per_trade: float = 2.0):
        """
        Initialize backtester
        
        Args:
            starting_balance: Starting account balance
            risk_per_trade: Risk percentage per trade
        """
        self.starting_balance = starting_balance
        self.risk_per_trade = risk_per_trade / 100.0
        
    def backtest_strategy(self, df: pd.DataFrame, signal_func, 
                         symbol: str, asset_type: str = 'crypto',
                         timeframe: str = '1h') -> BacktestResults:
        """
        Run comprehensive backtest on historical data
        
        Args:
            df: OHLCV DataFrame with at least 100 candles
            signal_func: Function that generates signals (must return dict with 'signal' key)
            symbol: Trading symbol
            asset_type: 'crypto', 'stock', 'forex', or 'commodity'
            timeframe: Candlestick timeframe
            
        Returns:
            BacktestResults object with complete analysis
        """
        if len(df) < 100:
            logger.error(f"Insufficient data: need 100+ candles, got {len(df)}")
            return self._empty_results(symbol, asset_type, timeframe)
        
        # Normalize columns
        df = df.copy()
        if 'Open' in df.columns:
            df.columns = df.columns.str.lower()
        
        trades = []
        equity_curve = [self.starting_balance]
        current_balance = self.starting_balance
        in_trade = False
        entry_data = {}
        
        logger.info(f"Starting backtest for {symbol} ({asset_type}) on {timeframe}")
        
        # Run backtest bar by bar
        for i in range(100, len(df)):
            current_bar = df.iloc[i]
            current_time = current_bar.name
            current_price = current_bar['close']
            
            try:
                # Generate signal on current data
                signal_result = signal_func(df.iloc[:i+1])
                signal = signal_result.get('signal', 'NEUTRAL')
                confidence = signal_result.get('confidence', 0)
            except Exception as e:
                logger.debug(f"Signal generation failed at bar {i}: {str(e)}")
                signal = 'NEUTRAL'
                confidence = 0
            
            # ENTRY LOGIC
            if not in_trade and signal in ['BUY', 'SELL'] and confidence >= 55:
                # Calculate position sizing
                atr = current_bar.get('ATR', current_price * 0.02)
                atr = max(atr, current_price * 0.001)  # Ensure minimum ATR
                
                # Stop loss and take profit based on signal direction
                if signal == 'BUY':
                    stop_loss = current_price - (atr * 2.0)
                    take_profit = current_price + (atr * 4.0)
                else:  # SELL
                    stop_loss = current_price + (atr * 2.0)
                    take_profit = current_price - (atr * 4.0)
                
                # Position size calculation
                risk_amount = current_balance * self.risk_per_trade
                risk_distance = abs(current_price - stop_loss)
                
                if risk_distance > 0:
                    quantity = risk_amount / risk_distance
                    
                    in_trade = True
                    entry_data = {
                        'entry_time': current_time,
                        'entry_price': current_price,
                        'entry_bar': i,
                        'signal': signal,
                        'confidence': confidence,
                        'quantity': quantity,
                        'stop_loss': stop_loss,
                        'take_profit': take_profit,
                        'atr': atr,
                        'risk_amount': risk_amount
                    }
                    logger.debug(f"[ENTRY] {symbol} {signal} @ {current_price:.6f} | SL: {stop_loss:.6f} | TP: {take_profit:.6f}")
            
            # EXIT LOGIC
            elif in_trade:
                signal_obj = signal_result if 'signal' in signal_result else {}
                exit_price = current_price
                exit_time = current_time
                
                # Check exit conditions
                hit_stop_loss = False
                hit_take_profit = False
                
                if entry_data['signal'] == 'BUY':
                    if current_price <= entry_data['stop_loss']:
                        hit_stop_loss = True
                    elif current_price >= entry_data['take_profit']:
                        hit_take_profit = True
                else:  # SELL
                    if current_price >= entry_data['stop_loss']:
                        hit_stop_loss = True
                    elif current_price <= entry_data['take_profit']:
                        hit_take_profit = True
                
                # Calculate P&L
                if hit_stop_loss or hit_take_profit or signal == 'NEUTRAL':
                    if entry_data['signal'] == 'BUY':
                        pnl = (exit_price - entry_data['entry_price']) * entry_data['quantity']
                    else:  # SELL
                        pnl = (entry_data['entry_price'] - exit_price) * entry_data['quantity']
                    
                    pnl_percent = (pnl / entry_data['risk_amount']) * 100 if entry_data['risk_amount'] > 0 else 0
                    
                    # Create trade record
                    trade = Trade(
                        entry_time=entry_data['entry_time'],
                        entry_price=entry_data['entry_price'],
                        exit_time=exit_time,
                        exit_price=exit_price,
                        direction=entry_data['signal'],
                        quantity=entry_data['quantity'],
                        risk=entry_data['risk_amount'],
                        reward=entry_data['quantity'] * entry_data['atr'] * 4,
                        pnl=pnl,
                        pnl_percent=pnl_percent,
                        status='CLOSED'
                    )
                    
                    trades.append(trade)
                    current_balance += pnl
                    equity_curve.append(current_balance)
                    
                    exit_reason = "TP" if hit_take_profit else ("SL" if hit_stop_loss else "Signal")
                    logger.debug(f"[EXIT] {symbol} {exit_reason} @ {exit_price:.6f} | P&L: {pnl:.2f} ({pnl_percent:.2f}%)")
                    
                    in_trade = False
                    entry_data = {}
        
        # Handle any open position at end of backtest
        if in_trade:
            exit_price = df.iloc[-1]['close']
            if entry_data['signal'] == 'BUY':
                pnl = (exit_price - entry_data['entry_price']) * entry_data['quantity']
            else:
                pnl = (entry_data['entry_price'] - exit_price) * entry_data['quantity']
            
            pnl_percent = (pnl / entry_data['risk_amount']) * 100 if entry_data['risk_amount'] > 0 else 0
            
            trade = Trade(
                entry_time=entry_data['entry_time'],
                entry_price=entry_data['entry_price'],
                exit_time=df.iloc[-1].name,
                exit_price=exit_price,
                direction=entry_data['signal'],
                quantity=entry_data['quantity'],
                risk=entry_data['risk_amount'],
                reward=entry_data['quantity'] * entry_data['atr'] * 4,
                pnl=pnl,
                pnl_percent=pnl_percent,
                status='OPEN'
            )
            
            trades.append(trade)
            current_balance += pnl
            equity_curve.append(current_balance)
        
        # Calculate statistics
        return self._calculate_stats(symbol, asset_type, timeframe, trades, equity_curve)
    
    def _calculate_stats(self, symbol: str, asset_type: str, timeframe: str,
                         trades: List[Trade], equity_curve: List[float]) -> BacktestResults:
        """Calculate performance statistics"""
        
        total_trades = len(trades)
        
        if total_trades == 0:
            return self._empty_results(symbol, asset_type, timeframe)
        
        # Win/Loss analysis
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]
        breakeven_trades = [t for t in trades if t.pnl == 0]
        
        winning_count = len(winning_trades)
        losing_count = len(losing_trades)
        
        win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in trades)
        total_pnl_percent = ((equity_curve[-1] - self.starting_balance) / self.starting_balance * 100)
        
        # Average win/loss
        avg_win = (sum(t.pnl for t in winning_trades) / len(winning_trades)) if winning_trades else 0
        avg_loss = (sum(t.pnl for t in losing_trades) / len(losing_trades)) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        # Sharpe ratio
        equity_returns = np.diff(equity_curve) / np.array(equity_curve[:-1])
        sharpe_ratio = (np.mean(equity_returns) / np.std(equity_returns)) * np.sqrt(252) if len(equity_returns) > 1 else 0
        
        return BacktestResults(
            symbol=symbol,
            asset_type=asset_type,
            timeframe=timeframe,
            total_trades=total_trades,
            winning_trades=winning_count,
            losing_trades=losing_count,
            win_rate=win_rate,
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=trades,
            equity_curve=equity_curve
        )
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown"""
        if len(equity_curve) < 2:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return max_dd * 100  # Return as percentage
    
    def _empty_results(self, symbol: str, asset_type: str, timeframe: str) -> BacktestResults:
        """Return empty backtest results"""
        return BacktestResults(
            symbol=symbol,
            asset_type=asset_type,
            timeframe=timeframe,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_pnl=0.0,
            total_pnl_percent=0.0,
            avg_win=0.0,
            avg_loss=0.0,
            profit_factor=0.0,
            max_drawdown=0.0,
            sharpe_ratio=0.0,
            trades=[],
            equity_curve=[self.starting_balance]
        )
    
    def print_results(self, results: BacktestResults):
        """Pretty print backtest results"""
        
        print("\n" + "="*80)
        print(f"BACKTEST RESULTS: {results.symbol} ({results.asset_type.upper()}) - {results.timeframe}")
        print("="*80)
        print(f"\n📊 TRADE STATISTICS:")
        print(f"  Total Trades:        {results.total_trades}")
        print(f"  Winning Trades:      {results.winning_trades} ({results.win_rate:.1f}%)")
        print(f"  Losing Trades:       {results.losing_trades}")
        print(f"\n💰 FINANCIAL METRICS:")
        print(f"  Total P&L:           {results.total_pnl:,.2f}")
        print(f"  Total P&L %:         {results.total_pnl_percent:.2f}%")
        print(f"  Average Win:         {results.avg_win:,.2f}")
        print(f"  Average Loss:        {results.avg_loss:,.2f}")
        print(f"  Profit Factor:       {results.profit_factor:.2f}x")
        print(f"\n📈 RISK METRICS:")
        print(f"  Max Drawdown:        {results.max_drawdown:.2f}%")
        print(f"  Sharpe Ratio:        {results.sharpe_ratio:.2f}")
        print("\n" + "="*80)
    
    def export_results(self, results: BacktestResults) -> Dict:
        """Export results as dictionary"""
        return {
            'symbol': results.symbol,
            'asset_type': results.asset_type,
            'timeframe': results.timeframe,
            'total_trades': results.total_trades,
            'winning_trades': results.winning_trades,
            'losing_trades': results.losing_trades,
            'win_rate': results.win_rate,
            'total_pnl': results.total_pnl,
            'total_pnl_percent': results.total_pnl_percent,
            'avg_win': results.avg_win,
            'avg_loss': results.avg_loss,
            'profit_factor': results.profit_factor,
            'max_drawdown': results.max_drawdown,
            'sharpe_ratio': results.sharpe_ratio,
            'trades_summary': [
                {
                    'entry_time': str(t.entry_time),
                    'entry_price': t.entry_price,
                    'exit_time': str(t.exit_time),
                    'exit_price': t.exit_price,
                    'direction': t.direction,
                    'pnl': t.pnl,
                    'pnl_percent': t.pnl_percent,
                    'status': t.status
                } for t in results.trades
            ]
        }
