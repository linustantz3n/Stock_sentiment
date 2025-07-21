# sentiment_analyzer.py (updated)
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from ticker_data import load_tickers

class StockSentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.valid_tickers = load_tickers()  # Load comprehensive list
        print(f"Loaded {len(self.valid_tickers)} valid tickers")
        
    def find_tickers(self, text):
        """Find valid stock tickers in text"""
        # Look for $TICKER or TICKER patterns
        pattern = r'\$?[A-Z]{1,5}\b'
        potential_tickers = re.findall(pattern, text.upper())
        
        # Clean and validate against our comprehensive list
        found_tickers = []
        for ticker in potential_tickers:
            ticker = ticker.replace('$', '')
            if ticker in self.valid_tickers:
                found_tickers.append(ticker)
                
        return list(set(found_tickers))
    
    def extract_ticker_context(self, text, ticker, context_length=200):
        """Extract text around ticker mentions for context"""
        excerpts = []
        
        # Search for ticker with or without $
        patterns = [
            rf'\${ticker}\b',  # $TICKER
            rf'\b{ticker}\b'   # TICKER
        ]
        
        for pattern in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            
            for match in matches:
                ticker_start = match.start()
                ticker_end = match.end()
                
                # Calculate context window ensuring ticker is centered
                half_context = context_length // 2
                
                # Start from half context before ticker
                start = max(0, ticker_start - half_context)
                
                # End at half context after ticker
                end = min(len(text), ticker_end + half_context)
                
                # If we're at the beginning, extend the end
                if start == 0:
                    end = min(len(text), ticker_end + context_length)
                
                # If we're at the end, extend the start
                if end == len(text):
                    start = max(0, ticker_start - context_length)
                
                # Extract excerpt
                excerpt = text[start:end].strip()
                
                # Add ellipsis if needed
                if start > 0:
                    excerpt = "..." + excerpt
                if end < len(text):
                    excerpt = excerpt + "..."
                
                # Clean up whitespace
                excerpt = ' '.join(excerpt.split())
                
                # Verify the ticker is actually in the excerpt
                if ticker.upper() in excerpt.upper():
                    excerpts.append(excerpt)
                else:
                    # If ticker got cut off, adjust the window
                    # This handles edge cases where the ticker is at the very edge
                    start = max(0, ticker_start - 20)
                    end = min(len(text), ticker_end + (context_length - 20))
                    excerpt = text[start:end].strip()
                    
                    if start > 0:
                        excerpt = "..." + excerpt
                    if end < len(text):
                        excerpt = excerpt + "..."
                        
                    excerpt = ' '.join(excerpt.split())
                    excerpts.append(excerpt)
        return excerpts
    
    def analyze_sentiment(self, text):
        """Get sentiment scores using VADER"""
        scores = self.vader.polarity_scores(text)
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound']
        }
    
    def analyze_post_and_comments(self, post_data):
        """Analyze sentiment for a post and its comments with context"""
        results = {}
        
        # Combine all text for analysis
        post_text = f"{post_data['title']} {post_data['text']}"
        all_text = post_text + " " + ' '.join(post_data['top_comments'])
        
        # Find all tickers
        all_tickers = self.find_tickers(all_text)
        
        # For each ticker, get sentiment and context
        ticker_details = {}
        
        for ticker in all_tickers:
            # Get excerpts mentioning this ticker
            excerpts = self.extract_ticker_context(all_text, ticker)
            
            # Analyze sentiment of each excerpt
            excerpt_sentiments = []
            for excerpt in excerpts:
                sentiment = self.analyze_sentiment(excerpt)
                excerpt_sentiments.append({
                    'text': excerpt,
                    'sentiment': sentiment['compound']
                })
            
            # Sort excerpts by sentiment (most extreme first)
            excerpt_sentiments.sort(key=lambda x: abs(x['sentiment']), reverse=True)
            
            ticker_details[ticker] = {
                'excerpts': excerpt_sentiments[:3],  # Top 3 most sentiment-heavy excerpts
                'avg_sentiment': sum(e['sentiment'] for e in excerpt_sentiments) / len(excerpt_sentiments) if excerpt_sentiments else 0
            }
        
        # Overall post sentiment
        post_sentiment = self.analyze_sentiment(post_text)
        
        return {
            'tickers': all_tickers,
            'ticker_details': ticker_details,
            'post_sentiment': post_sentiment['compound'],
            'post_score': post_data['score']
        }


if __name__ == "__main__":
    analyzer = StockSentimentAnalyzer()
    
    # Test ticker detection
    test_texts = [
        "AAPL is doing great today!",
        "I bought some $TSLA calls",
        "What do you think about NVDA?",
        "T seems overvalued"  # Testing single letter
    ]
    
    for text in test_texts:
        tickers = analyzer.find_tickers(text)
        print(f"Text: {text}")
        print(f"Found tickers: {tickers}\n")