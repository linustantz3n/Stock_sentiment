# Reddit Stock Sentiment Analyzer

A Flask web application that analyzes stock sentiment from Reddit discussions across multiple investment-focused subreddits. The application uses natural language processing to detect stock ticker mentions and analyze the sentiment around them.

## 🚀 Features

- **Real-time Reddit Analysis**: Monitors posts and comments from r/stocks, r/investing, and r/StockMarket
- **Intelligent Caching**: Background refresh system with 10-minute intervals to minimize Reddit API usage
- **VADER Sentiment Analysis**: Advanced sentiment scoring with context-aware ticker detection
- **Interactive Web Interface**: Clean, responsive UI with loading states and real-time progress
- **Comprehensive Ticker Database**: Validates against S&P 500, NASDAQ, and popular meme stocks
- **Signal Classification**: Automatically categorizes sentiment as BULLISH, BEARISH, or NEUTRAL
- **Context Extraction**: Shows relevant excerpts with sentiment scores for transparency

## 📊 How It Works

1. **Data Collection**: Continuously fetches recent posts and top comments from target subreddits
2. **Ticker Detection**: Uses regex patterns to identify stock symbols ($TICKER or TICKER format)
3. **Sentiment Analysis**: VADER analyzer processes text context around ticker mentions
4. **Signal Generation**: Aggregates sentiment scores to generate trading signals
5. **Results Display**: Shows top 10 most sentiment-relevant excerpts with Reddit links

## 🛠️ Installation

### Prerequisites
- Python 3.7+
- Reddit API credentials (see Configuration section)

### Setup
```bash
# Clone the repository
git clone https://github.com/linustantz3n/Stock_sentiment.git
cd reddit_stock_analyzer

# Install dependencies
pip install -r requirements.txt

# Configure Reddit API credentials (see Configuration section)
cp config.py.example config.py
# Edit config.py with your credentials

# Run the application
python app.py
```

Visit `http://localhost:5000` to access the web interface.

## ⚙️ Configuration

Create a `config.py` file in the project root with your Reddit API credentials:

```python
# Reddit API Configuration
REDDIT_CLIENT_ID = 'your_client_id_here'
REDDIT_CLIENT_SECRET = 'your_client_secret_here'
REDDIT_USER_AGENT = 'your_app_name:version (by /u/yourusername)'
```

### Getting Reddit API Credentials
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Note your client ID (under the app name) and client secret

## 🏗️ Architecture

### Core Components

- **`app.py`** - Main Flask application with caching system
- **`reddit_collector.py`** - Reddit API integration using PRAW
- **`sentiment_analyzer.py`** - VADER sentiment analysis with ticker detection
- **`ticker_data.py`** - Stock ticker database management
- **`config.py`** - API credentials (not committed to git)

### Templates
- **`base.html`** - Common layout template
- **`index.html`** - Search form interface
- **`loading.html`** - Progress indicator with real-time updates
- **`results.html`** - Analysis results display

## 🔧 Development Commands

### Running the Application
```bash
python app.py
```

### Type Checking
```bash
mypy .
```

### Testing Individual Components
```bash
python reddit_collector.py    # Test Reddit data collection
python sentiment_analyzer.py  # Test sentiment analysis
python ticker_data.py        # Download/update ticker lists
```

### Updating Ticker Database
```bash
python ticker_data.py
```

## 📈 API Endpoints

- **`GET /`** - Main search interface
- **`POST /analyze`** - Analyze specific ticker sentiment
- **`GET /api/tickers`** - List all available tickers in cache
- **`POST /api/refresh`** - Force cache refresh
- **`GET /check_cache`** - Check if cache is ready

## 🎯 Signal Classification

- **BULLISH** - Average sentiment > 0.3
- **BEARISH** - Average sentiment < -0.3  
- **NEUTRAL** - Average sentiment between -0.3 and 0.3
- **NO DATA** - No mentions found in recent posts

## 📊 Data Sources

- **Reddit Subreddits**: r/stocks, r/investing, r/StockMarket
- **Ticker Database**: S&P 500, NASDAQ, popular ETFs and meme stocks
- **Sentiment Engine**: VADER (Valence Aware Dictionary and sEntiment Reasoner)

## 🔄 Caching System

The application implements a sophisticated caching system:

- **Background Refresh**: Automatically updates data every 10 minutes
- **Post Analysis**: Pre-processes all posts for instant ticker lookups
- **Thread Safety**: Uses locks to ensure data consistency
- **Memory Efficient**: Maintains only recent, relevant data

## 🚨 Rate Limiting

- Reddit API calls are minimized through intelligent caching
- Background refresh prevents user-triggered API overuse
- Configurable refresh intervals (default: 10 minutes)

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational and research purposes only. Stock sentiment analysis should not be used as the sole basis for investment decisions. Always conduct your own research and consult with financial professionals before making investment choices.

## 🐛 Known Issues

- Reddit API rate limits may cause temporary delays during high usage
- Ticker detection may occasionally include false positives
- Sentiment analysis is context-dependent and may not capture all nuances

## 📞 Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/linustantz3n/Stock_sentiment).
