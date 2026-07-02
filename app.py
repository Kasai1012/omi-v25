import streamlit as st
import sqlite3

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="OMI Market v4.6", layout="wide")

# =========================
# DB CONNECT
# =========================
conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# =========================
# TITLE
# =========================
st.title("🏭 OMI Market v4.6")

# =========================
# SEARCH（完全版）
# =========================
search = st.text_input("🔍 商品検索（例：100KVA / ヤンマー）")

# =========================
# DATA FETCH（安全）
# =========================
try:
    rows = c.execute("SELECT title, kva, price FROM items").fetchall()
except:
    rows = []

# =========================
# FILTER LOGIC
# =========================
items = []

if search:
    for r in rows:
        if search.lower() in str(r[0]).lower():
            items.append(r)
else:
    items = rows

# =========================
# UI HEADER INFO
# =========================
col1, col2 = st.columns([3, 1])

with col1:
    st.write("## 📦 商品一覧")

with col2:
    st.button("🔐 ログイン")

# =========================
# LIST VIEW
# =========================
if len(items) == 0:
    st.warning("該当する商品がありません")
else:
    for i in items:
        st.markdown(f"""
        ---
        **商品名**：{i[0]}  
        **容量**：{i[1]} KVA  
        **価格**：¥{i[2]}
        """)
