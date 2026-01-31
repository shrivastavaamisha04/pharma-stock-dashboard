import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
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
            return df
        except:
            if attempt < retries - 1:
                time.sleep(2)
            continue
    return None

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
        html.P('Live data from Yahoo Finance | NSE India', style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'marginBottom': '30px'})
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
        html.P('💡 Data fetches may take 30-60 seconds | Free market data from Yahoo Finance', 
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '14px', 'marginTop': '20px'})
    ])
], style={'backgroundColor': '#ecf0f1', 'minHeight': '100vh', 'padding': '20px'})

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
    
    print(f"Fetching data for period: {selected_period}")
    
    for ticker, name in pharma_stocks.items():
        print(f"Fetching {name}...")
        df = get_stock_data(ticker, selected_period)
        
        if df is not None and len(df) > 0:
            pct_change = calculate_change(df)
            current_price = df['Close'].iloc[-1]
            all_data[name] = {'df': df, 'change': pct_change, 'current_price': current_price}
            performance_data.append({'Company': name, 'Change': pct_change, 'Price': current_price})
            print(f"✓ {name}: ₹{current_price:.2f} ({pct_change:+.2f}%)")
        else:
            print(f"✗ Failed to load {name}")
    
    if not performance_data:
        return html.Div([
            html.H3('⚠️ Unable to fetch stock data', style={'textAlign': 'center', 'color': '#e74c3c', 'marginTop': '100px'}),
            html.P('Please try clicking "Refresh Data" button', style={'textAlign': 'center', 'color': '#7f8c8d'})
        ]), go.Figure(), []
    
    performance_df = pd.DataFrame(performance_data).sort_values('Change', ascending=False)
    best = performance_df.iloc[0]
    worst = performance_df.iloc[-1]
    avg = performance_df['Change'].mean()
    
    summary = html.Div([
        html.Div([
            html.Div([
                html.H3('🏆 Best Performer', style={'color': '#27ae60', 'marginBottom': '10px'}),
                html.H2(best['Company'], style={'marginBottom': '5px'}),
                html.P(f"+{best['Change']:.2f}%", style={'fontSize': '24px', 'color': '#27ae60', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3('📊 Average Performance', style={'color': '#3498db', 'marginBottom': '10px'}),
                html.H2('All Stocks', style={'marginBottom': '5px'}),
                html.P(f"{avg:+.2f}%", style={'fontSize': '24px', 'color': '#3498db', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
            
            html.Div([
                html.H3('📉 Worst Performer', style={'color': '#e74c3c', 'marginBottom': '10px'}),
                html.H2(worst['Company'], style={'marginBottom': '5px'}),
                html.P(f"{worst['Change']:.2f}%", style={'fontSize': '24px', 'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={'backgroundColor': 'white', 'padding': '25px', 'borderRadius': '10px', 'flex': '1', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': '30px', 'justifyContent': 'space-around'})
    ])
    
    comp_fig = go.Figure()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for idx, (name, data) in enumerate(all_data.items()):
        df = data['df']
        normalized = (df['Close'] / df['Close'].iloc[0]) * 100
        comp_fig.add_trace(go.Scatter(x=df.index, y=normalized, mode='lines', name=name, line=dict(color=colors[idx], width=3)))
    
    comp_fig.update_layout(
        title='Normalized Performance (Base = 100)',
        xaxis_title='Date',
        yaxis_title='Indexed Value',
        height=500, 
        plot_bgcolor='white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    graphs = []
    for name, data in all_data.items():
        df, pct_change, current_price = data['df'], data['change'], data['current_price']
        change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
        change_symbol = '▲' if pct_change >= 0 else '▼'
        
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color='#3498db', width=2), fill='tozeroy', fillcolor='rgba(52, 152, 219, 0.1)'))
        price_fig.update_layout(title=f'{name} - Stock Price Trend', xaxis_title='Date', yaxis_title='Price (₹)', height=350, plot_bgcolor='white', hovermode='x unified')
        
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color='rgba(52, 152, 219, 0.6)'))
        volume_fig.update_layout(title='Trading Volume', xaxis_title='Date', yaxis_title='Volume', height=250, plot_bgcolor='white')
        
        graphs.append(html.Div([
            html.Div([
                html.Div([
                    html.H2(name, style={'marginBottom': '5px', 'color': '#2c3e50'}),
                    html.P(f'Current: ₹{current_price:.2f}', style={'color': '#7f8c8d', 'fontSize': '14px'})
                ], style={'flex': '1'}),
                html.Div([
                    html.P(f'{change_symbol} {pct_change:.2f}%', style={'color': change_color, 'fontSize': '24px', 'fontWeight': 'bold', 'marginBottom': '0'})
                ], style={'textAlign': 'right'})
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'}),
            dcc.Graph(figure=price_fig),
            dcc.Graph(figure=volume_fig)
        ], style={'backgroundColor': 'white', 'borderRadius': '10px', 'padding': '25px', 'marginBottom': '30px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}))
    
    return summary, comp_fig, graphs

if __name__ == '__main__':
    print("Starting dashboard...")
    app.run(debug=True, host='0.0.0.0', port=8050)
