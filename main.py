"""
Signals Bot - Main Entry Point
Professional Trading Signal Generator with Multi-Confirmation Strategy
"""

import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.bot_engine import BotOrchestrator
from src.bot_config import BotConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signals_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Signals Bot - Professional Trading Signal Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run interactive menu
  python main.py --run              # Run complete analysis
  python main.py --symbol BTC/USDT  # Analyze single asset
  python main.py --config           # Show configuration
        """
    )
    
    parser.add_argument('--run', action='store_true',
                       help='Run complete portfolio analysis')
    parser.add_argument('--symbol', type=str,
                       help='Analyze specific symbol (e.g., BTC/USDT)')
    parser.add_argument('--type', type=str, default='crypto',
                       choices=['crypto', 'stock', 'forex'],
                       help='Asset type for single symbol analysis')
    parser.add_argument('--config', action='store_true',
                       help='Show current configuration')
    parser.add_argument('--config-path', type=str,
                       help='Path to config.json file')
    parser.add_argument('--no-backtest', action='store_true',
                       help='Disable backtesting before signals')
    parser.add_argument('--interactive', action='store_true',
                       help='Run interactive menu (default)')
    
    args = parser.parse_args()
    
    try:
        logger.info("="*70)
        logger.info("SIGNALS BOT STARTING")
        logger.info(f"Started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
        # Initialize orchestrator
        orchestrator = BotOrchestrator(args.config_path)
        
        # Run mode
        if args.run:
            # Complete portfolio analysis
            orchestrator.run(show_config=True, backtest=not args.no_backtest)
        
        elif args.symbol:
            # Single asset analysis
            analysis = orchestrator.engine.analyze_single_asset(
                args.symbol,
                args.type,
                backtest=not args.no_backtest
            )
            orchestrator.interface.print_signal_analysis(args.symbol, analysis)
        
        elif args.config:
            # Show configuration
            orchestrator.config.print_config()
        
        else:
            # Interactive mode (default)
            orchestrator.run_interactive()
        
        logger.info("="*70)
        logger.info("SIGNALS BOT COMPLETED SUCCESSFULLY")
        logger.info(f"Completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*70)
        
    except KeyboardInterrupt:
        logger.info("\nBot interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
