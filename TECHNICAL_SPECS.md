# Signals Bot - Technical Specifications

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Signal Generator                         │
│                  (Orchestrates Everything)                   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌────────────┐      ┌──────────┐
    │   Data  │          │ Technical  │      │  Market  │
    │ Fetcher │          │ Indicators │      │  Regime  │
    └─────────┘          └────────────┘      └──────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Strategy Logic  │
                    │  (Multi-Confirm) │
                    └──────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌──────────┐        ┌──────────┐
    │   Risk  │          │   News   │        │  Signal  │
    │ Manager │          │Sentiment │        │Formatter │
    └─────────┘          └──────────┘        └──────────┘
```

## 📊 Data Flow

1. **DataFetcher** → Pulls OHLCV from Binance/Yahoo
2. **TechnicalIndicators** → Calculates 20+ indicators
3. **MarketRegime** → Classifies market condition
4. **StrategyLogic** → Evaluates multi-confirmations
5. **NewsAndSentiment** → Pulls and analyzes sentiment
6. **RiskManager** → Validates risk parameters
7. **SignalGenerator** → Combines all signals
8. **OutputFormatter** → Formats for display

## 🔢 Indicator Specifications

### Moving Averages
- **SMA**: 10, 20, 50, 100, 200 periods
- **EMA**: 10, 20, 50 periods (faster response)

### Momentum Indicators
- **RSI**: 14-period, overbought > 70, oversold < 30
- **Stochastic RSI**: Applies stochastic to RSI
- **MACD**: 12-26-9 (fast-slow-signal)
- **Histogram**: Difference between MACD and signal line

### Volatility Indicators
- **Bollinger Bands**: 20-period SMA ± 2 std dev
- **ATR**: 14-period, used for dynamic stops
- **ADX**: 14-period, trend strength (0-100)
  - < 20: Weak/Choppy
  - 20-25: Moderate
  - > 25: Strong

### Volume Indicators
- **OBV**: On-Balance Volume (cumulative)
- **VWAP**: Volume-Weighted Average Price
- **Volume MA**: 20-period volume average

### Support & Resistance
- **Fibonacci Levels**: 23.6%, 38.2%, 50%, 61.8%
- **Dynamic S/R**: Last 20-50 candle highs/lows
- **Price Channels**: Trendlines and bands

## 🎯 Signal Scoring

### Weight Distribution (Total = 100%)
| Component | Weight | Calculation |
|-----------|--------|-------------|
| Trend | 35% | EMA alignment, price structure |
| Momentum | 25% | RSI, MACD, Stochastic convergence |
| Volume | 20% | Volume MA ratio, OBV trend |
| Volatility | 20% | ATR suitability for regime |

### Confidence Calculation
```
Base Confidence = (Trend_Score × 0.35) + 
                  (Momentum_Score × 0.25) + 
                  (Volume_Score × 0.20) + 
                  (Volatility_Score × 0.20)

Adjusted = Base - (Losses × 5%) + (Sentiment × 15%)
Final = MIN(100, MAX(0, Adjusted))
```

### Signal Grades
| Grade | Confidence | Action |
|-------|-----------|--------|
| A+ | > 85% | Execute (strong setup) |
| B | 70-85% | Execute (cautious) |
| No-Trade | < 70% | Skip (wait for better) |

## 🌍 Market Regime Rules

### Regime Classification
```
If ADX > 25 AND volatility normal:
  → STRONG_TREND
  
Else if ADX 20-25:
  → MODERATE_TREND
  
Else if ADX < 20 AND BB_width < 3%:
  → COMPRESSION (breakout waiting)
  
Else if volatility > 5%:
  → HIGH_VOLATILITY (avoid)
  
Else if 1.5% < volatility < 5% AND ADX < 20:
  → RANGE_BOUND
  
Else:
  → CHOPPY
```

### Regime-Strategy Matching
| Regime | Strategy | Min Confidence |
|--------|----------|---|
| Strong Trend | Trend Following | 70% |
| Moderate Trend | Trend Following | 75% |
| Range Bound | Mean Reversion | 75% |
| Compression | Breakout Waiting | 80% |
| Choppy | NO TRADE | 85% |
| High Volatility | Caution | 90% |

## ⏱️ Multi-Timeframe Rules

**Higher Timeframe (4H):** Defines PRIMARY trend
**Lower Timeframe (1H):** Allows entry ONLY in primary direction

### Timeframe Conflict Resolution
```
If 4H Bullish AND 1H Bullish:
  → Strong BUY signal
  
Else if 4H Bullish AND 1H Bearish:
  → NEUTRAL (conflict)
  
Else if 4H Bearish AND 1H Bearish:
  → Strong SELL signal
  
Else if 4H Neutral OR 1H Neutral:
  → Evaluate on lower timeframe only
```

## 🛑 Risk Management Rules

### Position Sizing
```
Risk Amount = Account Balance × 1%
Position Size = Risk Amount / (Entry - Stop Loss)
```

### Stop Loss Placement (ATR-based)
```
BUY Stop Loss = Entry Price - (ATR × 2)
SELL Stop Loss = Entry Price + (ATR × 2)
```

### Risk-Reward Validation
```
Reward = |Take Profit - Entry|
Risk = |Entry - Stop Loss|
Ratio = Reward / Risk

