import ccxt
import time
import json
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd
import argparse
import os

# Configure logging
logging.basicConfig(filename='trade_fetcher.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradeFetcherBot:
    def __init__(self, exchange_name, symbol, fetch_interval, email_notifications):
        self.exchange = getattr(ccxt, exchange_name)()
        self.symbol = symbol
        self.fetch_interval = fetch_interval
        self.email_notifications = email_notifications
        self.trade_data = []

    def send_email_notification(self, message):
        if self.email_notifications:
            try:
                msg = MIMEText(message)
                msg['Subject'] = 'Trade Fetcher Notification'
                msg['From'] = 'ericinnocent04@outlook.com'
                msg['To'] = 'jayy.shoreoff@gmail.com'

                with smtplib.SMTP('smtp.office365.com', 587) as server:
                    server.starttls()
                    server.login('ericinnocent04@outlook.com', 'Monc.Ashborn04')
                    server.send_message(msg)
                logging.info("Email notification sent.")
            except Exception as e:
                logging.error(f"Error sending email: {e}")

    def fetch_recent_trades(self):
        try:
            trades = self.exchange.fetch_trades(self.symbol)
            return trades
        except Exception as e:
            logging.error(f"Error fetching trades: {e}")
            self.send_email_notification(f"Error fetching trades: {e}")
            return []

    def filter_trades(self, trades, min_volume=0):
        return [trade for trade in trades if trade['amount'] >= min_volume]

    def analyze_trades(self, trades):
        if trades:
            df = pd.DataFrame(trades)
            avg_price = df['price'].mean()
            total_volume = df['amount'].sum()
            logging.info(f"Average Price: {avg_price}, Total Volume: {total_volume}")
            return avg_price, total_volume
        return None, None

    def store_data(self):
        with open('trade_data.json', 'w') as f:
            json.dump(self.trade_data, f)
        logging.info("Trade data stored in JSON.")

    def run(self):
        try:
            while True:
                trades = self.fetch_recent_trades()
                filtered_trades = self.filter_trades(trades, min_volume=0.01)  # Example filter
                self.trade_data.extend(filtered_trades)

                avg_price, total_volume = self.analyze_trades(filtered_trades)
                if avg_price is not None:
                    self.store_data()

                time.sleep(self.fetch_interval)
        except KeyboardInterrupt:
            print("Program interrupted. Exiting...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Trade Fetcher Bot')
    parser.add_argument('--exchange', type=str, required=True, help='Exchange name (e.g., binance)')
    parser.add_argument('--symbol', type=str, required=True, help='Trading pair (e.g., BTC/USDT)')
    parser.add_argument('--interval', type=int, default=5, help='Fetch interval in seconds')
    parser.add_argument('--email', action='store_true', help='Enable email notifications')

    args = parser.parse_args()

    bot = TradeFetcherBot(args.exchange, args.symbol, args.interval, args.email)
    bot.run()
