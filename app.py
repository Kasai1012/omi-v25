import streamlit as st
import sqlite3
import requests
from bs4 import BeautifulSoup

# =========================
# DB
# =========================

conn = sqlite3.connect("omi.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    maker TEXT,
    kva INTEGER,
    hours INTEGER,
    price INTEGER,
    year INTEGER,
    note TEXT,
    image BLOB
)
""")

conn.commit()

# =========================
# SIMPLE SCRAPER
# =========================

def scrape_url(url):

    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        title = soup.title.text if soup.title else "Unknown Item"

        # 超簡易抽出（サイト依存）
        text = soup.get_text()

        price = 0
        kva = 0

        # ざっくり数値拾い
        import re

        price_match = re.search(r"([0-9,]+)円", text)
        if price_match:
            price = int(price_match.group(1).replace(",", ""))

        kva_match = re.search(r"(\d+)\s?kVA", text)
        if kva_match:
            kva = int(kva_match.group(1))

        return {
            "name": title[:50],
            "maker": "AUTO",
            "kva": kva,
            "price": price,
            "hours": 0,
            "year": 2020,
            "note": url,
            "image": None
        }

    except Exception as e:
        return {"error": str(e)}

# =========================
# INSERT
# =========================

def insert_item(item):

    c.execute("""
        INSERT INTO items
        (name, maker, kva, hours, price, year, note, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item["name"],
        item["maker"],
        item["kva"],
        item["hours"],
        item["price"],
        item["year"],
        item["note"],
        item["image"]
    ))

    conn.commit()

# =========================
# FETCH
# =========================

def fetch_items():
    c.execute("SELECT * FROM items")
    return c.fetchall()

# =========================
# UI
# =========================

st.title("OMI v4.7 - Semi Auto Market Import")

tab1, tab2 = st.tabs(["📥 URL取込", "📦 商品一覧"])

# =========================
# ① URL取込
# =========================

with tab1:

    st.subheader("外部サイトから取り込み")

    url = st.text_input("商品URLを入力")

    if st.button("解析する"):

        data = scrape_url(url)

        if "error" in data:
            st.error(data["error"])
        else:
            st.write("取得データ（仮）")
            st.json(data)

            if st.button("この内容で登録"):

                insert_item(data)
                st.success("登録完了")

# =========================
# ② 商品一覧
# =========================

with tab2:

    st.subheader("商品一覧")

    items = fetch_items()

    for i in items:

        st.write(i)
