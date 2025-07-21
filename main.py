from reddit_collector import get_posts_with_comments
from sentiment_analyzer import StockSentimentAnalyzer
from collections import defaultdict
import pandas as pd
from datetime import datetime


class RedditStockSentiment:
    def __init__(self, subreddit='stocks'):
        self.subreddit = subreddit
        self.analyzer = StockSentimentAnalyzer()
        self.ticker_sentiments = defaultdict(list)
        self.ticker_top_posts = {}
        self.ticker_excerpts = defaultdict(list)

    def collect_and_analyze(self, num_posts=10):
        """Collect posts and analyze sentiment for each ticker"""
        print(f"Collecting {num_posts} posts from r/{self.subreddit}...")
        posts = get_posts_with_comments(self.subreddit, limit=num_posts)
        
        for i, post in enumerate(posts, 1):
            print(f"Analyzing post {i}/{num_posts}...")
            
            # Analyze this post
            analysis = self.analyzer.analyze_post_and_comments(post)
            
            # Store sentiment for each ticker mentioned
            if 'ticker_details' in analysis:
                for ticker, details in analysis['ticker_details'].items():
                    # Store sentiment
                    self.ticker_sentiments[ticker].append({
                        'sentiment': details['avg_sentiment'],
                        'post_title': post['title'],
                        'post_score': post['score']
                    })
                    
                    # Store excerpts
                    if 'excerpts' in details:
                        self.ticker_excerpts[ticker].extend(details['excerpts'])
        
        return self.calculate_final_scores()
    
    def calculate_final_scores(self):
        """Calculate average sentiment for each ticker"""
        results = []
        
        for ticker, sentiments in self.ticker_sentiments.items():
            # Calculate metrics
            sentiment_values = [s['sentiment'] for s in sentiments]
            avg_sentiment = sum(sentiment_values) / len(sentiment_values)
            mention_count = len(sentiments)
            

             # Get all excerpts for this ticker
            all_excerpts = self.ticker_excerpts.get(ticker, [])
            
            # Sort excerpts by absolute sentiment (most extreme first)
            all_excerpts.sort(key=lambda x: abs(x['sentiment']), reverse=True)

            # Determine signal
            if avg_sentiment > 0.3:
                signal = "BULLISH"
            elif avg_sentiment < -0.3:
                signal = "BEARISH"
            else:
                signal = "NEUTRAL"
            
            results.append({
                'Ticker': ticker,
                'Avg_Sentiment': round(avg_sentiment, 3),
                'Mentions': mention_count,
                'Signal': signal,
                'excerpts': all_excerpts[:3] 
            })
        
        # Sort by mention count (most discussed first)
        results.sort(key=lambda x: x['Mentions'], reverse=True)
        return results
    
   # Update the display_results method in main.py
    def display_results(self, results):
        """Display results with context excerpts"""
        print("\n" + "="*100)
        print("REDDIT SENTIMENT ANALYSIS RESULTS")
        for result in results:
            print(f"\n📊 {result['Ticker']} - {result['Signal']}")
            print(f"   Sentiment: {result['Avg_Sentiment']} | Mentions: {result['Mentions']}")
            
            # Display most relevant excerpts
            if result.get('excerpts'):  # Use .get() for safety
                print(f"\n   📝 Context from discussions:")
                for i, excerpt in enumerate(result['excerpts'][:2], 1):
                    sentiment_emoji = "🟢" if excerpt['sentiment'] > 0 else "🔴" if excerpt['sentiment'] < 0 else "⚪"
                    # Truncate very long excerpts for display
                    display_text = excerpt['text'][:200] + "..." if len(excerpt['text']) > 200 else excerpt['text']
                    print(f"   {sentiment_emoji} ({excerpt['sentiment']:.2f}) \"{display_text}\"")
            else:
                print("   No specific excerpts found")
            
            print("-" * 100)
        
        print("\n" + "="*100)
        print("INTERPRETATION GUIDE:")
        print("- 🟢 Positive sentiment | 🔴 Negative sentiment | ⚪ Neutral")
        print("- Sentiment > 0.3: BULLISH | < -0.3: BEARISH")
        print("="*100)

if __name__ == "__main__":
    # Create our analyzer
    reddit_sentiment = RedditStockSentiment('stocks')
    
    # Collect and analyze posts
    results = reddit_sentiment.collect_and_analyze(num_posts=5)
    
    # Display results
    reddit_sentiment.display_results(results)
    
    # Bonus: Save to CSV
    df = pd.DataFrame(results)