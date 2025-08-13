from textblob import TextBlob
from typing import List 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from ..models.analysis_result import NarrativeIndicators
from ..data_sources.twitter_client import TwitterClient

class SentimentAnalyzer:
    def __init__(self, twitter_client:TwitterClient):
        self.twitter_client = twitter_client
        self.vader = SentimentIntensityAnalyzer()
        
        self.narrative_keywords = {
            'hype': ['moon', '🚀', 'rocket', 'bullish', 'pump', 'gem', 'alpha', 'lfg'],
            'fomo': ['fomo', 'dont miss', 'last chance', 'going crazy', 'exploding', 'parabolic'],
            'community': ['community', 'holders', 'diamond hands', '💎', 'hodl', 'strong hands'],
            'utility': ['utility', 'usecase', 'product', 'development', 'roadmap', 'team'],
            'meme': ['meme', 'viral', 'funny', 'lol', '😂', 'hilarious', 'based'],
            'risk': ['rug', 'scam', 'careful', 'dyor', 'risky', 'beware', 'sus', 'copytraders', 'crash']
        }
    
    async def analyze_token_sentiment(self, token_symbol: str, token_name: str = "") -> NarrativeIndicators:
          queries = [f"${token_symbol}", token_name, f"{token_symbol} token"]
          
          all_tweets = []
          for query in queries:
              if query:
                  tweets = await self.twitter_client.fetch_recent_tweets(query, max_results=100)
                  all_tweets.extend(tweets)
                  
          if not all_tweets:
              return NarrativeIndicators()
          
          return self.analyze_narrative_aspects(all_tweets)
      
    def analyze_narrative_aspects(self,  tweets: List[str]) -> NarrativeIndicators:
        indicators = NarrativeIndicators()
        
        if not tweets:
            return indicators
        
        aspect_scores = {aspect: [] for aspect in self.narrative_keywords.keys()}
        
        for tweet in tweets:
            tweet_lower = tweet.lower()
            sentiment = self.vader.polarity_scores(tweet)
            
            # Check for narrative keywords
            for aspect, keywords in self.narrative_keywords.items():
               aspect_score = 0
               keyword_count = 0
               
               for keyword in keywords:
                   if keyword in tweet_lower:
                       keyword_count += 1
                       aspect_score += sentiment['compound']
               if keyword_count > 0:
                   aspect_scores[aspect].append(aspect_score / keyword_count)
                   
        indicators.hype_level = self._calculate_aspect_score(aspect_scores['hype'])
        indicators.fomo_intensity = self._calculate_aspect_score(aspect_scores['fomo'])
        indicators.community_growth = self._calculate_aspect_score(aspect_scores['community'])
        indicators.utility_mentions = self._calculate_aspect_score(aspect_scores['utility'])
        indicators.meme_virality = self._calculate_aspect_score(aspect_scores['meme'])
        indicators.risk_awareness = abs(self._calculate_aspect_score(aspect_scores['risk']))
        
        return indicators
    
    def _calculate_aspect_score(self, scores: List[float]) -> float:
        if not scores:
            return 0.0
        
        avg_score = sum(scores) / len(scores)
        normalized = ((avg_score +1) / 2) * 100
        return round (normalized, 2)
        