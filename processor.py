from multiprocessing import Pool
from rule_engine import RuleEngine
import sqlite3

engine = RuleEngine()

def process_chunk(args):
    chunk_id, chunk = args
    text = "\n".join(chunk)

    result = engine.process(text)

    conn = sqlite3.connect("chunks.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chunk_results (chunk_id, word_count, keyword_count)
        VALUES (?, ?, ?)
    """, (chunk_id, result["word_count"], result["keyword_count"]))

    conn.commit()
    conn.close()

    return result