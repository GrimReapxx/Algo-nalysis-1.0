from datetime import datetime, timedelta
import pytz
import requests
import pandas as pd
from rich.console import Console
from rich.table import Table
import numpy as np
from textblob import TextBlob

API_KEY='RPKG4TZC9UCV70JU' # Alpha vantage forex api

def get_current_time():
    return datetime.now(pytz.utc)

def get_forex_sessions():
    return {
        "Sydney":{"start": timedelta(hours=22), "end": timedelta(hours=7)},
        "Tokyo":{"start": timedelta(hours=0), "end": timedelta(hours=9)},
        "London":{"start": timedelta(hours=8), "end": timedelta(hours=17)},
        "New York":{"start": timedelta(hours=13), "end": timedelta(hours=22)},
    }
    
def get_active_sessions(current_time, sessions):
    active_sessions = []
    # convert current time to hours for easier comparison
    current_hour = current_time.hour + current_time.minute/60.0
    
    for session, times in sessions.items():
        # Get session times in hours
        start_hour = times["start"].total_seconds()/3600
        end_hour = times["end"].total_seconds()/3600
        
        # Handle sessions that span across midnight
        if start_hour > end_hour:
            # Session spans across midnight
            if current_hour >= start_hour or current_hour <= end_hour:
                active_sessions.append(session)
        else:
            # Normal session within same day
            if start_hour <= current_hour <= end_hour:
                active_sessions.append(session)
    return active_sessions
    
def get_upcoming_session(current_time, sessions):
    upcoming_sessions = []
    current_hour = current_time.hour + current_time.minute/60.0
    
    for session, times in sessions.items():
        start_hour = times["start"].total_seconds()/3600
        
        # Handle sessions that might start tomorrow
        if start_hour < current_hour:
            # Session starts tomorrow
            upcoming_sessions.append(session)
        elif start_hour > current_hour:
            # Session starts later today
            upcoming_sessions.append(session)
    return upcoming_sessions
    
def fetch_market_data(pair):
    url = f"https://www.alphavantage.co/query?function=FX_DAILY&from_symbol={pair.split('/')[0]}&to_symbol={pair.split('/')[1]}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    # Print the response data for debugging
    print(f"Fetching data for {pair}...")
    # print("API Response:", data)
    
    return data

def analyze_volatility(data):
    # Check if the expected key exists in the data
    if 'Time Series FX (Daily)' not in data:
        raise ValueError("Invalid data format: 'Time Series FX (Daily)' key not found.")
    
    df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
    df.columns = ['open', 'high', 'low', 'close']
    df = df.astype(float)
    
    df['range'] = df['high'] - df['low']
    volatility = df['range'].mean()
    
    return volatility

def display_market_data(data):
    # Convert the data to a DataFrame
    df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
    df.columns = ['Open', 'High', 'Low', 'Close']
    df = df.astype(float)

    # Set display options for better readability
    pd.set_option('display.float_format', '${:,.2f}'.format)
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.width', 1000)     # Set display width

    # Print the DataFrame for structured output
    print("Structured DataFrame Output:")
    # print(df)

    # Now use rich for a colorful table
    console = Console()
    table = Table(title="Market Data", title_style="bold magenta")

    table.add_column("Date", justify="right", style="cyan")
    table.add_column("Open", justify="right", style="green")
    table.add_column("High", justify="right", style="green")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Close", justify="right", style="green")

    for date, values in data['Time Series FX (Daily)'].items():
        table.add_row(date, f"${float(values['1. open']):,.2f}", 
                      f"${float(values['2. high']):,.2f}", 
                      f"${float(values['3. low']):,.2f}", 
                      f"${float(values['4. close']):,.2f}")

    console.print(table)

def analyze_historical_data(data):
    # Convert the historical data to a DataFrame
    df = pd.DataFrame.from_dict(data['Time Series FX (Daily)'], orient='index')
    df.columns = ['Open', 'High', 'Low', 'Close']
    df = df.astype(float)

    # Calculate moving averages
    df['SMA_20'] = df['Close'].rolling(window=20).mean()  # 20-day simple moving average
    df['SMA_50'] = df['Close'].rolling(window=50).mean()  # 50-day simple moving average

    # Identify crossover points
    df['Signal'] = 0
    df.iloc[20:, df.columns.get_loc('Signal')] = np.where(df['SMA_20'].iloc[20:] > df['SMA_50'].iloc[20:], 1, 0)  # Buy signal
    df['Position'] = df['Signal'].diff()

    # Identify trends and reversals
    trends = df[df['Position'] == 1].index.tolist()  # Buy signals
    reversals = df[df['Position'] == -1].index.tolist()  # Sell signals

    return trends, reversals

