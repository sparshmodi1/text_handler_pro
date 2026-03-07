import os, re
import csv
from multiprocessing import Pool
from chunks import create_chunks
from processor import process_chunk
from database import create_result_table


def load_chunks():
    reviews = []

    # Read CSV
    with open("imdb.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            reviews.append(row[reader.fieldnames[0]]) 

    # Create chunks
    chunks = create_chunks(reviews, 100)

    return chunks


if __name__ == "__main__":

    # Load chunks from CSV
    chunks = load_chunks()

    # Create / Reset result table
    create_result_table()

    # Prepare chunk_id + data
    chunk_data = [(i + 1, chunk) for i, chunk in enumerate(chunks)]

    # Parallel processing
    with Pool(5) as pool:
        pool.map(process_chunk, chunk_data)
        

    print("Processing Completed!")