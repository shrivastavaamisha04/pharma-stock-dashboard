import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
import time

pharma_stocks = {
    'SUNPHARMA.NS': 'Sun Pharma',
    'DRREDDY.NS': "Dr. Reddy's Labs",
    'CIPLA.NS': 'Cipla',
    'LUPIN.NS': 'Lupin',
    'AUROPHARMA.NS': 'Aurobindo Pharma',
    'DIVISLAB.NS': "Divi's Laboratories"
}

def get_stock_data(ticker, period='1y', retries=3):
    for attempt in range(retries):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            if df.empty:
                time.sleep(2)
                continue
            info = stock.info if hasattr(stock, 'info') else {}
            return df, info
        except:
            if attempt < retries - 1:
                time.sleep(2)
            continue
    return None, {}

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

def format_number(num):
    try:
        num = float(num)
        if num >= 1e12:
            return f"₹{num/1e12:.2f}T"
        elif num >= 1e9:
            return f"₹{num/1e9:.2f}B"
        elif num >= 1e7:
            return f"₹{num/1e7:.2f}Cr"
        else:
            return f"₹{num:,.0f}"
    except:
        return "N/A"

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('📊 Indian Pharmaceutical Stocks Dashboard', 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '20px', 'marginBottom': '10px', 'fontFamily': 'Arial, sans-serif', 'fontSize': '42px'}),
        html.P('Live data from National Stock Exchange of India', style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'marginBottom': '30px'})
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
        )
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
    )
], style={'backgroundColor': '#ecf0f1', 'minHeight': '100vh', 'padding': '20px'})

@app.callback(
    [Output('summary-cards', 'children'),
     Output('comparison-chart', 'figure'),
     Output('graphs-container', 'children')],
    [Input('period-dropdown', 'value')]
)
def update_dashboard(selected_period):
    all_data = {}
    performance_data = []
    
    for ticker, name in pharma_stocks.items():
        df, info = get_stock_data(ticker, selected_period)
        if df is not None and len(df) > 0:
            pct_change = calculate_change(df)
            current_price = df['Close'].iloc[-1] if 'Close' in df.columns else 0
            all_data[name] = {'df': df, 'info': info, 'change': pct_change, 'current_price': current_price, 'ticker': ticker}
            performance_data.append({'Company': name, 'Change': pct_change, 'Price': current_price})
    
    if not performance_data:
        return html.Div([html.H3('⚠️ Unable to fetch data', style={'textAlign': 'center'})]), go.Figure(), []
    
    performance_df = pd.DataFrame(performance_data).sort_values('Change', ascending=False)
    best = performance_df.iloc[0] if len(performance_df) > 0 else None
    worst = performance_df.iloc[-1] if len(performance_df) > 0 else None
    avg = performance_df['Change'].mean()
    
    summary = html.Div([
        html.Div([
            html.Div([
                html.H3('🏆 Best', style={'color': '#27ae60'}),
                html.H2(best['Company'] if best is not None else 'N/A'),
                html.P(f"+{best['Change']:.2f}%" if best is not None else 'N/A', style={'fontSize': '24px', 'color': '#27ae60'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'}),
            html.Div([
                html.H3('📊 Average', style={'color': '#3498db'}),
                html.H2('All Stocks'),
                html.P(f"{avg:+.2f}%", style={'fontSize': '24px', 'color': '#3498db'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'}),
            html.Div([
                html.H3('📉 Worst', style={'color': '#e74c3c'}),
                html.H2(worst['Company'] if worst is not None else 'N/A'),
                html.P(f"{worst['Change']:.2f}%" if worst is not None else 'N/A', style={'fontSize': '24px', 'color': '#e74c3c'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center'})
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '30px'})
    ])
    
    comp_fig = go.Figure()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    for idx, (name, data) in enumerate(all_data.items()):
        df = data['df']
        if len(df) > 0:
            normalized = (df['Close'] / df['Close'].iloc[0]) * 100
            comp_fig.add_trace(go.Scatter(x=df.index, y=normalized, mode='lines', name=name, line=dict(color=colors[idx % len(colors)], width=3)))
    
    comp_fig.update_layout(title='Normalized (Base=100)', height=500, plot_bgcolor='white', paper_bgcolor='white')
    
    graphs = []
    for name, data in all_data.items():
        df, info, pct_change, current_price, ticker = data['df'], data['info'], data['change'], data['current_price'], data['ticker']
        change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
        change_symbol = '▲' if pct_change >= 0 else '▼'
        
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#3498db', width=2), fill='tozeroy'))
        price_fig.update_layout(title=f'{name}', height=350, plot_bgcolor='white')
        
        graphs.append(html.Div([
            html.Div([
                html.H2(name, style={'color': '#2c3e50'}),
                html.H3(f'₹{current_price:.2f}', style={'color': '#2c3e50'}),
                html.P(f'{change_symbol} {pct_change:.2f}%', style={'color': change_color, 'fontSize': '18px'})
            ], style={'marginBottom': '20px'}),
            dcc.Graph(figure=price_fig)
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '25px', 'marginBottom': '30px'}))
    
    return summary, comp_fig, graphs

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
