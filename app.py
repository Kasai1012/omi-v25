import streamlit as st
import sqlite3

# =========================
# DB INIT（安定版）
# =========================

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# ★ 安定化ポイント：毎回スキーマ保証（開発用）
c.execute("DROP TABLE IF EXISTS items")

c.execute("""
CREATE TABLE items (
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

    # 現実KVA帯評価
    if kva in [25, 45]:
        s += 15
    elif kva in [60, 80]:
        s += 25
    elif kva in [100, 150]:
        s += 40
    elif kva in [200, 220]:
        s += 45
    elif kva in [300, 500]:
        s += 35
    else:
        s += 10

    # 価格効率
    if price < 1000000:
        s += 20
    elif price < 2000000:
        s += 10
    else:
        s -= 5

    return s

# =========================
# DB INSERT
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

st.title("OMI v4.5 Stable - Industrial Market OS")

tab1, tab2 = st.tabs(["🧾 出品", "🔍 商品一覧"])

# =========================
# ① 出品（現実仕様KVA）
# =========================

with tab1:

    st.subheader("出品登録（安定版）")

    name = st.text_input("モデル名")

    maker = st.selectbox(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva = st.selectbox(
        "kVA（実務レンジ）",
        [25, 45, 60, 80, 100, 150, 200, 220, 300, 500]
    )

    year = st.selectbox(
        "年式",
        list(range(2026, 1990, -1))
    )

    hours = st.text_input("稼働時間")
    price = st.text_input("価格")
    note = st.text_area("備考")

    image_file = st.file_uploader("画像", type=["jpg", "png"])

    if st.button("出品する"):

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

        st.success("出品完了（安定版）")

# =========================
# ② 商品一覧
# =========================

with tab2:

    st.subheader("商品一覧")

    items = fetch_items()

    results = []

    for i in items:

        name, maker, kva, hours, price, year, note, image = i

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

    st.subheader(f"登録件数: {len(results)}件")

    for i, r in enumerate(results, 1):

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            if r["image"]:
                st.image(r["image"], width=160)

        with col2:
            st.markdown(f"""
### {r['name']}（{r['maker']}）

**🔥 Score: {r['score']}**

- ⚡ kVA: {r['kva']}
- 📅 年式: {r['year']}
- ⏱ 稼働: {r['hours']}
- 💰 価格: ¥{r['price']:,}

📝 {r['note']}
""")
