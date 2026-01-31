import streamlit as st
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Indian Pharma Stocks Dashboard", layout="wide", page_icon="📊")

pharma_stocks = {
    'SUNPHARMA.NS': 'Sun Pharma',
    'DRREDDY.NS': "Dr. Reddy's Labs",
    'CIPLA.NS': 'Cipla',
    'LUPIN.NS': 'Lupin',
    'AUROPHARMA.NS': 'Aurobindo Pharma',
    'DIVISLAB.NS': "Divi's Laboratories"
}

@st.cache_data(ttl=3600)
def get_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return None
        return df
    except Exception as e:
        st.error(f"Error fetching {ticker}: {e}")
        return None

def calculate_change(df):
    if df is not None and len(df) > 0:
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        if start_price > 0:
            return ((end_price - start_price) / start_price) * 100
    return 0

# Header
st.markdown("<h1 style='text-align: center; color: #2c3e50;'>📊 Indian Pharmaceutical Stocks Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7f8c8d;'>Live data from Yahoo Finance | NSE India</p>", unsafe_allow_html=True)

# Controls
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    period = st.selectbox(
        'Select Time Period:',
        options=['1mo', '3mo', '6mo', '1y', '2y'],
        format_func=lambda x: {'1mo': '1 Month', '3mo': '3 Months', '6mo': '6 Months', '1y': '1 Year', '2y': '2 Years'}[x],
        index=3
    )
    if st.button('🔄 Refresh Data', use_container_width=True):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# Fetch data
with st.spinner('Fetching stock data... This may take 30-60 seconds...'):
    all_data = {}
    performance_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, (ticker, name) in enumerate(pharma_stocks.items()):
        status_text.text(f"Fetching {name}...")
        df = get_stock_data(ticker, period)
        
        if df is not None and len(df) > 0:
            pct_change = calculate_change(df)
            current_price = df['Close'].iloc[-1]
            all_data[name] = {'df': df, 'change': pct_change, 'current_price': current_price}
            performance_data.append({'Company': name, 'Change': pct_change, 'Price': current_price})
        
        progress_bar.progress((idx + 1) / len(pharma_stocks))
    
    progress_bar.empty()
    status_text.empty()

if not performance_data:
    st.error("❌ Unable to fetch stock data. Please try refreshing the page.")
    st.stop()

# Summary Cards
performance_df = pd.DataFrame(performance_data).sort_values('Change', ascending=False)
best = performance_df.iloc[0]
worst = performance_df.iloc[-1]
avg = performance_df['Change'].mean()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
        <h3 style='color: #27ae60; margin-bottom: 10px;'>🏆 Best Performer</h3>
        <h2 style='margin-bottom: 5px;'>{best['Company']}</h2>
        <p style='font-size: 24px; color: #27ae60; font-weight: bold; margin: 0;'>+{best['Change']:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
        <h3 style='color: #3498db; margin-bottom: 10px;'>📊 Average Performance</h3>
        <h2 style='margin-bottom: 5px;'>All Stocks</h2>
        <p style='font-size: 24px; color: #3498db; font-weight: bold; margin: 0;'>{avg:+.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
        <h3 style='color: #e74c3c; margin-bottom: 10px;'>📉 Worst Performer</h3>
        <h2 style='margin-bottom: 5px;'>{worst['Company']}</h2>
        <p style='font-size: 24px; color: #e74c3c; font-weight: bold; margin: 0;'>{worst['Change']:.2f}%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Comparison Chart
st.markdown("### 📈 Stock Comparison Chart")
comp_fig = go.Figure()
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']

for idx, (name, data) in enumerate(all_data.items()):
    df = data['df']
    normalized = (df['Close'] / df['Close'].iloc[0]) * 100
    comp_fig.add_trace(go.Scatter(
        x=df.index, 
        y=normalized, 
        mode='lines', 
        name=name, 
        line=dict(color=colors[idx % len(colors)], width=3)
    ))

comp_fig.update_layout(
    title='Normalized Performance (Base = 100)',
    xaxis_title='Date',
    yaxis_title='Indexed Value',
    height=500,
    plot_bgcolor='white',
    hovermode='x unified',
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(comp_fig, use_container_width=True)

st.markdown("---")

# Individual Stock Charts
st.markdown("### 📊 Individual Stock Performance")

for name, data in all_data.items():
    df = data['df']
    pct_change = data['change']
    current_price = data['current_price']
    change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
    change_symbol = '▲' if pct_change >= 0 else '▼'
    
    with st.container():
        st.markdown(f"""
        <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;'>
                <div>
                    <h3 style='margin: 0; color: #2c3e50;'>{name}</h3>
                    <p style='margin: 5px 0 0 0; color: #7f8c8d;'>Current: ₹{current_price:.2f}</p>
                </div>
                <div style='text-align: right;'>
                    <p style='margin: 0; font-size: 24px; font-weight: bold; color: {change_color};'>{change_symbol} {pct_change:.2f}%</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Price chart
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'], 
            mode='lines', 
            line=dict(color='#3498db', width=2), 
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)',
            name='Price'
        ))
        price_fig.update_layout(
            title=f'{name} - Stock Price Trend',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            height=350,
            plot_bgcolor='white',
            hovermode='x unified'
        )
        st.plotly_chart(price_fig, use_container_width=True)
        
        # Volume chart
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(
            x=df.index, 
            y=df['Volume'], 
            marker_color='rgba(52, 152, 219, 0.6)',
            name='Volume'
        ))
        volume_fig.update_layout(
            title='Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            height=250,
            plot_bgcolor='white'
        )
        st.plotly_chart(volume_fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #95a5a6; font-size: 14px;'>💡 Data updates every hour | Free market data from Yahoo Finance</p>", unsafe_allow_html=True)
