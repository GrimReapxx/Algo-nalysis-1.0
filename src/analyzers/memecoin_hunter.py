from typing import Dict, List, Tuple
from ..models.analysis_result import NarrativeIndicators, MemecoinPotential
from datetime import datetime 

class MemecoinPotentialScorer:
    
    def score_potential(self,
                        token_data: Dict,
                        sentiment: NarrativeIndicators,
                        security_data: Dict,
                        chain: str) -> MemecoinPotential:
        
        """ Extracting basic data for Scoring the potential of a memecoin"""
        symbol = token_data.get('symbol', 'N/A')
        name = token_data.get('name', '')
        price = float(token_data.get('price', 0))
        market_cap = float(token_data.get('mc', 0))
        liquidity = float(token_data.get('liquidity', 0))
        volume_24h = float(token_data.get('volume24h', 0))
        price_change_24h = float(token_data.get('price24hchangepercent', 0))
        
        # Security assessment
        security_score, security_flags = self._assess_security(security_data)
        
        # Calculate potential score 
        overall_score, potential_type, reasoning = self._calculate_potential_score(
            sentiment, market_cap, liquidity, volume_24h, price_change_24h, security_score
        )
        
        confidence = self._calculate_confidence(security_score, sentiment)
        
        return MemecoinPotential(
            token_address=token_data.get('address', ''),
            symbol=symbol,
            name=name,
            chain=chain,
            price=price,
            market_cap=market_cap,
            liquidity=liquidity,
            volume_24h=volume_24h,
            price_change_24h=price_change_24h,
            narrative_indicators=sentiment,
            security_score=security_score,
            security_flags=security_flags,
            overall_score=overall_score,
            potential_type=potential_type,
            reasoning=reasoning,
            confidence=confidence,
            timestamp=datetime.now()
        )
        
    def _assess_security(self, security_data: Dict) -> Tuple[float, List[str]]:
        if not security_data:
            return 50.0, ["No security data available"]
        
        score = 100.0
        flags = []
        if security_data.get('rug_pull'):
            score -= 50
            flags.append("RUG PULL RISK DETECTED")
            
        if security_data.get('is_blacklisted'):
            score -= 40
            flags.append("⚠️ TOKEN BLACKLISTED")
            
        top_10_holders = security_data.get('top_10_holder_percent',0)
        if top_10_holders > 80:
            score -= 30
            flags.append(f"⚠️ HIGH CONCENTRATION: {top_10_holders}% IN TOP 10")
        elif top_10_holders > 60:
            score -= 15
            flags.append(f"⚠️ MODERATE CONCENTRATION: {top_10_holders}% IN TOP 10")
        if not security_data.get('is_liquidity_locked'):
            score -= 20
            flags.append("🔓 LIQUIDITY NOT LOCKED")
            
        return max(0, score), flags 
    def _calculate_potential_score(self,
                                sentiment: NarrativeIndicators,
                                market_cap: float,
                                liquidity: float,
                                volume_24h: float,
                                price_change_24h: float,
                                security_score: float) -> Tuple[float, str, str]:
        score = 0
        reasoning_parts = []
        
        sentiment_score = (
            sentiment.hype_level * 0.3 +
            sentiment.fomo_intensity * 0.2 + 
            sentiment.community_growth * 0.2 + 
            sentiment.meme_virality * 0.2 +
            sentiment.utility_mentions * 0.1 -
            sentiment.risk_awareness * 0.1 
        )
        score += sentiment_score * 0.4
        
        if sentiment_score > 60:
            reasoning_parts.append("🔥 Strong social sentiment")
        elif sentiment_score > 40:
            reasoning_parts.append("📈 Moderate social interest")
            
        volume_to_liquidity = (volume_24h / liquidity) if liquidity > 0 else 0
        if volume_to_liquidity > 0.5:
            score += 25
            reasoning_parts.append("💥 High Volume/Liquidity Ratio")
        elif volume_to_liquidity > 0.2:
            score += 15
            reasoning_parts.append("📊 Moderate Trading Activity")
            
        if 100000 <= market_cap <= 10000000:
            score += 20
            reasoning_parts.append("🎯 Optimal Market cap range")
        elif market_cap < 100000:
            score += 10 
            reasoning_parts.append("💎 Early stage potential: HIGH RISK")
            
        security_weight  = security_score * 0.3
        score += security_weight
        
        if security_score >= 80:
            reasoning_parts.append("🛡️ Strong security profile")
        elif security_score >= 60:
            reasoning_parts.append("⚠️ Moderate security risks")
        else: 
            reasoning_parts.append("🚨 High security risks") 
            
        # Determine potential type
        if price_change_24h < -20 and sentiment_score > 50:
            potential_type = "DIP_BUY"
            reasoning_parts.append("📉➡️📈 potential dip-buying opportunity")
        elif sentiment_score > 70 and volume_to_liquidity > 0.3:
            potential_type = "HYPE_TRAIN"
            reasoning_parts.append("🚀 High-momemtum play")
        else:
            potential_type = "NEW_GEM"
            reasoning_parts.append(" NEW GEM - Early stage discovery")
        
        reasoning = " | ".join(reasoning_parts)
        return min(100, max(0, score)), potential_type, reasoning
    
    def _calculate_confidence(self, security_score: float, sentiment: NarrativeIndicators) -> float:
        base_confidence = 70
        
        if security_score >= 80:
            base_confidence += 20
        elif security_score < 40:
            base_confidence -= 30
            
        sentiment_values = [
            sentiment.hype_level, sentiment.fomo_intensity,
            sentiment.community_growth, sentiment.meme_virality
        ]
        active_aspects = sum(1 for val in sentiment_values if val > 10)
        
        if active_aspects >= 3:
            base_confidence += 10
        elif active_aspects < 2:
            base_confidence -= 15
            
        return min(100, max(10, base_confidence))
     