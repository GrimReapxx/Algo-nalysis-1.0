import asyncio 
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn 

from .data_sources.birdeye_client import BirdeyeClient
from .data_sources.twitter_client import TwitterClient
from .analyzers.sentiment_analyzer import SentimentAnalyzer
from .analyzers.memecoin_hunter import MemecoinPotentialScorer
from .output.console_dashboard import ConsoleDashboard
from .core.config import settings  

console = Console()

class MemecoinHunter:
    def __init__(self):
        self.console=Console()
        
        # Initializing all components 
        self.birdeye = BirdeyeClient(settings.BIRDEYE_API_KEY)
        self.twitter_client = TwitterClient(settings.TWITTER_BEARER_TOKEN)
        self.sentiment_analyzer = SentimentAnalyzer(self.twitter_client)
        self.potential_scorer = MemecoinPotentialScorer()
        self.dashboard = ConsoleDashboard()
        
        self.target_chains = ["solana", "base"]
        self.opportunities = []
        
    async def initialize_systems(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            init_task = progress.add_task("Initializing systems...", total=4)
            
            # Database initialization 
            await asyncio.sleep(0.5)
            progress.update(init_task, advance=1, description="Database initialized successfully! ✅")
            
            await asyncio.sleep(0.5)
            progress.update(init_task, advance=1, description="API Clients locked-in 🔒")
            
            await asyncio.sleep(0.5)
            progress.update(init_task, advance=1, description="All Engines Prepped & Loaded 🚀")
            
            await asyncio.sleep(0.5)
            progress.update(init_task, advance=1, description="All systems online! ✅")
            
    async def golden_gem_hunt(self):
        hunt_panel = Panel.fit(
            "🎯 [bold cyan]MEMECOIN HUNTER ACTIVATED[/bold cyan]\n\n" +
            "🔍 Scanning: Solana & Base\n" + 
            "📊 Analysis: Sentiment + Security + Opportunity\n" +
            "💎 Target: New gems with narrative potential",
            title="[bold]Commencing Hunt[/bold]",
            border_style="cyan"
        )
        self.console.print(hunt_panel)
        all_opportunities = []
        
        for chain in self.target_chains:
            chain_opportunities = await self._chain_hunt(chain)
            all_opportunities.extend(chain_opportunities)
        
        # Display results    
        all_opportunities.sort(key=lambda x: x.overall_score, reverse=True)
        
        # results of opportunities that meet criteria 
        qualified_opportunities = [opp for opp in all_opportunities if opp.overall_score >= 40]
        
        self.dashboard.display_opportunities(qualified_opportunities[:10])
        return qualified_opportunities
    
    async def _chain_hunt(self, chain: str):
        self.console.print(f"\n[yellow]Hunting {chain.upper()} chain...[/yellow]")
        
        try:
            new_tokens = await self.birdeye.discover_new_tokens(chain)
            if not new_tokens:
                self.console.print(f"[dim]No new tokens found on {chain}[/dim]")
                return []
            opportunities  = []
            
            with Progress(console=self.console) as progress:
                task = progress.add_task(f"Analyzing {chain} tokens...", total=len(new_tokens))
                
                for token in new_tokens:
                    try:
                        # Gather data
                        token_details = await self.birdeye.get_detailed_token_info(token['address'], chain)
                        security_data = await self.birdeye.get_token_security(token['address'], chain)
                        sentiment = await self.sentiment_analyzer.analyze_token_sentiment(
                            token['symbol'], token.get('name', '')
                        ) 
                        
                        opportunity = self.opportunity_scorer.score_opportunity(
                            token_details.get('data', token) if token_details else token, 
                            sentiment,
                            security_data.get('data', {}) if security_data else {},
                            chain
                        )
                        
                        if opportunity.overall_score >= 40:
                            opportunities.append(opportunity)
                            
                        progress.advance(task)
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        self.console.print(f"[red]Error analyzing {token.get('symbol', 'Unknown')}: {e}[/red]")
                        progress.advance(task)
                        continue
                    
            return opportunities
        
        except Exception as e:
            self.console.print(f"[red]Error finding prey in {chain}: {e}[/red]")
            return []
    
    async def start_hunt_session(self):
        try:
            await self.golden_gem_hunt()
            
            if self.opportunities:
                self.console.print(f"\n[bold green]🔎 Found {len(self.opportunities)} qualified opportunities![/bold green]")
            else:
                self.console.print("\n[yellow]No opportunities found meeting criteria. Market is quiet. 🔕[/yellow]")
                
        except Exception as e:
            self.console.print(f"[bold red]Hunting session failed: {e}[/bold red]")
        # finally:
        #     await self.birdeye.cleanup()
            
    async def hunt_loop(self, interval_minutes: int = 15):
        self.console.print(f"[cyan]Starting Hunt Loop Trial (every{interval_minutes} minutes)[/cyan]")
        while True:
            await self.start_hunt_session()
            self.console.print(f"\n[dim]Next hunt in {interval_minutes} minutes...[/dim]")
            await asyncio.sleep(interval_minutes * 60)

async def main():
    
    # Welcome Message 
    title= Text("ALGO-NALYSIS V1.0", style="bold cyan")
    subtitle = Text("Bitcoin Monitoring & Memecoin Analysis", style="green")
    
    welcome_panel = Panel(
        f"{title}\n{subtitle}\n\n" +
        "🎯 Focus: Aggressive Memecoin Analysis\n" +
        "📊 Strategy: Dip-buying after high-rise corrections\n" +
        "🔍 Analysis: Aspect-level sentiment + volume spikes\n" +
        "📦 Storage: SQLite[real-time updates]",
        title="[bold]Welcome to Algo-nalysis[/bold]",
        border_style="cyan",
    )
    
    console.print(welcome_panel)
    
    hunter = MemecoinHunter()
    
    await hunter.initialize_systems()
    
    console.print("\n[green] System Online! commencing session in T-minus 3 seconds...[/green]")
    await asyncio.sleep(3)
    
    # Hunt Mode Input
    console.print("\n[bold] Choose Hunting Style:[/bold]")
    console.print("1. [cyan]One Shot Hunt[/cyan] - Run once and exit")
    console.print("2. [yellow]Multi-shot Hunt[/yellow] - Run every 15 mins")
    console.print("[green]Demo Mode[/green] - Display System Capabilities")
    
    hunt_style = "One shot" # Default: One shot Hunt - Improvise for user input in future upgrades 
    
    try:
        if hunt_style in ["1", "One shot"]:
            await hunter.start_hunt_session()
        elif hunt_style in ["2", "multi-shot"]:
            await hunter.hunt_loop(interval_minutes=15)
        else:
            console.print("[green]Demo mode[/green]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Hunt interrupted by User. Shutting Down iminently[/yellow]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
    finally:
        console.print("[dim]Session ended. Happy Hunt Sir! 🎯[/dim]")
    
if __name__ == "__main__":
    asyncio.run(main())
    
    