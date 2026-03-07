import re

class RuleEngine:

    def word_count(self, text):
        return len(text.split())

    def keyword_count(self, text, keywords):

      words = re.findall(r"\b\w+\b", text.lower())
      keyword_set = set(k.lower() for k in keywords)

      return sum(1 for word in words if word in keyword_set)

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

NEGATIONS = {"not", "never", "no"}
INTENSIFIERS = {"very", "extremely", "really"}


def calculate_sentiment(text):

    score = 0
    words = re.findall(r"\b\w+\b", text.lower())

    for i, word in enumerate(words):

        if word in SENTIMENT_WEIGHTS:

            value = SENTIMENT_WEIGHTS[word]

            # check negation (not good)
            if i > 0 and words[i-1] in NEGATIONS:
                value = -value

            # check intensifier (very good)
            if i > 0 and words[i-1] in INTENSIFIERS:
                value *= 2

            score += value

    return score

def score_to_emoji(score):

    if score >= 5:
        return "😍😍😍"      
    elif score >= 4:
        return "😊😊"        
    elif score >= 2:
        return "🙂🙂"        
    elif score >= -2:
        return "😐"        
    else:
        return "😡"        