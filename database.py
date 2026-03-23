import sqlite3

db_name = "chunks.db"

def get_connection(): 
    return sqlite3.connect(db_name)

def create_result_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id INTEGER UNIQUE,
        word_count INTEGER,
        keyword_count INTEGER,
        sentiment_score REAL,
        sentiment_label TEXT,
        execution_time REAL
    )
    """)
    conn.commit()
    conn.close()
    

def insert_result(chunk_id, word_count, keyword_count, sentiment_score, sentiment_label, exec_time):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Agar chunk_id already exist karta hai toh skip
    existing = cursor.execute(
        "SELECT chunk_id FROM chunk_results WHERE chunk_id = ?", (chunk_id,)
    ).fetchone()

    if existing:
        print(f"SKIP → Chunk {chunk_id} already exists")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO chunk_results
        (chunk_id, word_count, keyword_count, sentiment_score, sentiment_label, execution_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chunk_id, word_count, keyword_count, sentiment_score, sentiment_label, exec_time))

    conn.commit()
    conn.close()
    print(f"DB → Chunk {chunk_id} | Words:{word_count} | Keywords:{keyword_count} | Time:{exec_time:.4f}s")
