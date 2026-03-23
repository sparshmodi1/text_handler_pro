import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
import csv, re, time, os, io, json
from datetime import datetime

st.set_page_config(page_title="TextLens", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

# ── Rule Engine ───────────────────────────────────────────────────────────────
class RuleEngine:
    def word_count(self, text): return len(text.split())
    def keyword_count(self, text, keywords):
        words = re.findall(r"\b\w+\b", text.lower())
        kset  = set(k.lower() for k in keywords)
        return sum(1 for w in words if w in kset)

SENTIMENT_WEIGHTS = {
    # ★★★★★ — Exceptional (score +4 to +5)
    "masterpiece":5,"flawless":5,"perfection":5,"extraordinary":5,"phenomenal":5,
    "breathtaking":5,"unforgettable":5,"groundbreaking":5,"transcendent":5,

    # ★★★★ — Very Good (score +3)
    "outstanding":4,"excellent":4,"brilliant":4,"superb":4,"magnificent":4,
    "exceptional":4,"remarkable":4,"impressive":4,"captivating":4,"riveting":4,

    # ★★★ — Good (score +2)
    "amazing":3,"wonderful":3,"fantastic":3,"great":3,"terrific":3,
    "delightful":3,"engaging":3,"enjoyable":3,"compelling":3,"charming":3,

    # ★★½ — Decent (score +1)
    "good":2,"nice":2,"solid":2,"fine":2,"decent":2,
    "pleasant":2,"satisfying":2,"worthwhile":2,"recommend":2,
    "love":2,"loved":2,"beautiful":2,"enjoyed":2,"enjoy":2,"like":1,"liked":1,"best":1,

    # ★★★ — Neutral / Mixed (score 0)
    "okay":0,"ok":0,"average":0,"alright":0,"mixed":0,
    "ordinary":0,"predictable":0,"familiar":0,"typical":0,

    # ★★ — Below Average (score -1 to -2)
    "bad":-2,"poor":-2,"weak":-2,"dull":-2,"bland":-2,
    "boring":-2,"slow":-2,"mediocre":-2,"forgettable":-2,"disappointing":-2,
    "uninspired":-2,"generic":-2,"flat":-2,"tedious":-2,"overlong":-2,

    # ★ — Very Bad (score -3 to -4)
    "terrible":-3,"horrible":-3,"awful":-3,"dreadful":-3,"appalling":-3,
    "hate":-3,"hated":-3,"waste":-3,"pathetic":-3,"ridiculous":-3,
    "laughable":-3,"embarrassing":-3,"incoherent":-3,"unwatchable":-3,

    # ★☆☆☆☆ — Catastrophic (score -5)
    "worst":-5,"abysmal":-5,"atrocious":-5,"disgusting":-5,"unbearable":-5,
    "disaster":-5,"catastrophic":-5,"repulsive":-5,"offensive":-5,
}
NEGATIONS    = {"not","never","no","neither","nor","hardly","barely","scarcely"}
INTENSIFIERS = {"very","extremely","really","absolutely","incredibly","utterly"}

def calculate_sentiment(text):
    score = 0
    words = re.findall(r"\b\w+\b", text.lower())
    for i, word in enumerate(words):
        if word in SENTIMENT_WEIGHTS:
            val    = SENTIMENT_WEIGHTS[word]
            window = words[max(0,i-3):i]
            if any(w in NEGATIONS for w in window):      val = -val
            elif any(w in INTENSIFIERS for w in window): val *= 2
            score += val
    return score

def score_to_emoji(score, word_count=1):
    density = (score / max(word_count, 1)) * 1000
    if density >= 8:    return "★★★★★"
    elif density >= 4:  return "★★★★☆"
    elif density >= 1:  return "★★★☆☆"
    elif density >= -2: return "★★☆☆☆"
    else:               return "★☆☆☆☆"

engine = RuleEngine()

def create_chunks(reviews, chunk_size):
    return [reviews[i:i+chunk_size] for i in range(0, len(reviews), chunk_size)]

# ── File converter → reviews list ─────────────────────────────────────────────
def file_to_reviews(uploaded_file):
    """Silently converts CSV/Excel/JSON/TXT to a list of text strings."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
            uploaded_file.seek(0)
            return df.iloc[:, 0].astype(str).tolist(), df

        elif name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)
            return df.iloc[:, 0].astype(str).tolist(), df

        elif name.endswith(".json"):
            raw = json.load(uploaded_file)
            if isinstance(raw, list):
                # list of strings or list of dicts
                if isinstance(raw[0], str):
                    reviews = raw
                else:
                    key = list(raw[0].keys())[0]
                    reviews = [str(r.get(key, "")) for r in raw]
            elif isinstance(raw, dict):
                key = list(raw.keys())[0]
                reviews = [str(v) for v in raw[key]]
            df = pd.DataFrame({"text": reviews})
            return reviews, df

        elif name.endswith(".txt"):
            content = uploaded_file.read().decode("utf-8")
            reviews = [line.strip() for line in content.splitlines() if line.strip()]
            df = pd.DataFrame({"text": reviews})
            return reviews, df

        else:
            return None, None
    except Exception as e:
        return None, str(e)

# ── DB ────────────────────────────────────────────────────────────────────────
DB_NAME = "chunks.db"
KW      = ["story"]

def get_conn(db=None):    return sqlite3.connect(db or DB_NAME)

def setup_db(db=None):
    conn = get_conn(db)
    conn.execute("""CREATE TABLE IF NOT EXISTS chunk_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chunk_id INTEGER UNIQUE, word_count INTEGER,
        keyword_count INTEGER, sentiment_score REAL,
        sentiment_label TEXT, execution_time REAL)""")
    conn.commit(); conn.close()

def clear_db(db=None):
    conn = get_conn(db)
    conn.execute("DELETE FROM chunk_results")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='chunk_results'")
    conn.commit(); conn.close()

def insert_result(chunk_id, wc, kc, score, label, et, db=None):
    conn = get_conn(db)
    ex   = conn.execute("SELECT chunk_id FROM chunk_results WHERE chunk_id=?", (chunk_id,)).fetchone()
    if not ex:
        conn.execute("""INSERT INTO chunk_results
            (chunk_id,word_count,keyword_count,sentiment_score,sentiment_label,execution_time)
            VALUES (?,?,?,?,?,?)""", (chunk_id,wc,kc,score,label,et))
        conn.commit()
    conn.close()
    return not ex

def load_data(db=None):
    try:
        conn = get_conn(db)
        df   = pd.read_sql_query("SELECT * FROM chunk_results ORDER BY chunk_id", conn)
        conn.close()
        df.columns = ['id','chunk_id','word_count','keyword_count','sentiment_score','sentiment_label','execution_time']
        return df
    except: return pd.DataFrame()

# ── Theme (light only) ────────────────────────────────────────────────────────
T = {
    "bg":       "#f5f2ee",
    "surface":  "#ffffff",
    "surface2": "#ede9e3",
    "border":   "#d4cdc2",
    "text":     "#1a1714",
    "muted":    "#7a7168",
    "accent":   "#9c6b2e",
    "neg":      "#b83232",
    "pos":      "#2a7a4b",
    "neu":      "#5a5550",
    "line":     "#9c6b2e",
    "fill":     "rgba(156,107,46,0.07)",
    "grid":     "#e8e2d8",
    "input_bg": "#ffffff",
    "input_fg": "#1a1714",
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

* {{ box-sizing:border-box; }}

html, body, [class*="css"], .stApp {{
    font-family: 'DM Sans', sans-serif;
    background-color: {T['bg']} !important;
    color: {T['text']} !important;
}}
.stApp {{ background-color:{T['bg']} !important; }}

section[data-testid="stSidebar"] {{
    background: {T['surface']} !important;
    border-right: 1px solid {T['border']};
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {{ color:{T['text']} !important; }}

input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {{
    background:{T['input_bg']} !important;
    color:{T['input_fg']} !important;
    border-color:{T['border']} !important;
    border-radius:6px !important;
    font-family:'DM Mono',monospace !important;
    font-size:0.8rem !important;
}}
[data-baseweb="select"] > div {{
    background:{T['input_bg']} !important;
    border-color:{T['border']} !important;
    border-radius:6px !important;
    color:{T['input_fg']} !important;
    font-family:'DM Mono',monospace !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] div {{ color:{T['input_fg']} !important; }}

[data-testid="stSlider"] label,
[data-testid="stSlider"] p {{ color:{T['text']} !important; font-weight:500; }}
.stSlider > div > div > div {{ background:{T['accent']} !important; }}

/* Slider value — no box, just colored text */
div[data-baseweb="slider"] [data-testid="stThumbValue"],
div[data-baseweb="slider"] div[role="slider"] div {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {T['accent']} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
}}
/* Slider thumb value — plain text, no box */
[data-testid="stThumbValue"],
div[data-baseweb="slider"] [data-testid="stThumbValue"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: {T['accent']} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 0 !important;
}}
/* Slider min/max tick labels */
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {{
    color: {T['text']} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    background: transparent !important;
    border: none !important;
}}

[data-testid="metric-container"] {{
    background: {T['surface']};
    border: 1px solid {T['border']};
    border-radius: 10px;
    padding: 1.1rem 1.4rem;
    border-top: 3px solid {T['accent']};
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}}
[data-testid="stMetricValue"] {{
    color: {T['text']} !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 1.6rem !important;
    font-weight: 500 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {T['muted']} !important;
    font-size: 0.62rem !important;
    text-transform: uppercase;
    letter-spacing: 0.18em;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
}}
[data-testid="stMetricDelta"] {{
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {T['accent']} !important;
}}

.stButton > button {{
    background: {T['accent']};
    color: #ffffff;
    border: none;
    border-radius: 6px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.5rem 1.2rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    transition: opacity 0.15s, transform 0.1s;
    width: auto;
}}
.stButton > button:hover {{ opacity:0.85; transform:translateY(-1px); }}

/* Danger button */
.danger-btn > div > button {{
    background: {T['neg']} !important;
    color: #fff !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    background: {T['surface']};
    border-bottom: 2px solid {T['border']};
    border-radius: 0;
    gap: 0; padding: 0;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {T['muted']};
    border-radius: 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.75rem 1.5rem;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}}
.stTabs [aria-selected="true"] {{
    background: transparent !important;
    color: {T['accent']} !important;
    border-bottom: 2px solid {T['accent']} !important;
    font-weight: 500 !important;
}}

.stDataFrame {{ border:1px solid {T['border']}; border-radius:8px; overflow:hidden; }}

.stDownloadButton > button {{
    background: transparent !important;
    color: {T['accent']} !important;
    border: 1px solid {T['accent']} !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.45rem 1rem !important;
    transition: background 0.15s !important;
}}
.stDownloadButton > button:hover {{
    background: {T['accent']} !important;
    color: #fff !important;
}}

[data-testid="stFileUploader"] {{
    background: {T['surface']};
    border: 2px dashed {T['border']};
    border-radius: 10px;
    padding: 0.75rem;
}}
[data-testid="stFileUploader"] label {{ color:{T['text']} !important; font-weight:500; }}
[data-testid="stFileUploader"] span  {{ color:{T['muted']} !important; font-family:'DM Mono',monospace; font-size:0.75rem; }}

.sec {{
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.25em;
    color: {T['muted']};
    border-bottom: 1px solid {T['border']};
    padding-bottom: 0.4rem;
    margin: 1.4rem 0 0.9rem 0;
}}
.ic {{
    border-left: 3px solid {T['border']};
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
    line-height: 1.6;
    color: {T['text']};
    background: {T['surface']};
    border-radius: 0 6px 6px 0;
}}
.ic.pos {{ border-left-color:{T['pos']}; background:#f0faf4; }}
.ic.neg {{ border-left-color:{T['neg']}; background:#fdf3f3; }}
.ic.neu {{ border-left-color:{T['muted']}; }}

.mono {{
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: {T['text']};
    font-weight: 400;
    line-height: 2;
}}

.app-header {{
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    border-bottom: 2px solid {T['border']};
    padding-bottom: 1.2rem;
    margin-bottom: 1.8rem;
}}
.app-title {{
    font-family: 'DM Serif Display', serif;
    font-size: 3rem;
    font-weight: 400;
    font-style: italic;
    letter-spacing: -0.02em;
    line-height: 1;
    color: {T['text']};
    margin: 0;
}}
.app-title span {{ color:{T['accent']}; font-style:normal; }}
.app-meta {{
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem;
    color: {T['muted']};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    text-align: right;
    line-height: 2;
}}

.proc-box {{
    background: #f0faf4;
    border: 1px solid #b8dfc8;
    border-left: 4px solid {T['pos']};
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.9;
    color: {T['text']};
}}

p, label, span, div {{ color:{T['text']}; }}
/* Ensure all text on white bg is visible */
.stMarkdown p, .stMarkdown span, .stMarkdown div {{ color:{T['text']} !important; }}
.stSuccess, .stWarning, .stError, .stInfo {{ color:{T['text']} !important; }}
[data-testid="stText"] {{ color:{T['text']} !important; }}
/* Number inputs */
[data-baseweb="input"] input {{ color:{T['input_fg']} !important; }}
/* Select dropdown options */
[role="option"] {{ color:{T['text']} !important; background:{T['surface']} !important; }}
[role="option"]:hover {{ background:{T['surface2']} !important; }}
/* Dataframe text */
.stDataFrame td, .stDataFrame th {{ color:{T['text']} !important; font-family:'DM Mono',monospace !important; }}
</style>
""", unsafe_allow_html=True)

