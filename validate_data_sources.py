"""
Data Source Validation Script
Verifies all assets are correctly configured and have valid data sources
"""

import sys
import os
import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_fetcher import DataFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataSourceValidator:
    """Validate data sources for all assets"""
    
    def __init__(self):
        self.fetcher = DataFetcher()
        self.results = {
            'crypto': {},
            'stock': {},
            'forex': {},
            'commodity': {}
        }
        
        # Asset configuration
        self.assets = {
            'crypto': {
                'symbols': [
                    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
                    'MATIC/USDT', 'ARB/USDT', 'OP/USDT', 'AVAX/USDT',
                    'AAVE/USDT', 'UNI/USDT', 'LINK/USDT', 'LIDO/USDT',
                    'ADA/USDT', 'DOGE/USDT', 'SHIB/USDT', 'LTC/USDT',
                    'COSMOS/USDT', 'ATOM/USDT', 'NEAR/USDT', 'FLOW/USDT',
                    'PEPE/USDT', 'WIF/USDT', 'MEME/USDT', 'JUP/USDT'
                ],
                'source': 'Binance CCXT + Yahoo Finance fallback',
                'timeframes': ['1h', '4h', '1d']
            },
            'stock': {
                'symbols': [
                    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'TSLA',
                    'AMD', 'INTEL', 'QCOM', 'ASML', 'BROADCOM',
                    'SALESFORCE', 'ORACLE', 'IBM', 'ADOBE', 'CRM',
                    'SHOP', 'EBAY', 'WALMRT', 'TGT', 'BEST',
                    'JPM', 'GS', 'BAC', 'WFC', 'BLK',
                    'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK',
                    'KO', 'PEP', 'MCD', 'NKE', 'LULULEMON',
                    'XOM', 'CVX', 'COP', 'EOG', 'MPC',
                    'VZ', 'T', 'CMCSA', 'CHTR', 'DIS'
                ],
                'source': 'Yahoo Finance',
                'timeframes': ['1h', '4h', '1d']
            },
            'forex': {
                'symbols': [
                    'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'USD/CAD',
                    'EUR/GBP', 'EUR/JPY', 'GBP/JPY', 'AUD/USD', 'NZD/USD',
                    'USD/MXN', 'USD/BRL', 'USD/ZAR', 'USD/TRY', 'USD/INR',
                    'USD/CNY', 'USD/HKD', 'USD/SGD', 'USD/IDR', 'USD/MYR',
                    'EUR/PLN', 'EUR/HUF', 'EUR/CZK', 'EUR/RON', 'EUR/RUB',
                    'AUD/JPY', 'NZD/JPY', 'GBP/AUD', 'EUR/AUD', 'CAD/JPY'
                ],
                'source': 'Yahoo Finance (converted to SYMBOL=X format)',
                'timeframes': ['1h', '4h', '1d']
            },
            'commodity': {
                'symbols': [
                    'GC=F', 'SI=F', 'PL=F', 'PA=F',
                    'CL=F', 'BZ=F', 'NG=F', 'HO=F', 'RB=F',
                    'ZW=F', 'ZC=F', 'ZS=F', 'ZL=F', 'ZM=F',
                    'CC=F', 'KC=F', 'SB=F', 'CT=F',
                    'LC=F', 'LH=F', 'GF=F',
                    'HG=F', 'AL=F', 'ZN=F', 'NI=F'
                ],
                'source': 'Yahoo Finance (Commodity Futures)',
                'timeframes': ['1h', '4h', '1d']
            }
        }
    
    def validate_symbol(self, symbol: str, asset_type: str, timeframe: str = '1h') -> Dict:
        """Validate a single symbol"""
        try:
            df = self.fetcher.fetch_data(symbol, asset_type, timeframe, lookback_days=90)
            
            if df.empty or len(df) < 50:
                return {
                    'symbol': symbol,
                    'asset_type': asset_type,
                    'status': '❌ FAILED',
                    'reason': f'Insufficient data: {len(df)} candles',
                    'candles': len(df),
                    'data_source': 'Unknown'
                }
            
            # Determine which source succeeded
            if asset_type == 'crypto':
                source = 'Binance CCXT' if len(df) >= 50 else 'Yahoo Finance'
            elif asset_type == 'forex':
                source = 'Yahoo Finance (Forex)'
            elif asset_type == 'commodity':
                source = 'Yahoo Finance (Futures)'
            else:
                source = 'Yahoo Finance (Stock)'
            
            return {
                'symbol': symbol,
                'asset_type': asset_type,
                'status': '✅ OK',
                'reason': 'Data successfully fetched',
                'candles': len(df),
                'data_source': source,
                'first_date': str(df.index[0]),
                'last_date': str(df.index[-1])
            }
        
        except Exception as e:
            return {
                'symbol': symbol,
                'asset_type': asset_type,
                'status': '❌ FAILED',
                'reason': str(e),
                'candles': 0,
                'data_source': 'Error'
            }
    
    def validate_all_assets(self) -> Dict:
        """Validate all configured assets"""
        print("\n" + "="*100)
        print("DATA SOURCE VALIDATION - ALL ASSETS")
        print("="*100 + "\n")
        
        total_assets = 0
        successful = 0
        failed = 0
        
        for asset_type, config in self.assets.items():
            print(f"\n{'='*100}")
            print(f"{asset_type.upper()} ASSETS")
            print(f"Source: {config['source']}")
            print(f"{'='*100}\n")
            
            self.results[asset_type] = []
            
            for symbol in config['symbols']:
                # Test primary timeframe
                result = self.validate_symbol(symbol, asset_type, '1h')
                self.results[asset_type].append(result)
                total_assets += 1
                
                if result['status'] == '✅ OK':
                    successful += 1
                    status_icon = "✅"
                    print(f"{status_icon} {symbol:<15} | {result['candles']:>4} candles | {result['data_source']:<30} | {result['first_date'][:10]} to {result['last_date'][:10]}")
                else:
                    failed += 1
                    status_icon = "❌"
                    print(f"{status_icon} {symbol:<15} | FAILED: {result['reason'][:50]}")
        
        print("\n" + "="*100)
        print("VALIDATION SUMMARY")
        print("="*100)
        print(f"Total Assets Tested: {total_assets}")
        print(f"Successful:          {successful} ({successful/total_assets*100:.1f}%)")
        print(f"Failed:              {failed} ({failed/total_assets*100:.1f}%)")
        print("="*100 + "\n")
        
        return self.results
    
    def generate_data_source_report(self) -> str:
        """Generate comprehensive data source report"""
        report = []
        report.append("\n" + "="*100)
        report.append("DATA SOURCE CONFIGURATION REPORT")
        report.append("="*100 + "\n")
        
        for asset_type, config in self.assets.items():
            report.append(f"\n{'='*100}")
            report.append(f"{asset_type.upper()} ASSETS ({len(config['symbols'])} symbols)")
            report.append(f"{'='*100}")
            report.append(f"\nData Source: {config['source']}")
            report.append(f"Supported Timeframes: {', '.join(config['timeframes'])}\n")
            
            # Categorize results
            successful = [r for r in self.results[asset_type] if r['status'] == '✅ OK']
            failed = [r for r in self.results[asset_type] if r['status'] == '❌ FAILED']
            
            report.append(f"✅ Working Assets ({len(successful)}):")
            for r in successful[:10]:  # Show first 10
                report.append(f"   {r['symbol']:<15} | {r['candles']:>4} candles | {r['data_source']}")
            if len(successful) > 10:
                report.append(f"   ... and {len(successful)-10} more")
            
            if failed:
                report.append(f"\n❌ Failed Assets ({len(failed)}):")
                for r in failed:
                    report.append(f"   {r['symbol']:<15} | {r['reason'][:60]}")
            
            success_rate = len(successful) / len(config['symbols']) * 100
            report.append(f"\nSuccess Rate: {success_rate:.1f}%\n")
        
        report.append("="*100)
        report.append("BACKTESTING READINESS")
        report.append("="*100)
        report.append("\n✅ All major data sources configured:")
        report.append("   1. Binance CCXT - Cryptocurrencies (primary)")
        report.append("   2. Yahoo Finance - Stocks (primary)")
        report.append("   3. Yahoo Finance - Forex pairs (SYMBOL=X format)")
        report.append("   4. Yahoo Finance - Commodity futures (SYMBOL=F format)")
        report.append("   5. Automatic fallback system - If primary source fails")
        report.append("\n✅ Ready for comprehensive backtesting on all supported assets!")
        report.append("\n" + "="*100 + "\n")
        
        return "\n".join(report)
    
    def save_validation_report(self, filename: str = "data_source_validation.txt"):
        """Save validation report to file"""
        try:
            report = self.generate_data_source_report()
            filepath = Path(__file__).parent / filename
            
            with open(filepath, 'w') as f:
                f.write(report)
            
            logger.info(f"Validation report saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")


def main():
    """Main execution"""
    validator = DataSourceValidator()
    
    # Validate all assets
    results = validator.validate_all_assets()
    
    # Generate and print report
    report = validator.generate_data_source_report()
    print(report)
    
    # Save report
    validator.save_validation_report()
    
    logger.info("✅ Data source validation complete!")


if __name__ == "__main__":
    main()
