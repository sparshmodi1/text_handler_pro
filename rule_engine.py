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
    # ★★★★★ — Exceptional (score +4 to +5)
    "masterpiece":5,"flawless":5,"perfection":5,"extraordinary":5,"phenomenal":5,
    "breathtaking":5,"unforgettable":5,"groundbreaking":5,"transcendent":5,

    # ★★★★ — Very Good (score +3)
    "outstanding":4,"excellent":4,"brilliant":4,"superb":4,"magnificent":4,
    "exceptional":4,"remarkable":4,"impressive":4,"captivating":4,"riveting":4,

    # ★★★ — Good (score +2)
    "amazing":3,"wonderful":3,"fantastic":3,"great":3,"terrific":3,
    "delightful":3,"engaging":3,"enjoyable":3,"compelling":3,"charming":3,

    # ★★½ — Decent (score +1)
    "good":2,"nice":2,"solid":2,"fine":2,"decent":2,
    "pleasant":2,"satisfying":2,"worthwhile":2,"recommend":2,
    "love":2,"loved":2,"beautiful":2,"enjoyed":2,"enjoy":2,"like":1,"liked":1, "best":1,

    # ★★★ — Neutral / Mixed (score 0)
    "okay":0,"ok":0,"average":0,"alright":0,"mixed":0,
    "ordinary":0,"predictable":0,"familiar":0,"typical":0,

    # ★★ — Below Average (score -1 to -2)
    "bad":-2,"poor":-2,"weak":-2,"dull":-2,"bland":-2,
    "boring":-2,"slow":-2,"mediocre":-2,"forgettable":-2,"disappointing":-2,
    "uninspired":-2,"generic":-2,"flat":-2,"tedious":-2,"overlong":-2,

    # ★ — Very Bad (score -3 to -4)
    "terrible":-3,"horrible":-3,"awful":-3,"dreadful":-3,"appalling":-3,
    "hate":-3,"hated":-3,"waste":-3,"pathetic":-3,"ridiculous":-3,
    "laughable":-3,"embarrassing":-3,"incoherent":-3,"unwatchable":-3,

    # ★☆☆☆☆ — Catastrophic (score -5)
    "worst":-5,"abysmal":-5,"atrocious":-5,"disgusting":-5,"unbearable":-5,
    "disaster":-5,"catastrophic":-5,"repulsive":-5,"offensive":-5,
}
NEGATIONS    = {"not","never","no","neither","nor","hardly","barely","scarcely"}
INTENSIFIERS = {"very","extremely","really","absolutely","incredibly","utterly"}

def calculate_sentiment(text):
    score = 0
    words = re.findall(r"\b\w+\b", text.lower())
    for i, word in enumerate(words):
        if word in SENTIMENT_WEIGHTS:
            val    = SENTIMENT_WEIGHTS[word]
            window = words[max(0,i-3):i]
            if any(w in NEGATIONS for w in window):      val = -val
            elif any(w in INTENSIFIERS for w in window): val *= 2
            score += val
    return score

def score_to_emoji(score, word_count=1):
    density = (score / max(word_count, 1)) * 1000
    if density >= 8:    return "★★★★★"
    elif density >= 4:  return "★★★★☆"
    elif density >= 1:  return "★★★☆☆"
    elif density >= -2: return "★★☆☆☆"
    else:               return "★☆☆☆☆"

NEGATIONS = {"not", "never", "no"}
INTENSIFIERS = {"very", "extremely", "really"}