# ── Plot base ─────────────────────────────────────────────────────────────────
def pl(h=310, **kw):
    return dict(
        paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
        font=dict(family='DM Mono', color=T['muted'], size=10),
        margin=dict(l=10,r=10,t=36,b=10), height=h,
        xaxis=dict(gridcolor=T['grid'], zerolinecolor=T['grid'], linecolor=T['border'],
                   tickfont=dict(size=9,color=T['muted']), showline=True,
                   title_font=dict(color=T['text'])),
        yaxis=dict(gridcolor=T['grid'], zerolinecolor=T['grid'], linecolor=T['border'],
                   tickfont=dict(size=9,color=T['muted']), showline=True,
                   title_font=dict(color=T['text'])),
        **kw)

db_path  = "chunks.db"
csv_path = "imdb.csv"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sec">Stats</p>', unsafe_allow_html=True)
    df_s = load_data(db_path)
    if not df_s.empty:
        st.markdown(f'<p class="mono">CHUNKS &nbsp;&nbsp;&nbsp; {len(df_s):,}<br>LABELS &nbsp;&nbsp;&nbsp; {df_s["sentiment_label"].nunique()}<br>AVG SCORE &nbsp; {df_s["sentiment_score"].mean():.2f}<br>AVG TIME &nbsp;&nbsp; {df_s["execution_time"].mean()*1000:.1f}ms</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="mono" style="color:#9a8f7a">No data yet.</p>', unsafe_allow_html=True)

    st.markdown('<p class="sec">Database</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.78rem;color:#7a7168;margin-bottom:0.5rem">Clear all processed data and start fresh.</p>', unsafe_allow_html=True)
    if st.button("🗑 Clear Database"):
        if not df_s.empty:
            clear_db(db_path)
            st.success("Database cleared.")
            st.rerun()
        else:
            st.info("Already empty.")

