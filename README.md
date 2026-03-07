<h1 align="center">🚀 Parallel Text Handling Processor</h1>

<p align="center">
  <b>High-Performance Parallel Text Processing & Sentiment Analysis System</b>
</p>

<p align="center">
  🐍 Python • ⚡ Multiprocessing • 🗄️ SQLite • 🔎 Regex • 📊 Sentiment Analysis • 💻 VS Code
</p>

<p align="center">
  <i>Processing 50,000 IMDb Movie Reviews using Parallel Computing</i>
</p>

---

# 🌟 Project Overview

**Parallel Text Handling Processor** is a scalable Python-based system designed to efficiently process **large textual datasets** using multiprocessing and rule-based analysis.

The project analyzes **50K IMDb movie reviews** and performs:

✅ Parallel chunk processing  
✅ Keyword detection using Regex  
✅ Sentiment scoring (Positive / Negative)  
✅ Execution time tracking per chunk  
✅ Structured database storage  

The system demonstrates how real-world data pipelines can be optimized using parallel execution.

---

# 🧠 System Architecture (Visualization)

```
                IMDb Dataset (.csv)
                         │
                         ▼
              ┌────────────────────┐
              │   Dynamic Chunking │
              └────────────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │ Multiprocessing Pool│
              │      (5 CPUs)       │
              └────────────────────┘
                │     │     │
                ▼     ▼     ▼
           Chunk 1  Chunk 2 ... Chunk N
                │
                ▼
        ┌──────────────────────┐
        │   Rule Engine Layer   │
        │  • Keyword Matching   │
        │  • Sentiment Scoring  │
        │  • Time Measurement   │
        └──────────────────────┘
                         │
                         ▼
                 SQLite Database
                     chunks.db
```

---

# 🏗️ Project Structure

```
text_handler_pro/
│
├── main.py              # Program entry point
├── processor.py         # Parallel chunk processing
├── rule_engine.py       # Sentiment & rule evaluation
├── database.py          # Database setup & management
├── imdb_reviews.csv     # 50K IMDb dataset
├── chunks.db            # Result database
└── README.md
```

---

# ⚙️ How The System Works

### Step-by-Step Pipeline

1️⃣ Load IMDb reviews dataset (`.csv`)  
2️⃣ Divide data into chunks **in memory**  
3️⃣ Initialize/reset database  
4️⃣ Execute multiprocessing pool (5 workers)  
5️⃣ Apply rule engine logic  
6️⃣ Compute sentiment scores  
7️⃣ Measure execution time  
8️⃣ Store results in SQLite database  

---

# ⚡ Parallel Processing

```python
from multiprocessing import Pool

with Pool(5) as pool:
    pool.map(process_chunk, chunk_data)
```

### Why Multiprocessing?

- Utilizes multiple CPU cores
- Faster processing for large datasets
- Independent chunk execution
- Scalable architecture

---

# 🔎 Processing Features

Each chunk performs:

| Feature | Description |
|--------|-------------|
| Word Count | Total words analyzed |
| Keyword Detection | Regex-based keyword matching |
| Sentiment Analysis | Positive & Negative scoring |
| Execution Time | Performance measurement |
| Database Storage | Structured result saving |

---

# 🗄️ Database Schema

Database: **chunks.db**

Table: `chunk_results`

| id | chunk_id | word_count | keyword_count | sentiment_score | sentiment_label | execution_time |
|----|----------|------------|---------------|----------------|----------------|----------------|

✔ Fresh table created every run  
✔ No duplicate data  
✔ Performance metrics included  

---

# ▶️ How To Run (VS Code Guide)

## ✅ Step 1 — Open Project

Open folder in **VS Code**:

```
text_handler_pro
```

---

## ✅ Step 2 — Open Terminal

Press:

```
Ctrl + `
```

or:

```
Terminal → New Terminal
```

---

## ✅ Step 3 — Install Requirements

(No external libraries required — uses Python built-in modules)

Ensure Python is installed:

```bash
python --version
```

---

## ✅ Step 4 — Run Program

```bash
python main.py
```

---

## ✅ Step 5 — Verify Output

After execution:

```
Processing Completed!
```

Open:

```
chunks.db
```

to view results.

---

# 📊 Example Execution Flow

```
Dataset Loaded ✅
Chunks Created ✅
Parallel Workers Started ✅
Rule Engine Applied ✅
Database Updated ✅
Processing Completed ✅
```

---

# 🧩 Milestone Progress

### ✅ Milestone 1
- Chunk-based processing design
- Regex keyword detection
- SQLite integration
- Initial multiprocessing implementation

### ✅ Milestone 2
- Real IMDb dataset integration (50K reviews)
- Memory-based chunking (no temp files)
- Rule Engine implementation
- Sentiment scoring system
- Execution time tracking
- CPU workers upgraded (4 → 5)
- Clean modular architecture

---

# 🧠 Concepts Demonstrated

- Parallel Computing
- Python Multiprocessing
- Regex Text Analysis
- Database-driven Processing
- Rule-Based Systems
- Performance Optimization
- Scalable Software Design

---

# 🚀 Learning Outcomes

This project showcases how to build a **real-world parallel data processing pipeline** capable of handling large datasets efficiently using only Python’s built-in tools.

You learn:

- How parallel systems work internally
- How to design modular processing pipelines
- How to measure execution performance
- How databases integrate with computation workflows

---

# 👨‍💻 Built With

- Python 3.x
- VS Code
- SQLite (Built-in)
- IMDb Movie Reviews Dataset

---

<p align="center">
⭐ Efficient • Parallel • Intelligent • Scalable ⭐
</p>
