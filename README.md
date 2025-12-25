# Signals Bot 🤖

**Professional Trading Signal Generator** with Multi-Confirmation Strategy, Advanced Risk Management, and Historical Backtesting

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)]()

---

## ✨ Key Features

✅ **35+ Technical Indicators** - Basic & Advanced indicators for comprehensive analysis

✅ **Strict Multi-Confirmation** - Signals require 4 independent confirmations (Trend, Momentum, Volume, Volatility)

✅ **Mandatory Risk Management** - All trades validated against 6 risk checks before execution

✅ **Real-Time Backtesting** - Every signal backtested on 30+ days of historical data

✅ **User-Friendly Interface** - Interactive menu + CLI modes

✅ **Flexible Configuration** - JSON config + environment variables

✅ **Market Analysis** - Trend detection, regime identification, sentiment analysis

✅ **Professional Reporting** - Detailed analysis with confidence scores and recommendations

---

## 📊 Signal Generation Logic

```
IF trend is BULLISH ✓
   AND momentum confirms (≥3/5 indicators) ✓
   AND volume confirms (≥2/3 indicators) ✓
   AND volatility acceptable ✓
   AND risk rules pass (all 6 checks) ✓
   AND backtest validates ✓
→ BUY Signal (Grade: A+/B/C)
ELSE → NEUTRAL
```

---

## 🛡️ Risk Management

### 6 Mandatory Validation Checks
1. **Position Sizing** - ATR-based calculation
2. **Risk-Reward Ratio** - Minimum 2:1 required
3. **Market Conditions** - Volume & ADX confirmation
4. **Stop Loss Validity** - ≥1x ATR distance
5. **Take Profit Validity** - Realistic distance
6. **Drawdown Check** - Current < 10% max

**Trade is REJECTED if ANY check fails** 🔴

---

## 🚀 Quick Start

### Installation
```bash
# Clone repository
git clone <repo>
cd Signals_Bot

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run bot
python main.py
```

### Usage Examples

**Run Complete Analysis**
```bash
python main.py --run
```

**Analyze Single Asset**
```bash
python main.py --symbol BTC/USDT --type crypto
```

**Interactive Menu**
```bash
python main.py --interactive
```

**View Configuration**
```bash
python main.py --config
```
- **Moderate Trend** (ADX 20-25)
- **Range-Bound** (Low ADX + stable volatility)
- **Choppy** (Conflicting signals)
- **High-Volatility / Panic**
- **Low-Volatility Compression** (Breakout setup)

**Rules:**
- Trend strategies ONLY in trending regimes
- Mean-reversion ONLY in ranging markets
- Avoid signals during panic unless fully confirmed

### 🧠 Strategy Logic (Multi-Confirmation)
Weighted scoring model evaluates:
1. **Trend** (35%) - EMA alignment, price structure
2. **Momentum** (25%) - RSI, MACD, Stochastic convergence
3. **Volume** (20%) - Volume confirmation, OBV trend
4. **Volatility** (20%) - ATR suitability for regime

**Only issues BUY or SELL when multiple independent confirmations align**
- Conflicting signals → **NEUTRAL**

### 📰 News & Sentiment (MODIFIER ONLY)
- Keyword-based sentiment analysis
- High-impact event detection (CPI, FOMC, NFP, Earnings, etc.)
- **Sentiment never overrides technicals** - only adjusts confidence
- Negative sentiment reduces confidence by up to 30%

### 🛑 Risk Management (NON-NEGOTIABLE)
- **Risk per trade ≤ 1%** of account
- **ATR-based dynamic stop-loss** (2x ATR)
- **Minimum 1:2 risk-reward ratio**
- **NO trades if:**
  - ADX < 20 (choppy market)
  - Low volume
  - Wide spreads
  - Illiquid session hours

**Capital Protection Rules:**
- Reduce risk after consecutive losses
- Pause trading after max drawdown threshold
- Avoid correlated asset overexposure
- Default to NO TRADE on uncertainty

### 🏆 Signal Quality Grading
Each signal is classified:
- **A+ Setup** → Strong institutional alignment (confidence > 85%)
- **B Setup** → Acceptable but cautious (confidence 70-85%)
- **No-Trade Zone** → Protect capital

