"""
Signals Bot Integration Engine
Orchestrates all components: data fetching, indicators, signals, risk management, backtesting
"""

import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .data_fetcher import DataFetcher
from .technical_indicators import TechnicalIndicators
from .advanced_indicators import AdvancedIndicators
from .market_regime import MarketRegimeDetector
from .enhanced_signal_engine import EnhancedSignalEngine
from .enhanced_risk_manager import EnhancedRiskManager
from .backtest_engine import BacktestEngine
from .news_sentiment import NewsAndSentiment
from .bot_config import BotConfig
from .bot_interface import BotInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalsBotEngine:
    """Main orchestrator for the signals bot"""
    
    def __init__(self, config: BotConfig = None):
        """Initialize bot engine"""
        self.config = config or BotConfig()
        self.data_fetcher = DataFetcher()
        self.tech_indicators = TechnicalIndicators()
        self.advanced_indicators = AdvancedIndicators()
        self.market_regime = MarketRegimeDetector()
        self.signal_engine = EnhancedSignalEngine()
        self.risk_manager = EnhancedRiskManager(self.config.get('account_balance'))
        self.backtest_engine = BacktestEngine()
        self.news_analyzer = NewsAndSentiment()
        
        # Validation
        is_valid, errors = self.config.validate_config()
        if not is_valid:
            logger.warning(f"Configuration validation errors: {errors}")
    
    def analyze_single_asset(self, symbol: str, asset_type: str = 'crypto',
                           timeframe: str = '1h', backtest: bool = True) -> Dict:
        """
        Analyze single asset and generate signal
        
        Args:
            symbol: Asset symbol (e.g., 'BTC/USDT')
            asset_type: 'crypto', 'stock', or 'forex'
            timeframe: Candle timeframe
            backtest: Whether to run backtest before signal
        
        Returns:
            Dictionary with signal analysis
        """
        try:
            logger.info(f"Analyzing {symbol} ({asset_type}, {timeframe})...")
            
            # Step 1: Fetch data
            logger.debug("Step 1: Fetching market data...")
            df = self.data_fetcher.fetch_data(symbol, asset_type, timeframe, lookback_days=30)
            
            if df is None or df.empty:
                logger.warning(f"No data available for {symbol}")
                return self._neutral_signal(symbol, reason="No data available")
            
            if len(df) < 30:
                logger.warning(f"Insufficient data for {symbol}")
                return self._neutral_signal(symbol, reason="Insufficient historical data")
            
            # Step 2: Calculate all indicators
            logger.debug("Step 2: Calculating technical indicators...")
            df = self.tech_indicators.calculate_all_indicators(df, symbol)
            df = self.advanced_indicators.calculate_all_advanced_indicators(df, symbol)
            
            # Step 3: Detect market regime
            logger.debug("Step 3: Detecting market regime...")
            regime = self.market_regime.detect_regime(df)
            
            # Step 4: Analyze with enhanced signal engine
            logger.debug("Step 4: Running enhanced signal analysis...")
            signal_analysis = self.signal_engine.analyze(df, symbol)
            
            # Step 5: Run backtest if enabled
            backtest_results = None
            if backtest:
                logger.debug("Step 5: Running backtest validation...")
                backtest_results = self._run_backtest(df, symbol, signal_analysis)
                
                # Check backtest metrics
                if backtest_results:
                    if not self._validate_backtest_results(backtest_results):
                        logger.warning(f"Backtest validation failed for {symbol}")
                        signal_analysis['signal'] = 'NEUTRAL'
                        signal_analysis['confidence'] = 0
                        signal_analysis['reasons'] = {
                            'bullish_reasons': ['Backtest metrics do not meet minimum requirements']
                        }
            
            # Step 6: Risk validation
            logger.debug("Step 6: Running risk validation...")
            current_price = df['close'].iloc[-1]
            setup = signal_analysis.get('setup', {})
            
            risk_validation = self.risk_manager.enforce_risk_rules(
                entry=setup.get('entry', current_price),
                stop_loss=setup.get('stop_loss', current_price * 0.98),
                take_profit=setup.get('take_profit', current_price * 1.05),
                current_price=current_price,
                symbol=symbol,
                signal=signal_analysis.get('signal', 'NEUTRAL'),
                atr=df['atr'].iloc[-1] if 'atr' in df.columns else None
            )
            
            # Final signal - only BUY/SELL if risk rules pass
            if not risk_validation.get('allowed', False):
                signal_analysis['signal'] = 'NEUTRAL'
                signal_analysis['confidence'] = 0
                signal_analysis['risk_rejected'] = True
                signal_analysis['risk_reasons'] = risk_validation.get('reasons', [])
            
            # Step 7: News sentiment (if available)
            logger.debug("Step 7: Checking news sentiment...")
            sentiment = self.news_analyzer.analyze_sentiment(symbol)
            signal_analysis['sentiment'] = sentiment
            
            # Step 8: Add backtest results if available
            if backtest_results:
                signal_analysis['backtest'] = backtest_results
            
            # Add market regime
            signal_analysis['market_regime'] = regime
            signal_analysis['timestamp'] = datetime.now().isoformat()
            signal_analysis['symbol'] = symbol
            
            logger.info(f"Analysis complete for {symbol}: {signal_analysis.get('signal')} "
                       f"({signal_analysis.get('confidence', 0):.1f}%)")
            
            return signal_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}", exc_info=True)
            return self._neutral_signal(symbol, reason=f"Analysis error: {str(e)}")
    
    def analyze_portfolio(self, backtest: bool = True) -> List[Dict]:
        """
        Analyze all configured assets
        
        Args:
            backtest: Whether to run backtest before signals
        
        Returns:
            List of signal analyses for all assets
        """
        logger.info("Starting portfolio analysis...")
        
        assets = self.config.get('assets', [])
        analyses = []
        
        for asset in assets:
            symbol = asset.get('symbol')
            asset_type = asset.get('type', 'crypto')
            timeframe = asset.get('timeframe', '1h')
            
            analysis = self.analyze_single_asset(symbol, asset_type, timeframe, backtest)
            analyses.append(analysis)
        
        logger.info(f"Portfolio analysis complete. Analyzed {len(analyses)} assets")
        return analyses
    
    def _run_backtest(self, df: pd.DataFrame, symbol: str, signal_analysis: Dict) -> Dict:
        """Run backtest on the signal strategy"""
        try:
            if len(df) < 50:
                logger.warning("Insufficient data for backtest")
                return None
            
            # Get backtest settings
            backtest_settings = self.config.get_backtest_settings()
            
            # Run backtest
            setup = signal_analysis.get('setup', {})
            signal = signal_analysis.get('signal', 'NEUTRAL')
            
            if signal != 'BUY' and signal != 'SELL':
                return None
            
            backtest_result = self.backtest_engine.backtest_signal(
                df=df,
                symbol=symbol,
                signal=signal,
                entry_price=setup.get('entry'),
                stop_loss=setup.get('stop_loss'),
                take_profit=setup.get('take_profit')
            )
            
            return backtest_result
            
        except Exception as e:
            logger.error(f"Error running backtest for {symbol}: {e}")
            return None
    
    def _validate_backtest_results(self, backtest_results: Dict) -> bool:
        """Validate backtest results meet minimum thresholds"""
        if not backtest_results:
            return False
        
        settings = self.config.get_backtest_settings()
        
        # Check minimum metrics
        total_trades = backtest_results.get('total_trades', 0)
        win_rate = backtest_results.get('win_rate', 0)
        profit_factor = backtest_results.get('profit_factor', 0)
        
        if total_trades < settings.get('min_trades', 5):
            logger.debug(f"Backtest failed: {total_trades} trades < {settings.get('min_trades')}")
            return False
        
        if win_rate < settings.get('min_win_rate', 0.45):
            logger.debug(f"Backtest failed: {win_rate:.2%} win rate < {settings.get('min_win_rate'):.2%}")
            return False
        
        if profit_factor < settings.get('min_profit_factor', 1.2):
            logger.debug(f"Backtest failed: {profit_factor:.2f} PF < {settings.get('min_profit_factor'):.2f}")
            return False
        
        return True
    
    def _neutral_signal(self, symbol: str, reason: str = "No signal") -> Dict:
        """Generate neutral signal"""
        return {
            'symbol': symbol,
            'signal': 'NEUTRAL',
            'confidence': 0.0,
            'quality': 'NEUTRAL',
            'timestamp': datetime.now().isoformat(),
            'reasons': {
                'bullish_reasons': [reason]
            },
            'confirmations': {
                'trend': 'N/A',
                'trend_strength': 0,
                'momentum_confirmed': False,
                'momentum_strength': 0,
                'volume_confirmed': False,
                'volatility_acceptable': False
            },
            'setup': {
                'entry': 0,
                'stop_loss': 0,
                'take_profit': 0,
                'rr_ratio': 0
            }
        }


