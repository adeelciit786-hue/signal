# Signals Bot - Quick Start Guide

## ✅ Setup Complete!

Your professional trading signal generation bot is ready to use. Here's what you have:

### 📦 What's Included

**Core Modules:**
- ✓ Data Fetcher (Crypto & Stocks)
- ✓ Technical Indicators (20+ indicators)
- ✓ Market Regime Detection
- ✓ Multi-Confirmation Strategy
- ✓ Risk Management Engine
- ✓ News & Sentiment Analysis
- ✓ Signal Generator & Formatter

**Virtual Environment:**
- ✓ Python 3.14 venv activated
- ✓ All dependencies installed

### 🚀 Running the Bot

```bash
# From the workspace directory
python main.py
```

The bot will:
1. Analyze BTC/USDT, ETH/USDT, and AAPL
2. Generate detailed signal reports
3. Output CSV summary
4. Provide risk notes and validation

### 📊 Current Output Example

```
ASSET: BTC/USDT
Signal: NEUTRAL | Confidence: 42% | Grade: No-Trade

Current Price:        $87534.88
Market Regime:        COMPRESSION (breakout awaiting)
Liquidity Level:      LOW (London session)

Indicator Alignment:
  Trend:     SLIGHTLY_BEARISH (50%)
  Momentum:  BEARISH (100%)
  Volume:    GOOD_CONFIRMATION (60%)
  Volatility: UNSUITABLE (20%)
```

### 🔧 Customization

**Change Assets:**
Edit `main.py`, line 29-35:
```python
ASSETS_TO_ANALYZE = [
    {'symbol': 'BTC/USDT', 'type': 'crypto'},
    {'symbol': 'ETH/USDT', 'type': 'crypto'},
    {'symbol': 'AAPL', 'type': 'stock'},
    # Add more here
]
```

**Modify Account Settings:**
Edit `main.py`, line 27:
```python
ACCOUNT_BALANCE = 10000  # Your account size
```

**Adjust Risk per Trade:**
In `src/risk_manager.py`:
```python
def __init__(self, account_balance: float = 10000, risk_per_trade: float = 0.01):
    # 0.01 = 1% per trade (change as needed)
```

### 📋 Analysis Includes

For each asset, you get:

1. **Signal & Confidence**
   - BUY / SELL / NEUTRAL
   - Confidence score (0-100%)
   - Grade: A+, B, or No-Trade

2. **Setup Details**
   - Entry price
   - Stop loss (ATR-based)
   - Take profit (risk-reward optimized)
   - Position size

3. **Technical Analysis**
   - All 20+ indicator values
   - Trend confirmation
   - Support/Resistance levels
   - Fibonacci retracements

4. **Market Context**
   - Regime classification
   - Liquidity assessment
   - Market session status
   - Suggested strategy

5. **Risk Assessment**
   - Risk-reward ratio
   - Liquidity check
   - ADX trend strength
   - Sentiment impact

6. **News & Sentiment**
   - Overall sentiment
   - High-impact events
   - Recommendation

### 🎯 Signal Interpretation

**A+ Signals (Confidence > 85%)**
- Strong institutional alignment
- Multiple indicators confirm
- Good risk-reward setup
- Ready to trade

**B Signals (Confidence 70-85%)**
- Acceptable setup
- Solid confirmation
- Consider position sizing down
- Monitor closely

**No-Trade (Confidence < 70% or NEUTRAL)**
- Insufficient confirmation
- Skip the trade
- Wait for better setup
- Protect capital

### 🛑 Risk Management Rules

1. **Never Risk More Than 1% Per Trade**
   - Automatically enforced by position sizing
   - $10,000 account = max $100 risk

2. **Minimum 2:1 Risk-Reward**
   - Only trades with RR ≥ 2.0 execute
   - Ensures profit potential > risk

