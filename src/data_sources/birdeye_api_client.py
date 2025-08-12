import asyncio
import aiohttp 
import json 
import time 
import tweepy 
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from rich.console import Console 
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

console = Console()

class BirdeyeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://public-api.birdeye.so"
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.chains = {
            "solana": "solana",
            "base": "base",
        }
        self.min_liquidity = 50000
        self.min_volume_24h = 100000
        self.max_age_hours = 24
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        try:
            session = await self.get_accessed()
            url = f"{self.base_url}/{endpoint}"
            
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    console.print(f"[red]Birdeye API Error {response.status}: {await response.text()}[/red]")
                    return None
        except Exception as e:
            console.print(f"[red]Request Failed: {e}[/red]")
            return None
        
    async def discover_new_tokens(self, chain: str = "solana") -> List[Dict]:
        console.print(f"[yellow]🔍 Scanning {chain.upper()} for new memecoins...[/yellow]")
        
        params = {
            "sort_by": "created_time",
            "sort_type": "desc",
            "offset": 0,
            "limit": 50
        }
        
        response = await self.make_request(f"/defi/tokenlist?chain={chain}", params)
        if not response or 'data' not in response:
            return []
        
        new_tokens = []
        for token in response['data']['tokens']:
            if self.meets_criteria(token):
                new_tokens.append(token)

        console.print(f"[green]✅ Found {len(new_tokens)} potential new tokens on {chain.upper()}[/green]")
        return new_tokens
    
    def meets_criteria(self, token: Dict) -> bool:
        """Check if token meets our memecoin criteria"""
        try:
            # Basic filters
            liquidity = float(token.get('liquidity', 0))
            volume_24h = float(token.get('volume_24h', 0))
            creation_time = token.get('creation_time')
            if creation_time:
                token_age = (datetime.now() - datetime.fromtimestamp(creation_time))
                if token_age.total_seconds() > self.max_age_hours * 3600:
                    return False
            return (
                liquidity >= self.min_liquidity and
                volume_24h >= self.min_volume_24h and
                token.get('symbol') is not None and
                len(token.get('symbol', '')) <= 10
            )
        except (ValueError, TypeError):
            return False
        
    async def get_token_security(self, token_address: str, chain: str) -> Dict:
        params = {"address": token_address}
        return await self.make_request(f"/defi/token_security?chain={chain}", params)
    
    async def get_detailed_token_info(self, token_address: str, chain: str) -> Dict:
        params = {"address": token_address}
        return await self.make_request(f"/defi/token_overview?chain={chain}", params)