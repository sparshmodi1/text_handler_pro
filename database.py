import sqlite3
from datetime import datetime

db_name = "chunks.db"


def get_connection():
    return sqlite3.connect(db_name)


def create_result_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id INTEGER,
        word_count INTEGER,
        keyword_count INTEGER,
        sentiment_score INTEGER,
        sentiment_label TEXT,
        execution_time REAL
    )
    """)

    # Clear old data
    cursor.execute("DELETE FROM chunk_results")

    conn.commit()
    conn.close()
    
def insert_result(chunk_id, word_count, keyword_count, score, sentiment, exec_time):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chunk_results
        (chunk_id, word_count, keyword_count, sentiment_score, sentiment_label, execution_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        chunk_id,
        word_count,
        keyword_count,
        score, 
        sentiment,
        exec_time,
    ))

    conn.commit()
    conn.close()

    print(f"DB → Chunk {chunk_id} | Words:{word_count} | Keywords:{keyword_count} | Time:{exec_time:.4f}s")    