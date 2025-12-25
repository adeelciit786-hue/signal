# Signals Bot - Quick Reference Guide

## 🚀 Getting Started (2 Minutes)

### Installation
```bash
cd "Signals Bot"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### First Run
```bash
python main.py --run
```

---

## 📊 Command Reference

### Analyze Portfolio (All Assets)
```bash
python main.py --run
```
- Analyzes all configured assets
- Shows detailed signals
- Includes backtest results
- ~30 seconds total

### Analyze Single Asset
```bash
python main.py --symbol BTC/USDT --type crypto
```
- Options: `--type crypto|stock|forex`
- ~8 seconds per asset

### Interactive Menu
```bash
python main.py
```
Or explicitly:
```bash
python main.py --interactive
```

Menu options:
1. Analyze All Assets
2. Analyze Single Asset
3. View Configuration
4. Edit Configuration
5. Run Backtest
6. Exit

### View Configuration
```bash
python main.py --config
```

### Fast Analysis (No Backtest)
```bash
python main.py --run --no-backtest
```
~2-3 seconds instead of 10+ seconds

---

## ⚙️ Configuration Quick Reference

### Edit config.json
Key settings:
```json
{
    "account_balance": 10000,           # Starting capital
    "risk_percent": 1.0,                # Risk per trade (%)
    "min_rr_ratio": 2.0,                # Min reward:risk ratio
    "min_adx": 20.0,                    # Min trend strength
    "backtest_lookback_days": 30        # Backtest window (days)
}
```

### Edit .env
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Then edit values:
```
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.0
MIN_RR_RATIO=2.0
```

### Via Interactive Menu
```bash
python main.py
# Select: 4 - Edit Configuration
# Enter key and value
```

---

## 📈 Signal Interpretation

### Signal Types
| Signal | Meaning | Confidence | Action |
|--------|---------|-----------|--------|
| 🟢 BUY | Buy signal | 50-100% | Consider entry |
| 🔴 SELL | Sell signal | 50-100% | Consider exit |
| 🟡 NEUTRAL | No clear signal | <50% | Wait for confirmation |

### Quality Grades
| Grade | Confidence | Risk | Action |
|-------|-----------|------|--------|
| **A+** | 90%+ | Low | Strong signal |
| **B** | 70-89% | Medium | Good signal |
| **C** | 50-69% | Higher | Weak signal |
| **NEUTRAL** | <50% | N/A | Wait |

### Confidence Interpretation
- **90%+** = Very strong, all confirmations aligned
- **75-89%** = Strong, most confirmations good
- **60-74%** = Moderate, several confirmations
- **45-59%** = Weak, minimal confirmations
- **<45%** = No signal (NEUTRAL)

---

## 🛡️ Risk Management Checks

### 6 Mandatory Checks
Each trade validated against:

1. **Position Size** ✓
   - Max: 5% of account
   - Based on ATR
   
2. **Risk-Reward Ratio** ✓
   - Min: 2:1
   - Example: Risk $100 to make $200
   
3. **Market Conditions** ✓
   - Volume: > 50% of 20-day MA
   - Trend: ADX > 20
   
4. **Stop Loss** ✓
   - Distance: ≥ 1x ATR
   - Prevents premature exit
   
5. **Take Profit** ✓
   - Distance: < 10x ATR
   - Realistic targets only
   
6. **Drawdown** ✓
   - Current: < 10% of account
   - Prevents over-trading

**IF ANY check fails → Trade REJECTED** 🔴

---

## 📊 Signal Analysis Breakdown

### What's Shown in Signal Report

```
╔════════════════════════════════════════╗
│ Signal: BUY                           │
│ Confidence: 77.5%                     │
│ Quality: B                            │
├────────────────────────────────────────┤
│ CONFIRMATIONS:                        │
│ • Trend: BULLISH                     │
│ • Momentum: ✓ YES (3/5)              │
│ • Volume: ✓ YES (2/3)                │
│ • Volatility: ✓ OK                   │
├────────────────────────────────────────┤
│ Setup:                                │
│ Entry: $100   SL: $96   TP: $108    │
│ RR Ratio: 2.0:1                      │
├────────────────────────────────────────┤
│ Backtest: Win Rate 58% | PF 1.65    │
└────────────────────────────────────────┘
```

### Key Metrics Explained

**Confidence (0-100%)**
- How sure the bot is about the signal
- Based on weighted indicator agreement
- Weight: Trend 35%, Momentum 25%, Volume 20%, Volatility 20%

**Quality Grade (A+/B/C)**
- Overall signal strength
- A+ = All indicators strongly agree
- B = Most indicators agree
- C = Minimal indicators agree

**RR Ratio (e.g., 2.0:1)**
- Reward divided by Risk
- Higher is better
- Min required: 2.0:1

**Win Rate**
- Percentage of winning trades in backtest
- 50% = Break even (before fees)
- 60%+ = Profitable

**Profit Factor**
- Total wins / Total losses
- 1.0 = Break even
- 1.5+ = Good
- 2.0+ = Excellent

---

## 🔧 Troubleshooting

### No Signal Generated
**Check:**
1. Internet connection (API call failed)
2. Asset exists (typo in symbol)
3. Sufficient data available
4. All risk checks passing

**Solution:**
```bash
# Verify data
python main.py --symbol BTC/USDT

