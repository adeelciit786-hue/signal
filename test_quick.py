#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test of signal generation"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')

from src.data_fetcher import DataFetcher
from src.technical_indicators import TechnicalIndicators
from src.strategy_logic import StrategyLogic
import logging

logging.basicConfig(level=logging.WARNING)

# Test multiple assets
assets = [
    ('BTC/USDT', 'crypto'),
    ('AUD/USD', 'forex'),
    ('AAPL', 'stock'),
]

for symbol, asset_type in assets:
    print(f"\n{'='*50}")
    print(f"Testing: {symbol} ({asset_type})")
    print(f"{'='*50}")
    
    try:
        # Fetch data
        f = DataFetcher()
        df = f.fetch_data(symbol, asset_type, '1h', 30)
        print(f'[OK] Fetched {len(df)} candles')
        
        if len(df) < 50:
            print(f'[ERROR] Insufficient data')
            continue
        
        # Calculate indicators
        TechnicalIndicators.calculate_all_indicators(df)
        
        # Generate signals
        trend, trend_conf = StrategyLogic.evaluate_trend(df)
        momentum, momentum_conf = StrategyLogic.evaluate_momentum(df)
        volume, volume_conf = StrategyLogic.evaluate_volume(df)
        volatility, volatility_conf = StrategyLogic.evaluate_volatility_suitability(df, 'normal')
        
        composite = StrategyLogic.generate_composite_signal(
            (trend, trend_conf), 
            (momentum, momentum_conf), 
            (volume, volume_conf), 
            (volatility, volatility_conf), 
            'normal'
        )
        
        signal_type = composite.get("signal", "N/A")
        signal_conf = composite.get("confidence", 0)
        
        print(f'[OK] Trend: {trend} ({trend_conf:.0f}%)')
        print(f'[OK] Momentum: {momentum} ({momentum_conf:.0f}%)')
        print(f'[OK] Volume: {volume} ({volume_conf:.0f}%)')
        print(f'[SIGNAL] {signal_type} ({signal_conf:.0f}% confidence)')
        print(f'[OK] Price: ${df["close"].iloc[-1]:.4f}')
    
    except Exception as e:
        print(f'[ERROR] {str(e)}')
