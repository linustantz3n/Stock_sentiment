# ticker_data.py
import requests
import pandas as pd
import yfinance as yf
import pickle



popular_additions = {
        'GME', 'AMC', 'BB', 'NOK', 'BBBY', 'PLTR', 'NIO', 'LCID', 
        'RIVN', 'SOFI', 'WISH', 'CLOV', 'SPCE', 'DKNG', 'PENN',
        'COIN', 'HOOD', 'RBLX', 'ABNB', 'DASH', 'SNOW', 'U', 'AI',
        'QQQ', 'SPY', 'IWM', 'DIA', 'VTI', 'VOO', 'AAPL', 'T', 'TSLA'  # Popular ETFs
    }
def download_all_tickers():
    """Download a comprehensive list of stock tickers"""
    
    print("Downloading ticker lists...")
    
    all_tickers = set()
    
    # Method 1: Get S&P 500 tickers from Wikipedia
    all_tickers.update(get_nasdaq_tickers())
    all_tickers.update(get_sp500_tickers())
    
    # Method 2: Add popular tech/meme stocks manually
  
    all_tickers.update(popular_additions)
    
    # Save to file for offline use
    with open('tickers.txt', 'w') as f:
        for ticker in sorted(all_tickers):
            f.write(f"{ticker}\n")
    
    print(f"Total tickers collected: {len(all_tickers)}")
    return all_tickers

def load_tickers():
    """Load tickers from file or download if not exists"""
    try:
        with open('tickers.txt', 'r') as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return download_all_tickers()




def get_sp500_tickers():
    """Get S&P 500 tickers using yfinance"""
    try:
        # Get S&P 500 ticker list
        sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        return set(sp500['Symbol'].str.replace('.', '-').tolist())
    except:
        # Fallback to manual list
        print("DEBUG: failed to import sp500")
        return set()

def get_nasdaq_tickers():
    """Get NASDAQ listed tickers"""
    try:
        nasdaq_url = "https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=5000"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(nasdaq_url, headers=headers)
        data = response.json()
        
        tickers = set()
        for row in data['data']['rows']:
            ticker = row['symbol']
            if ticker.isalpha() and len(ticker) <= 5:  # Basic validation
                tickers.add(ticker)
        return tickers
    except:
        print("DEBUG: failed to import nasdaq")
        return set()

# Run once to create the ticker file
if __name__ == "__main__":
    tickers = download_all_tickers()
    print(f"\nSample tickers: {list(tickers)[:10]}")