# Integration & Architecture Guide

## System Architecture

The Signals Bot is built with a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Bot Orchestrator  │  Interactive Menu  │  CLI Args  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  ORCHESTRATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SignalsBotEngine (Main Orchestrator)               │  │
│  │  - Coordinates all components                       │  │
│  │  - Manages data flow                                │  │
│  │  - Enforces execution order                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  ANALYSIS LAYER                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Data Fetcher → Indicators → Signal Engine → Backtest │ │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  VALIDATION LAYER                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Risk Manager (6 Mandatory Checks)                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  OUTPUT LAYER                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Bot Interface (Formatted Reports & Tables)          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Module Relationships

### Data Flow: Single Asset Analysis

```
1. DataFetcher
   ↓ Fetches OHLCV data (30+ days)
   
2. TechnicalIndicators
   ↓ Calculates 20+ basic indicators
   
3. AdvancedIndicators
   ↓ Calculates 15+ advanced indicators
   
4. EnhancedSignalEngine
   ├─ Evaluates Trend Strength (35% weight)
   ├─ Evaluates Momentum (25% weight)
   ├─ Evaluates Volume (20% weight)
   ├─ Evaluates Volatility (20% weight)
   └─ Generates Signal + Confidence Score
   
5. BacktestEngine (if enabled)
   ↓ Validates signal on historical data
   └─ Returns metrics: Win Rate, PF, Drawdown
   
6. EnhancedRiskManager
   ├─ Check 1: Position Sizing
   ├─ Check 2: Risk-Reward Ratio
   ├─ Check 3: Market Conditions
   ├─ Check 4: Stop Loss Validity
   ├─ Check 5: Take Profit Validity
   └─ Check 6: Drawdown Check
   └─ Returns: Allowed (True/False) + Reasons
   
7. BotInterface
   └─ Formats and displays report
```

### Data Flow: Complete Portfolio

```
BotOrchestrator.run()
    ↓
For each configured asset:
    └─ SignalsBotEngine.analyze_single_asset()
       └─ Execute steps 1-7 above
       └─ Collect result
    ↓
Aggregate results from all assets
    ↓
BotInterface.print_summary_table()
BotInterface.print_footer()
```

## Component Integration Examples

### 1. DataFetcher → TechnicalIndicators

```python
from src.data_fetcher import DataFetcher
from src.technical_indicators import TechnicalIndicators

# Step 1: Fetch data
df = DataFetcher().fetch_data('BTC/USDT', 'crypto', '1h', lookback_days=30)

# Step 2: Calculate indicators
df = TechnicalIndicators().calculate_all_indicators(df, 'BTC/USDT')

# Now df has columns:
# ['open', 'high', 'low', 'close', 'volume',
#  'sma10', 'ema20', 'rsi', 'macd', 'bb_upper', 'bb_lower',
#  'atr', 'adx', 'obv', 'vwap', ...]
```

### 2. Indicators → EnhancedSignalEngine

```python
from src.enhanced_signal_engine import EnhancedSignalEngine

signal_engine = EnhancedSignalEngine()
signal_analysis = signal_engine.analyze(df, 'BTC/USDT')

# signal_analysis contains:
# {
#     'signal': 'BUY',              # or 'SELL', 'NEUTRAL'
#     'confidence': 77.5,           # 0-100%
#     'quality': 'B',               # 'A+', 'B', 'C', 'NEUTRAL'
#     'setup': {
#         'entry': 45230.00,
#         'stop_loss': 44890.00,
#         'take_profit': 46980.00,
#         'rr_ratio': 2.4
#     },
#     'confirmations': {
#         'trend': 'BULLISH',
#         'momentum_confirmed': True,
#         'volume_confirmed': True,
#         'volatility_acceptable': True
#     },
#     'reasons': {
#         'bullish_reasons': [...]
#     }
# }
```

### 3. BacktestEngine Validation

