import streamlit as st
import sqlite3
import uuid

# =========================
# DB
# =========================
conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS sellers (
    seller_id TEXT PRIMARY KEY,
    company_name TEXT,
    contact_name TEXT,
    phone TEXT,
    email TEXT
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
    note TEXT
)
""")

conn.commit()

# =========================
# SESSION
# =========================
if "seller_id" not in st.session_state:
    st.session_state.seller_id = None

# =========================
# HEADER
# =========================
st.title("OMI Market v4.7")

menu = st.sidebar.radio(
    "Menu",
    ["🔍 商品を見る（公開）", "🏪 出品者ログイン", "📦 出品者ダッシュボード"]
)

# =========================
# PUBLIC VIEW（v4.7コア）
# =========================
if menu == "🔍 商品を見る（公開）":

    st.subheader("発電機・建機マーケット")

    items = c.execute("""
        SELECT item_id, title, maker, kva, price
        FROM items
    """).fetchall()

    for i in items:
        st.write(f"🟢 {i[1]} / {i[2]} / {i[3]}KVA / ¥{i[4]}")

        if st.button(f"詳細を見る {i[0]}"):
            st.session_state.selected_item = i[0]

    # =====================
    # LOGIN LINK（ここが重要）
    # =====================
    st.markdown("---")
    st.info("出品者の方はこちら → ログインして出品管理できます")
    if st.button("🔑 出品者ログインへ"):
        st.session_state.goto_login = True
        st.experimental_rerun()

# =========================
# LOGIN
# =========================
elif menu == "🏪 出品者ログイン":

    st.subheader("出品者ログイン（簡易）")

    seller_name = st.text_input("会社名（仮ログイン）")

    if st.button("ログイン"):
        seller = c.execute("""
            SELECT seller_id FROM sellers WHERE company_name=?
        """, (seller_name,)).fetchone()

        if seller:
            st.session_state.seller_id = seller[0]
            st.success("ログイン成功")
        else:
            st.error("出品者が見つかりません")

# =========================
# DASHBOARD（v5側）
# =========================
elif menu == "📦 出品者ダッシュボード":

    if not st.session_state.seller_id:
        st.warning("先にログインしてください")
        st.stop()

    st.subheader("あなたの出品管理")

    # 自分のアイテム
    items = c.execute("""
        SELECT item_id, title, kva, price
        FROM items
        WHERE seller_id=?
    """, (st.session_state.seller_id,)).fetchall()

    st.write("## 出品一覧")

    for i in items:
        st.write(f"📦 {i[1]} / {i[2]}KVA / ¥{i[3]}")

    st.write("---")
    st.write("## 新規出品")

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")

    kva = st.selectbox("KVA", ["20", "25", "45", "60", "100", "150", "200"])

    hours = st.text_input("稼働時間")
    price = st.text_input("価格")
    year = st.text_input("年式")
    note = st.text_area("備考")

    if st.button("出品する"):
        item_id = str(uuid.uuid4())

        c.execute("""
            INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            st.session_state.seller_id,
            title,
            maker,
            kva,
            hours,
            price,
            year,
            note
        ))

        conn.commit()
        st.success("出品完了")
