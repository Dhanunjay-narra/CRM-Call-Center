from app.modules.calls.sentiment import analyze_call_sentiment

def test_sentiment_analyzer():
    res = analyze_call_sentiment("Thank you so much, this is great and resolved my issue!")
    assert res["sentiment_label"] == "POSITIVE"
    assert res["sentiment_score"] > 0
