import csv
from multiprocessing import Pool
from chunks import create_chunks
from processor import process_chunk
from database import create_result_table
from search import search_menu

def load_chunks():
    with open("imdb.csv", encoding="utf-8") as f:
        r = csv.DictReader(f)
        reviews = [row[r.fieldnames[0]] for row in r]
    return create_chunks(reviews, 100)

def run():
    while True:
        print("\n1.Process  2.Search  3.Exit")
        c = input("> ").strip()
        if c == "3": break
        elif c == "1":
            create_result_table()
            with Pool(5) as pool:
                pool.map(process_chunk, [(i+1, ch) for i, ch in enumerate(load_chunks())])
            print("Done!")
        elif c == "2": search_menu()
        else: print("Invalid.")

if __name__ == "__main__":
    run()