import os
import time
from database import insert_result
from rule_engine import RuleEngine, calculate_sentiment, score_to_emoji
engine = RuleEngine()


def process_chunk(args):

    chunk_id, chunk = args
    pid = os.getpid()

    start_time = time.perf_counter()

    #processing
    text = " ".join(chunk)
    word_count = engine.word_count(text)
    
    KW = ["story"]
    keyword_count = engine.keyword_count(text, KW)
    score = calculate_sentiment(text)
    sentiment = score_to_emoji(score)
    exec_time = time.perf_counter() - start_time

    insert_result(chunk_id, word_count, keyword_count, score, sentiment, exec_time)

    output = f"""
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CHUNK ID        : {chunk_id}
PROCESS ID      : {pid}
WORDS COUNT     : {word_count}
KEYWORDS FOUND  : {keyword_count}
EXECUTION TIME  : {exec_time:.6f} sec
SCORE           : {score}
SENTIMENTS      : {sentiment}
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
"""

    print(output)