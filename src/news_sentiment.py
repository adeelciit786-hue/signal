"""
News & Sentiment Analysis Module
Pulls news and sentiment (basic implementation using keyword analysis)
News never overrides technicals but modifies confidence
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Literal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsAndSentiment:
    """News and sentiment analysis (modifier only)"""
    
    # High-impact economic events
    HIGH_IMPACT_EVENTS = {
        'CPI': 'Consumer Price Index',
        'FOMC': 'Federal Open Market Committee',
        'NFP': 'Non-Farm Payroll',
        'EARNINGS': 'Company Earnings',
        'GDP': 'Gross Domestic Product',
        'INFLATION': 'Inflation Data',
        'FED': 'Federal Reserve Decision',
        'ECB': 'European Central Bank',
        'CENTRAL_BANK': 'Central Bank Decision',
        'INTEREST_RATE': 'Interest Rate Decision'
    }
    
    BULLISH_KEYWORDS = [
        'surge', 'rally', 'jump', 'breakout', 'bullish', 'gains', 'strong',
        'positive', 'upbeat', 'optimistic', 'growth', 'recovery', 'outperform',
        'beat', 'upgrade', 'profit', 'rise', 'climb', 'advance', 'bull'
    ]
    
    BEARISH_KEYWORDS = [
        'crash', 'plunge', 'collapse', 'bearish', 'losses', 'weak',
        'negative', 'pessimistic', 'decline', 'recession', 'underperform',
        'miss', 'downgrade', 'loss', 'fall', 'drop', 'retreat', 'bear',
        'sell-off', 'correction', 'fear'
    ]
    
    @staticmethod
    def analyze_sentiment_keywords(text: str) -> Tuple[str, float]:
        """
        Simple keyword-based sentiment analysis
        
        Returns:
            (sentiment, strength_0_to_1)
        """
        if not text:
            return 'NEUTRAL', 0.5
        
        text_lower = text.lower()
        
        bullish_count = sum(1 for keyword in NewsAndSentiment.BULLISH_KEYWORDS if keyword in text_lower)
        bearish_count = sum(1 for keyword in NewsAndSentiment.BEARISH_KEYWORDS if keyword in text_lower)
        
        total_sentiment_words = bullish_count + bearish_count
        
        if total_sentiment_words == 0:
            return 'NEUTRAL', 0.5
        
        bullish_strength = bullish_count / total_sentiment_words
        
        if bullish_strength > 0.65:
            return 'POSITIVE', bullish_strength
        elif bullish_strength < 0.35:
            return 'NEGATIVE', 1 - bullish_strength
        else:
            return 'NEUTRAL', 0.5
    
    @staticmethod
    def detect_high_impact_events(text: str) -> Tuple[bool, str]:
        """
        Detect if news contains high-impact economic event
        
        Returns:
            (is_high_impact, event_type)
        """
        if not text:
            return False, 'NONE'
        
        text_upper = text.upper()
        
        for event, description in NewsAndSentiment.HIGH_IMPACT_EVENTS.items():
            if event in text_upper:
                return True, event
        
        return False, 'NONE'
    
    @staticmethod
    def simulate_news_feed(symbol: str) -> list:
        """
        Simulate news feed for demonstration
        In production, integrate with NewsAPI or Finnhub
        
        Returns:
            List of news articles
        """
        sample_news = [
            {
                'title': f'{symbol} shows strong technical setup with bullish divergence',
                'description': 'Price action confirms recovery with institutional buying',
                'published_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'source': 'Technical Analysis'
            },
            {
                'title': f'Market sentiment turns positive on {symbol} recovery',
                'description': 'Traders optimistic about next resistance level breakthrough',
                'published_at': (datetime.now() - timedelta(hours=4)).isoformat(),
                'source': 'Market News'
            }
        ]
        return sample_news
    
    @staticmethod
    def get_sentiment_impact_on_confidence(sentiment: str, strength: float) -> Tuple[float, str]:
        """
        Modify signal confidence based on news sentiment
        Never overrides technicals, only adjusts confidence
        
        Returns:
            (confidence_adjustment, impact_description)
        """
        if sentiment == 'POSITIVE':
            adjustment = strength * 15  # +5 to +15% confidence boost
            impact = f"Positive sentiment +{adjustment:.1f}% to confidence"
            return adjustment, impact
        
        elif sentiment == 'NEGATIVE':
            adjustment = -(strength * 20)  # -10 to -20% confidence reduction
            impact = f"Negative sentiment {adjustment:.1f}% to confidence"
            return adjustment, impact
        
        else:
            return 0, "Neutral sentiment - no adjustment"
    
    @staticmethod
    def evaluate_news_and_sentiment(symbol: str) -> Dict:
        """
        Complete sentiment evaluation for a symbol
        
        Returns:
            Dict with sentiment analysis and modifications
        """
        # Simulate fetching news
        news = NewsAndSentiment.simulate_news_feed(symbol)
        
        sentiments = []
        high_impact_detected = False
        impact_events = []
        
        for article in news:
            title = article.get('title', '')
            description = article.get('description', '')
            combined_text = f"{title} {description}"
            
            sentiment, strength = NewsAndSentiment.analyze_sentiment_keywords(combined_text)
            sentiments.append({'sentiment': sentiment, 'strength': strength, 'source': article.get('source')})
            
            is_high_impact, event = NewsAndSentiment.detect_high_impact_events(combined_text)
            if is_high_impact:
                high_impact_detected = True
                impact_events.append(event)
        
        # Aggregate sentiment
        positive_count = sum(1 for s in sentiments if s['sentiment'] == 'POSITIVE')
        negative_count = sum(1 for s in sentiments if s['sentiment'] == 'NEGATIVE')
        
        if positive_count > negative_count:
            aggregate_sentiment = 'POSITIVE'
            avg_strength = sum(s['strength'] for s in sentiments if s['sentiment'] == 'POSITIVE') / max(positive_count, 1)
        elif negative_count > positive_count:
            aggregate_sentiment = 'NEGATIVE'
            avg_strength = sum(s['strength'] for s in sentiments if s['sentiment'] == 'NEGATIVE') / max(negative_count, 1)
        else:
            aggregate_sentiment = 'NEUTRAL'
            avg_strength = 0.5
        
        # Get confidence adjustment
        confidence_adjustment, impact_desc = NewsAndSentiment.get_sentiment_impact_on_confidence(
            aggregate_sentiment, avg_strength
        )
        
        return {
            'overall_sentiment': aggregate_sentiment,
            'sentiment_strength': avg_strength,
            'confidence_adjustment': confidence_adjustment,
            'impact_description': impact_desc,
            'high_impact_event_detected': high_impact_detected,
            'high_impact_events': impact_events,
            'recommendation': NewsAndSentiment._get_news_trading_recommendation(
                aggregate_sentiment, high_impact_detected
            ),
            'articles_analyzed': len(news),
            'article_details': sentiments
        }
    
    @staticmethod
    def _get_news_trading_recommendation(sentiment: str, high_impact: bool) -> str:
        """Get trading recommendation based on sentiment"""
        if high_impact:
            return "⚠️ High-impact event detected - consider reducing exposure or using tighter stops"
        
        if sentiment == 'POSITIVE':
            return "✓ Positive sentiment supports bullish trades"
        elif sentiment == 'NEGATIVE':
            return "🛑 Negative sentiment - avoid aggressive long positions or skip trades"
        else:
            return "News sentiment neutral - follow technical signals"
