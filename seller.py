import streamlit as st
import sqlite3
from datetime import datetime

# =========================
# DB
# =========================
conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# =========================
# PAGE
# =========================
st.set_page_config(page_title="OMI Seller", layout="wide")

st.title("🛠 出品者管理ページ（Seller）")

# =========================
# LOGIN（簡易版）
# =========================
st.subheader("🔐 ログイン（簡易）")

user = st.text_input("ユーザー名")
password = st.text_input("パスワード", type="password")

login_ok = False

if st.button("ログイン"):
    if user and password:
        login_ok = True
        st.success("ログイン成功（仮）")
    else:
        st.error("ユーザー名とパスワードを入力してください")

# =========================
# ITEM ENTRY
# =========================
if login_ok or (user and password):

    st.subheader("📦 出品登録")

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")

    kva = st.selectbox(
        "KVA（容量）",
        [50, 100, 150, 200, 300, 500, 750, 1000]
    )

    price = st.number_input("価格（円）", min_value=0, step=1000)

    year = st.selectbox(
        "年式",
        list(range(1990, datetime.now().year + 1))
    )

    note = st.text_area("備考")

    if st.button("登録する"):

        if title and maker:

            c.execute("""
                INSERT INTO items (title, maker, kva, price, year, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, maker, kva, price, year, note))

            conn.commit()

            st.success("登録完了")

        else:
            st.error("商品名とメーカーは必須です")

    # =========================
    # MY ITEMS
    # =========================
    st.subheader("📋 自分の出品一覧（全件表示）")

    try:
        items = c.execute("SELECT title, kva, price, year FROM items").fetchall()
    except:
        items = []

    if len(items) == 0:
        st.info("まだ出品がありません")
    else:
        for i in items:
            st.write(f"{i[0]} / {i[1]}KVA / ¥{i[2]} / {i[3]}年")
