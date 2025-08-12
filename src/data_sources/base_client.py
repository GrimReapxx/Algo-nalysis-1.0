from abc import ABC, abstractmethod
import asyncio 
import aiohttp
from typing import Dict, Any, Optional
import time 

class BaseAPIClient(ABC):
    
    def __init__(self, base_url: str, rate_limit_per_minute: int = 60):
        self.base_url = base_url
        self.rate_limit = rate_limit_per_minute
        self.last_request_time = 0
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def rate_limit_wait(self):
        elapsed = time.time() - self.last_request_time
        min_interval = 60 / self.rate_limit
        if elapsed < min_interval:
            await asyncio.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
        
    async def make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        await self.rate_limit_wait()
        
        try:
            session = await self.get_session()
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error {response.status}: {await response.text()}")
                return None
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    @abstractmethod
    async def get_market_data(self, coin_ids: list[str]) -> Dict[str, Any]:
        """Fetch market data by each Client."""
        pass
    
    async def cleanup(self):
        if self._session and not self._session.closed:
            await self._session.close()