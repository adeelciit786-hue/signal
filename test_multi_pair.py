#!/usr/bin/env python
"""Test signals across multiple pairs"""

import sys
sys.path.insert(0, 'src')
from bot_engine import BotOrchestrator

pairs = [
    ('BTC/USDT', 'crypto', '4h'),
    ('ETH/USDT', 'crypto', '1h'),
    ('AAPL', 'stock', '4h'),
]

print('=' * 70)
print('MULTI-PAIR SIGNAL ANALYSIS')
print('=' * 70)

bot = BotOrchestrator('config.json')

for symbol, asset_type, timeframe in pairs:
    print(f'\n{symbol} ({timeframe}):')
    print('-' * 70)
    
    try:
        result = bot.engine.analyze_single_asset(symbol, asset_type, timeframe, backtest=False)
        
        signal = result.get('signal', 'NEUTRAL')
        confidence = result.get('confidence', 0)
        setup = result.get('setup', {})
        confirmations = result.get('confirmations', {})
        
        # Display signal
        signal_icon = 'BUY' if signal == 'BUY' else 'SELL' if signal == 'SELL' else 'NEUTRAL'
        print(f'Signal: {signal} - {confidence:.1f}% confidence')
        
        # Display trend and momentum
        trend = confirmations.get('trend', 'N/A')
        trend_str = confirmations.get('trend_strength', '0%')
        momentum = confirmations.get('momentum_confirmed', False)
        momentum_str = confirmations.get('momentum_strength', '0%')
        volume = confirmations.get('volume_confirmed', False)
        
        print(f'   Trend: {trend} ({trend_str})')
        print(f'   Momentum: {"YES" if momentum else "NO"} ({momentum_str})')
        print(f'   Volume: {"Confirmed" if volume else "Low (but OK)"}')
        
        # Setup
        if signal != 'NEUTRAL':
            entry = setup.get('entry', 0)
            sl = setup.get('stop_loss', 0)
            tp = setup.get('take_profit', 0)
            rr = setup.get('rr_ratio', 0)
            print(f'   Setup: Entry ${entry:.4f} | SL ${sl:.4f} | TP ${tp:.4f} | R:R {rr:.2f}:1')
        
        # Risk
        risk = result.get('risk_validation', {})
        print(f'   Risk: {"APPROVED" if risk.get("allowed") else "REJECTED"}')
        
    except Exception as e:
        print(f'   ERROR: {e}')

print('\n' + '=' * 70)
print('Analysis complete')
