"""
User-Friendly Interface for Signals Bot
Beautiful, intuitive output formatting
"""

from typing import Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotInterface:
    """User-friendly interface for the trading bot"""
    
    @staticmethod
    def print_header():
        """Print application header"""
        header = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║              SIGNALS BOT - PROFESSIONAL TRADING BOT               ║
║                                                                    ║
║        Multi-Confirmation Strategy | Risk-Managed Trading        ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """
        print(header)
    
    @staticmethod
    def print_signal_analysis(symbol: str, analysis: Dict):
        """Print detailed signal analysis"""
        signal = analysis.get('signal', 'NEUTRAL')
        confidence = analysis.get('confidence', 0)
        quality = analysis.get('quality', 'NEUTRAL')
        
        # Color coding
        signal_color = '🟢' if signal == 'BUY' else ('🔴' if signal == 'SELL' else '🟡')
        quality_color = '★★★' if 'STRONG' in quality else ('★★' if 'GOOD' in quality else '★')
        
        print(f"\n┌{'─'*68}┐")
        print(f"│ {symbol.upper():^66} │")
        print(f"├{'─'*68}┤")
        
        # Signal
        print(f"│ {signal_color} SIGNAL: {signal:<20} CONFIDENCE: {confidence:>5.1f}%  QUALITY: {quality:<10} │")
        print(f"├{'─'*68}┤")
        
        # Confirmations
        confirmations = analysis.get('confirmations', {})
        print(f"│ CONFIRMATIONS:                                                     │")
        print(f"│   • Trend:     {confirmations.get('trend', 'N/A'):<10} ({confirmations.get('trend_strength', 'N/A')})")
        print(f"│   • Momentum:  {'✓ YES' if confirmations.get('momentum_confirmed') else '✗ NO':<10} ({confirmations.get('momentum_strength', 'N/A')})")
        print(f"│   • Volume:    {'✓ YES' if confirmations.get('volume_confirmed') else '✗ NO':<10}")
        print(f"│   • Volatility: {'✓ OK' if confirmations.get('volatility_acceptable') else '✗ RISKY':<10}")
        print(f"├{'─'*68}┤")
        
        # Setup
        setup = analysis.get('setup', {})
        print(f"│ SETUP DETAILS:                                                     │")
        print(f"│   Entry:  ${setup.get('entry', 0):>10.2f}  │  Stop:  ${setup.get('stop_loss', 0):>10.2f}  │  TP:  ${setup.get('take_profit', 0):>10.2f}  │")
        print(f"│   RR Ratio: {setup.get('rr_ratio', 0):.2f}:1                                                │")
        print(f"├{'─'*68}┤")
        
        # Reasons
        reasons = analysis.get('reasons', {})
        print(f"│ WHY THIS SIGNAL:                                                   │")
        if reasons.get('bullish_reasons'):
            for reason in reasons['bullish_reasons'][:3]:
                print(f"│   ✓ {reason:<61} │")
        print(f"├{'─'*68}┤")
        print(f"│ {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<66} │")
        print(f"└{'─'*68}┘")
    
    @staticmethod
    def print_risk_validation(validation: Dict):
        """Print risk validation results"""
        allowed = validation.get('allowed', False)
        reasons = validation.get('reasons', [])
        
        status_symbol = '✓ APPROVED' if allowed else '✗ REJECTED'
        status_color = '🟢' if allowed else '🔴'
        
        print(f"\n┌{'─'*68}┐")
        print(f"│ {status_color} RISK VALIDATION {status_symbol:<48} │")
        print(f"├{'─'*68}┤")
        
        for reason in reasons:
            if len(reason) > 66:
                # Split long lines
                print(f"│ {reason[:66]:<66} │")
                print(f"│ {reason[66:]:<66} │")
            else:
                print(f"│ {reason:<66} │")
        
        print(f"└{'─'*68}┘")
    
    @staticmethod
    def print_market_analysis(df_analysis: Dict):
        """Print market analysis details"""
        print(f"\n┌{'─'*68}┐")
        print(f"│ MARKET ANALYSIS                                                    │")
        print(f"├{'─'*68}┤")
        
        # Trend
        trend = df_analysis.get('detailed_analysis', {}).get('trend', {})
        print(f"│ TREND:                                                             │")
        print(f"│   Status:  {trend.get('trend', 'N/A'):<20} | ADX: {trend.get('adx', 0):>6.1f}        │")
        
        # Momentum
        momentum = df_analysis.get('detailed_analysis', {}).get('momentum', {})
        print(f"│ MOMENTUM:                                                          │")
        print(f"│   RSI: {momentum.get('rsi', 0):>6.1f}  │  MFI: {momentum.get('mfi', 0):>6.1f}  │  Score: {momentum.get('score', 0)}/5         │")
        
        # Volume
        volume = df_analysis.get('detailed_analysis', {}).get('volume', {})
        print(f"│ VOLUME:                                                            │")
        print(f"│   Status: {volume.get('reason', 'N/A'):<30}                   │")
        
        # Volatility
        volatility = df_analysis.get('detailed_analysis', {}).get('volatility', {})
        print(f"│ VOLATILITY:                                                        │")
        print(f"│   {volatility.get('reason', 'N/A'):<62} │")
        
        print(f"└{'─'*68}┘")
    
    @staticmethod
    def print_backtest_results(backtest: Dict):
        """Print backtest results"""
        print(f"\n┌{'─'*68}┐")
        print(f"│ BACKTEST RESULTS                                                   │")
        print(f"├{'─'*68}┤")
        
        total = backtest.get('total_trades', 0)
        wins = backtest.get('winning_trades', 0)
        losses = backtest.get('losing_trades', 0)
        wr = backtest.get('win_rate', 0)
        
        # Trade stats
        print(f"│ TRADE STATISTICS:                                                  │")
        print(f"│   Total Trades: {total:>4}  │  Wins: {wins:>4}  │  Losses: {losses:>4}  │  Win Rate: {wr:>6.1f}%       │")
        
        # P&L
        pnl = backtest.get('total_pnl', 0)
        pnl_pct = backtest.get('total_pnl_percent', 0)
        final = backtest.get('final_balance', 0)
        
        pnl_color = '🟢' if pnl > 0 else '🔴'
        print(f"│ PROFIT/LOSS:                                                       │")
        print(f"│ {pnl_color} Total P&L: ${pnl:>10.2f}  │  Percent: {pnl_pct:>7.2f}%  │  Final: ${final:>10.2f} │")
        
        # Risk
        drawdown = backtest.get('max_drawdown', 0)
        pf = backtest.get('profit_factor', 0)
        
        print(f"│ RISK METRICS:                                                      │")
        print(f"│   Max Drawdown: {drawdown:>6.2f}%  │  Profit Factor: {pf:>5.2f}  │  Avg Hold: {backtest.get('avg_bars_held', 0):>5.0f} bars │")
        
        print(f"└{'─'*68}┘")
    
    @staticmethod
    def print_configuration(config: Dict):
        """Print current configuration"""
        print(f"\n┌{'─'*68}┐")
        print(f"│ CONFIGURATION                                                      │")
        print(f"├{'─'*68}┤")
        print(f"│ Account Balance:       ${config.get('account_balance', 0):>15,.2f}                │")
        print(f"│ Risk per Trade:        {config.get('risk_percent', 1.0):>15.1f}%                 │")
        print(f"│ Max Risk Amount:       ${config.get('max_risk_amount', 0):>15,.2f}                │")
        print(f"│ Min R:R Ratio:         {config.get('min_rr_ratio', 2.0):>15.1f}:1                │")
        print(f"│ Min Trend (ADX):       {config.get('min_adx', 20):>15.1f}                   │")
        print(f"│ Max Drawdown:          {config.get('max_drawdown', 10.0):>15.1f}%                 │")
        print(f"└{'─'*68}┘")
    
    @staticmethod
    def print_summary_table(analyses: List[Dict]):
        """Print summary table of all analyzed assets"""
        print(f"\n┌{'─'*88}┐")
        print(f"│ SIGNALS SUMMARY                                                                        │")
        print(f"├{'─'*88}┤")
        print(f"│ Symbol  │ Signal │ Conf.  │ Quality │ Trend    │ Momentum │ Volume │ Volatility        │")
        print(f"├{'─'*88}┤")
        
        for analysis in analyses:
            symbol = analysis.get('symbol', 'N/A')[:7]
            signal = analysis.get('signal', 'NEUTRAL')[:6]
            conf = analysis.get('confidence', 0)
            quality = analysis.get('quality', 'NEUTRAL')[:7]
            
            confirmations = analysis.get('confirmations', {})
            trend = confirmations.get('trend', 'N/A')[:8]
            momentum = "✓" if confirmations.get('momentum_confirmed') else "✗"
            volume = "✓" if confirmations.get('volume_confirmed') else "✗"
            volatility = "✓" if confirmations.get('volatility_acceptable') else "✗"
            
            print(f"│ {symbol:<7} │ {signal:<6} │ {conf:>5.1f}% │ {quality:<7} │ {trend:<8} │ {momentum:^8} │ {volume:^6} │ {volatility:^17} │")
        
        print(f"└{'─'*88}┘")
    
    @staticmethod
    def print_footer(timestamp: str = None):
        """Print footer"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        footer = f"""
┌{'─'*68}┐
│ Analysis Complete - {timestamp:<39} │
│ Remember: Capital Preservation > Profits                           │
│ Always validate signals before trading                             │
└{'─'*68}┘
        """
        print(footer)
