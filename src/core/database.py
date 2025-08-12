import sqlite3
import json
from config import settings
from datetime import datetime 
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = settings.DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        with self.get_connection() as conn:
            # Coin data table 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coins(
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL, 
                    is_memecoin BOOLEAN DEFAULT FALSE,
                    first_detected TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Price data table 
            conn.execute("""
                CREATE TABLE IF NOT EXISTS price_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    price REAL NOT NULL,
                    volume_24h REAL, 
                    market_cap REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(coin_id) REFERENCES coins(id)
                )
                """)
            
            #Sentiment_analysis table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_data(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    sentiment_score REAL NOT NULL, 
                    aspect_scores TEXT, -- JSON for aspect-level analysis 
                    mention_count INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                    FOREIGN KEY (coin_id) REFERENCES coins(id)
                )
                 """)
            
            # Trading potential table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trading_potential(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    coin_id TEXT NOT NULL,
                    potential_type TEXT NOT NULL, -- 'dip_spike', 'volume_spike'
                    confidence_score REAL NOT NULL,
                    details TEXT, -- JSON for additional details
                    is_active BOOLEAN DEFAULT TRUE, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (coin_id) REFERENCES coins(id)
                 )
                 """)
            
            # Performance Indexing
            conn.execute("CREATE INDEX IF NOT EXISTS idx_price_timestamp ON price_data(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_coin_symbol ON coins(symbol)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_potential_active ON trading_potential(is_active)")
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
            
    def insert_coin_data(self, coin_data: Dict[str, Any]) -> bool:
        try: 
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO coins(id, symbol, name, is_memecoin, last_updated)
                    VALUES(?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    coin_data['id'], 
                    coin_data['symbol'], 
                    coin_data['name'], 
                    coin_data.get('is_memecoin', False)
                        ))
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
        
# Database Instance        
db = DatabaseManager()