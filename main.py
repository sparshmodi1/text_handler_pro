import sqlite3
from chunks import create_chunks
from processor import process_chunk
from database import create_result_table
from multiprocessing import Pool

# Fetch data from DB
conn = sqlite3.connect("chunks.db")
cursor = conn.cursor()

cursor.execute("SELECT content FROM large_text_data")
rows = cursor.fetchall()
conn.close()

lines = [row[0] for row in rows]

# Create chunks
chunks = create_chunks(lines, 100)

# Create result table
create_result_table()

# Parallel processing
if __name__ == "__main__":
    chunk_data = [(i+1, chunk) for i, chunk in enumerate(chunks)]

    with Pool(4) as pool:
        results = pool.map(process_chunk, chunk_data)

    print("Processing Completed!")