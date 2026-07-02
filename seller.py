import streamlit as st
import sqlite3
from datetime import datetime

st.set_page_config(page_title="OMI SELLER", layout="wide")

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

st.title("🛠 SELLER管理画面")

# =========================
# BACK TO TOP
# =========================
if st.button("← TOPへ戻る"):
    st.switch_page("app.py")

# =========================
# LOGIN（簡易）
# =========================
st.subheader("🔐 ログイン")

user = st.text_input("ユーザー名")
pw = st.text_input("パスワード", type="password")

login = (user != "" and pw != "")

if login:
    st.success("ログイン状態")

    st.subheader("📦 出品登録")

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")

    kva = st.selectbox("KVA", [50, 100, 200, 300, 500, 750, 1000])

    price = st.number_input("価格", min_value=0)

    year = st.selectbox("年式", list(range(1990, datetime.now().year + 1)))

    note = st.text_area("備考")

    if st.button("登録"):
        c.execute("""
            INSERT INTO items (title, maker, kva, price, year, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, maker, kva, price, year, note))
        conn.commit()
        st.success("登録完了")

    st.write("## 📋 出品一覧")

    items = c.execute("SELECT title, kva, price, year FROM items").fetchall()

    for i in items:
        st.write(f"{i[0]} / {i[1]}KVA / ¥{i[2]} / {i[3]}年")
