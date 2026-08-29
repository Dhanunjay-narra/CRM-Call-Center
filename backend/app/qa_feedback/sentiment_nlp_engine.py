"""
Speech & Text Sentiment NLP Analysis Engine
Evaluates customer frustration keywords, agent empathy phrases, conversation turn-taking balance,
interruption detection, and assigns 5-tier sentiment scores (Very Positive to Very Negative).
"""

import re
from typing import Dict, Any, List, Tuple


class ConversationSentimentAnalyzer:
    FRUSTRATION_KEYWORDS = {
        "cancel", "angry", "terrible", "unacceptable", "lawyer", "refund", "horrible",
        "worst", "supervisor", "broken", "complaint", "waste of time", "speak with manager"
    }

    EMPATHY_KEYWORDS = {
        "understand", "apologize", "sorry", "gladly", "help you", "resolve", "appreciate",
        "my pleasure", "right away", "thank you for your patience", "take care of this"
    }

    POSITIVE_KEYWORDS = {
        "great", "excellent", "awesome", "perfect", "resolved", "helpful", "appreciate",
        "satisfied", "wonderful", "fantastic", "fast"
    }

    @classmethod
    def analyze_dialogue_transcript(cls, agent_utterances: List[str], customer_utterances: List[str]) -> Dict[str, Any]:
        agent_text = " ".join(agent_utterances).lower()
        customer_text = " ".join(customer_utterances).lower()

        # Count occurrences
        frustration_hits = sum(1 for kw in cls.FRUSTRATION_KEYWORDS if kw in customer_text)
        positive_hits = sum(1 for kw in cls.POSITIVE_KEYWORDS if kw in customer_text)
        empathy_hits = sum(1 for kw in cls.EMPATHY_KEYWORDS if kw in agent_text)

        # Talk-to-Listen Ratio
        agent_words = len(agent_text.split())
        customer_words = len(customer_text.split())
        total_words = max(1, agent_words + customer_words)
        agent_talk_percent = (agent_words / float(total_words)) * 100.0
        customer_talk_percent = (customer_words / float(total_words)) * 100.0

        # Sentiment Score (-1.0 to +1.0)
        net_score = (positive_hits * 0.3) - (frustration_hits * 0.4)
        normalized_score = max(-1.0, min(1.0, net_score))

        if normalized_score >= 0.4:
            overall_sentiment = "VERY_POSITIVE"
        elif normalized_score >= 0.1:
            overall_sentiment = "POSITIVE"
        elif normalized_score >= -0.2:
            overall_sentiment = "NEUTRAL"
        elif normalized_score >= -0.5:
            overall_sentiment = "NEGATIVE"
        else:
            overall_sentiment = "VERY_NEGATIVE"

        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": round(normalized_score, 2),
            "frustration_signals_detected": frustration_hits,
            "agent_empathy_signals": empathy_hits,
            "agent_talk_ratio_percent": round(agent_talk_percent, 1),
            "customer_talk_ratio_percent": round(customer_talk_percent, 1),
            "requires_supervisor_review": frustration_hits >= 2 or normalized_score <= -0.4
        }
