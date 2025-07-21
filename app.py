# app.py
from flask import Flask, render_template, request, jsonify
from reddit_collector import get_posts_with_comments
from sentiment_analyzer import StockSentimentAnalyzer
from datetime import datetime
import threading
import time

app = Flask(__name__)

class TickerSentimentAnalyzer:
    def __init__(self):
        self.analyzer = StockSentimentAnalyzer()
        self.cache = {}  # Cache results to avoid repeated API calls
        self.cache_duration = 300  # 5 minutes
        
    def analyze_ticker(self, ticker, num_posts=30):
        """Analyze sentiment for a specific ticker"""
        ticker = ticker.upper()
        
        # Check cache first
        if ticker in self.cache:
            cached_time, cached_data = self.cache[ticker]
            if time.time() - cached_time < self.cache_duration:
                return cached_data
        
        print(f"Analyzing sentiment for {ticker}...")
        
        # Collect posts from multiple subreddits
        all_mentions = []
        subreddits = ['stocks', 'wallstreetbets', 'investing', 'StockMarket']
        
        for subreddit in subreddits:
            try:
                posts = get_posts_with_comments(subreddit, limit=num_posts)
                print(f"DEBUG: successfully loaded {len(posts)} from {subreddit}")
                
                for post in posts:
                    # Analyze each post
                    analysis = self.analyzer.analyze_post_and_comments(post)
                    
                    # Check if this ticker is mentioned
                    if ticker in analysis.get('ticker_details', {}):
                        ticker_data = analysis['ticker_details'][ticker]
                        
                        # Get excerpts for this ticker
                        for excerpt in ticker_data.get('excerpts', []):
                            all_mentions.append({
                                'subreddit': subreddit,
                                'title': post['title'],
                                'excerpt': excerpt['text'],
                                'sentiment': excerpt['sentiment'],
                                'post_score': post['score'],
                                'url': f"https://reddit.com{post.get('permalink', '')}" if post.get('permalink') else None
                            })
            except Exception as e:
                print(f"Error fetching from r/{subreddit}: {e}")
        
        # Calculate overall sentiment
        if all_mentions:
            sentiments = [m['sentiment'] for m in all_mentions]
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Determine signal
            if avg_sentiment > 0.3:
                signal = "BULLISH"
                signal_class = "bullish"
            elif avg_sentiment < -0.3:
                signal = "BEARISH"
                signal_class = "bearish"
            else:
                signal = "NEUTRAL"
                signal_class = "neutral"
            
            # Sort mentions by absolute sentiment (most extreme first)
            all_mentions.sort(key=lambda x: abs(x['sentiment']), reverse=True)
            
            result = {
                'ticker': ticker,
                'avg_sentiment': round(avg_sentiment, 3),
                'signal': signal,
                'signal_class': signal_class,
                'mention_count': len(all_mentions),
                'mentions': all_mentions[:10],  # Top 10 most relevant mentions
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            result = {
                'ticker': ticker,
                'avg_sentiment': 0,
                'signal': 'NO DATA',
                'signal_class': 'no-data',
                'mention_count': 0,
                'mentions': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Cache the result
        self.cache[ticker] = (time.time(), result)
        
        return result

# Initialize analyzer
ticker_analyzer = TickerSentimentAnalyzer()

@app.route('/')
def home():
    """Main page with search form"""
    return render_template('index.html')


@app.route('/loading', methods=['POST'])
def loading():
    ticker = request.form['ticker'].strip().upper()
    return render_template('loading.html', ticker=ticker)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a specific ticker"""
    ticker = request.form.get('ticker', '').strip().upper()
    
    if not ticker:
        return jsonify({'error': 'Please enter a ticker symbol'}), 400
    
    # Validate ticker length
    if len(ticker) > 5:
        return jsonify({'error': 'Invalid ticker symbol'}), 400
    
    try:
        result = ticker_analyzer.analyze_ticker(ticker)
        return render_template('results.html', data=result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)