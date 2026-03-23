import csv
from database import get_connection

def fetch(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(query, params).fetchall()
    conn.close()
    return rows

def show(rows):
    if not rows: print("No results."); return
    for r in rows:
        print(f"{r[0]} | chunk:{r[1]} | words:{r[2]} | score:{r[4]} | {r[5]} | {r[6]:.2f}s")
    print(f"Total: {len(rows)}\n")

def export_rows(rows):
    name = input("File prefix (enter for 'export'): ").strip() or "export"
    filename = f"{name}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Chunk", "Words", "Score", "Sentiment", "Time"])
        writer.writerows(rows)
    print(f"Saved to {filename} ✔")

def keyword_search(filepath="imdb.csv"):
    keyword = input("Keyword: ").strip().lower()
    if not keyword:
        print("No keyword entered.")
        return []

    results = []
    try:
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            text_col = reader.fieldnames[0]  # first column = review text
            for i, row in enumerate(reader):
                text = row[text_col]
                if keyword in text.lower():
                    preview = text[:100].replace("\n", " ")
                    results.append((i + 1, preview))
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return []

    if not results:
        print("No matches found.")
    else:
        for row_num, preview in results:
            print(f"Row {row_num}: {preview}...")
        print(f"Total matches: {len(results)}")

    return results

def export_keyword_results(results):
    name = input("File prefix (enter for 'export'): ").strip() or "export"
    filename = f"{name}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Row", "Preview"])
        writer.writerows(results)
    print(f"Saved to {filename} ✔")

def search_menu():
    last_rows = []
    last_keyword_results = []

    while True:
        print("\n1.All  2.Sentiment  3.Score Range  4.Keyword Search  5.Export Last Search  6.Exit")
        c = input("> ").strip()

        if c == "6":
            break

        elif c == "1":
            rows = fetch("SELECT * FROM chunk_results")
            show(rows)

        elif c == "2":
            available = fetch("SELECT DISTINCT sentiment_label FROM chunk_results")
            print("Available labels:", [r[0] for r in available])
            label = input("Sentiment: ").strip()
            last_rows = fetch("SELECT * FROM chunk_results WHERE sentiment_label = ?", (label,))
            last_keyword_results = []
            show(last_rows)

        elif c == "3":
            lo, hi = float(input("Min: ")), float(input("Max: "))
            last_rows = fetch("SELECT * FROM chunk_results WHERE sentiment_score BETWEEN ? AND ?", (lo, hi))
            last_keyword_results = []
            show(last_rows)

        elif c == "4":
            last_keyword_results = keyword_search("imdb.csv")
            last_rows = []

        elif c == "5":
            if last_rows:
                export_rows(last_rows)
            elif last_keyword_results:
                export_keyword_results(last_keyword_results)
            else:
                print("Please perform a search first (2, 3, or 4).")

        else:
            print("Invalid.")
