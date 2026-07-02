import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import json
import os

# =========================
# DB
# =========================

DB_FILE = "omi_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

# =========================
# FETCH
# =========================

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, headers=headers, timeout=10).text

# =========================
# IMPROVED EXTRACTION
# =========================

def extract_kva(html):
    """
    ラベル近傍ベース抽出
    """
    patterns = [
        r'(\d{2,3})\s?KVA',
        r'(\d{2,3})KVA',
        r'出力[^0-9]{0,10}(\d{2,3})',
        r'定格[^0-9]{0,10}(\d{2,3})'
    ]

    text = html.upper()

    for p in patterns:
        m = re.search(p, text)
        if m:
            return int(m.group(1))

    return 50  # fallback


def extract_price(html):
    """
    本体価格優先 + 構造優先
    """

    text = html

    # 本体価格優先
    m = re.search(r'本体価格[^¥]{0,50}¥\s?([\d,]+)', text)
    if m:
        return int(m.group(1).replace(",", ""))

    # 税込
    m = re.search(r'税込価格[^¥]{0,50}¥\s?([\d,]+)', text)
    if m:
        return int(m.group(1).replace(",", ""))

    # fallback
    m = re.findall(r'¥\s?([\d,]+)', text)
    if m:
        return int(m[0].replace(",", ""))

    return None


def extract_model(html):
    patterns = [
        r'DCA-\d+[A-Z0-9-]*',
        r'SDG\d+[A-Z0-9-]*',
        r'EF\d+[A-Z0-9-]*'
    ]

    text = html.upper()

    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0)

    return "UNKNOWN"

# =========================
# PARSE
# =========================

def parse(html):
    model = extract_model(html)
    kva = extract_kva(html)
    price = extract_price(html)

    return model, kva, price

# =========================
# SCORE ENGINE
# =========================

def omi_score(kva, price):
    score = 0

    # kVA評価
    if 50 <= kva <= 100:
        score += 40
    elif 100 < kva <= 150:
        score += 35
    else:
        score += 25

    # 価格評価
    if price:
        if price < 1_000_000:
            score += 15
        elif price < 2_000_000:
            score += 10
        else:
            score -= 5

    return min(score, 100)


def decision(score):
    if score >= 80:
        return "🟢 BUY"
    elif score >= 60:
        return "🟡 HOLD"
    return "🔴 SKIP"

# =========================
# ANALYZE
# =========================

def analyze(url):
    html = fetch(url)
    model, kva, price = parse(html)

    score = omi_score(kva, price)

    return {
        "url": url,
        "model": model,
        "kva": kva,
        "price": price,
        "score": score,
        "decision": decision(score)
    }

# =========================
# STREAMLIT
# =========================

st.title("OMI Market Scanner v2.9 FIXED")

db = load_db()

urls_input = st.text_area("URLを複数入力（改行区切り）")

if st.button("ANALYZE") and urls_input:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    for url in urls:
        try:
            results.append(analyze(url))
        except Exception as e:
            results.append({
                "url": url,
                "model": "ERROR",
                "kva": None,
                "price": None,
                "score": 0,
                "decision": str(e)
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    db.extend(results)
    save_db(db)

    st.subheader("🏆 RANKING")

    for i, r in enumerate(results, 1):
        st.markdown(f"""
### #{i} {r['model']}

- URL: {r['url']}
- kVA: {r['kva']}
- Price: {r['price']}
- Score: {r['score']}
- Decision: {r['decision']}
""")

# =========================
# HISTORY
# =========================

st.subheader("📦 HISTORY")

if db:
    for i, r in enumerate(sorted(db, key=lambda x: x["score"], reverse=True)[:10], 1):
        st.write(f"{i}. {r['model']} | {r['score']} | {r['decision']}")
else:
    st.write("No history")else:
    st.write("No history yet")
