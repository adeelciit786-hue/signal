# Signals Bot - Streamlit Deployment Guide

## Quick Start

### Local Development
```bash
# 1. Clone the repository
git clone https://github.com/adeelciit786-hue/signal.git
cd signal

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run locally with Streamlit
streamlit run streamlit_app.py
```

### Deploy to Streamlit Cloud
1. Push your code to GitHub (already done)
2. Go to [streamlit.io](https://streamlit.io)
3. Click "New app"
4. Connect your GitHub account
5. Select repository: `signal`
6. Select branch: `main`
7. Set main file path: `streamlit_app.py`
8. Click "Deploy"

## Features

✅ **Real-time Analysis**
- Multi-timeframe technical analysis
- Market regime detection
- Sentiment analysis

✅ **Multi-Confirmation Strategy**
- Trend confirmation (ADX)
- Momentum confirmation (RSI, MACD)
- Volume confirmation
- Volatility assessment

✅ **Risk Management**
- Automatic SL/TP calculation
- R:R ratio validation
- Risk per trade settings
- Position sizing

✅ **Backtesting**
- Historical performance validation
- Win rate calculation
- Drawdown analysis
- Profit factor

## Configuration

### Environment Variables (Optional)
Create a `.env` file in the root directory:

```
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.0
MIN_RR_RATIO=2.0
MIN_ADX=20.0
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

### Streamlit Secrets (Cloud Deployment)
In Streamlit Cloud dashboard:
1. Go to app settings
2. Click "Secrets"
3. Add your environment variables

## Troubleshooting

### ImportError on Streamlit
If you encounter import errors:
1. Ensure all modules are in the `src/` directory
2. Check that `src/__init__.py` exists
3. Verify class names match imports (MarketRegimeDetector, NewsAndSentiment)
4. Clear Streamlit cache: `streamlit cache clear`

### Module Not Found
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Connection Issues
- Check internet connectivity
- Verify API keys are valid
- Ensure firewall allows access to exchanges

## Project Structure

```
signal/
├── streamlit_app.py          # Main Streamlit entry point
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
├── config.json              # Default configuration
├── .streamlit/
│   └── config.toml          # Streamlit config
├── src/
│   ├── __init__.py
│   ├── bot_engine.py        # Main orchestrator
│   ├── bot_config.py        # Configuration manager
│   ├── bot_interface.py     # CLI interface
│   ├── data_fetcher.py      # Data retrieval
│   ├── technical_indicators.py  # Basic indicators
│   ├── advanced_indicators.py   # Advanced indicators
│   ├── market_regime.py     # Market regime detection
│   ├── news_sentiment.py    # Sentiment analysis
│   ├── enhanced_signal_engine.py # Signal generation
│   ├── enhanced_risk_manager.py  # Risk management
│   ├── backtest_engine.py   # Backtesting
│   ├── strategy_logic.py
│   ├── signal_generator.py
│   └── risk_manager.py
└── README.md
```

## Performance Tips

1. **Caching**: Streamlit caches data automatically
2. **Selective Asset Analysis**: Analyze one asset at a time for speed
3. **Timeframe Selection**: Use longer timeframes (1h, 4h) for faster analysis
4. **Backtest Lookback**: Adjust lookback days in configuration for speed

## Support

For issues or questions:
1. Check the GitHub repository: https://github.com/adeelciit786-hue/signal
2. Review error messages carefully
3. Check logs in `.streamlit/logs/`

## Disclaimer

⚠️ **This tool is for educational purposes only.** Always do your own research before trading. Past performance does not guarantee future results. Use at your own risk.
