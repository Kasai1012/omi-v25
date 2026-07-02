import streamlit as st
import sqlite3

# =========================
# DB RESET + INIT
# =========================

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# ★完全リセット（開発用）
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
# SCORE
# =========================

def score(kva, price):

    s = 0

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

    if price < 1000000:
        s += 20
    elif price < 2000000:
        s += 10
    else:
        s -= 5

    return s

# =========================
# DB
# =========================

def insert_item(name, maker, kva, hours, price, year, note, image):

    c.execute("""
        INSERT INTO items
        (name, maker, kva, hours, price, year, note, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, maker, kva, hours, price, year, note, image))

    conn.commit()

def fetch_items():

    c.execute("""
        SELECT id, name, maker, kva, hours, price, year, note, image
        FROM items
    """)

    return c.fetchall()

def get_item(item_id):

    c.execute("""
        SELECT id, name, maker, kva, hours, price, year, note, image
        FROM items WHERE id=?
    """, (item_id,))

    return c.fetchone()

# =========================
# UI
# =========================

st.title("OMI v4.6 - Marketplace + Detail View")

tab1, tab2 = st.tabs(["🧾 出品", "🔍 検索"])

# =========================
# ① 出品
# =========================

with tab1:

    st.subheader("出品登録")

    name = st.text_input("モデル名")

    maker = st.selectbox(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva = st.selectbox(
        "kVA",
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

        st.success("出品完了")

# =========================
# ② 検索
# =========================

with tab2:

    st.subheader("検索")

    items = fetch_items()

    # フィルタ
    maker_filter = st.multiselect(
        "メーカー",
        ["デンヨー", "AIRMAN", "ヤンマー", "その他"]
    )

    kva_filter = st.multiselect(
        "kVA",
        [25, 45, 60, 80, 100, 150, 200, 220, 300, 500]
    )

    price_max = st.number_input("最大価格", value=10000000)

    results = []

    for i in items:

        item_id, name, maker, kva, hours, price, year, note, image = i

        if maker_filter and maker not in maker_filter:
            continue

        if kva_filter and kva not in kva_filter:
            continue

        if price > price_max:
            continue

        results.append({
            "id": item_id,
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

    results.sort(key=lambda x: x["score"], reverse=True)

    st.subheader(f"検索結果: {len(results)}件")

    # =========================
    # カード表示 + 詳細導線
    # =========================

    for r in results:

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        with col1:
            if r["image"]:
                st.image(r["image"], width=150)

        with col2:
            st.markdown(f"""
### {r['name']}（{r['maker']}）

**🔥 Score: {r['score']}**

- ⚡ kVA: {r['kva']}
- 📅 年式: {r['year']}
- ⏱ 稼働: {r['hours']}
- 💰 価格: ¥{r['price']:,}
""")

            if st.button(f"詳細を見る（ID:{r['id']}）"):
                st.session_state.selected_id = r["id"]

# =========================
# 詳細ページ
# =========================

if "selected_id" in st.session_state:

    item = get_item(st.session_state.selected_id)

    if item:

        _, name, maker, kva, hours, price, year, note, image = item

        st.markdown("---")
        st.header("📄 商品詳細")

        col1, col2 = st.columns([1, 2])

        with col1:
            if image:
                st.image(image)

        with col2:
            st.markdown(f"""
## {name}（{maker}）

- ⚡ kVA: {kva}
- 📅 年式: {year}
- ⏱ 稼働時間: {hours}
- 💰 価格: ¥{price:,}

---

### 📝 備考
{note}
""")
