import streamlit as st
import sqlite3

# =========================
# DB SETUP
# =========================

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    maker TEXT,
    kva INTEGER,
    year INTEGER,
    hours INTEGER,
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
# DB FUNCTIONS
# =========================

def insert_item(name, maker, kva, year, hours, price):
    c.execute("""
        INSERT INTO items (name, maker, kva, year, hours, price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, maker, kva, year, hours, price))
    conn.commit()

def fetch_items():
    c.execute("SELECT name, maker, kva, year, hours, price FROM items")
    return c.fetchall()

# =========================
# UI
# =========================

st.title("OMI v4.2改 - SQLite Market OS")

tab1, tab2 = st.tabs(["🧾 出品", "🔍 検索"])

# =========================
# ① 出品（改善版）
# =========================

with tab1:

    st.subheader("出品登録")

    name = st.text_input("モデル名")

    maker = st.selectbox(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva = st.number_input("kVA", value=50)

    year = st.selectbox(
        "年式",
        list(range(2026, 1990, -1))
    )

    hours = st.number_input("稼働時間", value=3000)

    price = st.number_input("価格", value=1000000)

    if st.button("出品する"):

        insert_item(name, maker, kva, year, hours, price)
        st.success("登録完了")

# =========================
# ② 検索
# =========================

with tab2:

    st.subheader("検索")

    min_kva = st.number_input("Min KVA", value=0)
    max_kva = st.number_input("Max KVA", value=200)

    items = fetch_items()

    results = []

    for i in items:

        name, maker, kva, year, hours, price = i

        if min_kva <= kva <= max_kva:

            results.append({
                "name": name,
                "maker": maker,
                "kva": kva,
                "year": year,
                "hours": hours,
                "price": price,
                "score": score(kva, price)
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    st.subheader("検索結果")

    for i, r in enumerate(results, 1):

        st.markdown(f"""
---

### #{i} {r['name']}（{r['maker']}）

**🔥 Score: {r['score']}**

- kVA: {r['kva']}
- 年式: {r['year']}
- 稼働時間: {r['hours']}
- 価格: ¥{r['price']:,}
""")