# ── Load data ─────────────────────────────────────────────────────────────────
df = load_data(db_path)

total   = len(df) if not df.empty else 0
neg_pct = ((df['sentiment_score'] < 0).sum() / total * 100) if total else 0
pos_pct = ((df['sentiment_score'] > 0).sum() / total * 100) if total else 0

# ── Header ────────────────────────────────────────────────────────────────────
if df.empty:
    st.markdown(f"""
    <div class="app-header">
        <p class="app-title">Text<span>Lens</span></p>
        <div class="app-meta">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="app-header">
        <p class="app-title">Text<span>Lens</span></p>
        <div class="app-meta">
            {total:,} CHUNKS &nbsp;·&nbsp; {df['sentiment_label'].nunique()} CLASSES<br>
            {df['sentiment_score'].mean():.2f} AVG SCORE &nbsp;·&nbsp; {df['execution_time'].mean()*1000:.1f}ms AVG TIME<br>
            {datetime.now().strftime('%d %b %Y  %H:%M')}
        </div>
    </div>""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
if df.empty:
    tab0, = st.tabs(["⬆  Upload & Process"])
else:
    tab0,tab1,tab2,tab3,tab4,tab5 = st.tabs([
        "⬆  Upload & Process","Overview","Search & Filter","Analytics","Live Analyzer","Export"])

# ══ TAB 0 — UPLOAD & PROCESS ══════════════════════════════════════════════════
with tab0:
    st.markdown('<p class="sec">Upload File & Process</p>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Drop your file here — CSV, Excel, JSON, or TXT supported",
        type=["csv","xlsx","xls","json","txt"],
        label_visibility="visible")

    chunk_size = 100
    run_btn    = st.button("▶  Process Now")

    if uploaded is not None:
        reviews, preview_df = file_to_reviews(uploaded)

        if reviews is None:
            st.error(f"Could not read file: {preview_df if isinstance(preview_df, str) else 'Supported: CSV, Excel (.xlsx/.xls), JSON, TXT'}")
        elif len(reviews) == 0:
            st.warning("⚠ The uploaded file is empty — no rows found to process.")
        else:
            st.markdown(f'<p class="sec">Preview — {len(reviews):,} rows detected from <b>{uploaded.name}</b></p>', unsafe_allow_html=True)
            st.dataframe(preview_df.head(5), use_container_width=True, height=180)

            if run_btn:
                try:
                    st.markdown('<p class="sec">Processing...</p>', unsafe_allow_html=True)
                    prog   = st.progress(0)
                    status = st.empty()

                    setup_db(db_path)
                    chunks = create_chunks(reviews, chunk_size)
                    new_c  = skip_c = 0

                    for i, chunk in enumerate(chunks):
                        t0  = time.perf_counter()
                        txt = " ".join(chunk)
                        wc  = engine.word_count(txt)
                        kc  = engine.keyword_count(txt, KW)
                        sc  = calculate_sentiment(txt)
                        lbl = score_to_emoji(sc, wc)
                        et  = time.perf_counter() - t0
                        is_new = insert_result(i+1, wc, kc, sc, lbl, et, db_path)
                        if is_new: new_c  += 1
                        else:      skip_c += 1
                        pct = int((i+1)/len(chunks)*100)
                        prog.progress(pct)
                        status.markdown(f'<p class="mono" style="color:{T["muted"]}">Chunk {i+1}/{len(chunks)} · {pct}% · {lbl} · score {sc}</p>', unsafe_allow_html=True)

                    prog.progress(100)
                    status.empty()
                    st.markdown(f"""<div class="proc-box">
                        ✦ Done &nbsp;·&nbsp; {len(chunks)} chunks processed<br>
                        ↑ New &nbsp;&nbsp;&nbsp;&nbsp;{new_c} inserted<br>
                        ⊘ Skipped &nbsp;{skip_c} (already existed)<br>
                        ◈ Saved to &nbsp;{db_path}
                    </div>""", unsafe_allow_html=True)
                    st.rerun()

                except Exception as e:
                    st.error(f"Processing failed: {e}")
    else:
        st.markdown(f"""<div class="ic neu" style="margin-top:1rem">
            ◈ &nbsp; Upload any file above to get started.<br>
            &nbsp;&nbsp;&nbsp;&nbsp; Supported formats: <b>CSV, Excel, JSON, TXT</b><br>
            &nbsp;&nbsp;&nbsp;&nbsp; First column / first key will be used as text source.
        </div>""", unsafe_allow_html=True)

# ── Re-load ───────────────────────────────────────────────────────────────────
df = load_data(db_path)
if df.empty:
    st.stop()

total   = len(df)
neg_pct = (df['sentiment_score'] < 0).sum() / total * 100
pos_pct = (df['sentiment_score'] > 0).sum() / total * 100

# ══ TAB 1 — OVERVIEW ══════════════════════════════════════════════════════════
with tab1:
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("Total Chunks",  f"{total:,}")
    k2.metric("Avg Score",     f"{df['sentiment_score'].mean():.2f}")
    k3.metric("Positive %",    f"{pos_pct:.1f}%")
    k4.metric("Negative %",    f"{neg_pct:.1f}%")
    k5.metric("Avg Exec",      f"{df['execution_time'].mean()*1000:.1f}ms")
    st.markdown("<br>", unsafe_allow_html=True)

    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown('<p class="sec">Sentiment Breakdown</p>', unsafe_allow_html=True)
        counts = df['sentiment_label'].value_counts()
        browns = ['#9c6b2e','#b8860b','#c9a84c','#d4b896','#e8d5b0']
        fig_d  = go.Figure(go.Pie(
            labels=counts.index, values=counts.values, hole=0.68,
            marker=dict(colors=browns[:len(counts)], line=dict(color='#ffffff',width=2)),
            textfont=dict(family='DM Mono', size=11, color='#1a1714'),
            textinfo='percent',
            textposition='inside',
            hoverlabel=dict(
                bgcolor='#ffffff',
                font=dict(family='DM Mono', size=12, color='#1a1714'),
                bordercolor='#d4cdc2'
            )))
        fig_d.add_annotation(text=f"<b>{total}</b>", x=0.5, y=0.55,
            font=dict(size=20,family='DM Mono',color=T['text']), showarrow=False)
        fig_d.add_annotation(text="chunks", x=0.5, y=0.40,
            font=dict(size=9,family='DM Mono',color=T['muted']), showarrow=False)
        fig_d.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            font=dict(family='DM Mono',color='#1a1714',size=11),
            height=360, showlegend=True,
            legend=dict(
                orientation='v',
                x=1.02, y=0.5,
                font=dict(family='DM Mono', size=11, color='#1a1714'),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=10, r=120, t=10, b=10))
        st.plotly_chart(fig_d, use_container_width=True)

    with c2:
        st.markdown('<p class="sec">Sentiment Score Trend (15-chunk rolling avg)</p>', unsafe_allow_html=True)
        rolling = df['sentiment_score'].rolling(15, center=True).mean()
        fig_l   = go.Figure()
        fig_l.add_trace(go.Scatter(x=df['chunk_id'],y=df['sentiment_score'],mode='lines',
            name='Raw', line=dict(color=T['muted'],width=0.8), opacity=0.25))
        fig_l.add_trace(go.Scatter(x=df['chunk_id'],y=rolling,mode='lines',
            name='Rolling Avg', line=dict(color=T['accent'],width=2.5),
            fill='tozeroy', fillcolor=T['fill']))
        fig_l.add_hline(y=0, line_dash='dot', line_color=T['neg'], line_width=1, opacity=0.5)
        fig_l.update_layout(**pl(320), xaxis_title="chunk id", yaxis_title="score",
            legend=dict(bgcolor='rgba(0,0,0,0)',font=dict(size=9,color=T['muted'])))
        st.plotly_chart(fig_l, use_container_width=True)

    st.markdown('<p class="sec">Execution Time per Chunk (ms)</p>', unsafe_allow_html=True)
    exec_ms = df['execution_time'] * 1000
    fig_e   = go.Figure(go.Bar(x=df['chunk_id'], y=exec_ms,
        marker=dict(color=exec_ms,
            colorscale=[[0,T['grid']],[0.5,T['muted']],[1,T['accent']]],
            showscale=False)))
    avg_e = exec_ms.mean()
    fig_e.add_hline(y=avg_e, line_dash='dash', line_color=T['neg'], line_width=1,
        annotation_text=f"avg {avg_e:.1f}ms",
        annotation_font=dict(size=9,family='DM Mono',color=T['neg']))
    fig_e.update_layout(**pl(190), xaxis_title="chunk id", yaxis_title="ms")
    st.plotly_chart(fig_e, use_container_width=True)

    st.markdown('<p class="sec">Insights</p>', unsafe_allow_html=True)
    top_lbl  = df['sentiment_label'].value_counts().index[0]
    top_cnt  = df['sentiment_label'].value_counts().iloc[0]
    slowest  = df.loc[df['execution_time'].idxmax()]
    outliers = df[df['sentiment_score'].abs() > df['sentiment_score'].abs().quantile(0.95)]
    st.markdown(f'<div class="ic pos">↑ Dominant: <b>{top_lbl}</b> — {top_cnt} chunks ({top_cnt/total*100:.1f}%)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ic {"neg" if neg_pct>40 else "pos"}">{"⚠" if neg_pct>40 else "✓"} {neg_pct:.1f}% negative &nbsp;·&nbsp; {pos_pct:.1f}% positive</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ic neu">⏱ Slowest: chunk #{int(slowest["chunk_id"])} at {slowest["execution_time"]*1000:.2f}ms &nbsp;·&nbsp; {len(outliers)} score outliers</div>', unsafe_allow_html=True)

# ══ TAB 2 — SEARCH & FILTER ═══════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="sec">Filter</p>', unsafe_allow_html=True)
    f1,f2,f3 = st.columns(3)
    with f1: sel = st.selectbox("Sentiment Label", ['All']+sorted(df['sentiment_label'].unique().tolist()))
    with f2:
        smin,smax = float(df['sentiment_score'].min()), float(df['sentiment_score'].max())
        sr = st.slider("Score Range", smin, smax, (smin,smax), step=1.0)
    with f3:
        wmax = int(df['word_count'].max())
        wr   = st.slider("Word Count", 0, wmax, (0,wmax), step=500)

    filt = df.copy()
    if sel != 'All': filt = filt[filt['sentiment_label']==sel]
    filt = filt[(filt['sentiment_score']>=sr[0])&(filt['sentiment_score']<=sr[1])
               &(filt['word_count']>=wr[0])&(filt['word_count']<=wr[1])]

    st.markdown(f'<p class="sec">{len(filt)} results</p>', unsafe_allow_html=True)

    def style_table(data):
        import numpy as np

        def score_color(val):
            # Red for negative, yellow for neutral, green for positive
            if pd.isna(val): return 'background-color:#f5f2ee; color:#1a1714'
            if val >= 50:    return 'background-color:#1a6e3c; color:#ffffff; font-weight:600'
            elif val >= 20:  return 'background-color:#2a9d5c; color:#ffffff'
            elif val >= 5:   return 'background-color:#6dc28a; color:#1a1714'
            elif val >= -5:  return 'background-color:#f5f0e8; color:#5a4a30'
            elif val >= -20: return 'background-color:#f9b17a; color:#5a2010'
            elif val >= -50: return 'background-color:#e8604a; color:#ffffff'
            else:            return 'background-color:#b83232; color:#ffffff; font-weight:600'

        def label_color(val):
            colors = {
                "★★★★★": 'background-color:#1a6e3c; color:#fff; font-weight:700; letter-spacing:2px',
                "★★★★☆": 'background-color:#2a9d5c; color:#fff; font-weight:600; letter-spacing:2px',
                "★★★☆☆": 'background-color:#6dc28a; color:#1a1714; font-weight:600; letter-spacing:2px',
                "★★☆☆☆": 'background-color:#e8a050; color:#5a2010; font-weight:600; letter-spacing:2px',
                "★☆☆☆☆": 'background-color:#b83232; color:#fff; font-weight:700; letter-spacing:2px',
            }
            return colors.get(val, 'background-color:#f5f2ee; color:#1a1714')

        def wc_color(val):
            if pd.isna(val): return ''
            mx = data['word_count'].max()
            ratio = val / max(mx, 1)
            if ratio > 0.8:   return 'background-color:#1e5799; color:#fff'
            elif ratio > 0.6: return 'background-color:#3a7fbf; color:#fff'
            elif ratio > 0.4: return 'background-color:#7ab3d9; color:#1a1714'
            elif ratio > 0.2: return 'background-color:#c2dff0; color:#1a1714'
            else:             return 'background-color:#eaf4fb; color:#1a1714'

        def et_color(val):
            if pd.isna(val): return ''
            mx = data['execution_time'].max()
            ratio = val / max(mx, 1)
            if ratio > 0.8:   return 'background-color:#b83232; color:#fff'
            elif ratio > 0.6: return 'background-color:#d4622a; color:#fff'
            elif ratio > 0.4: return 'background-color:#e8a050; color:#1a1714'
            elif ratio > 0.2: return 'background-color:#f5d090; color:#1a1714'
            else:             return 'background-color:#fdf6e3; color:#1a1714'

        styled = data.style
        styled = styled.map(score_color, subset=['sentiment_score'])
        styled = styled.map(label_color, subset=['sentiment_label'])
        styled = styled.map(wc_color,    subset=['word_count'])
        # Black bg white text for all other columns
        styled = styled.set_properties(subset=['id','chunk_id','keyword_count','execution_time'], **{
            'background-color': '#1a1714',
            'color':            '#f5f2ee',
            'font-family':      'DM Mono, monospace',
            'font-size':        '0.78rem',
        })
        return styled

    st.markdown("""
    <style>
    [data-testid="stDataFrame"] table { border-collapse: collapse !important; }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        border: 1px solid #1a1714 !important;
    }
    </style>""", unsafe_allow_html=True)
    st.dataframe(style_table(filt), use_container_width=True, height=380)
    if not filt.empty:
        st.download_button("↓ Export Filtered", data=filt.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

    st.markdown('<p class="sec">Keyword Search in Source CSV</p>', unsafe_allow_html=True)
    kc1,kc2 = st.columns([4,1])
    with kc1: kw = st.text_input("Keyword", placeholder="e.g.  brilliant  /  terrible  /  masterpiece")
    with kc2:
        st.markdown("<br>", unsafe_allow_html=True)
        do_kw = st.button("Search →")
    if do_kw and kw.strip():
        try:
            res = []
            with open(csv_path, encoding='utf-8') as f:
                reader = csv.DictReader(f)
                tcol   = reader.fieldnames[0]
                for i,row in enumerate(reader):
                    if kw.lower() in row[tcol].lower():
                        res.append({"Row":i+1,"Preview":row[tcol][:200].replace("\n"," ")})
            if res:
                st.success(f"{len(res)} matches for '{kw}'")
                kdf = pd.DataFrame(res)
                st.dataframe(kdf, use_container_width=True, height=280)
                st.download_button("↓ Export Keyword Results", data=kdf.to_csv(index=False).encode('utf-8-sig'),
                    file_name=f"kw_{kw}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
            else: st.warning(f"No matches for '{kw}'")
        except FileNotFoundError:
            st.error(f"'{csv_path}' not found.")

# ══ TAB 3 — ANALYTICS ════════════════════════════════════════════════════════
with tab3:
    a1,a2 = st.columns(2)
    with a1:
        st.markdown('<p class="sec">Avg Score by Label</p>', unsafe_allow_html=True)
        avg_l = df.groupby('sentiment_label')['sentiment_score'].mean().reset_index().sort_values('sentiment_score')
        bar_c = [T['neg'] if v<0 else T['pos'] for v in avg_l['sentiment_score']]
        fig_b = go.Figure(go.Bar(
            x=avg_l['sentiment_label'], y=avg_l['sentiment_score'],
            marker=dict(color=bar_c, line=dict(color='#ffffff',width=1)),
            text=[f"{v:.1f}" for v in avg_l['sentiment_score']],
            textposition='outside',
            textfont=dict(family='DM Mono',size=11,color='#1a1714')))
        fig_b.add_hline(y=0, line_color='#1a1714', line_width=1)
        fig_b.update_layout(
            paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            font=dict(family='DM Mono', color='#1a1714', size=11),
            height=320, margin=dict(l=10,r=10,t=36,b=10),
            xaxis=dict(title=dict(text="label", font=dict(color='#1a1714',size=11)),
                       tickfont=dict(color='#1a1714',size=11), gridcolor=T['grid'],
                       zerolinecolor=T['grid'], linecolor=T['border'], showline=True),
            yaxis=dict(title=dict(text="avg score", font=dict(color='#1a1714',size=11)),
                       tickfont=dict(color='#1a1714',size=11), gridcolor=T['grid'],
                       zerolinecolor=T['grid'], linecolor=T['border'], showline=True))
        st.plotly_chart(fig_b, use_container_width=True)
    with a2:
        st.markdown('<p class="sec">Word Count vs Score</p>', unsafe_allow_html=True)
        fig_sc = go.Figure(go.Scatter(
            x=df['word_count'], y=df['sentiment_score'], mode='markers',
            marker=dict(color=df['sentiment_score'],
                colorscale=[[0,T['neg']],[0.5,T['muted']],[1,T['pos']]],
                size=5, opacity=0.6, line=dict(width=0))))
        fig_sc.add_hline(y=0, line_dash='dot', line_color='#1a1714', line_width=1)
        fig_sc.update_layout(
            paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            font=dict(family='DM Mono', color='#1a1714', size=11),
            height=300, margin=dict(l=10,r=10,t=36,b=10),
            xaxis=dict(title=dict(text="word count", font=dict(color='#1a1714',size=11)),
                       tickfont=dict(color='#1a1714',size=11), gridcolor=T['grid'],
                       zerolinecolor=T['grid'], linecolor=T['border'], showline=True),
            yaxis=dict(title=dict(text="score", font=dict(color='#1a1714',size=11)),
                       tickfont=dict(color='#1a1714',size=11), gridcolor=T['grid'],
                       zerolinecolor=T['grid'], linecolor=T['border'], showline=True))
        st.plotly_chart(fig_sc, use_container_width=True)

# ══ TAB 4 — LIVE ANALYZER ════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="sec">Analyze Any Text</p>', unsafe_allow_html=True)
    user_text = st.text_area("Text Input", height=130,
        placeholder="Paste any review, sentence, or paragraph here…",
        label_visibility="collapsed")
    if st.button("Analyze →") and user_text.strip():
        pol = calculate_sentiment(user_text)
        wc  = engine.word_count(user_text)
        kc  = engine.keyword_count(user_text, KW)
        lbl = score_to_emoji(pol, wc)

        if pol >= 5:    ltxt,lcol = "★★★★★  EXCEPTIONAL",  T['pos']
        elif pol >= 2:  ltxt,lcol = "★★★★☆  VERY GOOD",    "#2a9d5c"
        elif pol >= 0:  ltxt,lcol = "★★★☆☆  DECENT",       T['muted']
        elif pol >= -3: ltxt,lcol = "★★☆☆☆  BELOW AVG",   "#c07830"
        else:           ltxt,lcol = "★☆☆☆☆  NEGATIVE",    T['neg']

        m1,m2,m3,m4 = st.columns(4)
        m1.metric("Score",    f"{pol}")
        m2.metric("Label",    lbl)
        m3.metric("Words",    wc)
        m4.metric("Keywords", kc)

        clamped = max(-10, min(10, pol))
        fig_g   = go.Figure()
        fig_g.add_trace(go.Bar(x=[clamped], y=[""], orientation='h',
            marker=dict(color=lcol), width=0.35))
        fig_g.add_vline(x=0, line_color=T['border'], line_width=2)
        fig_g.update_layout(
            paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            height=110, margin=dict(l=10,r=10,t=38,b=10),
            font=dict(family='DM Mono',color=T['muted'],size=10),
            title=dict(text=f"{lbl} &nbsp; {ltxt}", font=dict(family='DM Mono',size=12,color=lcol)),
            xaxis=dict(range=[-10,10], gridcolor=T['grid'], zerolinecolor=T['grid'],
                       tickvals=[-10,-5,0,5,10], tickfont=dict(color=T['muted'],size=9), showline=True),
            yaxis=dict(showticklabels=False, showgrid=False))
        st.plotly_chart(fig_g, use_container_width=True)

# ══ TAB 5 — EXPORT ════════════════════════════════════════════════════════════
with tab5:
    e1,e2 = st.columns(2)
    with e1:
        st.markdown('<p class="sec">All Chunks</p>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:0.78rem;color:#7a7168;margin-bottom:0.5rem">Exports all processed chunk results from the database.</p>', unsafe_allow_html=True)
        st.download_button("↓ Download All Chunk Results", data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"chunk_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv", use_container_width=True)
    with e2:
        st.markdown('<p class="sec">By Label</p>', unsafe_allow_html=True)
        exp_lbl = st.selectbox("Label", df['sentiment_label'].unique(), key="exp_lbl")
        ldf     = df[df['sentiment_label']==exp_lbl]
        st.download_button(f"↓ Download ({len(ldf)} rows)",
            data=ldf.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"lbl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv", use_container_width=True)

    st.markdown('<p class="sec">By Score Range</p>', unsafe_allow_html=True)
    sr1,sr2 = st.columns(2)
    with sr1: rmin = st.number_input("Min Score", value=float(df['sentiment_score'].min()))
    with sr2: rmax = st.number_input("Max Score", value=float(df['sentiment_score'].max()))
    rdf = df[(df['sentiment_score']>=rmin)&(df['sentiment_score']<=rmax)]
    st.markdown(f'<p class="mono">{len(rdf)} chunks in range [{rmin:.0f}, {rmax:.0f}]</p>', unsafe_allow_html=True)
    st.download_button("↓ Download by Sentiment Score", data=rdf.to_csv(index=False).encode('utf-8-sig'),
        file_name=f"score_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv", use_container_width=True)

    st.markdown('<p class="sec">Summary Stats</p>', unsafe_allow_html=True)
    st.dataframe(df.describe().round(3), use_container_width=True)