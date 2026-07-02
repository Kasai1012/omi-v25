import streamlit as st
import sqlite3

st.set_page_config(page_title="OMI v4.6", layout="wide")

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

st.title("🏭 OMI Market v4.6")

# SELLERリンク（これだけでOK）
st.markdown("👉 [SELLERを開く](http://localhost:8502)")

# SEARCH
search = st.text_input("🔍 商品検索")

rows = c.execute("SELECT title, kva, price, year FROM items").fetchall()

if search:
    items = [r for r in rows if search.lower() in str(r[0]).lower()]
else:
    items = rows

st.write("## 商品一覧")

for i in items:
    st.write(f"{i[0]} / {i[1]}KVA / ¥{i[2]} / {i[3]}年")