def display_trends_reversals(trends, reversals):
    console = Console()
    
    # Create a table for trends
    trends_table = Table(title="Identified Trends", title_style="bold green")
    trends_table.add_column("Date", justify="right", style="cyan")
    
    for trend in trends:
        trends_table.add_row(trend)
    
    console.print(trends_table)

    # Create a table for reversals
    reversals_table = Table(title="Identified Reversals", title_style="bold red")
    reversals_table.add_column("Date", justify="right", style="cyan")
    
    for reversal in reversals:
        reversals_table.add_row(reversal)
    
    console.print(reversals_table)

def fetch_news_sentiment(api_key):
    url = f"https://newsapi.org/v2/everything?q=forex&apiKey={api_key}"
    response = requests.get(url)
    news_data = response.json()

    sentiments = []
    for article in news_data['articles']:
        text = (article['title'] or "") + " " + (article['description'] or "")
        sentiment = TextBlob(text).sentiment.polarity  # Get sentiment polarity
        sentiments.append({
            'title': article['title'],
            'description': article['description'],
            'sentiment': sentiment
        })

    return sentiments

def display_news_sentiment(news_sentiment):
    console = Console()
    
    # Create a table for news sentiment
    news_table = Table(title="News Sentiment Analysis", title_style="bold magenta")
    news_table.add_column("Title", justify="left", style="green")
    news_table.add_column("Sentiment", justify="right", style="yellow")
    
    for news in news_sentiment:
        news_table.add_row(news['title'], f"{news['sentiment']:.2f}")
    
    console.print(news_table)

def display_analysis_results(volatility, trends, reversals):
    console = Console()
    
    # Create a table for analysis results
    analysis_table = Table(title="Market Analysis Results", title_style="bold blue")
    
    # Add columns
    analysis_table.add_column("Metric", style="cyan")
    analysis_table.add_column("Value", style="green")
    
    # Add volatility
    analysis_table.add_row("Average Volatility", f"{volatility:.4f}")
    
    # Add trends
    trends_str = "\n".join(trends) if trends else "No trends identified"
    analysis_table.add_row("Trend Dates", trends_str)
    
    # Add reversals
    reversals_str = "\n".join(reversals) if reversals else "No reversals identified"
    analysis_table.add_row("Reversal Dates", reversals_str)
    
    console.print(analysis_table)

def main():
    while True:
        pair = input("Enter currency pair (e.g., GBP/JPY, EUR/USD): ").upper()
        # Validate input format
        if '/' in pair and len(pair.split('/')) == 2:
            if all(len(currency) == 3 for currency in pair.split('/')):
                break
            else:
                print("Each currency code should be 3 letters (e.g., USD, EUR, GBP)")
        else:
            print("Invalid format. Please use format like 'EUR/USD'")
    
    current_time = get_current_time()
    sessions = get_forex_sessions()
    
    active_sessions = get_active_sessions(current_time, sessions)
    upcoming_sessions = get_upcoming_session(current_time, sessions)
    
    print(f"Current Time (GMT): {current_time}")
    print(f"Active Sessions: {active_sessions}")
    print(f"Upcoming Sessions: {upcoming_sessions}")
    
    # Move analysis outside the sessions loop
    print(f"Analyzing market conditions for {pair}...")
    market_data = fetch_market_data(pair)
    display_market_data(market_data)
    
    trends, reversals = analyze_historical_data(market_data)
    display_trends_reversals(trends, reversals)
    
    news_sentiment = fetch_news_sentiment('e5a8dbc140154c97aace5e76a35a772d')
    display_news_sentiment(news_sentiment)
    
    volatility = analyze_volatility(market_data)
    display_analysis_results(volatility, trends, reversals)

    # Ask user if they want to analyze another currency pair
    another_pair = input("Do you want to analyze another currency pair? (yes/no): ").strip().lower()
    if another_pair == 'yes':
        main()

# Ask user if they want to analyze another currency pair
another_pair = input("Do you want to analyze another currency pair? (yes/no): ").strip().lower()
if another_pair == 'yes':
    main()  # Restart the main function
        