```python
from src.backtest_engine import BacktestEngine

backtest = BacktestEngine()
results = backtest.backtest_signal(
    df=df,
    symbol='BTC/USDT',
    signal='BUY',
    entry_price=45230,
    stop_loss=44890,
    take_profit=46980
)

# results contains:
# {
#     'total_trades': 12,
#     'winning_trades': 7,
#     'losing_trades': 5,
#     'win_rate': 0.583,
#     'profit_factor': 1.65,
#     'max_drawdown': 0.062,
#     'total_pnl': 450.00,
#     'total_pnl_percent': 4.5
# }
```

### 4. EnhancedRiskManager Validation

```python
from src.enhanced_risk_manager import EnhancedRiskManager
from src.bot_config import BotConfig

config = BotConfig()
risk_mgr = EnhancedRiskManager(config.get('account_balance'))

validation = risk_mgr.enforce_risk_rules(
    entry=45230,
    stop_loss=44890,
    take_profit=46980,
    current_price=45200,
    symbol='BTC/USDT',
    signal='BUY',
    atr=180
)

# validation contains:
# {
#     'allowed': True,           # or False if any check fails
#     'reasons': [
#         '✓ Position size valid: 1.5% of account',
#         '✓ R:R ratio 2.4:1 (> 2.0 minimum)',
#         '✓ Market conditions favorable',
#         '✓ Stop loss distance valid (1.2x ATR)',
#         '✓ Take profit distance valid (2.4x ATR)',
#         '✓ Drawdown 3.2% (< 10% max)'
#     ]
# }
```

### 5. Configuration Management

```python
from src.bot_config import BotConfig

# Load config
config = BotConfig('my_config.json')

# Get specific settings
balance = config.get('account_balance')
risk_pct = config.get('risk_percent')

# Get grouped settings
account_settings = config.get_account_settings()
trading_rules = config.get_trading_rules()
indicator_settings = config.get_indicator_settings()

# Modify settings
config.set('risk_percent', 2.0)
config.set('min_adx', 25.0)

# Save changes
config.save_config()

# Validate
is_valid, errors = config.validate_config()
if not is_valid:
    print(f"Errors: {errors}")
```

### 6. Interface Reporting

```python
from src.bot_interface import BotInterface

interface = BotInterface()

# Print header
interface.print_header()

# Print detailed signal
interface.print_signal_analysis('BTC/USDT', signal_analysis)

# Print risk validation
interface.print_risk_validation(validation)

# Print backtest results
interface.print_backtest_results(backtest_results)

# Print summary table
interface.print_summary_table(analyses)

# Print footer
interface.print_footer()
```

## Integration Workflows

### Workflow 1: Complete Analysis (Default)

```python
from src.bot_engine import BotOrchestrator

orchestrator = BotOrchestrator()

# Run complete portfolio analysis with backtesting
orchestrator.run(show_config=True, backtest=True)
```

**Flow:**
1. Load configuration
2. For each asset:
   - Fetch data
   - Calculate indicators
   - Generate signal
   - Run backtest
   - Validate risk rules
3. Display results
4. Print summary

### Workflow 2: Single Asset Analysis

```python
from src.bot_engine import SignalsBotEngine

engine = SignalsBotEngine()

# Analyze one asset
analysis = engine.analyze_single_asset(
    symbol='BTC/USDT',
    asset_type='crypto',
    timeframe='1h',
    backtest=True
)

# Use analysis
print(f"Signal: {analysis['signal']}")
print(f"Confidence: {analysis['confidence']}%")
```

### Workflow 3: Fast Monitoring (No Backtest)

```python
from src.bot_engine import SignalsBotEngine

engine = SignalsBotEngine()

# Quick analysis without backtesting (faster)
analysis = engine.analyze_single_asset(
    symbol='BTC/USDT',
    asset_type='crypto',
    timeframe='1h',
    backtest=False  # Skip backtest for speed
)
```

### Workflow 4: Backtest-Only Analysis

