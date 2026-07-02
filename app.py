import streamlit as st
import sqlite3

# =========================
# DB INITIALIZE
# =========================

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    kva INTEGER,
    price INTEGER
)
""")

conn.commit()

# =========================
# SCORE ENGINE
# =========================

def score(kva, price):

    s = 0

    if 50 <= kva <= 100:
        s += 40
    elif 100 < kva <= 150:
        s += 35
    else:
        s += 20

    if price < 1000000:
        s += 20
    elif price < 2000000:
        s += 10
    else:
        s -= 5

    return s

# =========================
# INSERT
# =========================

def insert_item(name, kva, price):
    c.execute(
        "INSERT INTO items (name, kva, price) VALUES (?, ?, ?)",
        (name, kva, price)
    )
    conn.commit()

# =========================
# FETCH
# =========================

def fetch_items():
    c.execute("SELECT name, kva, price FROM items")
    return c.fetchall()

# =========================
# UI
# =========================

st.title("OMI v4.1 - SQLite Market OS")

tab1, tab2 = st.tabs(["🧾 出品", "🏆 ランキング"])

# -------------------------
# 出品
# -------------------------

with tab1:

    st.subheader("出品登録")

    name = st.text_input("モデル名")
    kva = st.number_input("kVA", value=50)
    price = st.number_input("価格", value=1000000)

    if st.button("出品する"):

        insert_item(name, kva, price)
        st.success("登録完了")

# -------------------------
# ランキング
# -------------------------

with tab2:

    st.subheader("TOPランキング")

    items = fetch_items()

    ranked = []

    for i in items:
        name, kva, price = i
        ranked.append({
            "name": name,
            "kva": kva,
            "price": price,
            "score": score(kva, price)
        })

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    for i, r in enumerate(ranked[:30], 1):

        st.markdown(f"""
### #{i} {r['name']}
- kVA: {r['kva']}
- Price: {r['price']}
- Score: {r['score']}
""")
