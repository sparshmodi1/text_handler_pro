import re

class RuleEngine:

    def word_count(self, text):
        return len(text.split())

    def keyword_count(self, text, keyword):
        matches = re.findall(rf"\b{keyword}\b", text, re.IGNORECASE)
        return len(matches)

    def process(self, text, keyword="data"):
        return {
            "word_count": self.word_count(text),
            "keyword_count": self.keyword_count(text, keyword)
        }
        

SENTIMENT_WEIGHTS = {
    # positive
    "excellent": 3,
    "amazing": 2,
    "good": 1,

    # negative
    "bad": -1,
    "worst": -2,
    "terrible": -3
}


def calculate_sentiment(text):

    score = 0
    words = re.findall(r"\b\w+\b", text.lower())

    for word in words:
        if word in SENTIMENT_WEIGHTS:
            score += SENTIMENT_WEIGHTS[word]

    return score


def classify_sentiment(score):

    if score > 1:
        return "POSITIVE"
    elif score < -1:
        return "NEGATIVE"
    else:
        return "NEUTRAL"