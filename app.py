import streamlit as st
import sqlite3
import uuid
from datetime import datetime

# =====================
# DB初期化
# =====================
conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS sellers (
    seller_id TEXT PRIMARY KEY,
    company_name TEXT,
    contact_name TEXT,
    phone TEXT,
    email TEXT,
    location TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    seller_id TEXT,
    title TEXT,
    maker TEXT,
    kva TEXT,
    hours TEXT,
    price TEXT,
    year TEXT,
    description TEXT,
    image TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS leads (
    lead_id TEXT PRIMARY KEY,
    item_id TEXT,
    seller_id TEXT,
    message TEXT,
    created_at TEXT
)
""")

conn.commit()

# =====================
# UI
# =====================
st.title("OMI v5.1 Market System")

menu = st.sidebar.selectbox(
    "Menu",
    ["出品者登録", "商品登録", "商品一覧", "商品詳細"]
)

# =====================
# 出品者登録
# =====================
if menu == "出品者登録":
    st.header("出品者登録")

    company = st.text_input("会社名")
    contact = st.text_input("担当者")
    phone = st.text_input("電話番号")
    email = st.text_input("Email")
    location = st.text_input("所在地")

    if st.button("登録"):
        seller_id = str(uuid.uuid4())

        c.execute("""
        INSERT INTO sellers VALUES (?, ?, ?, ?, ?, ?)
        """, (seller_id, company, contact, phone, email, location))

        conn.commit()
        st.success("出品者登録完了")

# =====================
# 商品登録
# =====================
elif menu == "商品登録":
    st.header("商品登録")

    sellers = c.execute("SELECT seller_id, company_name FROM sellers").fetchall()
    seller_dict = {s[1]: s[0] for s in sellers}

    seller_name = st.selectbox("出品者", list(seller_dict.keys()) if sellers else [])

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")

    kva = st.selectbox("KVA", ["20", "25", "45", "60", "100", "150", "200", "300"])

    hours = st.text_input("稼働時間")
    price = st.text_input("価格")
    year = st.text_input("年式")
    desc = st.text_area("備考")
    img = st.text_input("画像URL（仮）")

    if st.button("登録"):
        item_id = str(uuid.uuid4())
        seller_id = seller_dict.get(seller_name)

        c.execute("""
        INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, seller_id, title, maker, kva, hours, price, year, desc, img))

        conn.commit()
        st.success("商品登録完了")

# =====================
# 商品一覧
# =====================
elif menu == "商品一覧":
    st.header("商品一覧")

    items = c.execute("""
    SELECT item_id, title, maker, kva, price FROM items
    """).fetchall()

    for i in items:
        st.write(f"🟢 {i[1]} / {i[2]} / {i[3]}KVA / ¥{i[4]}")

# =====================
# 商品詳細
# =====================
elif menu == "商品詳細":
    st.header("商品詳細")

    item_id_input = st.text_input("商品IDを入力")

    if item_id_input:
        item = c.execute("""
        SELECT * FROM items WHERE item_id=?
        """, (item_id_input,)).fetchone()

        if item:
            seller = c.execute("""
            SELECT company_name, phone, email FROM sellers WHERE seller_id=?
            """, (item[1],)).fetchone()

            st.subheader(item[2])
            st.write(f"メーカー: {item[3]}")
            st.write(f"KVA: {item[4]}")
            st.write(f"稼働時間: {item[5]}")
            st.write(f"価格: {item[6]}")
            st.write(f"年式: {item[7]}")
            st.write(f"備考: {item[8]}")

            st.markdown("### 出品者情報")
            st.write(seller)

            st.markdown("### 問い合わせ")
            msg = st.text_area("問い合わせ内容")

            if st.button("送信"):
                lead_id = str(uuid.uuid4())

                c.execute("""
                INSERT INTO leads VALUES (?, ?, ?, ?, ?)
                """, (lead_id, item_id_input, item[1], msg, str(datetime.now())))

                conn.commit()
                st.success("送信完了")
        else:
            st.error("商品が見つかりません")
