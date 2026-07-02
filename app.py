import streamlit as st
import sqlite3

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

st.title("OMI Market v4.7")

# =========================
# TOP（固定・ここが核）
# =========================
st.subheader("発電機・建機マーケット")

items = c.execute("""
SELECT item_id, title, maker, kva, price FROM items
""").fetchall()

if len(items) == 0:
    st.info("まだ商品がありません")
else:
    for i in items:
        st.write(f"🟢 {i[1]} / {i[2]} / {i[3]}KVA / ¥{i[4]}")
        st.markdown(f"[詳細を見る](#)")

# =========================
# 区切り線
# =========================
st.markdown("---")

# =========================
# 出品者入口（ただのリンク）
# =========================
st.subheader("出品者の方へ")

if st.button("ログイン / 出品管理"):
    st.info("ここにログイン画面を後付けする")
