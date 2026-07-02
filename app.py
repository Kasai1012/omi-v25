import streamlit as st
import sqlite3

# =========================
# DB
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
# SCORE
# =========================

def score(kva, price):

    s = 0

    if kva in [25, 45]:
        s += 20
    elif kva in [60, 100]:
        s += 40
    elif kva in [150, 200]:
        s += 35
    else:
        s += 10

    if price < 1000000:
        s += 20
    elif price < 2000000:
        s += 10
    else:
        s -= 5

    return s

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

st.title("OMI v4.5 - Advanced Search Market")

tab1, tab2 = st.tabs(["🧾 出品", "🔍 検索"])

# =========================
# ① 出品（変更なし）
# =========================

with tab1:

    st.subheader("出品（v4.4）")

    name = st.text_input("モデル名")

    maker = st.selectbox(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva = st.selectbox(
        "kVA",
        [25, 45, 60, 100, 150, 200]
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

        c.execute("""
            INSERT INTO items
            (name, maker, kva, hours, price, year, note, image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, maker, kva, hours_val, price_val, year, note, img_bytes))

        conn.commit()

        st.success("出品完了")

# =========================
# ② 検索（強化版）
# =========================

with tab2:

    st.subheader("検索フィルタ")

    col1, col2, col3 = st.columns(3)

    with col1:
        maker_filter = st.multiselect(
            "メーカー",
            ["デンヨー", "AIRMAN", "ヤンマー", "その他"],
            default=[]
        )

    with col2:
        kva_filter = st.multiselect(
            "kVA",
            [25, 45, 60, 100, 150, 200],
            default=[]
        )

    with col3:
        year_filter = st.slider(
            "年式（範囲）",
            1990, 2026,
            (2000, 2026)
        )

    price_min = st.number_input("最低価格", value=0)
    price_max = st.number_input("最高価格", value=10000000)

    sort_type = st.selectbox(
        "並び順",
        ["おすすめ順", "価格が安い順", "価格が高い順", "新しい順", "kVA大きい順"]
    )

    items = fetch_items()

    results = []

    for i in items:

        name, maker, kva, hours, price, year, note, image = i

        # フィルタ
        if maker_filter and maker not in maker_filter:
            continue

        if kva_filter and kva not in kva_filter:
            continue

        if not (year_filter[0] <= year <= year_filter[1]):
            continue

        if not (price_min <= price <= price_max):
            continue

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

    # ソート
    if sort_type == "おすすめ順":
        results.sort(key=lambda x: x["score"], reverse=True)

    elif sort_type == "価格が安い順":
        results.sort(key=lambda x: x["price"])

    elif sort_type == "価格が高い順":
        results.sort(key=lambda x: x["price"], reverse=True)

    elif sort_type == "新しい順":
        results.sort(key=lambda x: x["year"], reverse=True)

    elif sort_type == "kVA大きい順":
        results.sort(key=lambda x: x["kva"], reverse=True)

    # 表示
    st.subheader(f"検索結果：{len(results)}件")

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
