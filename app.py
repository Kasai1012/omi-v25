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
    hours INTEGER,
    price INTEGER,
    year INTEGER,
    note TEXT,
    image BLOB
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

def insert_item(name, maker, kva, hours, price, year, note, image):

    c.execute("""
        INSERT INTO items
        (name, maker, kva, hours, price, year, note, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, maker, kva, hours, price, year, note, image))

    conn.commit()

# =========================
# FETCH
# =========================

def fetch_items():

    c.execute("""
        SELECT name, maker, kva, hours, price, year, note, image
        FROM items
    """)

    return c.fetchall()

# =========================
# UI
# =========================

st.title("OMI v4.3 - Practical Market OS")

tab1, tab2 = st.tabs(["🧾 出品", "🔍 検索"])

# =========================
# ① 出品（実務仕様）
# =========================

with tab1:

    st.subheader("出品登録（業者仕様）")

    name = st.text_input("モデル名")

    maker = st.selectbox(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva = st.number_input("kVA", value=50)

    hours = st.text_input("稼働時間（例: 3745h / 不明でもOK）")

    price = st.text_input("価格（例: 1,200,000）")

    year = st.selectbox(
        "年式",
        list(range(2026, 1990, -1))
    )

    note = st.text_area("備考（状態・整備履歴など）")

    image_file = st.file_uploader("画像（1枚）", type=["jpg", "png"])

    if st.button("出品する"):

        # 数値変換（ゆるく）
        try:
            hours_val = int(''.join(filter(str.isdigit, hours)))
        except:
            hours_val = 0

        try:
            price_val = int(''.join(filter(str.isdigit, price)))
        except:
            price_val = 0

        img_bytes = image_file.read() if image_file else None

        insert_item(
            name, maker, kva,
            hours_val, price_val,
            year, note, img_bytes
        )

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

        name, maker, kva, hours, price, year, note, image = i

        if min_kva <= kva <= max_kva:

            results.append({
                "name": name,
                "maker": maker,
                "kva": kva,
                "hours": hours,
                "price": price,
                "year": year,
                "note": note,
                "image": image,
                "score": score(kva, price)
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    st.subheader("検索結果")

    for i, r in enumerate(results, 1):

        st.markdown(f"""
---

## #{i} {r['name']}（{r['maker']}）

**🔥 Score: {r['score']}**

- kVA: {r['kva']}
- 年式: {r['year']}
- 稼働時間: {r['hours']}
- 価格: ¥{r['price']:,}

**📝 備考**
{r['note']}
""")

        if r["image"]:
            st.image(r["image"])
