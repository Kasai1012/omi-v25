import streamlit as st
import sqlite3

st.title("OMI Market v4.6")

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# itemsテーブル確認（無くても落ちない）
try:
    items = c.execute("SELECT title, kva, price FROM items").fetchall()
except:
    items = []

st.write("## 商品一覧")

if len(items) == 0:
    st.info("商品がまだありません")
else:
    for i in items:
        st.write(f"{i[0]} / {i[1]}KVA / ¥{i[2]}")
