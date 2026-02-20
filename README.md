<h1 align="center">🚀 Parallel Text Handling Processor</h1>

<p align="center">
  <b>Parallel Chunk-Based Text Processing System using Python</b>
</p>

<p align="center">
  🐍 Python | ⚡ Multiprocessing | 🗄️ SQLite | 🔎 Regex | 💻 VS Code
</p>

---

# 📌 About The Project

Parallel Text Handling Processor is a scalable text processing system designed to handle large text files efficiently.

The system works by:

- Splitting large text files into smaller chunks  
- Processing each chunk in parallel using multiprocessing  
- Applying regex-based keyword matching  
- Using a rule-based evaluation layer  
- Storing processed results inside an SQLite database  

This project demonstrates practical implementation of parallel execution, modular architecture, and structured database integration.

---

# 🏗️ Project Structure

```
text_handler_pro/
│
├── main.py              # Entry point of the program
├── processor.py         # Handles chunk processing logic
├── rule_engine.py       # Rule-based evaluation layer
├── database.py          # Database table creation & management
├── chunks_output/       # Contains chunk_1.txt ... chunk_11.txt
├── chunks.db            # SQLite database (stores results)
└── README.md
```

---

# ⚙️ How The System Works

1️⃣ Load chunk files from `chunks_output/`  
2️⃣ Sort files numerically  
3️⃣ Create/reset result table  
4️⃣ Use multiprocessing (`Pool`) to process chunks  
5️⃣ Apply rule-based logic  
6️⃣ Store results in SQLite database  

---

# 🔄 Parallel Processing Implementation

```python
from multiprocessing import Pool

with Pool(4) as pool:
    pool.map(process_chunk, chunk_data)
```

- Uses multiple CPU cores  
- Improves performance  
- Each chunk processed independently  

---

# 🗄️ Database Integration

Results are stored in:

```
chunks.db
```

Table: `chunk_results`

| id | chunk_id | word_count | keyword_count |
|----|----------|------------|---------------|

Each execution:
- Clears old data  
- Inserts fresh processed results  
- Prevents duplication  

---

# 💻 How to Run (Using VS Code)

## Step 1
Open the `text_handler_pro` folder in VS Code.

## Step 2
Open Terminal:

```
Ctrl + `
```

## Step 3
Run:

```bash
python main.py
```

## Step 4
After execution, check:

```
chunks.db
```

You should see processed results stored inside the database.

---

# 🧠 Key Concepts Demonstrated

- File Handling (`os`)
- Regex Keyword Matching (`re`)
- Multiprocessing (`Pool`)
- SQLite Database Integration
- Modular Python Architecture
- Rule-Based Processing

---

# 📈 Milestone Summary

### ✅ Milestone 1
- Implemented chunk creation  
- Basic multiprocessing  
- Regex keyword matching  
- SQLite result storage  

### ✅ Milestone 2
- Defined processing domain clearly  
- Implemented rule engine module  
- Connected database to actual chunk results  
- Removed hardcoded demo data  
- Cleaned and modularized project structure  

---

# 🚀 Learning Outcome

This project demonstrates how to design a structured, scalable, and parallel text processing system using Python and built-in modules.

It highlights practical understanding of:
- Parallel computing
- Database-driven applications
- Clean code architecture
- Progressive system enhancement

---

<p align="center">
🔥 Efficient • Modular • Parallel • Scalable 🔥
</p>
