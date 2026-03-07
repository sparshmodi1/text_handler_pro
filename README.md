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

The system processes **50K IMDb movie reviews** and performs:

✅ Parallel chunk processing  
✅ Keyword detection using Regex  
✅ Rule-based sentiment analysis  
✅ Emoji-based sentiment output  
✅ Execution time tracking per chunk  
✅ Structured database storage  

The project demonstrates how **real-world data pipelines can be optimized using parallel computing**.

---

# 🧠 System Architecture

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

### Processing Pipeline

1️⃣ Load IMDb dataset  
2️⃣ Divide reviews into chunks in memory  
3️⃣ Initialize database  
4️⃣ Start multiprocessing workers  
5️⃣ Apply rule engine logic  
6️⃣ Calculate sentiment score and emoji label  
7️⃣ Measure execution time  
8️⃣ Store results in SQLite database  

---

# ⚡ Parallel Processing

```python
from multiprocessing import Pool

with Pool(5) as pool:
    pool.map(process_chunk, chunk_data)
```

### Benefits

- Utilizes multiple CPU cores
- Faster processing for large datasets
- Independent chunk execution
- Scalable architecture

---

# 🔎 Processing Features

Each chunk performs the following operations:

| Feature | Description |
|--------|-------------|
| Word Count | Total number of words processed |
| Keyword Detection | Regex-based keyword matching |
| Sentiment Analysis | Rule-based sentiment scoring |
| Sentiment Label | Emoji-based sentiment representation |
| Execution Time | Processing performance measurement |
| Database Storage | Structured storage of results |

---

# 🔑 Keyword Detection

The keyword detection logic uses **list-based keyword input** instead of a single keyword.

Currently the list contains one keyword, but the structure allows **easy expansion to multiple keywords**.

Example:

```python
KW = ["story"]
keyword_count = engine.keyword_count(text, KW)
```

Future expansion:

```python
KW = ["story", "acting", "director"]
```

This design makes the rule engine **more flexible and scalable**.

---

# 😊 Sentiment Output

Instead of traditional star ratings, the system uses **emoji-based sentiment labels**.

Example mapping:

| Score Range | Emoji |
|-------------|------|
| High Positive | 😄 |
| Positive | 🙂 |
| Neutral | 😐 |
| Negative | 😞 |

This improves readability of the analysis results.

---

# 🗄️ Database Schema

Database: **chunks.db**

Table: `chunk_results`

| id | chunk_id | word_count | keyword_count | sentiment_score | sentiment_label | execution_time |
|----|----------|------------|---------------|----------------|----------------|----------------|

Features:

✔ Table recreated every run  
✔ No duplicate records  
✔ Performance metrics included  

---

# 📊 Example Chunk Output

```
CHUNK ID        : 201
PROCESS ID      : 10412
WORDS COUNT     : 23512
KEYWORDS FOUND  : 3
EXECUTION TIME  : 0.028231 sec
SCORE           : 2
SENTIMENT       : 🙂
```

---

# ▶️ How To Run (VS Code)

### Step 1 — Open Project

Open folder in VS Code:

```
text_handler_pro
```

### Step 2 — Open Terminal

Press:

```
Ctrl + `
```

### Step 3 — Check Python

```
python --version
```

### Step 4 — Run Program

```
python main.py
```

### Step 5 — View Results

Open:

```
chunks.db
```

---

# 🧩 Milestone Progress

### ✅ Milestone 1

- Chunk-based processing architecture
- Regex keyword detection
- SQLite database integration
- Initial multiprocessing implementation

### ✅ Milestone 2

- Real IMDb dataset integration (50K reviews)
- Memory-based chunking
- Rule engine implementation
- Sentiment scoring system
- Emoji-based sentiment output
- Keyword detection using list-based input
- Execution time tracking
- CPU workers upgraded (4 → 5)
- Modular architecture

---

# 🧠 Concepts Demonstrated

- Parallel Computing
- Python Multiprocessing
- Regex Text Processing
- Rule-Based Systems
- Database Integration
- Performance Measurement
- Scalable Data Pipelines

---

# 🚀 Learning Outcomes

This project demonstrates how to build a **real-world parallel data processing pipeline** capable of handling large datasets efficiently using only Python’s built-in tools.

You learn:

- Parallel processing fundamentals
- Designing modular data pipelines
- Measuring execution performance
- Integrating computation with databases

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
