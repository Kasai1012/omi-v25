import streamlit as st
import sqlite3
from datetime import datetime

st.title("🛠 SELLER（出品管理）")

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# ログイン（簡易）
user = st.text_input("ユーザー名")
pw = st.text_input("パスワード", type="password")

if user and pw:
    st.success("ログイン状態")

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")
    kva = st.selectbox("KVA", [50,100,200,300,500,750,1000])
    price = st.number_input("価格", min_value=0)
    year = st.selectbox("年式", list(range(1990, datetime.now().year+1)))
    note = st.text_area("備考")

    if st.button("登録"):
        c.execute("""
            INSERT INTO items (title, maker, kva, price, year, note)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, maker, kva, price, year, note))
        conn.commit()
        st.success("登録完了")