class BotOrchestrator:
    """High-level bot orchestrator with reporting"""
    
    def __init__(self, config_path: str = None):
        """Initialize orchestrator"""
        self.config = BotConfig(config_path)
        self.engine = SignalsBotEngine(self.config)
        self.interface = BotInterface()
    
    def run(self, show_config: bool = False, backtest: bool = True):
        """
        Run complete bot analysis and display results
        
        Args:
            show_config: Whether to display configuration
            backtest: Whether to run backtests
        """
        # Header
        self.interface.print_header()
        
        # Configuration
        if show_config:
            self.interface.print_configuration(self.config.get_account_settings())
        
        # Analyze portfolio
        analyses = self.engine.analyze_portfolio(backtest=backtest)
        
        # Display results
        logger.info("\n" + "="*70)
        logger.info("SIGNALS ANALYSIS RESULTS")
        logger.info("="*70)
        
        for analysis in analyses:
            self.interface.print_signal_analysis(
                analysis.get('symbol'),
                analysis
            )
            
            # Show backtest if available
            if 'backtest' in analysis and analysis['backtest']:
                self.interface.print_backtest_results(analysis['backtest'])
        
        # Summary table
        self.interface.print_summary_table(analyses)
        
        # Footer
        self.interface.print_footer()
        
        return analyses
    
    def run_interactive(self):
        """Run interactive menu"""
        self.interface.print_header()
        
        while True:
            print("\n" + "="*70)
            print("MAIN MENU")
            print("="*70)
            print("1. Analyze All Assets")
            print("2. Analyze Single Asset")
            print("3. View Configuration")
            print("4. Edit Configuration")
            print("5. Run Backtest")
            print("6. Exit")
            print("="*70)
            
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                self.run(show_config=False, backtest=True)
            
            elif choice == '2':
                symbol = input("Enter symbol (e.g., BTC/USDT): ").strip()
                asset_type = input("Asset type (crypto/stock/forex): ").strip() or 'crypto'
                timeframe = input("Timeframe (e.g., 1h, 4h, 1d): ").strip() or '1h'
                
                analysis = self.engine.analyze_single_asset(symbol, asset_type, timeframe)
                self.interface.print_signal_analysis(symbol, analysis)
            
            elif choice == '3':
                self.config.print_config()
            
            elif choice == '4':
                key = input("Enter config key: ").strip()
                value = input("Enter new value: ").strip()
                
                try:
                    # Try to convert to number if possible
                    if '.' in value:
                        self.config.set(key, float(value))
                    elif value.isdigit():
                        self.config.set(key, int(value))
                    else:
                        self.config.set(key, value)
                    
                    self.config.save_config()
                    print(f"✓ Configuration updated: {key} = {value}")
                except Exception as e:
                    print(f"✗ Error updating configuration: {e}")
            
            elif choice == '5':
                symbol = input("Enter symbol for backtest: ").strip()
                asset_type = input("Asset type (crypto/stock/forex): ").strip() or 'crypto'
                
                df = self.engine.data_fetcher.fetch_data(symbol, asset_type, '1h', lookback_days=30)
                if df is not None:
                    df = self.engine.tech_indicators.calculate_all_indicators(df, symbol)
                    signal_analysis = self.engine.signal_engine.analyze(df, symbol)
                    
                    backtest_result = self.engine._run_backtest(df, symbol, signal_analysis)
                    if backtest_result:
                        self.interface.print_backtest_results(backtest_result)
                    else:
                        print("Backtest failed or no results available")
                else:
                    print("Failed to fetch data")
            
            elif choice == '6':
                print("\nGoodbye!")
                break
            
            else:
                print("Invalid option. Please try again.")
