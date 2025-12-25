# Signals Bot - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Installation & Setup](#installation--setup)
4. [Quick Start](#quick-start)
5. [Configuration](#configuration)
6. [Signal Logic](#signal-logic)
7. [Risk Management](#risk-management)
8. [Backtesting](#backtesting)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)

---

## Overview

**Signals Bot** is a professional-grade trading signal generator using multi-confirmation strategy with strict risk management, advanced technical analysis, and historical backtesting.

### Core Philosophy
- **Capital Preservation > Profits**: Risk management is mandatory
- **Multi-Confirmation Required**: Signals require 4+ independent confirmations
- **Historical Validation**: Every signal backtested before generation
- **Transparent Analysis**: Clear reasoning for each signal

### Key Features
- 35+ technical indicators (basic + advanced)
- Multi-timeframe analysis (1H, 4H, 1D)
- Strict IF-THEN signal rules
- Mandatory 6-check risk validation
- Real-time backtesting before signals
- User-friendly interface (CLI & interactive menu)
- Flexible configuration management
- Comprehensive logging & reporting

---

## Features

### Technical Indicators
**Basic Indicators (20+):**
- Moving Averages: SMA, EMA, VWAP
- Momentum: RSI, MACD, Momentum, CCI
- Volatility: Bollinger Bands, ATR, NATR, Historical Volatility
- Trend: ADX, Supertrend, Linear Regression
- Volume: OBV, Volume MA, Accumulation/Distribution

**Advanced Indicators (15+):**
- Ichimoku Cloud (multi-timeframe trends)
- Keltner Channels (adaptive volatility)
- Supertrend (trend + volatility based)
- Williams %R (momentum overbought/oversold)
- Money Flow Index (volume-weighted momentum)
- Rate of Change (momentum confirmation)
- Aroon Indicator (trend direction & strength)
- Mass Index (volatility reversal)
- Chaikin Money Flow (volume sentiment)

### Signal Generation
```
IF trend is BULLISH
   AND momentum confirms (≥3/5 indicators)
   AND volume confirms (≥2/3 indicators)
   AND volatility acceptable (NATR 1-8%)
   AND risk rules pass (all 6 checks)
→ BUY Signal (with A+/B/C grading)
ELSE → NEUTRAL Signal
```

### Risk Management (Mandatory Enforcement)
All 6 checks must PASS for trade execution:
1. **Position Sizing**: ATR-based calculation (max 5% of account)
2. **Risk-Reward Validation**: Minimum 2:1 ratio
3. **Market Conditions**: Volume & trend strength checks
4. **Stop Loss Validity**: ≥1x ATR distance from entry
5. **Take Profit Validity**: Reasonable distance (<10x ATR)
6. **Drawdown Check**: Current DD < max allowed (10%)

### Backtesting Engine
- Simulates strategy on 30+ days historical data
- Calculates metrics: Win Rate, Profit Factor, Max Drawdown
- Validates minimum thresholds before signal approval
- Provides equity curve tracking
- Reports consecutive loss streaks

### Market Analysis
- **Trend Detection**: Multiple confirmation methods
- **Momentum Analysis**: 5-point confidence scoring
- **Volume Validation**: MA-based confirmation
- **Volatility Assessment**: Normal, High, Critical levels
- **Market Regime**: Identifies trending vs. ranging markets

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- pip (package manager)
- Virtual environment (recommended)

### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings
# (or use config.json for persistent settings)
```

### Step 4: Test Installation
```bash
python main.py --config
```

Expected output: Configuration settings displayed successfully

---

## Quick Start

### Run Complete Analysis
```bash
python main.py --run
```
- Analyzes all configured assets
- Shows detailed signals for each
- Displays summary table
- Includes backtest results

### Analyze Single Asset
```bash
python main.py --symbol BTC/USDT --type crypto
```

### Interactive Menu
```bash
python main.py
# OR
python main.py --interactive
```

Available options:
1. Analyze All Assets
2. Analyze Single Asset
3. View Configuration
4. Edit Configuration
5. Run Backtest
6. Exit

---

## Configuration

### Configuration Files
1. **config.json** - Primary persistent settings
2. **.env** - Environment variables (overrides)
3. **Default values** - Built-in fallbacks

### Key Settings

#### Account Settings
```json
{
    "account_balance": 10000,        # Starting capital
    "risk_percent": 1.0,             # Risk per trade (%)
    "max_drawdown": 10.0             # Max portfolio drawdown (%)
}
```

#### Trading Rules
```json
{
    "min_rr_ratio": 2.0,             # Min reward:risk ratio
    "min_adx": 20.0,                 # Min trend strength
    "confidence_threshold": 60.0     # Min signal confidence (%)
}
```

#### Backtest Settings
```json
{
    "backtest_lookback_days": 30,    # Historical data window
    "min_backtest_trades": 5,        # Min trades required
    "min_win_rate": 0.45,            # Min success rate
    "min_profit_factor": 1.2         # Min profit/loss ratio
}
```

#### Assets to Monitor
```json
{
    "assets": [
        {
            "symbol": "BTC/USDT",
            "type": "crypto",        # crypto, stock, forex
            "timeframe": "1h"        # 15m, 1h, 4h, 1d
        }
    ]
}
```

### Editing Configuration

**Via Interactive Menu:**
```bash
python main.py
# Select option 4: Edit Configuration
```

**Programmatically:**
```python
from src.bot_config import BotConfig

config = BotConfig()
config.set('risk_percent', 2.0)
config.set('min_adx', 25.0)
config.save_config()
```

**Via .env File:**
```bash
# Edit .env (automatically loaded on startup)
ACCOUNT_BALANCE=50000
RISK_PERCENT=2.0
MIN_ADX=25.0
```

---

## Signal Logic

### How Signals Are Generated

#### Step 1: Data Collection
- Fetch 30+ days OHLCV data
- Multi-source: Binance, Yahoo Finance, etc.

#### Step 2: Indicator Calculation
- Basic indicators (20+)
- Advanced indicators (15+)
- Market regime detection

#### Step 3: Trend Analysis (Weight: 35%)
6-point evaluation:
- EMA alignment (fast > slow)
- ADX > minimum threshold
- Supertrend direction
- Aroon indicator confirmation
- Price structure (higher highs/lows)
- Score: 0-6 points

#### Step 4: Momentum Analysis (Weight: 25%)
5-point evaluation:
- RSI in proper zone (not extreme)
- MACD histogram direction
- Rate of Change (ROC) positive
- Williams %R trending correctly
- Money Flow Index confirmation
- Score: 0-5 points

#### Step 5: Volume Confirmation (Weight: 20%)
3-point evaluation:
- Volume > 50% of MA
- OBV trending direction
- Chaikin Money Flow positive
- Score: 0-3 points

#### Step 6: Volatility Assessment (Weight: 20%)
Acceptable range:
- NATR between 1-8%
- Not in extreme expansion
- Not at multi-month lows

#### Step 7: Signal Generation
```
Trend Score: 5/6 (83%)  → Bullish ✓
Momentum:    4/5 (80%)  → Confirmed ✓
Volume:      2/3 (67%)  → Confirmed ✓
Volatility:  NORMAL     → Acceptable ✓

CONFIDENCE = (83% + 80% + 67% + normal) = 77%
SIGNAL = BUY (Quality: B)
```

#### Step 8: Risk Validation
All 6 mandatory checks:
1. ✓ Position size valid (1.5% account)
2. ✓ R:R ratio 2.5:1 (> 2.0 min)
3. ✓ Market conditions bullish (ADX=28)
4. ✓ SL distance 1.2x ATR (valid)
5. ✓ TP distance 2.4x ATR (valid)
6. ✓ Drawdown 3.2% (< 10% max)

**Result: APPROVED** → Signal allowed

#### Step 9: Backtest Validation
- Run 30-day historical backtest
- Check: Win Rate 52%, PF 1.45, Trades 12
- All metrics > minimum thresholds
- **Result: VALIDATED** → Signal confirmed

### Signal Quality Grades

**A+ (90%+ confidence)**
- All 6 trend confirmations
- 5/5 momentum indicators
- Strong volume
- Low volatility
- Perfect risk setup

**B (70-89% confidence)**
- 4-5 trend confirmations
- 3-4 momentum indicators
- Good volume
- Normal volatility
- Valid risk setup

**C (50-69% confidence)**
- 3 trend confirmations
- 2-3 momentum indicators
- Adequate volume
- Higher volatility
- Marginal risk setup

**NEUTRAL (< 50%)**
- Insufficient confirmations
- Risk rules failed
- Backtest failed
- Market regime unfavorable

---

## Risk Management

### The 6 Mandatory Checks

#### 1. Position Sizing
```python
Position Size = (Account × Risk %) / ATR
```
**Rules:**
- Max 5% of account per trade
- Based on ATR for volatility adjustment
- Prevents over-leverage

**Example:**
- Account: $10,000
- Risk: 1% = $100
- ATR: $50
- Position: $100 / $50 = 2 shares

#### 2. Risk-Reward Validation
```python
RR Ratio = (TP - Entry) / (Entry - SL)
```
**Rule:** RR Ratio ≥ 2.0 (minimum)

**Example:**
- Entry: $100
- SL: $96 (Risk: $4)
- TP: $108 (Reward: $8)
- RR = $8 / $4 = 2.0 ✓

#### 3. Market Conditions
```
Volume > 50% of 20-day MA  ✓
ADX > 20 (trend strength)  ✓
Price not at extremes      ✓
```

#### 4. Stop Loss Validity
```
SL Distance ≥ 1x ATR from Entry
```
Prevents premature stops in normal volatility

#### 5. Take Profit Validity
```
TP Distance < 10x ATR from Entry
```
Prevents unrealistic profit targets

#### 6. Drawdown Check
```
Current Drawdown < Max Allowed (10%)
```
Prevents trading when account is stressed

### Trade Rejection Scenarios

**Example 1: Failed R:R Ratio**
```
Entry: $100, SL: $98, TP: $102
RR = 2 / 2 = 1.0 < 2.0
❌ REJECTED - "R:R ratio below minimum"
```

**Example 2: Failed SL Validity**
```
ATR: $5, SL Distance: $3 < $5
❌ REJECTED - "Stop loss too close to entry"
```

**Example 3: High Drawdown**
```
Account Peak: $10,000
Current Value: $8,500
Drawdown: 15% > 10% max
❌ REJECTED - "Maximum drawdown exceeded"
```

---

## Backtesting

### What Gets Backtested

Every signal runs a 30-day backtest BEFORE generation:
1. Historical price data (30+ days)
2. Same indicators (real-time calculated)
3. Same entry/exit rules
4. Same position sizing
5. Slippage simulation

### Backtest Metrics

**Key Statistics:**
- **Total Trades**: Number of signals that would have triggered
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross wins / Gross losses
- **Max Drawdown**: Largest peak-to-trough decline
- **Consecutive Losses**: Longest losing streak

**Minimum Thresholds (Configurable):**
```json
{
    "min_backtest_trades": 5,      # Need 5+ trades to validate
    "min_win_rate": 0.45,           # Min 45% win rate
    "min_profit_factor": 1.2        # Min 1.2x profit factor
}
```

### Example Backtest Report
```
╔════════════════════════════════════════════╗
║         BACKTEST RESULTS (30-day)          ║
╠════════════════════════════════════════════╣
│ Total Trades:        12                    │
│ Winning Trades:      6                     │
│ Losing Trades:       6                     │
│ Win Rate:            50.0%                 │
├────────────────────────────────────────────┤
│ Total P&L:           $450.00               │
│ Return %:            4.5%                  │
│ Profit Factor:       1.35                  │
│ Max Drawdown:        8.2%                  │
│ Avg Hold Time:       12 bars (12 hours)   │
├────────────────────────────────────────────┤
│ Result: ✓ VALIDATED - Signal approved      │
└════════════════════════════════════════════┘
```

### Running Manual Backtest

```bash
# Via interactive menu
python main.py
# Select option 5: Run Backtest

# Or programmatically
from src.bot_engine import SignalsBotEngine

engine = SignalsBotEngine()
results = engine._run_backtest(df, 'BTC/USDT', signal_analysis)
print(results)
```

---

## Advanced Usage

### Programmatic API

#### Analyze Single Asset
```python
from src.bot_engine import SignalsBotEngine
from src.bot_config import BotConfig

config = BotConfig()
engine = SignalsBotEngine(config)

analysis = engine.analyze_single_asset(
    symbol='BTC/USDT',
    asset_type='crypto',
    timeframe='1h',
    backtest=True
)

print(f"Signal: {analysis['signal']}")
print(f"Confidence: {analysis['confidence']}%")
print(f"Setup: {analysis['setup']}")
```

#### Analyze Portfolio
```python
analyses = engine.analyze_portfolio(backtest=True)

for analysis in analyses:
    print(f"{analysis['symbol']}: {analysis['signal']}")
```

#### Access Risk Manager
```python
from src.enhanced_risk_manager import EnhancedRiskManager

risk_mgr = EnhancedRiskManager(account_balance=10000)

validation = risk_mgr.enforce_risk_rules(
    entry=100,
    stop_loss=96,
    take_profit=108,
    current_price=100,
    symbol='BTC/USDT',
    signal='BUY'
)

if validation['allowed']:
    print("Trade APPROVED")
else:
    print(f"Trade REJECTED: {validation['reasons']}")
```

#### Run Backtest
```python
from src.backtest_engine import BacktestEngine

backtest = BacktestEngine()

results = backtest.backtest_signal(
    df=df,
    symbol='BTC/USDT',
    signal='BUY',
    entry_price=100,
    stop_loss=96,
    take_profit=108
)

print(f"Win Rate: {results['win_rate']:.1%}")
print(f"Profit Factor: {results['profit_factor']:.2f}")
```

### Custom Configuration

```python
from src.bot_config import BotConfig

# Load config
config = BotConfig('my_config.json')

# Modify settings
config.set('risk_percent', 2.0)
config.set('min_adx', 25.0)

# Add custom asset
assets = config.get('assets')
assets.append({
    'symbol': 'EURUSD',
    'type': 'forex',
    'timeframe': '4h'
})
config.set('assets', assets)

# Save
config.save_config()

# Validate
is_valid, errors = config.validate_config()
if is_valid:
    print("Config is valid!")
else:
    print(f"Errors: {errors}")
```

### Event Logging

All signals logged to `signals_bot.log`:
```
2024-01-15 10:30:45 - signals_bot - INFO - Starting portfolio analysis...
2024-01-15 10:30:46 - signals_bot - INFO - Analyzing BTC/USDT (crypto, 1h)...
2024-01-15 10:30:48 - signals_bot - INFO - Step 2: Calculating technical indicators...
2024-01-15 10:30:49 - signals_bot - INFO - Step 5: Running backtest validation...
2024-01-15 10:30:52 - signals_bot - INFO - Analysis complete for BTC/USDT: BUY (77.5%)
```

---

## Troubleshooting

### Issue: "No data available for BTC/USDT"

**Cause:** Data source connection failed or asset not supported

**Solution:**
```bash
# Check internet connection
ping www.google.com

# Verify asset exists
python main.py --symbol BTC/USDT --type crypto

# Check data source
# Edit config.json:
# "crypto_exchange": "coinbase"  # Try alternative
```

### Issue: "Backtest failed or no results available"

**Cause:** Insufficient historical data or calculation error

**Solution:**
```bash
# Increase lookback period
# In .env or config.json:
BACKTEST_LOOKBACK_DAYS=60  # Instead of 30

# Check for indicator calculation errors in logs
# tail -20 signals_bot.log
```

### Issue: "Configuration validation errors"

**Cause:** Invalid config values

**Solution:**
```bash
# Check config validity
python main.py --config

# Look for errors in output

# Reset to defaults
rm config.json
# Will recreate with defaults

# Or fix manually in config.json
# Review required ranges in documentation
```

### Issue: "Maximum drawdown exceeded"

**Cause:** Account has lost too much capital

**Solution:**
```bash
# Option 1: Reduce position size
# config.json: "risk_percent": 0.5

# Option 2: Improve backtest parameters
# Ensure winning trades are larger than losing trades

# Option 3: Reset account in simulation
# Only proceed with real money when confident
```

### Issue: "Insufficient data for BTC/USDT"

**Cause:** Asset has < 30 days of data

**Solution:**
```bash
# Use symbol that has more history
# BTC/USDT has unlimited history
# Newer tokens may not

# Or use longer timeframe
# 1d instead of 1h = less bars needed
```

---

## Performance Considerations

### Optimization Tips

1. **Reduce Number of Assets**
   - Fewer assets = faster analysis
   - Default: 3 assets = ~30-60 seconds

2. **Disable Backtesting for Speed**
   ```bash
   python main.py --run --no-backtest
   ```
   - Backtesting adds 20-30% overhead
   - Use for monitoring only

3. **Increase Backtest Window**
   - More data = more accurate but slower
   - Minimum recommended: 30 days
   - Maximum practical: 90 days

4. **Use Longer Timeframes**
   - 1h analysis is ~6-7 seconds per asset
   - 4h analysis is ~2-3 seconds per asset

### Example Performance
```
3 assets, 1h timeframe, with backtest:
- BTC/USDT:  8 seconds
- ETH/USDT:  7 seconds
- AAPL:      6 seconds
- Total:     21 seconds
```

---

## Support & Resources

### Documentation Files
- `README.md` - Quick overview
- `INSTALLATION.md` - Setup guide
- `CONFIGURATION.md` - Detailed config options
- `API_REFERENCE.md` - Code documentation

### Example Scripts
- `examples/single_asset.py` - Analyze one asset
- `examples/portfolio_watch.py` - Monitor multiple assets
- `examples/custom_config.py` - Use custom settings
- `examples/backtest_only.py` - Run backtest only

### Log Files
- `signals_bot.log` - Complete analysis logs
- Rolling backups: `signals_bot.log.1`, `.log.2`, etc.

---

## Disclaimer

This bot is for **educational and informational purposes only**. It does not constitute financial advice. Trading involves risk of loss. Always:

1. **Test thoroughly** before using real money
2. **Start small** with minimal position sizes
3. **Monitor regularly** and adjust as needed
4. **Never risk more** than you can afford to lose
5. **Consult professionals** for financial advice

---

**Version**: 2.0 (Enhanced)
**Last Updated**: January 2024
**Status**: Production Ready ✓
