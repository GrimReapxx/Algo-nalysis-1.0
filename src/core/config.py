import os 
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import Dict,List, Optional

load_dotenv("/config/api_keys.env")

@dataclass
class Settings:
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")
    TWITTER_BEARER_TOKEN: str = os.getenv("TWITTER_BEARER_TOKEN", "")
    BIRDEYE_API_URL: str = "https://public-api.birdeye.so"
    BIRDEYE_API_KEY: str = os.getenv("BIRDEYE_API_KEY", "")
    
    # Database config 
    DATABASE_PATH: str = "/data/algo-nalysis.db"
    
    # Analysis Thresholds
    MEMECOIN_VOLUME_SPIKE_THRESHOLD: float = 500.0
    MEMECOIN_PRICE_DROP_THRESHOLD: float = -30.0
    MEMECOIN_SOCIAL_MENTION_THRESHOLD: int = 1000
    NEW_TOKEN_MIN_LIQUIDITY: float = (30000.0,50000.0) #(min, max)
    
    # Analysis Depth Settings 
    SENTIMENT_ANALYSIS_DEPTH: str = "aspect-level"
    SOCIAL_PLATFORMS: List[str] = field(default_factory=lambda: ["Twitter", "Reddit", "Telegram"])

    # Real-Time Settings
    WEBSOCKET_RECONNECT_INTERVAL: int = 30
    CONSOLE_UPDATE_INTERVAL: int = 10
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Alert System
    EMAIL_ALERTS_ENABLED: bool = True
    CONSOLE_ALERTS_ENABLED: bool = True
    TELEGRAM_ALERTS_ENABLED: bool = False # future implementation 
    
    # Performance settings 
    MAX_CONCURRENT_REQUESTS: int = 15
    CACHE_DURATION: int = 120 # seconds
    DATABASE_BATCH_SIZE: int = 100 
    
settings = Settings()
