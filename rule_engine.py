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