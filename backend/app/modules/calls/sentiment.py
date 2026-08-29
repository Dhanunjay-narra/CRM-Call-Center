from typing import Dict

def analyze_call_sentiment(transcript: str) -> Dict[str, any]:
    positive_words = {"happy", "thanks", "great", "resolved", "excellent", "helpful", "good"}
    negative_words = {"angry", "bad", "terrible", "frustrated", "broken", "issue", "crash", "worst"}
    
    words = transcript.lower().split()
    pos_count = sum(1 for w in words if w in positive_words)
    neg_count = sum(1 for w in words if w in negative_words)
    
    if pos_count > neg_count:
        score = min(1.0, 0.5 + (pos_count * 0.1))
        label = "POSITIVE"
    elif neg_count > pos_count:
        score = max(-1.0, -0.5 - (neg_count * 0.1))
        label = "NEGATIVE"
    else:
        score = 0.0
        label = "NEUTRAL"
        
    return {"sentiment_score": score, "sentiment_label": label}