```python
from src.bot_engine import SignalsBotEngine
from src.data_fetcher import DataFetcher
from src.technical_indicators import TechnicalIndicators
from src.enhanced_signal_engine import EnhancedSignalEngine

# Fetch data
df = DataFetcher().fetch_data('BTC/USDT', 'crypto', '1h', lookback_days=30)

# Calculate indicators
df = TechnicalIndicators().calculate_all_indicators(df, 'BTC/USDT')

# Generate signal
signal = EnhancedSignalEngine().analyze(df, 'BTC/USDT')

# Run backtest only
engine = SignalsBotEngine()
backtest_results = engine._run_backtest(df, 'BTC/USDT', signal)

# Print results
print(f"Win Rate: {backtest_results['win_rate']:.1%}")
print(f"Profit Factor: {backtest_results['profit_factor']:.2f}")
```

## Error Handling & Recovery

### Try-Catch Pattern

```python
from src.bot_engine import SignalsBotEngine
import logging

logger = logging.getLogger(__name__)

try:
    engine = SignalsBotEngine()
    analysis = engine.analyze_single_asset('BTC/USDT')
    
except Exception as e:
    logger.error(f"Analysis failed: {e}", exc_info=True)
    # Return neutral signal
    analysis = {
        'signal': 'NEUTRAL',
        'confidence': 0,
        'reasons': {'error': str(e)}
    }
```

### Data Validation

```python
from src.data_fetcher import DataFetcher

df = DataFetcher().fetch_data('BTC/USDT', 'crypto', '1h')

# Check if data is valid
if df is None or df.empty:
    print("No data available")
elif len(df) < 30:
    print("Insufficient historical data")
else:
    # Proceed with analysis
    pass
```

## Module Testing

### Unit Test Pattern

```python
import unittest
from src.technical_indicators import TechnicalIndicators
import pandas as pd
import numpy as np

class TestTechnicalIndicators(unittest.TestCase):
    
    def setUp(self):
        # Create sample data
        dates = pd.date_range('2024-01-01', periods=100)
        self.df = pd.DataFrame({
            'open': np.random.rand(100) * 100,
            'high': np.random.rand(100) * 100,
            'low': np.random.rand(100) * 100,
            'close': np.random.rand(100) * 100,
            'volume': np.random.rand(100) * 1000000,
        }, index=dates)
    
    def test_rsi_calculation(self):
        ti = TechnicalIndicators()
        result = ti.calculate_rsi(self.df['close'], 14)
        
        # RSI should be between 0 and 100
        self.assertTrue((result >= 0).all() or (result <= 100).all())
    
    def test_ema_calculation(self):
        ti = TechnicalIndicators()
        result = ti.calculate_ema(self.df['close'], 20)
        
        # EMA should be close to price
        self.assertTrue((abs(result - self.df['close']).max() < 100))

if __name__ == '__main__':
    unittest.main()
```

## Performance Optimization

### Caching Strategies

```python
from functools import lru_cache

class DataFetcher:
    @lru_cache(maxsize=32)
    def fetch_data(self, symbol, asset_type, timeframe, lookback_days):
        # Data is cached to avoid repeated API calls
        pass
```

### Vectorized Operations

```python
import numpy as np
import pandas as pd

# Instead of looping:
# for i in range(len(df)):
#     df.iloc[i]['rsi'] = calculate_rsi(...)

# Use vectorized operations:
df['rsi'] = calculate_rsi_vectorized(df['close'])
```

## Extensibility

### Adding New Indicators

```python
from src.advanced_indicators import AdvancedIndicators

class CustomIndicators(AdvancedIndicators):
    def calculate_my_indicator(self, df):
        """Add custom indicator calculation"""
        # Implementation
        return result
    
    def calculate_all_indicators(self, df, symbol):
        # Call parent
        df = super().calculate_all_indicators(df, symbol)
        # Add custom
        df['my_indicator'] = self.calculate_my_indicator(df)
        return df
```

### Adding New Signal Rules

```python
from src.enhanced_signal_engine import EnhancedSignalEngine

class CustomSignalEngine(EnhancedSignalEngine):
    def apply_strict_signal_rules(self, df):
        # Call parent
        signal_result = super().apply_strict_signal_rules(df)
        
        # Add custom rule
        if df['my_indicator'].iloc[-1] > threshold:
            signal_result['confidence'] *= 1.1  # Boost confidence
        
        return signal_result
```

---

This integration guide should help you understand how all components work together and how to extend or customize the bot.
