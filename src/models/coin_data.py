from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List

@dataclass
class CoinData:
    id: str
    symbol: str
    name: str
    price: float
    volume_24h: float
    market_cap: float
    price_change_24h: float
    is_memecoin: bool = False
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class SentimentResult:
    platform: str
    overall_sentiment: float
    aspect_scores: Dict[str, float]
    mention_count: int
    confidence: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
            
@dataclass
class TradingPotential:
    coin_id: str
    potential_type: str  # e.g., 'dip_spike', 'volume_spike'
    confidence_score: float
    price_entry: float 
    volume_indicator: float
    sentiment_boost: float
    reasoning: str
    is_active: bool = True
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()