Valid if Ratio >= 2.0 (min 1:2)
```

### Trading Filters
Trade only if ALL of these are true:
1. ✓ Timeframe alignment (no conflicts)
2. ✓ Market regime supports strategy
3. ✓ ADX > 20 (or valid for regime)
4. ✓ Volume > 50% of MA (recent vs average)
5. ✓ Risk-Reward ≥ 2:1
6. ✓ Adequate liquidity for session
7. ✓ No high-impact news uncertainty

If ANY filter fails → NEUTRAL signal

### Drawdown Management
- Max Drawdown Threshold: 10% of account
- Reduce position size after consecutive losses:
  - 1 loss: 75% position size
  - 2 losses: 50% position size
  - 3+ losses: PAUSE trading

## 📰 News & Sentiment Rules

### Sentiment Adjustment
```
Positive Sentiment:
  Confidence += (Strength × 15%) up to +15%
  
Negative Sentiment:
  Confidence -= (Strength × 20%) up to -20%
  
Neutral:
  No adjustment
```

### High-Impact Events
If detected: NEUTRAL signal (avoid trading)
- CPI (inflation)
- FOMC (interest rates)
- NFP (employment)
- Earnings
- GDP releases
- Central Bank decisions

### News Override Rules
✗ News NEVER overrides technicals
✓ Negative sentiment REDUCES confidence
✓ High-impact events TRIGGER NEUTRAL

## 💾 Data Specifications

### OHLCV Data Required
- Open, High, Low, Close, Volume
- Minimum 100 candles for analysis
- Preferably 200+ for full analysis

### Data Sources
| Source | Asset Type | Timeframes |
|--------|-----------|-----------|
| Binance API | Crypto | 1m-1M |
| Yahoo Finance | Stocks/Forex | Daily-Monthly |
| ccxt library | Crypto | Multiple exchanges |
| yfinance library | Stocks | All intervals |

### Timeframes Used
- **1H**: Detailed entry analysis
- **4H**: Primary trend confirmation
- **1D**: Longer-term structure

## 🔐 Error Handling

### Graceful Degradation
- Missing data → Skip asset
- API failure → Use cached data
- Invalid signals → Default to NEUTRAL
- Calc errors → Return NEUTRAL

### Validation Checks
- Data > 100 candles minimum
- No NaN values in indicators
- Price within reasonable range
- Volume > 0

## 📈 Output Specifications

### Signal Report Includes
1. Symbol and Timestamp
2. Signal (BUY/SELL/NEUTRAL)
3. Confidence (0-100%)
4. Grade (A+/B/No-Trade)
5. Current Price
6. Entry, Stop Loss, Take Profit
7. Position Size
8. Technical Indicator Values
9. Market Regime
10. Liquidity Assessment
11. Key Support/Resistance
12. Fibonacci Levels
13. Sentiment Analysis
14. Risk Notes
15. Validation Messages

### CSV Output Format
```
Symbol | Signal | Confidence | Grade | Regime | Liquidity | Price | Stop | Profit | RR
BTC/USDT | BUY | 88% | A+ | STRONG_TREND | HIGH | $42500 | $41200 | $46800 | 3.25
```

## ⚡ Performance Specifications

### Calculation Time
- Single asset analysis: ~2-3 seconds
- 3 assets: ~6-9 seconds
- 10 assets: ~20-30 seconds

### Memory Usage
- Base: ~50 MB
- Per asset: ~10-15 MB
- 10 assets: ~150 MB

### Data Refresh
- Default: On-demand
- Update frequency: Configurable
- History: 1-2 years maintained

## 🔄 Update Cycle

```
Every analysis:
1. Fetch latest OHLCV (5-30 seconds)
2. Calculate indicators (1-2 seconds)
3. Analyze regime (1 second)
4. Generate signals (1-2 seconds)
5. Format output (0.5 seconds)

Total: ~10 seconds per asset
```

## 📋 Configuration Options

### Adjustable Parameters
- `ACCOUNT_BALANCE`: Starting capital
- `RISK_PER_TRADE`: % risk per trade (default 1%)
- `MIN_ADX_THRESHOLD`: ADX minimum (default 20)
- `MIN_RISK_REWARD`: RR ratio minimum (default 2.0)
- `MAX_DRAWDOWN`: Max drawdown % (default 10%)
- `MAX_LOSSES`: Consecutive losses before pause (default 3)

### Command Line Overrides
```bash
python main.py --symbol BTC/USDT
python main.py --account 50000
python main.py --risk 0.02
```

## 🔌 Extension Points

### Add Custom Indicators
File: `src/technical_indicators.py`
```python
@staticmethod
def calculate_custom_indicator(data):
    # Your calculation
    return result
```

### Add Data Source
File: `src/data_fetcher.py`
```python
def fetch_from_custom_api(self, symbol):
    # Your API call
    return dataframe
```

### Modify Risk Rules
File: `src/risk_manager.py`
```python
def custom_filter(self):
    # Your validation
    return is_valid, message
```

### Add Strategy
File: `src/strategy_logic.py`
```python
@staticmethod
def custom_strategy(df):
    # Your signal logic
    return signal_direction, confidence
```

## 🧪 Testing Specifications

### Unit Tests
- Indicator calculations
- Risk validations
- Signal generation
- Data parsing

### Integration Tests
- Full pipeline
- Multiple assets
- Error scenarios
- Edge cases

### Backtesting
- Historical data analysis
- Win rate tracking
- Risk metrics
- Performance stats

## 📚 Dependencies

### Core Libraries
```
pandas==2.3.3        # Data manipulation
numpy==2.4.0         # Numerical computing
ccxt==4.5.29         # Crypto API
requests==2.32.5     # HTTP requests
yfinance==1.0        # Stock data
python-dotenv==1.2.1 # Environment vars
```

### Version Requirements
- Python: 3.9+
- pandas: 1.3+
- numpy: 1.19+

---

**Last Updated:** December 25, 2025
**Version:** 1.0.0
**Status:** Production Ready
