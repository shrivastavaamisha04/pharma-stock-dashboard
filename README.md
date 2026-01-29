# 📊 Indian Pharmaceutical Stocks Dashboard

A real-time dashboard displaying live stock data for major Indian pharmaceutical companies listed on the National Stock Exchange (NSE).

## Features

- **Live Stock Data**: Real-time price updates from Yahoo Finance
- **Interactive Charts**: Zoom, pan, and hover for detailed information
- **Comparison View**: Compare all stocks on a normalized chart
- **Performance Metrics**: Market cap, P/E ratio, and trading volume
- **Summary Cards**: Quick view of best/worst performers
- **Multiple Time Periods**: View data from 1 month to 5 years

## Companies Tracked

- Sun Pharma
- Dr. Reddy's Laboratories
- Cipla
- Lupin
- Aurobindo Pharma
- Divi's Laboratories

## Tech Stack

- **Python**: Core programming language
- **Dash**: Web framework for interactive dashboards
- **Plotly**: Data visualization library
- **yfinance**: Yahoo Finance API for stock data
- **Pandas**: Data manipulation and analysis

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the dashboard:
```bash
python dashboard_enhanced.py
```

3. Open your browser to: `http://127.0.0.1:8050/`

## Project Structure

```
pharma-dashboard/
├── dashboard_enhanced.py  # Main application file
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

## Data Source

Stock data is fetched in real-time from Yahoo Finance using the yfinance library.

## Author

Created as a portfolio project demonstrating:
- Data visualization skills
- API integration
- Product management thinking
- Full-stack development capabilities

---

*Last updated: January 2026*
