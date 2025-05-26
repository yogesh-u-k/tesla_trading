import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts
from utils.helpers import parse_level_array

import pandas as pd
from config.constants import COLOR_BULL, COLOR_BEAR, COLOR_SUPPORT, COLOR_RESISTANCE
@st.cache_data

def prepare_chart_data(df):
    """Prepare data for lightweight charts"""
    # Candlestick data
    candles_data = []
    volume_data = []
    support_min_data = []
    support_max_data = []
    resistance_min_data = []
    resistance_max_data = []
    
    for _, row in df.iterrows():
        try:
            # Candlestick data
            candles_data.append({
                'time': row['time'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close'])
            })
            
            # Volume data
            volume_data.append({
                'time': row['time'],
                'value': float(row['volume']),
                'color': row['color']
            })
            
            # Support levels
            if pd.notna(row['support_min']):
                support_min_data.append({
                    'time': row['time'],
                    'value': float(row['support_min'])
                })
            
            if pd.notna(row['support_max']):
                support_max_data.append({
                    'time': row['time'],
                    'value': float(row['support_max'])
                })
            
            # Resistance levels
            if pd.notna(row['resistance_min']):
                resistance_min_data.append({
                    'time': row['time'],
                    'value': float(row['resistance_min'])
                })
            
            if pd.notna(row['resistance_max']):
                resistance_max_data.append({
                    'time': row['time'],
                    'value': float(row['resistance_max'])
                })
                
        except (ValueError, TypeError) as e:
            st.warning(f"Skipping invalid data row: {e}")
            continue
    
    st.write("✅ Number of candlesticks:", len(candles_data))
    if candles_data:
        st.write("✅ Sample candlestick:")
        st.json(candles_data[:2])

    return {
        'candles': candles_data,
        'volume': volume_data,
        'support_min': support_min_data,
        'support_max': support_max_data,
        'resistance_min': resistance_min_data,
        'resistance_max': resistance_max_data
    }

def create_trading_signals_markers(df, direction_col):
    """Create markers for trading signals"""
    markers = []
    
    if direction_col:
        for idx, row in df.iterrows():
            if pd.notna(row[direction_col]) and row[direction_col] != 'NEUTRAL':
                direction = str(row[direction_col]).upper()
                
                if direction == 'LONG':
                    markers.append({
                        'time': row['time'],
                        'position': 'belowBar',
                        'color': '#4CAF50',
                        'shape': 'arrowUp',
                        'text': 'LONG'
                    })
                elif direction == 'SHORT':
                    markers.append({
                        'time': row['time'],
                        'position': 'aboveBar',
                        'color': '#F44336',
                        'shape': 'arrowDown',
                        'text': 'SHORT'
                    })
    
    return markers

def create_lightweight_chart(df, show_volume=True, show_signals=True, show_support_resistance=True):
    """Create professional candlestick chart with lightweight-charts"""
    try:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Tesla TSLA - Professional Candlestick Chart")
        
        # Prepare chart data
        chart_data = prepare_chart_data(df)
        
        if not chart_data['candles']:
            st.error("No valid chart data available")
            return
        
        # Chart configuration for multipane layout
        chart_options = []
        series_config = []
        
        # Main candlestick chart
        main_chart_options = {
            "width": 800,
            "height": 500,
            "layout": {
                "background": {
                    "type": "solid",
                    "color": '#111'
                },
                "textColor": "white"
            },
            "grid": {
                "vertLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                },
                "horzLines": {
                    "color": "rgba(197, 203, 206, 0.5)"
                }
            },
            "crosshair": {
                "mode": 0
            },
            "priceScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)"
            },
            "timeScale": {
                "borderColor": "rgba(197, 203, 206, 0.8)",
                "barSpacing": 15
            },
            "watermark": {
                "visible": True,
                "fontSize": 48,
                "horzAlign": 'center',
                "vertAlign": 'center',
                "color": 'rgba(171, 71, 188, 0.3)',
                "text": 'TSLA',
            }
        }
        
        # Main candlestick series
        main_series = [{
            "type": 'Candlestick',
            "data": chart_data['candles'],
            "options": {
                "upColor": COLOR_BULL,
                "downColor": COLOR_BEAR,
                "borderVisible": True,
                "borderColor": "black",
                "wickUpColor": COLOR_BULL,
                "wickDownColor": COLOR_BEAR
            }
        }]
        
        # Add support and resistance lines
        if show_support_resistance:
            if chart_data['support_min']:
                main_series.append({
                    "type": 'Line',
                    "data": chart_data['support_min'],
                    "options": {
                        "color": COLOR_SUPPORT,
                        "lineWidth": 2,
                        "title": "Support Min"
                    }
                })
            
            if chart_data['support_max']:
                main_series.append({
                    "type": 'Line',
                    "data": chart_data['support_max'],
                    "options": {
                        "color": 'rgba(76, 175, 80, 0.6)',
                        "lineWidth": 2,
                        "title": "Support Max"
                    }
                })
            
            if chart_data['resistance_min']:
                main_series.append({
                    "type": 'Line',
                    "data": chart_data['resistance_min'],
                    "options": {
                        "color": COLOR_RESISTANCE,
                        "lineWidth": 2,
                        "title": "Resistance Min"
                    }
                })
            
            if chart_data['resistance_max']:
                main_series.append({
                    "type": 'Line',
                    "data": chart_data['resistance_max'],
                    "options": {
                        "color": 'rgba(244, 67, 54, 0.6)',
                        "lineWidth": 2,
                        "title": "Resistance Max"
                    }
                })
        
        # Add trading signals markers
        if show_signals:
            direction_col = None
            possible_direction_names = ['direction', 'Direction', 'signal', 'Signal', 'trade_direction']
            
            for col in possible_direction_names:
                if col in df.columns:
                    direction_col = col
                    break
            
            if direction_col:
                markers = create_trading_signals_markers(df, direction_col)
                if markers:
                    # Add markers to the candlestick series
                    main_series[0]["markers"] = markers
        
        chart_options.append(main_chart_options)
        series_config.append({
            "chart": main_chart_options,
            "series": main_series
        })
        
        # Volume chart (if enabled)
        if show_volume and chart_data['volume']:
            volume_chart_options = {
                "width": 800,
                "height": 150,
                "layout": {
                    "background": {
                        "type": 'solid',
                        "color": 'transparent'
                    },
                    "textColor": 'black',
                },
                "grid": {
                    "vertLines": {
                        "color": 'rgba(42, 46, 57, 0)',
                    },
                    "horzLines": {
                        "color": 'rgba(42, 46, 57, 0.6)',
                    }
                },
                "timeScale": {
                    "visible": False,
                },
                "watermark": {
                    "visible": True,
                    "fontSize": 18,
                    "horzAlign": 'left',
                    "vertAlign": 'top',
                    "color": 'rgba(171, 71, 188, 0.7)',
                    "text": 'Volume',
                }
            }
            
            volume_series = [{
                "type": 'Histogram',
                "data": chart_data['volume'],
                "options": {
                    "priceFormat": {
                        "type": 'volume',
                    },
                    "priceScaleId": ""
                },
                "priceScale": {
                    "scaleMargins": {
                        "top": 0,
                        "bottom": 0,
                    },
                    "alignLabels": False
                }
            }]
            
            series_config.append({
                "chart": volume_chart_options,
                "series": volume_series
            })
        
        # Render the charts
        renderLightweightCharts(series_config, 'tesla_chart')
        
        # Add legend
        st.markdown("""
        <div class="legend-container">
            <div class="legend-item">
                <div style="width: 12px; height: 12px; background: #4CAF50; border-radius: 50%;"></div>
                <span>LONG Signal</span>
            </div>
            <div class="legend-item">
                <div style="width: 12px; height: 12px; background: #F44336; border-radius: 50%;"></div>
                <span>SHORT Signal</span>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 8px; background: rgba(76, 175, 80, 0.6);"></div>
                <span>Support Levels</span>
            </div>
            <div class="legend-item">
                <div style="width: 20px; height: 8px; background: rgba(244, 67, 54, 0.6);"></div>
                <span>Resistance Levels</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error creating lightweight chart: {str(e)}")
        st.info("Make sure you have installed: pip install streamlit-lightweight-charts")
        
        # Fallback to basic Streamlit charts
        st.subheader("📈 Fallback - Basic Price Chart")
        try:
            chart_data = df.set_index('timestamp')[['open', 'high', 'low', 'close']]
            st.line_chart(chart_data)
        except Exception as fallback_error:
            st.error(f"Even fallback chart failed: {fallback_error}")
            st.write("Please check your data format and try again.")

def create_additional_charts(df):
    """Create additional analysis charts"""
    try:
        # Volume analysis
        st.subheader("📊 Volume Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Volume chart
            volume_chart_data = df.set_index('timestamp')[['volume']]
            st.bar_chart(volume_chart_data)
        
        with col2:
            # Price vs Volume correlation
            st.write("**Price vs Volume Correlation**")
            correlation = df['close'].corr(df['volume'])
            st.metric("Correlation Coefficient", f"{correlation:.3f}")
            
            # Volume moving average
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            volume_ma_data = df.set_index('timestamp')[['volume', 'volume_ma']].dropna()
            st.line_chart(volume_ma_data)
        
        # Support/Resistance Analysis
        st.subheader("🎯 Support & Resistance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Support Levels Distribution**")
            support_data = df[df['support_min'].notna()]
            if not support_data.empty:
                support_chart = support_data.set_index('timestamp')[['support_min', 'support_max']]
                st.line_chart(support_chart)
                
                avg_support = support_data[['support_min', 'support_max']].mean()
                st.write(f"Average Support Range: ${avg_support['support_min']:.2f} - ${avg_support['support_max']:.2f}")
            else:
                st.info("No support level data available")
        
        with col2:
            st.write("**Resistance Levels Distribution**")
            resistance_data = df[df['resistance_min'].notna()]
            if not resistance_data.empty:
                resistance_chart = resistance_data.set_index('timestamp')[['resistance_min', 'resistance_max']]
                st.line_chart(resistance_chart)
                
                avg_resistance = resistance_data[['resistance_min', 'resistance_max']].mean()
                st.write(f"Average Resistance Range: ${avg_resistance['resistance_min']:.2f} - ${avg_resistance['resistance_max']:.2f}")
            else:
                st.info("No resistance level data available")
        
    except Exception as e:
        st.error(f"Error creating additional charts: {str(e)}")