from rich.console import Console
from rich.table import Table 
from rich.panel import Panel
from typing import List
from ..models.analysis_result import MemecoinPotential
from datetime import datetime 

class ConsoleDashboard:
    def __init__(self):
        self.console = Console()
        
    def display_opportunities(self, opportunities: List[MemecoinPotential]):
        if not opportunities:
            self.console.print("[yellow] No Opportunities found meeting set criteria's[/yellow]")
        
        table = Table(title="🎯 POTENTIAL MEMECOIN GEMS")
        table.add_column("Symbol", style="cyan", width=8) 
        table.add_column("Chain", style="magenta", width=8) 
        table.add_column("Score", style="green", width=6) 
        table.add_column("Type", style="yellow", width=10) 
        table.add_column("Market Cap", style="blue", width=10) 
        table.add_column("Sentiment", style="green", width=8) 
        table.add_column("Security", style="red", width=8) 
        table.add_column("Reasoning", style="white", width=40)
        
        for opp in opportunities:
            mc_str = f"${opp.market_cap/1000:.0f}K" if opp.market_cap < 1000000 else f"${opp.market_cap/1000000:.1f}M"
            sentiment_avg = (opp.narrative_indicators.hype_level + opp.narrative_indicators.fomo_intensity) / 2
            score_color = "green" if opp.overall_score >= 70 else "yellow" if opp.overall_score >= 50 else "red"
            security_color ="green" if opp.security_score >= 70 else "yellow" if opp.security_score >= 50 else "red"
            
            table.add_row(
                f"${opp.symbol}", 
                opp.chain.upper(),
                f"$[{score_color}]{opp.overall_score:.0f}[/{score_color}]",
                opp.potential_type.replace('_', ' ').title(),
                mc_str,
                f"{sentiment_avg:.0f}",
                f"[{security_color}] {opp.security_score:.0f}[/{security_color}]",
                opp.reasoning[:40] + "..." if len(opp.reasoning) > 40 else opp.reasoning
            )
            
        self.console.print(table)
        
        avg_score = sum(opp.overall_score for opp in opportunities) / len(opportunities)
        high_confidence = len([opp for opp in opportunities if opp.confidence >= 70])
        
        summary = Panel.fit(
            f"📊 [bold]HUNT SUMMARY[/bold]\n\n" +
            f"🎯 Opportunities FOund: {len(opportunities)}\n" +
            f"📈 Average Score: {avg_score:.1f}\n" +
            f"🔥 High Confidence: {high_confidence}\n" +
            f"⏰ Scan Time: {datetime.now().strftime('%H:%M:%S')}",
            title = "[bold green]Results[/bold green]",
            border_style="green"
        )
        
        self.console.print(summary)