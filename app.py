import streamlit as st
import sqlite3
import uuid

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

st.title("OMI Market")

# =========================
# SESSION
# =========================
if "seller_id" not in st.session_state:
    st.session_state.seller_id = None

# =========================
# PUBLIC VIEW（v4.7コア）
# =========================
def public_view():

    st.subheader("発電機・建機マーケット")

    items = c.execute("""
        SELECT item_id, title, kva, price FROM items
    """).fetchall()

    for i in items:
        st.write(f"🟢 {i[1]} / {i[2]}KVA / ¥{i[3]}")

        st.markdown(f"[詳細を見る](?item={i[0]})")

    st.markdown("---")
    st.markdown("### 出品者の方はこちら")
    if st.button("ログイン / 出品管理"):
        st.session_state.page = "login"
        st.rerun()

# =========================
# LOGIN
# =========================
def login_view():

    st.subheader("出品者ログイン")

    name = st.text_input("会社名")

    if st.button("ログイン"):
        seller = c.execute("""
            SELECT seller_id FROM sellers WHERE company_name=?
        """, (name,)).fetchone()

        if seller:
            st.session_state.seller_id = seller[0]
            st.session_state.page = "dashboard"
            st.rerun()
        else:
            st.error("未登録です")

    if st.button("← 戻る"):
        st.session_state.page = "public"
        st.rerun()

# =========================
# DASHBOARD（v5）
# =========================
def dashboard_view():

    if not st.session_state.seller_id:
        st.session_state.page = "login"
        st.rerun()

    st.subheader("出品者ダッシュボード")

    items = c.execute("""
        SELECT title, kva, price FROM items
        WHERE seller_id=?
    """, (st.session_state.seller_id,)).fetchall()

    for i in items:
        st.write(f"📦 {i[0]} / {i[1]}KVA / ¥{i[2]}")

    st.markdown("---")

    st.write("### 新規出品")

    title = st.text_input("商品名")
    kva = st.selectbox("KVA", ["20","25","45","60","100","150","200"])
    price = st.text_input("価格")
    year = st.text_input("年式")
    note = st.text_area("備考")

    if st.button("出品する"):
        item_id = str(uuid.uuid4())

        c.execute("""
            INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item_id, st.session_state.seller_id, title, kva, price, year, note, ""))
        conn.commit()

        st.success("出品完了")

# =========================
# ROUTER（最小）
# =========================
if "page" not in st.session_state:
    st.session_state.page = "public"

if st.session_state.page == "public":
    public_view()

elif st.session_state.page == "login":
    login_view()

elif st.session_state.page == "dashboard":
    dashboard_view()
