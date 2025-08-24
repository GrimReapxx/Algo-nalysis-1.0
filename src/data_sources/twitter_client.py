import tweepy 
from typing import Dict, List, Optional
from rich.console import Console

class TwitterClient:
    def __init__(self, bearer_token: str):
        self.client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
        self.console = Console()
        
    async def fetch_recent_tweets(self, query: str, max_results: int = 100) -> List[str]:
        try: 
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query= f"{query}-is:retweet lang:en",
                max_results=max_results,
                tweet_fields=['created_at','public_metrics']
            ).flatten(limit=max_results)
            
            return [tweet.text for tweet in tweets if tweet.text]
        except Exception as e:
            self.console.print(f"[red]Twitter API Error: {e}[/red]")
            return []
        
    async def get_tweet_metrics(self, query:str) -> dict:
        """Get metrics for a tweets about a topic"""
        try:
            tweets = await self.fetch_recent_tweets(query)
            if not tweets:
                return {"error": "No tweets found"}

            # Get metrics for each tweet
            metrics = {}
            for tweet in tweets:
                metrics[tweet.id] = {
                    "likes": tweet.public_metrics['like_count'],
                    "retweets": tweet.public_metrics['retweet_count'],
                    "replies": tweet.public_metrics['reply_count'],
                }
            return metrics
        except Exception as e:
            self.console.print(f"[red]Twitter API Error: {e}[/red]")
            return {"error": str(e)}