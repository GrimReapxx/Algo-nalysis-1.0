import asyncio 
import os
from rich.console import Console
from rich.panel import Panel 
from rich.table import Table 
from rich.progress import Progress, SpinnerColumn, TextColumn 
from rich.text import Text 
from datetime import datetime
from dotenv import load_dotenv

# Load enviroment variables
load_dotenv('config/api_keys.env')

console = Console()

class APITester:
    def __init__(self):
        self.console = console
        self.test_results = {}
        
        self.api_keys = { 
            'BIRDEYE_API_KEY': os.getenv('BIRDEYE_API_KEY'),
            'TWITTER_BEARER_TOKEN': os.getenv('TWITTER_BEARER_TOKEN'),
            'COINGECKO_API_KEY': os.getenv('COINGECKO_API_KEY', 'demo'),
        }
        
    async def enviroment_test_setup(self):
        self.console.print("\n[bold cyan]🔧 TESTING ENVIROMENT SETUP[/bold cyan]")
        
        env_table = Table(title="Enviroment Variables check")
        env_table.add_column("API Key", style="cyan")
        env_table.add_column("Status", style="green")
        env_table.add_column("Value Preview", style="dim")
        
        env_results = {}
        
        for key, value in self.api_keys.items():
            if value:
                status = "✅ Found"
                preview = f"{value[:8]}..." if len(value) > 8 else value 
                env_results[key] = True
            else:
                status = "❌ Missing"
                preview = "Not set"
                env_results[key] = False 
                
            env_table.add_row(key, status, preview)
            
        self.console.print(env_table)
        
        self.test_results.update(env_results)
        return all(env_results.values())
    
    async def test_birdeye_api(self):
        self.console.print("\n[bold yellow]🦅 TESTING BIRDEYE API[/bold yellow]") 
        
        if not self.api_keys['BIRDEYE_API_KEY']:
            self.console.print("[red]❌ Birdeye API key not found[/red]")
            return False
        
        try:
            import aiohttp
            
            headers = {
                "X-API-KEY": self.api_keys['BIRDEYE_API_KEY'],
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                self.console.print("Testing basic connectivity...")
                async with session.get(
                    "https://public-api.birdeye.so/defi/tokenlist",
                    headers=headers,
                    params={"sort_by": "v24hUSD", "sort_type": "desc", "offset": 0, "limit": 5}
                ) as response: 
                    if response.status == 200:
                        data = await response.json()
                        self.console.print("✅ Birdeye API: Connected sucessfully")
                        self.console.print(f"📊 Sample Data received: {len(data.get('data', {}).get('tokens', []))} tokens")
                        return True
                    else:
                        error_text = await response.text()
                        self.console.print(f"❌ Birdeye API Error {response.status}: {error_text}")
                        return False
                    
        except Exception as e:
            self.console.print(f"❌ Birdeye API Connection Failed: {e}")
            return False
        
    async def test_twitter_api(self):
        self.console.print("\n[bold blue]🐦 TESTING TWITTER API[/bold blue]")
        
        if not self.api_keys['TWITTER_BEARER_TOKEN']:
            self.console.print("[red]❌ Twitter Bearer Token not found[/red]")
            return False
        
        try:
            import tweepy
            
            client = tweepy.client(bearer_token=self.api_keys['TWITTER_BEARER_TOKEN'])
            self.console.print("Testing Twitter API Connectivity...")
            
            tweets = client.search_recent_tweets( 
                query="bitcoin -is:retweet lang:en",
                max_results=10,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            
            if tweets and tweets.data:
                self.console.print("✅ Twitter API: Connect Sucessfully")
                self.console.print(f"📊 Retrieved {len(tweets.data)} sample tweets")
                
                sample_tweet = tweets.data[0].text[:50] + "..." if len(tweets.data[0].text) > 50 else tweets.data[0].text
                self.console.print(f"📝 Sample tweet: \"{sample_tweet}\"")
                return True
            else:
                self.console.print("❌ Twitter API: No data returned")
                return False
            
        except Exception as e:
            self.console.print(f"❌ Twitter API Connection Failed: {e}")
            self.console.print("💡 Make sure your Bearer Token has the correct permissions")
            return False
    
    async def test_coingecko_api(self):
        self.console.print("\n[bold green]🦎 TESTING COINGECKO API[/bold green]")
        
        try:
            import aiohttp
            
            headers = {}
            if self.api_keys['COINGECKO_API_KEY'] and self.api_keys['COINGECKO_API_KEY'] != 'demo':
                headers['x-cg-demo-api-key']  = self.api_keys['COINGECKO_API_KEY']
                
            async with aiohttp.ClientSession() as session:
                self.console.print("Testing CoinGecko connectivity...")
                async with session.get(
                    "https://api.coingecko.com/api/v3/simple/price",
                    headers=headers,
                    params={"ids": "bitcoin,ethereum", "vs_currencies": "usd", "include_24hr_change": "true"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        self.console.print("CoinGecko API: Connected Successfully")
                        
                    if 'bitcoin' in data:
                        btc_price = data['bitcoin']['usd']
                        btc_change = data['bitcoin']['usd_24hr_change']
                        self.console.print(f"📊 BTC Price: ${btc_price:,.2f} ({btc_change:+.2f}% 24h)")
                        
                        return True
                    else:
                        error_text = await response.json()
                        self.console.print(f" CoinGecko API Error {response.status}: {error_text}")
                        return False
        except Exception as e:
            self.console.print(f"CoinGecko API Connection Failed: {e}")
            return False
        
    async def test_memecoin_hunter_integration(self):
        self.console.print("\n[bold magenta]🎯 TESTING MEMECOIN HUNTER INTEGRATION[/bold magenta]")
        
        try:
            from src.data_sources.birdeye_client import BirdeyeClient
            from src.data_sources.twitter_client import TwitterClient
            from src.analyzers.sentiment_analyzer import SentimentAnalyzer
            
            self.console.print("Initializing MemecoinHunter components...")
            
            birdeye = BirdeyeClient(self.api_keys['BIRDEYE_API_KEY'])
            twitter_client = TwitterClient(self.api_keys['TWITTER_BEARER_TOKEN'])
            sentiment_analyzer = SentimentAnalyzer(twitter_client)
            
            self.console.print("✅ All components initialized successfully")
            self.console.print("Testing basic workflow...")
            
            sample_tokens = await birdeye.discover_new_tokens("solana")
            
            if sample_tokens:
                self.console.print(f"✅ Workflow test: Found {len(sample_tokens)} tokens")
                
                sentiment = await sentiment_analyzer.analyze_token_sentiment("SOL", "solana")
                self.console.print(f"✅ Sentiment analysis: Hype level {sentiment.hype_level:.1f}")
                
                return True
            else:
                self.console.print("⚠️ No tokens found, but integration works")
                return True
            
        except ImportError as e:
            self.console.print(f"❌Import Error: {e}")
            self.console.print("💡 Make sure your structure matches the imports")
            return False
        except Exception as e:
            self.console.print(f"Integration Test Failed: {e}")
            return False
        
    async def run_full_test_suite(self):
        
        # Welcome
        welcome_panel = Panel.fit(
            "🧪 [bold cyan]API INTEGRATION TEST SUITE[/bold cyan]\n\n" +
            "Testing all components before dashboard launch\n" +
            "This will validate your API keys and integrations",
            title="[bold]API Test Suite[/bold]",
            border_style="cyan"
        )
        
        self.console.print(welcome_panel)
        
        final_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            task = progress.add_task("Running tests...", total=5)
            
            # Test 1: Enviroment
            progress.update(task, description="Testing enviroment setup...")
            final_results['enviroment'] = await self.enviroment_test_setup()
            progress.advance(task)
            
            # Test 2: Birdeye
            progress.update(task, description="Testing Birdeye API...")
            final_results['birdeye'] = await self.test_birdeye_api()
            progress.advance(task)
            
            # Test 3: Twitter
            progress.update(task, description="Testing Twitter API...")
            final_results['twitter'] = await self.test_twitter_api()
            progress.advance(task)
            
            # Test 4: CoinGecko
            progress.update(task, description="Testing CoinGecko API...")
            final_results['coingecko'] = await self.test_coingecko_api()
            progress.advance(task)
            
            # Test 5: Integration
            progress.update(task, description="Testing full integration...")
            final_results['integration'] = await self.test_memecoin_hunter_integration()
            progress.advance(task)
            
        self.display_test_summary(final_results)
        
        return final_results
    
    def display_test_summary(self, results):
        summary_table = Table(title="🧪 API Test Results Summary")
        summary_table.add_column("Component", style="cyan")
        summary_table.add_column("Status", style="green")
        summary_table.add_column("Next Steps", style="yellow")
        
        passed = sum(results.values())
        total= len(results)
        
        for test, passed_status in results.items():
            status = "✅ PASSED" if passed_status else "❌ FAILED"
            
            if passed_status:
                next_steps  ="Ready for production"
            else:
                if test == 'enviroment':
                    next_steps = "Add missing API keys to .env"
                elif test == 'birdeye':
                    next_steps = "Check Birdeye API key validity"
                elif test == 'twitter':
                    next_steps = "Verify Twitter Bearer Token permissions"
                elif test == 'coingecko':
                    next_steps = "CoinGecko validity setup"
                else:
                    next_steps = "Fix import paths and dependencies"
                    
            summary_table.add_row(test.title(), status, next_steps)
            
        self.console.print(summary_table)
        
        if passed == total:
            status_panel = Panel.fit(
                "✅ [bold green]ALL TESTS PASSED![/bold green]\n\n" +
                "✅ Environment configured correctly\n" +
                "✅ All API connections working\n" +
                "✅ Ready to launch MemecoinHunter\n\n", # Return to modify!!
                title="[bold green]Test Suite Complete[/bold green]",
                border_style="green"  
            )
        else:
            failed_tests = [test for test, result in results.items() if not result]
            status_panel = Panel.fit(
                f"⚠️  [bold yellow]{passed}/{total} TESTS PASSED[/bold yellow]\n\n" +
                f"❌ Failed: {', '.join(failed_tests)}\n\n" +
                "📋 Check the 'Next Steps' column above\n" +
                "🔧 Fix failed components before proceeding",
                title="[bold yellow]Action Required[/bold yellow]",
                border_style="yellow"
            )
            
        self.console.print(status_panel)
        
async def main():
    tester = APITester()
    results = await tester.run_full_test_suite()
    
    if all(results.values()):
        console.print("\n[bold cyan] QUICK START:[/bold cyan]")
        console.print("1. Run `python -m src.main` to start hunt")
        console.print("2. Check Console for real-time data results")
        console.print("3. Monitor for Dip-buying signals")
        
        
if __name__ == "__main__":
    asyncio.run(main())
        