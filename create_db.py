import sqlite3
import re, os
from multiprocessing import Pool

'''creating database'''
conn = sqlite3.connect("milestone1.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS large_text_data (
    id INTEGER PRIMARY KEY,
    content TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")

'''Connecting to database'''
conn = sqlite3.connect("milestone1.db")
cursor = conn.cursor()

# Read text file
with open("large_text_1000.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()

# Insert all lines at once (fast method)
cursor.executemany(
    "INSERT INTO large_text_data (content) VALUES (?)",
    [(line.strip(),) for line in lines]
)

conn.commit()
conn.close()

print("All text file data inserted successfully!")


'''divided into chunks and stored it into separate file'''
db_name = "milestone1.db"
table_name = "large_text_data"
column_name = "content"
chunk_size = 100
output_folder = "chunks_output"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

cursor.execute(f"SELECT {column_name} FROM {table_name}")
rows = cursor.fetchall()

conn.close()

full_text = "\n".join([row[0] for row in rows])
all_lines = full_text.split("\n")

chunks = [
    all_lines[i:i + chunk_size]
    for i in range(0, len(all_lines), chunk_size)
]

for i, chunk in enumerate(chunks):
    file_path = os.path.join(output_folder, f"chunk_{i+1}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(chunk))

print("Done")

words = sum(len(line.split()) for line in chunk)
print("Total words:", words)


'''word count using multiprocessing in a chunk file'''

chunk_folder = "chunks_output"

def process_file(filename):
    path = os.path.join(chunk_folder, filename)

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    word_count = len(text.split())

    print(f"{filename} → {word_count} words")

    return word_count

if __name__ == "__main__":

    files = os.listdir(chunk_folder)

    with Pool(4) as pool:   # 4 parallel processes
        results = pool.map(process_file, files)

    print("Total words in all chunks:", sum(results))


'''pattern matching task'''

with open("chunks_output/chunk_4.txt", "r", encoding="utf-8") as f:
    text = f.read()

keyword = "data"

matches = re.findall(rf"\b{keyword}\b", text, re.IGNORECASE)

print("Keyword count:", len(matches))