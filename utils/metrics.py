def calculate_metrics(df):
    direction_col = next((col for col in ['direction', 'Direction', 'signal', 'Signal'] if col in df.columns), None)

    total_trades = len(df[df[direction_col].notna() & (df[direction_col] != 'NEUTRAL')]) if direction_col else 0
    long_trades = len(df[df[direction_col].str.upper() == 'LONG']) if direction_col else 0
    short_trades = len(df[df[direction_col].str.upper() == 'SHORT']) if direction_col else 0

    return {
        'total_trades': total_trades,
        'long_trades': long_trades,
        'short_trades': short_trades,
        'avg_volume': df['volume'].mean() / 1_000_000,
        'price_change': ((df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0]) * 100,
        'current_price': df['close'].iloc[-1],
        'highest_price': df['high'].max(),
        'lowest_price': df['low'].min(),
        'direction_col': direction_col
    }
