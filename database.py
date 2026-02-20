import sqlite3

def create_result_table():
    conn = sqlite3.connect("chunks.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id INTEGER,
        word_count INTEGER,
        keyword_count INTEGER
    )
    """)

    # Clear old data
    cursor.execute("DELETE FROM chunk_results")

    conn.commit()
    conn.close()