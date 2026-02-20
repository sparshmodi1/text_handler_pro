import os
import re
from multiprocessing import Pool
from processor import process_chunk
from database import create_result_table

def load_chunks():
    chunk_folder = "chunks_output"
    chunks = []

    files = os.listdir(chunk_folder)

    #numeric sorting
    def extract_number(filename):
        match = re.search(r'\d+', filename)
        return int(match.group())

    files.sort(key=extract_number)

    for filename in files:
        path = os.path.join(chunk_folder, filename)

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            chunks.append(lines)

    return chunks


if __name__ == "__main__":

    #Load all chunk files
    chunks = load_chunks()

    # Create / Reset result table
    create_result_table()

    # Prepare chunk_id + data
    chunk_data = [(i + 1, chunk) for i, chunk in enumerate(chunks)]

    #Parallel processing
    with Pool(4) as pool:
        pool.map(process_chunk, chunk_data)

    print("Processing Completed!")