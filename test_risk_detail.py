#!/usr/bin/env python
"""Test signal with detailed risk checks"""

import sys
sys.path.insert(0, 'src')
from bot_engine import BotOrchestrator

print('Testing Signal with Detailed Risk Info...')
print('=' * 70)

try:
    bot = BotOrchestrator('config.json')
    result = bot.engine.analyze_single_asset('BTC/USDT', 'crypto', '4h', backtest=False)

    signal = result.get('signal', 'NEUTRAL')
    confidence = result.get('confidence', 0)
    setup = result.get('setup', {})
    
    print(f'Signal: {signal}')
    print(f'Confidence: {confidence:.2f}%')
    print()
    
    risk = result.get('risk_validation', {})
    print('RISK VALIDATION DETAILS:')
    print(f'  Allowed: {"YES" if risk.get("allowed") else "NO"}')
    print()
    
    if 'checks' in risk:
        print('Risk Checks:')
        for check_name, check_result in risk['checks'].items():
            if isinstance(check_result, dict):
                is_valid = check_result.get('valid', False)
                reason = check_result.get('reason', 'No details')
                print(f'  [{check_name}]: {"PASS" if is_valid else "FAIL"} - {reason}')
    
    print()
    if 'reasons' in risk:
        print('Risk Reasons/Messages:')
        for reason in risk['reasons']:
            print(f'  • {reason}')
    
    print()
    print('=' * 70)
    
except Exception as e:
    print(f'ERROR: {e}')
    import traceback
    traceback.print_exc()