# Check config
python main.py --config

# View logs
tail -20 signals_bot.log
```

### "Insufficient Data for BTC/USDT"
**Cause:** Asset has < 30 days historical data

**Solution:**
- Use asset with longer history
- Use longer timeframe (1d instead of 1h)
- Increase `backtest_lookback_days`

### Trade Rejected by Risk Manager
**Check reasons:**
```
✗ Position size exceeds 5% of account
✗ R:R ratio 1.5:1 < 2.0 minimum
✗ Stop loss too close to entry
```

**Solutions:**
- Increase account size
- Increase take profit target
- Increase stop loss distance

### Performance Too Slow
**Speed up:**
```bash
# Disable backtesting
python main.py --run --no-backtest

# Reduce assets
# Edit config.json, remove assets

# Use longer timeframe
# Edit config.json: "timeframe": "4h"
```

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `config.json` | Main configuration |
| `.env` | Environment overrides |
| `signals_bot.log` | Analysis logs |
| `README.md` | Quick start |
| `DOCUMENTATION.md` | Complete guide |
| `INTEGRATION_GUIDE.md` | Architecture |
| `ENHANCEMENT_SUMMARY.md` | What's new |

---

## 💡 Common Workflows

### Workflow 1: Daily Monitoring
```bash
# Every morning, check all assets
python main.py --run

# Takes ~30 seconds
# Shows all signals for the day
```

### Workflow 2: Single Asset Deep Dive
```bash
# Analyze one asset with details
python main.py --symbol BTC/USDT

# Shows detailed confirmation breakdown
# Shows backtest results
```

### Workflow 3: Configuration Adjustment
```bash
# Interactive menu
python main.py

# Option 4: Edit Configuration
# Change risk_percent, min_adx, etc.
```

### Workflow 4: Backtest Validation
```bash
# Interactive menu
python main.py

# Option 5: Run Backtest
# Validate strategy historically
```

---

## 📊 Indicator Summary

### Trend Indicators (4+)
- EMA, SMA, Supertrend, ADX, Linear Regression

### Momentum Indicators (8+)
- RSI, MACD, ROC, Williams %R, MFI, Stochastic, CCI

### Volume Indicators (6+)
- OBV, Volume MA, VWAP, Accumulation/Distribution, CMF

### Volatility Indicators (6+)
- Bollinger Bands, ATR, NATR, Keltner Channels, Ichimoku

### Support/Resistance (2+)
- Fibonacci, Price Action

---

## 🚨 Critical Rules

1. **All 6 risk checks must pass** before any trade
2. **Backtest must validate** before signal approval
3. **R:R ratio must be ≥ 2:1** (minimum reward)
4. **Stop loss must be ≥ 1x ATR** (proper distance)
5. **Account drawdown must be < 10%** (capital protection)

---

## 📞 Quick Help

### Check System Status
```bash
python main.py --config
```

### View Latest Signals
```bash
python main.py --run
```

### Analyze Specific Asset
```bash
python main.py --symbol EURUSD --type forex
```

### View Recent Logs
```bash
tail -50 signals_bot.log
```

---

## ⏱️ Expected Timing

| Task | Time |
|------|------|
| Single asset analysis (with backtest) | 8-10 sec |
| Single asset analysis (no backtest) | 2-3 sec |
| 3 assets (with backtest) | 30 sec |
| 3 assets (no backtest) | 6-9 sec |
| Configuration display | <1 sec |
| Interactive menu load | <1 sec |

---

## 🎓 Learning Path

1. **Start Here:** [README.md](README.md) (5 min read)
2. **Quick Setup:** Run `python main.py --run` (see examples)
3. **Understand Signals:** Read signal interpretation section above
4. **Learn Configuration:** Edit `config.json` with menu option 4
5. **Deep Dive:** Read [DOCUMENTATION.md](DOCUMENTATION.md) (30 min)
6. **Advanced:** Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)

---

## ⚖️ Disclaimer

**Educational Purpose Only**

This tool is for learning and analysis purposes. Trading involves risk. Always:
- Test thoroughly
- Start with small sizes
- Monitor actively
- Consult professionals

---

## 🎯 Tips for Best Results

1. **Use Appropriate Timeframes**
   - 1h: Scalping/day trading
   - 4h: Swing trading
   - 1d: Position trading

2. **Monitor Backtest Results**
   - Win rate should be > 45%
   - Profit factor should be > 1.2x
   - Max drawdown < 20%

3. **Adjust for Market Conditions**
   - Increase min_adx in choppy markets
   - Increase risk_percent in good trades
   - Decrease during high drawdowns

4. **Keep Logs**
   - Review `signals_bot.log` regularly
   - Track signal accuracy
   - Adjust parameters as needed

5. **Diversify**
   - Monitor multiple assets
   - Use different timeframes
   - Vary position sizes

---

## 📞 Support Resources

- **Logs:** `signals_bot.log` (all analysis recorded)
- **Config:** `config.json` (all settings documented)
- **Docs:** `DOCUMENTATION.md` (comprehensive guide)
- **Architecture:** `INTEGRATION_GUIDE.md` (how components work)

---

**Last Updated:** January 2024
**Version:** 2.0
**Status:** Production Ready ✅
