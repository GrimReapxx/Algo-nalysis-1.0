from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class NarrativeIndicators:
    hype_level: float = 0.0
    fomo_intensity: float = 0.0
    community_growth: float = 0.0
    utility_mentions: float = 0.0
    meme_virality: float = 0.0
    risk_awareness: float = 0.0

@dataclass
class MemecoinPotential:
    token_address: str
    symbol: str
    name: str
    chain: str 
    
    # Market metrics 
    price: float
    market_cap: float
    liquidity: float
    volume_24h: float
    price_change_24h: float
    
    # Sentiment analysis
    narrative_indicators: NarrativeIndicators
    
    # Security analysis
    security_score: float
    security_flags: List[str]
    
    # Potential scoring 
    overall_score: float
    potential_type: str
    confidence: float 
    reasoning: str
    
    timestamp: datetime 
