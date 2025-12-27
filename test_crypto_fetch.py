import sys
import logging

# Setup logging to see what's happening
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

# Test the exact import and execution path
print("\n" + "="*80)
print("TESTING EXACT STREAMLIT CODE PATH")
print("="*80 + "\n")

try:
    print("Step 1: Importing DataFetcher...")
    from src.data_fetcher import DataFetcher
    print("OK - Import successful\n")
    
    print("Step 2: Creating DataFetcher instance...")
    fetcher = DataFetcher()
    print(f"OK - Instance created\n")
    
    print("Step 3: Calling fetch_data('BTC/USDT', 'crypto', '1h', lookback_days=90)...")
    df = fetcher.fetch_data('BTC/USDT', 'crypto', '1h', lookback_days=90)
    print(f"OK - fetch_data returned: {type(df)}\n")
    
    print(f"Step 4: Checking result...")
    print(f"  - DataFrame type: {type(df)}")
    print(f"  - DataFrame shape: {df.shape if hasattr(df, 'shape') else 'N/A'}")
    print(f"  - Is empty: {df.empty if hasattr(df, 'empty') else 'N/A'}")
    print(f"  - Length: {len(df) if hasattr(df, '__len__') else 'N/A'}")
    
    if len(df) > 0:
        print(f"\nSUCCESS! Got {len(df)} candles\n")
    else:
        print(f"\nFAILED! DataFrame is empty\n")
        
except Exception as e:
    print(f"\nEXCEPTION: {type(e).__name__}: {str(e)}\n")
    import traceback
    traceback.print_exc()

print("="*80 + "\n")
