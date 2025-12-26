#!/usr/bin/env python
"""Test enhanced signal engine"""

import sys
sys.path.insert(0, 'src')
from bot_engine import BotOrchestrator

print('Testing Enhanced Signal Engine...')
print('=' * 60)

try:
    bot = BotOrchestrator('config.json')
    result = bot.engine.analyze_single_asset('BTC/USDT', 'crypto', '4h', backtest=False)

    signal = result.get('signal', 'NEUTRAL')
    confidence = result.get('confidence', 0)
    setup = result.get('setup', {})
    confirmations = result.get('confirmations', {})

    print(f'Signal: {signal}')
    print(f'Confidence: {confidence:.2f}%')
    print(f'Quality: {result.get("quality", "N/A")}')
    print()
    print('SETUP:')
    print(f'  Entry: ${setup.get("entry", 0):.2f}')
    print(f'  Stop Loss: ${setup.get("stop_loss", 0):.2f}')
    print(f'  Take Profit: ${setup.get("take_profit", 0):.2f}')
    print(f'  R:R Ratio: {setup.get("rr_ratio", 0):.2f}:1')
    print()
    print('CONFIRMATIONS:')
    print(f'  Trend: {confirmations.get("trend", "N/A")}')
    print(f'  Trend Strength: {confirmations.get("trend_strength", "N/A")}')
    print(f'  Momentum: {"YES" if confirmations.get("momentum_confirmed") else "NO"}')
    print(f'  Volume: {"YES" if confirmations.get("volume_confirmed") else "NO"}')
    print(f'  Volatility: {confirmations.get("volatility_reason", "N/A")}')
    print()
    print('RISK VALIDATION:')
    risk = result.get('risk_validation', {})
    print(f'  Allowed: {"YES" if risk.get("allowed") else "NO"}')

    print()
    print('=' * 60)
    print('✓ Enhanced signal engine working!')
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