### 📤 Output Format
For every asset analyzed:
```
BUY / SELL / NEUTRAL
Confidence score (0–100)
Signal quality (A+, B, No-Trade)
Indicator alignment summary
Key support & resistance
News sentiment impact
Risk notes (why safe or avoided)
```

## 🎯 Core Philosophy
1. **Capital preservation first**
2. **Fewer trades, higher accuracy**
3. **Confirmation over prediction**
4. **Discipline over emotion**
5. **Survival over profit**
6. **Always choose NO TRADE if conditions are unclear**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (already activated)

### Installation
```bash
pip install pandas numpy ccxt requests yfinance python-dotenv
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your API keys (optional for free data)
3. Edit asset list in `main.py`

### Running the Bot
```bash
python main.py
```

## 📂 Project Structure
```
Signals Bot/
├── src/
│   ├── __init__.py
│   ├── data_fetcher.py          # Data retrieval from multiple sources
│   ├── technical_indicators.py   # All indicator calculations
│   ├── market_regime.py          # Regime detection & classification
│   ├── strategy_logic.py         # Multi-confirmation strategy
│   ├── risk_manager.py           # Position sizing & risk control
│   ├── news_sentiment.py         # Sentiment analysis
│   └── signal_generator.py       # Main signal orchestrator
├── config/
│   └── .env.example             # Configuration template
├── data/                        # Cache historical data
├── main.py                      # Entry point
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## 📊 Example Analysis Output

```
======================================================================
TRADING SIGNAL ANALYSIS
======================================================================

📊 ASSET: BTC/USDT
⏰ TIME: 2025-12-25T14:30:00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Signal: BUY | Confidence: 88% | Grade: A+

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 SETUP DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Current Price:        $42,500.00
Entry Price:          $42,500.00
Stop Loss:            $41,200.00
Take Profit:          $46,800.00
Risk-Reward Ratio:    3.25:1
Position Size:        0.2350 units

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 INDICATOR ALIGNMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Trend                BULLISH (confidence: 85%)
Momentum             BULLISH (confidence: 78%)
Volume               STRONG_CONFIRMATION (confidence: 82%)
Volatility           SUITABLE (confidence: 75%)

...
```

## 🔐 Risk Considerations

This bot is designed to **generate signals only, not execute trades automatically**. Always:
- Use a demo/paper trading account first
- Start with small position sizes
- Monitor trades actively
- Never risk more than 1% per trade
- Use the provided risk management rules
- Validate signals independently

## 📝 Trade Filtering Rules

A signal is only executed if:
1. ✓ Multi-timeframe alignment (no conflicts)
2. ✓ Market regime supports strategy type
3. ✓ ADX > 20 (or valid for regime)
4. ✓ Volume > 50% of MA
5. ✓ Risk-reward ratio ≥ 2:1
6. ✓ Adequate liquidity for session
7. ✓ No high-impact news uncertainty

Otherwise → **NEUTRAL / NO TRADE**

## 🛠️ Extending the Bot

### Add Custom Indicators
Edit `src/technical_indicators.py`:
```python
@staticmethod
def calculate_your_indicator(data):
    # Implementation
    return result
```

### Add New Data Sources
Edit `src/data_fetcher.py`:
```python
def fetch_from_custom_source(self, symbol):
    # Implementation
    return dataframe
```

### Modify Risk Rules
Edit `src/risk_manager.py`:
```python
def custom_risk_check(self):
    # Your rules
    return is_valid, message
```

## 📚 References

### Technical Indicators
- RSI: Wilder's RSI formula
- MACD: 12-26-9 moving averages
- Bollinger Bands: 2 standard deviations
- ATR: Wilder's smoothing method
- ADX: Directional movement system

### Market Regimes
- Trend classification based on ADX (Wilder's DMI)
- Volatility assessment via ATR and Bollinger Bands
- Structure analysis using price action

## 🤝 Contributing

Feel free to:
- Add new technical indicators
- Improve signal accuracy
- Optimize risk management
- Add new data sources

## ⚖️ Disclaimer

**This bot is for educational and analytical purposes only.** It is not financial advice. Always:
- Trade responsibly
- Understand your risk tolerance
- Never invest money you can't afford to lose
- Consult with financial professionals
- Backtest extensively before live trading

## 📄 License

MIT License - See LICENSE file

---

**Made with ❤️ for traders who value discipline and system-based trading**

Happy trading! 🚀📈