3. **Market Regime Filtering**
   - Trend strategies only in trends (ADX > 20)
   - Mean-reversion only in ranges
   - Avoid choppy markets

4. **Liquidity Checks**
   - Skip trades in low liquidity sessions
   - Avoid wide spreads
   - Check volume vs average

5. **Sentiment Modulation**
   - Negative news reduces confidence
   - High-impact events = NEUTRAL signal
   - Positive sentiment adds confidence

### 📈 Market Regime Definitions

**STRONG_TREND** (ADX > 25)
- Use trend-following strategies
- Trade in direction of trend
- Highest probability setups

**MODERATE_TREND** (ADX 20-25)
- Trend strategies viable
- Requires confirmation
- Good risk-reward

**RANGE_BOUND** (Low ADX + stable)
- Use mean-reversion strategies
- Trade bounces off support/resistance
- Smaller position sizes

**COMPRESSION** (Low volatility)
- Await breakout
- Prepare for large move
- Don't trade yet

**CHOPPY** (Conflicting signals)
- Avoid trading
- Wait for clarity
- Capital preservation

**HIGH_VOLATILITY**
- Very risky
- Require 90%+ confidence
- Tight stops required

### 🔌 Adding Real API Keys

**For Live Data:**

1. Create `.env` file from `.env.example`:
```bash
cp config/.env.example config/.env
```

2. Add your API keys:
```
BINANCE_API_KEY=your_key_here
COINBASE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
```

3. The bot will use real data instead of defaults

### 📊 Understanding the CSV Output

```
Symbol | Signal | Confidence | Grade | Regime | Liquidity | Price | Stop | Profit | RR Ratio
BTC/USDT | NEUTRAL | 42% | No-Trade | COMPRESSION | LOW | $87534 | $0 | $0 | 0.00
ETH/USDT | NEUTRAL | 42% | No-Trade | COMPRESSION | LOW | $2926 | $0 | $0 | 0.00
AAPL | NEUTRAL | 36% | No-Trade | COMPRESSION | LOW | $274 | $0 | $0 | 0.00
```

### 🐛 Troubleshooting

**"Insufficient data" error:**
- Asset doesn't exist or has limited history
- Check symbol spelling (e.g., 'BTC/USDT', not 'BTCUSD')

**Low confidence signals:**
- Market conditions are choppy
- Waiting for better setup
- This is working as designed!

**Unicode errors:**
- Already fixed in latest version
- All output uses ASCII characters

**API connection errors:**
- Network issue or API rate limit
- Wait a moment and retry
- Use fewer assets to analyze

### 📚 Next Steps

1. **Paper Trade First**
   - Test signals on demo account
   - Track win rate
   - Validate your settings

2. **Backtest**
   - Add historical backtest module
   - Test strategy across past data
   - Optimize parameters

3. **Live Trading (When Ready)**
   - Start with 1-2 assets
   - Trade smallest position size
   - Monitor every trade
   - Scale up gradually

4. **Enhance**
   - Add more data sources
   - Create custom indicators
   - Implement notifications
   - Add trade logging

### 💡 Pro Tips

1. **Market Hours Matter**
   - Trade during peak liquidity
   - Avoid illiquid sessions
   - Multi-session overlap = best liquidity

2. **Confirmation is Key**
   - Wait for multiple indicators
   - Don't force trades
   - No trade > bad trade

3. **Risk Always**
   - 1% rule never violated
   - Protect capital first
   - Profits come naturally

4. **Review Regularly**
   - Analyze your winning trades
   - Learn from losses
   - Refine strategy

5. **Sentiment Matters**
   - Don't ignore news
   - High-impact events need care
   - Let technicals lead

### 📞 Support

For issues or questions:
- Check README.md for full documentation
- Review the code comments
- Test with demo/paper trading
- Start simple, scale up

---

**Happy Trading! Remember: Capital Preservation > Profits**

Trade smart, trade safe, trade consistently! 🚀
