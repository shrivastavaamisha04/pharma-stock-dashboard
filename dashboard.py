import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

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
        return df
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def calculate_change(df):
    if df is not None and len(df) > 0:
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        return change
    return 0

app = dash.Dash(__name__)
app.title = "Indian Pharma Stocks Dashboard"

app.layout = html.Div([
    html.Div([
        html.H1('Indian Pharmaceutical Stocks Dashboard', 
                style={
                    'textAlign': 'center', 
                    'color': '#2c3e50', 
                    'marginTop': '30px',
                    'fontFamily': 'Arial, sans-serif'
                }),
        html.P('Live data from National Stock Exchange of India',
               style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '16px'})
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
    ], style={'textAlign': 'center', 'margin': '30px'}),
    
    html.Div(id='graphs-container', style={'padding': '20px'})
], style={'backgroundColor': '#ecf0f1', 'minHeight': '100vh', 'padding': '20px'})

@app.callback(
    Output('graphs-container', 'children'),
    [Input('period-dropdown', 'value')]
)
def update_graphs(selected_period):
    graphs = []
    
    for ticker, name in pharma_stocks.items():
        df = get_stock_data(ticker, selected_period)
        
        if df is not None and len(df) > 0:
            pct_change = calculate_change(df)
            change_color = '#27ae60' if pct_change >= 0 else '#e74c3c'
            change_symbol = 'up' if pct_change >= 0 else 'down'
            
            current_price = df['Close'].iloc[-1]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=df['Close'],
                mode='lines',
                name=name,
                line=dict(color='#3498db', width=2),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.1)'
            ))
            
            fig.update_layout(
                title=f'{name} - {change_symbol} {pct_change:.2f}% | Current: Rs {current_price:.2f}',
                xaxis_title='Date',
                yaxis_title='Price (Rupees)',
                hovermode='x unified',
                height=400,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family='Arial, sans-serif')
            )
            
            graphs.append(
                html.Div([
                    dcc.Graph(figure=fig)
                ], style={
                    'backgroundColor': 'white',
                    'borderRadius': '10px',
                    'padding': '20px',
                    'marginBottom': '20px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
                })
            )
    
    return graphs

if __name__ == '__main__':
    print("Starting dashboard...")
    print("Open your browser and go to: http://127.0.0.1:8050/")
    print("Press CTRL+C to stop the server")
    app.run(debug=True)