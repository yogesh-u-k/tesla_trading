import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import parse_level_array, validate_ohlcv_row

@st.cache_data
def load_tesla_data_from_csv(uploaded_file):
    """Load Tesla data from uploaded CSV file"""
    if uploaded_file is None:
        return None

    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.write("**Available Columns:**")
        st.sidebar.write(list(df.columns))
        cleaned_df = clean_tsla_data_for_charts(df)
        return cleaned_df

    except Exception as e:
        st.error(f"❌ Error loading CSV file: {str(e)}")
        return None

def clean_tsla_data_for_charts(df):
    st.info("🧹 Cleaning and processing uploaded data...")
    df_cleaned = df.copy()

    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df_cleaned.columns]
    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
        return None

    ohlcv_cols = ['open', 'high', 'low', 'close', 'volume']
    original_rows = len(df_cleaned)
    df_cleaned = df_cleaned.drop_duplicates(subset=ohlcv_cols, keep='first').copy()
    duplicates_removed = original_rows - len(df_cleaned)

    possible_timestamp_names = ['timestamp', 'date', 'time', 'datetime', 'Date', 'Time', 'DateTime']
    timestamp_col = next((col for col in possible_timestamp_names if col in df_cleaned.columns), None)
    if not timestamp_col:
        st.error("❌ No timestamp column found.")
        return None

    df_cleaned['timestamp'] = pd.to_datetime(df_cleaned[timestamp_col])
    df_cleaned = df_cleaned.sort_values('timestamp').reset_index(drop=True)
    validated = df_cleaned[ohlcv_cols].apply(validate_ohlcv_row, axis=1)
    df_cleaned[ohlcv_cols] = validated

    support_col = next((col for col in ['Support', 'support', 'support_levels'] if col in df_cleaned.columns), None)
    resistance_col = next((col for col in ['Resistance', 'resistance', 'resistance_levels'] if col in df_cleaned.columns), None)

    if support_col:
        df_cleaned['support_levels'] = df_cleaned[support_col].apply(parse_level_array)
        df_cleaned['support_min'] = df_cleaned['support_levels'].apply(lambda x: min(x) if x else None)
        df_cleaned['support_max'] = df_cleaned['support_levels'].apply(lambda x: max(x) if x else None)
    else:
        df_cleaned['support_levels'] = [[] for _ in range(len(df_cleaned))]
        df_cleaned['support_min'] = None
        df_cleaned['support_max'] = None

    if resistance_col:
        df_cleaned['resistance_levels'] = df_cleaned[resistance_col].apply(parse_level_array)
        df_cleaned['resistance_min'] = df_cleaned['resistance_levels'].apply(lambda x: min(x) if x else None)
        df_cleaned['resistance_max'] = df_cleaned['resistance_levels'].apply(lambda x: max(x) if x else None)
    else:
        df_cleaned['resistance_levels'] = [[] for _ in range(len(df_cleaned))]
        df_cleaned['resistance_min'] = None
        df_cleaned['resistance_max'] = None

    direction_col = next((col for col in ['direction', 'Direction', 'signal'] if col in df_cleaned.columns), None)
    if direction_col:
        df_cleaned['direction'] = df_cleaned[direction_col].fillna('NEUTRAL')
        df_cleaned['direction'] = df_cleaned['direction'].replace('', 'NEUTRAL')

    price_cols = ['open', 'high', 'low', 'close', 'support_min', 'support_max', 'resistance_min', 'resistance_max']
    existing_price_cols = [col for col in price_cols if col in df_cleaned.columns]
    df_cleaned[existing_price_cols] = df_cleaned[existing_price_cols].round(2)
    df_cleaned['volume'] = df_cleaned['volume'].round(0).astype(int)

    from config.constants import COLOR_BEAR, COLOR_BULL
    df_cleaned['color'] = np.where(df_cleaned['open'] > df_cleaned['close'], COLOR_BEAR, COLOR_BULL)
    df_cleaned['time'] = df_cleaned['timestamp'].dt.strftime('%Y-%m-%d')

    return df_cleaned
