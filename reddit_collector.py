# reddit_collector.py
import praw
import re
from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# Let's start simple - just connect and print some posts
def create_reddit_instance():
    """Create and return a Reddit instance using our credentials"""
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
    return reddit

def find_tickers(text):
    """Find stock tickers in text (basic version)"""
    # Match 1-5 uppercase letters that look like tickers
    # This is imperfect but a good start!
    pattern = r'\b[A-Z]{1,5}\b'
    potential_tickers = re.findall(pattern, text)
    
    # Filter out common words that aren't tickers
    common_words = {'I', 'A', 'THE', 'IS', 'IT', 'TO', 'IN', 'OF', 'AND', 'OR', 'FOR'}
    tickers = [t for t in potential_tickers if t not in common_words]
    
    return tickers


def get_posts_with_comments(subreddit_name, limit=5):
    """Get posts AND their top comments"""
    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)

    print(f"DEBUG: Fetching {limit} posts from r/{subreddit_name}")

    posts_data = []
    
    for i, post in enumerate(subreddit.hot(limit=limit)):
        # Combine title and body for analysis
        print(f"DEBUG: Processing post {i+1}: {post.title[:50]}...")
        full_text = f"{post.title} {post.selftext}"
        
        # Get top comments
        post.comments.replace_more(limit=0)  # Remove "more comments" objects
        top_comments = []
        
        for comment in post.comments[:5]:  # Top 5 comments
            if hasattr(comment, 'body'):
                top_comments.append(comment.body)
        
        posts_data.append({
            'title': post.title,
            'text': post.selftext,
            'full_text': full_text,
            'score': post.score,
            'num_comments': post.num_comments,
            'top_comments': top_comments,
            'found_tickers': find_tickers(full_text)
        })
    
        print(f"DEBUG: Found {len(posts_data)} posts")

    return posts_data



# Test it!
if __name__ == "__main__":
    print("Collecting posts from r/stocks...")
    posts = get_posts_with_comments('stocks', limit=3)
    
    for i, post in enumerate(posts, 1):
        print(f"\n{'='*50}")
        print(f"POST {i}: {post['title'][:60]}...")
        print(f"Tickers found: {post['found_tickers']}")
        print(f"Number of comments collected: {len(post['top_comments'])}")
        
        # Show first comment as example
        if post['top_comments']:
            print(f"Sample comment: {post['top_comments'][0][:100]}...")