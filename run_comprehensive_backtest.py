"""
Comprehensive Backtesting Script
Tests all supported assets across different strategies
"""

import sys
import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_fetcher import DataFetcher
from src.signal_generator import SignalGenerator
from src.comprehensive_backtest import ComprehensiveBacktester, BacktestResults

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AssetBacktestRunner:
    """Run comprehensive backtests on all supported assets"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.signal_gen = SignalGenerator()
        self.backtester = ComprehensiveBacktester(starting_balance=10000, risk_per_trade=2)
        self.results = {}
        
        # Asset configuration
        self.assets = {
            'crypto': {
                'symbols': [
                    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'LINK/USDT',
                    'MATIC/USDT', 'AVAX/USDT', 'ARB/USDT', 'OP/USDT'
                ],
                'timeframes': ['1h', '4h'],
                'lookback_days': 90
            },
            'stock': {
                'symbols': [
                    'AAPL', 'GOOGL', 'MSFT', 'NVDA',
                    'META', 'TESLA', 'JPM', 'XOM'
                ],
                'timeframes': ['1h', '4h'],
                'lookback_days': 180
            },
            'forex': {
                'symbols': [
                    'EUR/USD', 'GBP/USD', 'USD/JPY',
                    'AUD/USD', 'EUR/GBP', 'USD/CAD'
                ],
                'timeframes': ['1h', '4h'],
                'lookback_days': 90
            },
            'commodity': {
                'symbols': [
                    'Gold (GC=F)', 'Silver (SI=F)', 'Crude Oil - WTI (CL=F)',
                    'Natural Gas (NG=F)', 'Corn (ZC=F)', 'Copper (HG=F)'
                ],
                'timeframes': ['1h', '4h'],
                'lookback_days': 180
            }
        }
    
    def _extract_symbol(self, symbol_display: str) -> str:
        """Extract actual symbol from display name"""
        if "(" in symbol_display and ")" in symbol_display:
            return symbol_display.split("(")[1].split(")")[0]
        return symbol_display
    
    def run_backtest(self, asset_type: str, symbol: str, timeframe: str) -> BacktestResults:
        """Run backtest for a single asset"""
        try:
            # Extract actual symbol
            actual_symbol = self._extract_symbol(symbol)
            
            logger.info(f"\n📊 Backtesting {actual_symbol} ({asset_type}) on {timeframe}")
            
            # Fetch data
            lookback_days = self.assets[asset_type]['lookback_days']
            df = self.fetcher.fetch_data(actual_symbol, asset_type, timeframe, lookback_days)
            
            if df.empty or len(df) < 100:
                logger.warning(f"❌ Insufficient data for {actual_symbol}: {len(df)} candles")
                return None
            
            logger.info(f"✓ Fetched {len(df)} candles for {actual_symbol}")
            
            # Run backtest
            def signal_func(data):
                return self.signal_gen.generate_signal(data)
            
            results = self.backtester.backtest_strategy(
                df, signal_func,
                actual_symbol, asset_type, timeframe
            )
            
            return results
        
        except Exception as e:
            logger.error(f"Error backtesting {symbol}: {str(e)}")
            return None
    
    def run_all_backtests(self) -> Dict:
        """Run backtests for all configured assets"""
        all_results = {}
        total_tests = 0
        successful_tests = 0
        
        for asset_type, config in self.assets.items():
            all_results[asset_type] = {}
            
            for symbol in config['symbols']:
                all_results[asset_type][symbol] = {}
                
                for timeframe in config['timeframes']:
                    total_tests += 1
                    results = self.run_backtest(asset_type, symbol, timeframe)
                    
                    if results:
                        successful_tests += 1
                        all_results[asset_type][symbol][timeframe] = results
                        self.backtester.print_results(results)
                    else:
                        all_results[asset_type][symbol][timeframe] = None
        
        logger.info(f"\n\n{'='*80}")
        logger.info(f"BACKTEST SUMMARY: {successful_tests}/{total_tests} successful")
        logger.info(f"{'='*80}")
        
        return all_results
    
    def generate_report(self, results_dict: Dict) -> str:
        """Generate comprehensive backtest report"""
        report = []
        report.append("\n" + "="*100)
        report.append("COMPREHENSIVE BACKTESTING REPORT - ALL ASSETS")
        report.append("="*100 + "\n")
        
        # Summary by asset type
        for asset_type, symbols_results in results_dict.items():
            report.append(f"\n{'='*100}")
            report.append(f"{asset_type.upper()} ASSETS")
            report.append(f"{'='*100}\n")
            
            for symbol, timeframe_results in symbols_results.items():
                report.append(f"\n📊 {symbol.upper()}")
                report.append("-" * 100)
                
                for timeframe, results in timeframe_results.items():
                    if results is None:
                        report.append(f"  ❌ {timeframe}: No data available")
                        continue
                    
                    status = "✅" if results.win_rate > 50 else "⚠️"
                    report.append(f"\n  {status} {timeframe.upper()} Timeframe:")
                    report.append(f"     Trades:        {results.total_trades} (W: {results.winning_trades} | L: {results.losing_trades})")
                    report.append(f"     Win Rate:      {results.win_rate:.1f}%")
                    report.append(f"     Total P&L:     {results.total_pnl_percent:+.2f}%")
                    report.append(f"     Profit Factor: {results.profit_factor:.2f}x")
                    report.append(f"     Max Drawdown:  {results.max_drawdown:.2f}%")
                    report.append(f"     Sharpe Ratio:  {results.sharpe_ratio:.2f}")
        
        report.append("\n" + "="*100)
        report.append("END OF REPORT")
        report.append("="*100 + "\n")
        
        return "\n".join(report)
    
    def save_results(self, results_dict: Dict, filename: str = "backtest_results.json"):
        """Save backtest results to JSON"""
        try:
            export_data = {}
            
            for asset_type, symbols_results in results_dict.items():
                export_data[asset_type] = {}
                
                for symbol, timeframe_results in symbols_results.items():
                    export_data[asset_type][symbol] = {}
                    
                    for timeframe, results in timeframe_results.items():
                        if results:
                            export_data[asset_type][symbol][timeframe] = self.backtester.export_results(results)
                        else:
                            export_data[asset_type][symbol][timeframe] = None
            
            filepath = Path(__file__).parent / filename
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Results saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")


def main():
    """Main execution"""
    print("\n" + "="*100)
    print("COMPREHENSIVE BACKTESTING SYSTEM")
    print("Testing all supported assets: Crypto, Stocks, Forex, Commodities")
    print("="*100 + "\n")
    
    runner = AssetBacktestRunner()
    
    # Run all backtests
    logger.info("Starting comprehensive backtesting...")
    results = runner.run_all_backtests()
    
    # Generate and print report
    report = runner.generate_report(results)
    print(report)
    
    # Save results
    runner.save_results(results)
    
    print("✅ Backtesting complete!")


if __name__ == "__main__":
    main()
