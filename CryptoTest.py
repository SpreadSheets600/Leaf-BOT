# import os
# import finnhub
# from coinpaprika.client import Client

# from dotenv import *
# load_dotenv()

# finnhub = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
# coinpaprika = Client()

# def get_stock_price(symbol: str):
#     data = coinpaprika.ticker(symbol)
#     return data

# coin = "BTC - Bitcoin".replace(" ","").lower()

# print(get_stock_price(coin))
# coins = coinpaprika.coins()

# # Only First 20 Coins
# search = input("Search Coin : ")

# search_coins = []

# for coin in coins:
#     if search.lower() in coin["name"].lower():
#         search_coins.append(coin)

# print(search_coins[0])


# import matplotlib.pyplot as plt

# # Time intervals
# time_intervals = ['15m', '30m', '1h', '6h', '12h', '24h']

# # Percentage changes corresponding to the time intervals
# percentage_changes = [0.03, -0.02, 0.08, 0.06, 0.66, 0.37]

# # Create the plot
# plt.figure(figsize=(10, 6))
# plt.plot(time_intervals, percentage_changes, marker='o', color='b')

# # Add labels and title
# plt.xlabel('Time Interval')
# plt.ylabel('Percentage Change')
# plt.title('Percentage Change in Bitcoin Price Over Different Time Intervals')

# # Display the grid
# plt.grid(True)

# # Show the plot
# plt.show()

# import requests
# import matplotlib.pyplot as plt
# from datetime import datetime

# # Function to get Bitcoin data from CoinGecko
# def get_bitcoin_data(days):
#     url = f"https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days={days}&interval=daily"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print("Error fetching data")
#         return None

# # Function to plot Bitcoin price over time
# def plot_bitcoin_data(data):
#     prices = data['prices']
    
#     # Extract dates and prices
#     dates = [datetime.fromtimestamp(item[0] / 1000) for item in prices]
#     btc_prices = [item[1] for item in prices]
    
#     # Plot the data
#     plt.figure(figsize=(10, 6))
#     plt.plot(dates, btc_prices, label="Bitcoin Price (USD)", color='b', marker='o', markersize=2)
    
#     plt.xlabel('Date')
#     plt.ylabel('Price (USD)')
#     plt.title('Bitcoin Price Over Time')
#     plt.grid(True)
#     plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
#     plt.tight_layout()
#     plt.legend()
    
#     # Show the plot
#     plt.show()

# # Main execution
# if __name__ == "__main__":
#     # Get Bitcoin data for the past 30 days (you can adjust the number of days)
#     days = 30
#     bitcoin_data = get_bitcoin_data(days)
    
#     if bitcoin_data:
#         plot_bitcoin_data(bitcoin_data)


import requests
import pandas as pd
import mplfinance as mpf
from datetime import datetime
import matplotlib.pyplot as plt

# Fetch data from CoinGecko API
url = 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=20'

response = requests.get(url)
data = response.json()


df = pd.DataFrame(data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close_time', 'Quote_asset_volume', 'Number_of_trades', 'Taker_buy_base', 'Taker_buy_quote', 'Ignore'])

# Convert values to the appropriate data types
df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='ms')
df['Open'] = df['Open'].astype(float)
df['High'] = df['High'].astype(float)
df['Low'] = df['Low'].astype(float)
df['Close'] = df['Close'].astype(float)
df['Volume'] = df['Volume'].astype(float)

# Set the 'Timestamp' as the index for the candlestick chart
df.set_index('Timestamp', inplace=True)

# plot background color to black
mc = mpf.make_marketcolors(up='#49c686',down='#c2423f',inherit=True)
plot = mpf.plot(df, type='candle', style='nightclouds', title='Bitcoin Price', ylabel='Price (USD)', volume=True, figscale=1.5, figratio=(10,6))

plt.show()