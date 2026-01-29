import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px

pharma_stocks = {
    'SUNPHARMA.NS': 'Sun Pharma',
    'DRREDDY.NS': "Dr. Reddy's Labs",
    'CIPLA.NS': 'Cipla',
    'LUPIN.NS': 'Lupin',
    'AUROPHARMA.NS': 'Aurobindo Pharma',
    'DIVISLAB.NS': "Divi's Laboratories"
}

def get_stock_data(ticker, period='1y'):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        info = stock.info
        return df, info
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None, {}

def calculate_change(df):
    if df is not None and len(df) > 0:
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        return change
    return 0

def format_number(num):
    if num >= 1e12:
        return f"₹{num/1e12:.2f}T"
    elif num >= 1e9:
        return f"₹{num/1e9:.2f}B"
    elif num >= 1e7:
        return f"₹{num/1e7:.2f}Cr"
    else:
        return f"₹{num:,.0f}"

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.Div([
        html.H1('📊 Indian Pharmaceutical Stocks Dashboard', 
                style={
                    'textAlign': 'center', 
                    'color': '#2c3e50', 
                    'marginTop': '20px',
                    'marginBottom': '10px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '42px'
                }),
        html.P('Live data from National Stock Exchange of India | Updates in real-time',
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px', 'marginBottom': '30px'})
    ]),
    
    html.Div([
        html.Label('Select Time Period:', 
                   style={'fontSize': '18px', 'fontWeight': 'bold', 'marginRight': '10px'}),
        dcc.Dropdown(
            id='period-dropdown',
            options=[
                {'label': '1 Month', 'value': '1mo'},
                {'label': '3 Months', 'value': '3mo'},
                {'label': '6 Months', 'value': '6mo'},
                {'label': '1 Year', 'value': '1y'},
                {'label': '2 Years', 'value': '2y'},
                {'label': '5 Years', 'value': '5y'}
            ],
            value='1y',
            style={'width': '200px', 'display': 'inline-block'}
        )
    ], style={'textAlign': 'center', 'margin': '20px'}),
    
    html.Div(id='summary-cards', style={'padding': '0 20px'}),
    
    html.Div([
        html.H2('📈 Stock Comparison Chart', 
                style={'textAlign': 'center', 'color': '#34495e', 'marginTop': '40px', 'marginBottom': '20px'}),
        dcc.Graph(id='comparison-chart')
    ], style={'padding': '20px', 'backgroundColor': 'white', 'borderRadius': '10px', 'margin': '20px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'}),
    
    html.Div([
        html.H2('📊 Individual Stock Performance', 
                style={'textAlign': 'center', 'color': '#34495e', 'marginTop': '40px', 'marginBottom': '20px'})
    ]),
    
    html.Div(id='graphs-container'),
    
    html.Div([
        html.P('💡 Tip: Hover over charts for detailed information | Click and drag to zoom | Double-click to reset',
               style={'textAlign': 'center', 'color': '#95a5a6', 'fontSize': '14px', 'marginTop': '40px', 'marginBottom': '20px'})
    ])
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
            current_price = df['Close'].iloc[-1]
            all_data[name] = {
                'df': df,
                'info': info,
                'change': pct_change,
                'current_price': current_price,
                'ticker': ticker
            }
            performance_data.append({
                'Company': name,
                'Change': pct_change,
                'Price': current_price
            })
    
    performance_df = pd.DataFrame(performance_data).sort_values('Change', ascending=False)
    
    best_performer = performance_df.iloc[0] if len(performance_df) > 0 else None
    worst_performer = performance_df.iloc[-1] if len(performance_df) > 0 else None
    avg_performance = performance_df['Change'].mean() if len(performance_df) > 0 else 0
    
    summary_cards = html.Div([
        html.Div([
            html.Div([
                html.H3('🏆 Best Performer', style={'color': '#27ae60', 'marginBottom': '10px'}),
                html.H2(best_performer['Company'] if best_performer is not None else 'N/A', 
                        style={'marginBottom': '5px'}),
                html.P(f"+{best_performer['Change']:.2f}%" if best_performer is not None else 'N/A',
                       style={'fontSize': '24px', 'color': '#27ae60', 'fontWeight': 'bold'})
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'textAlign': 'center',
                'flex': '1',
                'margin': '10px'
            }),
            
            html.Div([
                html.H3('📊 Average Performance', style={'color': '#3498db', 'marginBottom': '10px'}),
                html.H2('All Stocks', style={'marginBottom': '5px'}),
                html.P(f"{avg_performance:+.2f}%",
                       style={'fontSize': '24px', 'color': '#3498db', 'fontWeight': 'bold'})
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'textAlign': 'center',
                'flex': '1',
                'margin': '10px'
            }),
            
            html.Div([
                html.H3('📉 Worst Performer', style={'color': '#e74c3c', 'marginBottom': '10px'}),
                html.H2(worst_performer['Company'] if worst_performer is not None else 'N/A',
                        style={'marginBottom': '5px'}),
                html.P(f"{worst_performer['Change']:.2f}%" if worst_performer is not None else 'N/A',
                       style={'fontSize': '24px', 'color': '#e74c3c', 'fontWeight': 'bold'})
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
                'textAlign': 'center',
                'flex': '1',
                'margin': '10px'
            })
        ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'marginBottom': '30px'})
    ])
    
    comparison_fig = go.Figure()
    colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    for idx, (name, data) in enumerate(all_data.items()):
        df = data['df']
        normalized_prices = (df['Close'] / df['Close'].iloc[0]) * 100
        comparison_fig.add_trace(go.Scatter(
            x=df.index,
            y=normalized_prices,
            mode='lines',
            name=name,
            line=dict(color=colors[idx % len(colors)], width=3)
        ))
    
    comparison_fig.update_layout(
        title='Normalized Performance (Base = 100)',
        xaxis_title='Date',
        yaxis_title='Indexed Value',
        hovermode='x unified',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif', size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    graphs = []
    for name, data in all_data.items():
        df = data['df']
        info = data['info']
        pct_change = data['change']
        current_price = data['current_price']
        ticker = data['ticker']
        
        change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
        change_symbol = '▲' if pct_change >= 0 else '▼'
        
        market_cap = info.get('marketCap', 0)
        pe_ratio = info.get('trailingPE', 0)
        volume = df['Volume'].iloc[-1] if 'Volume' in df.columns else 0
        
        price_fig = go.Figure()
        price_fig.add_trace(go.Scatter(
            x=df.index, 
            y=df['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#3498db', width=2),
            fill='tozeroy',
            fillcolor='rgba(52, 152, 219, 0.1)'
        ))
        
        price_fig.update_layout(
            title=f'{name} - Stock Price Trend',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            hovermode='x unified',
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif')
        )
        
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(
            x=df.index,
            y=df['Volume'] if 'Volume' in df.columns else [0],
            name='Volume',
            marker_color='rgba(52, 152, 219, 0.6)'
        ))
        
        volume_fig.update_layout(
            title='Trading Volume',
            xaxis_title='Date',
            yaxis_title='Volume',
            height=250,
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif')
        )
        
        graphs.append(
            html.Div([
                html.Div([
                    html.Div([
                        html.H2(name, style={'marginBottom': '5px', 'color': '#2c3e50'}),
                        html.P(ticker, style={'color': '#7f8c8d', 'fontSize': '14px'})
                    ], style={'flex': '1'}),
                    html.Div([
                        html.H3(f'₹{current_price:.2f}', style={'marginBottom': '5px', 'color': '#2c3e50'}),
                        html.P(f'{change_symbol} {pct_change:.2f}%', 
                               style={'color': change_color, 'fontSize': '18px', 'fontWeight': 'bold'})
                    ], style={'textAlign': 'right'})
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '20px'}),
                
                html.Div([
                    html.Div([
                        html.P('Market Cap', style={'color': '#7f8c8d', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.P(format_number(market_cap), style={'fontSize': '16px', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px'}),
                    
                    html.Div([
                        html.P('P/E Ratio', style={'color': '#7f8c8d', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.P(f'{pe_ratio:.2f}' if pe_ratio else 'N/A', style={'fontSize': '16px', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px'}),
                    
                    html.Div([
                        html.P('Volume', style={'color': '#7f8c8d', 'fontSize': '12px', 'marginBottom': '5px'}),
                        html.P(f'{volume:,.0f}', style={'fontSize': '16px', 'fontWeight': 'bold'})
                    ], style={'flex': '1', 'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderRadius': '5px', 'margin': '5px'})
                ], style={'display': 'flex', 'marginBottom': '20px'}),
                
                dcc.Graph(figure=price_fig),
                dcc.Graph(figure=volume_fig)
                
            ], style={
                'backgroundColor': 'white',
                'borderRadius': '10px',
                'padding': '25px',
                'marginBottom': '30px',
                'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
            })
        )
    
    return summary_cards, comparison_fig, graphs

if __name__ == '__main__':
    print("Starting enhanced dashboard...")
    print("Open your browser and go to: http://127.0.0.1:8050/")
    print("Press CTRL+C to stop the server")
    app.run(debug=True)
