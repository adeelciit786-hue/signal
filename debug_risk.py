#!/usr/bin/env python
"""Debug risk validation"""

import sys
sys.path.insert(0, 'src')
from bot_engine import BotOrchestrator
import json

print('Debugging Risk Validation...')
print('=' * 70)

try:
    bot = BotOrchestrator('config.json')
    result = bot.engine.analyze_single_asset('BTC/USDT', 'crypto', '4h', backtest=False)

    risk = result.get('risk_validation', {})
    
    print(f'Risk Allowed: {risk.get("allowed")}')
    print()
    
    if 'reasons' in risk:
        print('Reasons:')
        for reason in risk.get('reasons', []):
            print(f'  {reason}')
    
    print()
    if 'checks' in risk:
        print('Checks:')
        for name, check in risk['checks'].items():
            print(f'  {name}: {check}')
    
    print()
    print('Full Risk Result:')
    print(json.dumps(risk, indent=2, default=str))
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
