import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import requests
import time
import os
from datetime import datetime, timedelta

# Get API key from environment variable (secure) or use default for local testing
API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY', '1F15KKVN0EN9XRR5')

pharma_stocks = {
    'SUNPHARMA': 'Sun Pharma',
    'DRREDDY': "Dr. Reddy's Labs",
    'CIPLA': 'Cipla',
    'LUPIN': 'Lupin',
    'AUROPHARMA': 'Aurobindo Pharma',
    'DIVISLAB': "Divi's Laboratories"
}

def get_stock_data_alpha(symbol, outputsize='full'):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize={outputsize}&apikey={API_KEY}'
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            print(f"Error fetching {symbol}: {data.get('Note', data.get('Error Message', 'Unknown'))}")
            return None
        
        time_series = data['Time Series (Daily)']
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def filter_by_period(df, period):
    if df is None or len(df) == 0:
        return None
    
    end_date = df.index[-1]
    period_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730}
    days = period_map.get(period, 365)
    start_date = end_date - timedelta(days=days)
    return df[df.index >= start_date]

def calculate_change(df):
    if df is not None and len(df) > 0:
        try:
            start_price = df['Close'].iloc[0]
            end_price = df['Close'].iloc[-1]
            if start_price > 0:
                return ((end_price - start_price) / start_price) * 100
        except:
            pass
    return 0

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('📊 Indian Pharmaceutical Stocks Dashboard', 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px', 'fontFamily': 'Arial, sans-serif', 'fontSize': '42px'}),
        html.P('Live data from Alpha Vantage | NSE India', style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'marginBottom': '30px'})
    ]),
    
    html.Div([
        html.Label('Select Time Period:', style={'fontSize': '18px', 'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='period-dropdown',
            options=[
                {'label': '1 Month', 'value': '1mo'},
                {'label': '3 Months', 'value': '3mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '2 Years', 'value': '2y'}
            ],
            value='1y',
            style={'width': '200px', 'display': 'inline-block'}
        ),
        html.Button('Refresh Data', id='refresh-button', n_clicks=0, 
                   style={'marginLeft': '20px', 'padding': '10px 20px', 'fontSize': '16px', 'backgroundColor': '#3498db', 'color': 'white', 'border': 'none', 'borderRadius': '5px'})
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    dcc.Loading(
        id="loading",
        type="circle",
        children=[
            html.Div(id='summary-cards'),
            html.Div([
                html.H2('📈 Stock Comparison', style={'textAlign': 'center', 'color': '#34495e'}),
                dcc.Graph(id='comparison-chart')
            ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '20px'}),
            html.Div(id='graphs-container')
        ]
    ),
    
    html.Div([
        html.P('💡 First load may take 1-2 minutes (fetching data for 6 stocks)', 
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '14px', 'marginTop': '20px'})
    ])
], style={'backgroundColor': '#ecf0f1', 'minHeight': '100vh', 'padding': '20px'})

cached_data = {}

@app.callback(
    [Output('summary-cards', 'children'),
     Output('comparison-chart', 'figure'),
     Output('graphs-container', 'children')],
    [Input('period-dropdown', 'value'),
     Input('refresh-button', 'n_clicks')]
)
def update_dashboard(selected_period, n_clicks):
    all_data = {}
    performance_data = []
    
    for symbol, name in pharma_stocks.items():
        if symbol not in cached_data:
            print(f"Fetching {name}...")
            df = get_stock_data_alpha(symbol)
            if df is not None:
                cached_data[symbol] = df
            time.sleep(13)
        
        df = filter_by_period(cached_data.get(symbol), selected_period)
        
        if df is not None and len(df) > 0:
            pct_change = calculate_change(df)
            current_price = df['Close'].iloc[-1]
            all_data[name] = {'df': df, 'change': pct_change, 'current_price': current_price}
            performance_data.append({'Company': name, 'Change': pct_change, 'Price': current_price})
    
    if not performance_data:
        return html.Div([html.H3('⚠️ Loading data... Please wait 1-2 minutes and refresh', style={'textAlign': 'center'})]), go.Figure(), []
    
    performance_df = pd.DataFrame(performance_data).sort_values('Change', ascending=False)
    best = performance_df.iloc[0]
    worst = performance_df.iloc[-1]
    avg = performance_df['Change'].mean()
    
    summary = html.Div([
        html.Div([
            html.Div([
                html.H3('🏆 Best', style={'color': '#27ae60'}),
                html.H2(best['Company']),
                html.P(f"+{best['Change']:.2f}%", style={'fontSize': '24px', 'color': '#27ae60', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3('📊 Average', style={'color': '#3498db'}),
                html.H2('All Stocks'),
                html.P(f"{avg:+.2f}%", style={'fontSize': '24px', 'color': '#3498db', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'}),
            
            html.Div([
                html.H3('📉 Worst', style={'color': '#e74c3c'}),
                html.H2(worst['Company']),
                html.P(f"{worst['Change']:.2f}%", style={'fontSize': '24px', 'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '30px'})
    ])
    
    comp_fig = go.Figure()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for idx, (name, data) in enumerate(all_data.items()):
        df = data['df']
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        comp_fig.add_trace(go.Scatter(x=df.index, y=normalized, mode='lines', name=name, line=dict(color=colors[idx], width=3)))
    
    comp_fig.update_layout(title='Normalized (Base=100)', height=500, plot_bgcolor='white')
    
    graphs = []
    for name, data in all_data.items():
        df, pct_change, current_price = data['df'], data['change'], data['current_price']
        change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
        change_symbol = '▲' if pct_change >= 0 else '▼'
        
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#3498db', width=2), fill='tozeroy'))
        price_fig.update_layout(title=f'{name}', height=350, plot_bgcolor='white')
        
        graphs.append(html.Div([
            html.Div([
                html.H2(name, style={'color': '#2c3e50'}),
                html.H3(f'₹{current_price:.2f}'),
                html.P(f'{change_symbol} {pct_change:.2f}%', style={'color': change_color, 'fontSize': '18px'})
            ]),
            dcc.Graph(figure=price_fig)
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '25px', 'marginBottom': '30px'}))
    
    return summary, comp_fig, graphs

if __name__ == '__main__':
    print("Starting dashboard with Alpha Vantage...")
    print(f"Using API key: {API_KEY[:4]}...{API_KEY[-4:]}")  # Print partial key for verification
    app.run(debug=True, host='0.0.0.0', port=8050)
