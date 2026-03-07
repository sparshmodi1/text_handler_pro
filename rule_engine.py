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
    "excellent": 2,
    "amazing": 2,
    "good": 1,

    # negative
    "bad": -1,
    "boring": -2,
    "worst": -2
}


def calculate_sentiment(text):

    score = 0
    words = re.findall(r"\b\w+\b", text.lower())

    for word in words:
        if word in SENTIMENT_WEIGHTS:
            score += SENTIMENT_WEIGHTS[word]

    return score


    
def score_to_star(score):

    if score >= 5:
        return "⭐⭐⭐⭐⭐"
    elif score >= 4:
        return "⭐⭐⭐⭐"
    elif score >= 2:
        return "⭐⭐⭐"
    elif score >= -2:
        return "⭐⭐"
    else:
        return "⭐"    