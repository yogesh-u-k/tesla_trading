import ast
import pandas as pd

def parse_level_array(level_str):
    try:
        if pd.isna(level_str) or level_str == '' or level_str == '[]':
            return []
        if isinstance(level_str, str):
            return ast.literal_eval(level_str) if level_str.startswith('[') else [float(x.strip()) for x in level_str.split(',')]
        elif isinstance(level_str, list):
            return level_str
    except:
        return []

def validate_ohlcv_row(row):
    high, low, open_, close, volume = row['high'], row['low'], row['open'], row['close'], row['volume']
    if high < low: high, low = low, high
    open_ = max(low, min(high, open_))
    close = max(low, min(high, close))
    volume = max(0, volume)
    return pd.Series({'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume})
