import streamlit as st
import sqlite3

# =========================
# DB
# =========================
conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="OMI Market", layout="wide")

# =========================
# BOOTSTRAP CSS
# =========================
st.markdown("""
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

# =========================
# HEADER（Bootstrap）
# =========================
st.markdown("""
<nav class="navbar navbar-expand-lg navbar-dark bg-dark px-3">
  <a class="navbar-brand" href="#">OMI Market</a>

  <div class="ms-auto d-flex">
    <input class="form-control me-2" placeholder="検索（例：100KVA）">
    <button class="btn btn-outline-light">検索</button>
    <button class="btn btn-warning ms-2">ログイン</button>
  </div>
</nav>
""", unsafe_allow_html=True)

# =========================
# DATA
# =========================
items = c.execute("""
SELECT item_id, title, maker, kva, price, year FROM items
""").fetchall()

# =========================
# MAIN TITLE
# =========================
st.markdown("## 🔍 発電機・建機マーケット")

# =========================
# GRID（Bootstrap風カード）
# =========================
cols = st.columns(3)

for idx, i in enumerate(items):
    with cols[idx % 3]:
        st.markdown(f"""
        <div class="card shadow-sm mb-3">
            <div class="card-body">
                <h5 class="card-title">{i[1]}</h5>
                <p class="card-text">
                    メーカー：{i[2]}<br>
                    容量：{i[3]} KVA<br>
                    年式：{i[5]}<br>
                    <b>価格：¥{i[4]}</b>
                </p>
                <a class="btn btn-primary btn-sm">詳細を見る</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
