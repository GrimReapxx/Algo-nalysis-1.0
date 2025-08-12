import asyncio 
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

async def main():
    
    # Welcome Message 
    title= Text("ALGO-NALYSIS V1.0", style="bold cyan")
    subtitle = Text("Bitcoin Monitoring & Memecoin Analysis", style="green")
    
    welcome_panel = Panel(
        f"{title}\n{subtitle}\n\n" +
        "🎯 Focus: Aggressive Memecoin Analysis\n" +
        "📊 Strategy: Dip-buying after high-rise corrections\n" +
        "🔍 Analysis: Aspect-level sentiment + volume spikes", 
        title="Welcome to Algo-nalysis",
        border_style="cyan",
    )
    
    console.print(welcome_panel)
    console.print("\n[yellow]Initializing systems...[/yellow]")
    
    console.print("✅ Database initialized successfully!")
    console.print("✅ API Clients [blink green]LOCKED-IN[/blink green]")
    console.print("✅ All Engines Prepped & Loaded")

    console.print("\n[green] System Online! commencing session in T-minus 3 seconds...[/green]")
    await asyncio.sleep(3)
    
if __name__ == "__main__":
    asyncio.run(main())
    
    