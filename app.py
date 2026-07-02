import streamlit as st
import sqlite3
import uuid

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

st.title("OMI Market v4.7")

# =========================
# SESSION
# =========================
if "seller_id" not in st.session_state:
    st.session_state.seller_id = None

if "page" not in st.session_state:
    st.session_state.page = "TOP"

# =========================
# TOP PAGE（必ず表示）
# =========================
def show_top():

    st.subheader("公開マーケット（TOP）")

    items = c.execute("""
        SELECT item_id, title, maker, kva, price FROM items
    """).fetchall()

    for i in items:
        st.write(f"🟢 {i[1]} / {i[2]} / {i[3]}KVA / ¥{i[4]}")

    st.markdown("---")

    if st.button("🔑 出品者ログイン"):
        st.session_state.page = "LOGIN"
        st.rerun()

# =========================
# LOGIN
# =========================
def show_login():

    st.subheader("ログイン")

    name = st.text_input("会社名")

    if st.button("ログイン"):
        seller = c.execute("""
            SELECT seller_id FROM sellers WHERE company_name=?
        """, (name,)).fetchone()

        if seller:
            st.session_state.seller_id = seller[0]
            st.session_state.page = "DASH"
            st.rerun()
        else:
            st.error("見つかりません")

    if st.button("← TOPへ戻る"):
        st.session_state.page = "TOP"
        st.rerun()

# =========================
# DASHBOARD
# =========================
def show_dashboard():

    if not st.session_state.seller_id:
        st.warning("未ログイン")
        st.session_state.page = "TOP"
        st.rerun()

    st.subheader("出品者ダッシュボード")

    items = c.execute("""
        SELECT title, kva, price FROM items
        WHERE seller_id=?
    """, (st.session_state.seller_id,)).fetchall()

    for i in items:
        st.write(f"📦 {i[0]} / {i[1]} / ¥{i[2]}")

    if st.button("← TOPへ"):
        st.session_state.page = "TOP"
        st.rerun()

# =========================
# ROUTER
# =========================
if st.session_state.page == "TOP":
    show_top()

elif st.session_state.page == "LOGIN":
    show_login()

elif st.session_state.page == "DASH":
    show_dashboard()
