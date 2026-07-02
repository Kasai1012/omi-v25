import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import json
import os

# =========================
# FETCH（簡易）
# =========================

def fetch(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        return r.text
    except:
        return ""

# =========================
# PARSER
# =========================

def parse(html):
    text = html.upper()

    model = re.search(r'DCA-\d+[A-Z0-9-]*|SDG\d+[A-Z0-9-]*|EF\d+[A-Z0-9-]*', text)
    model = model.group(0) if model else "UNKNOWN"

    kva = re.search(r'(\d{2,3})\s?KVA', text)
    kva = int(kva.group(1)) if kva else 50

    price = re.search(r'¥\s?([\d,]+)', text)
    price = int(price.group(1).replace(",", "")) if price else None

    return model, kva, price

# =========================
# MARKET MODEL（ここがv3.0核）
# =========================

def market_mean(price_list):
    prices = [p for p in price_list if p]
    if not prices:
        return 0
    return sum(prices) / len(prices)

def discount_rate(price, mean):
    if not price or not mean:
        return 0
    return (mean - price) / mean * 100

# =========================
# SCORE ENGINE v3.0
# =========================

def omi_score(kva, price, mean):
    score = 0

    # 基礎kVA価値
    if 50 <= kva <= 100:
        score += 40
    elif 100 < kva <= 150:
        score += 35
    else:
        score += 25

    # 割安度（ここが新核）
    dr = discount_rate(price, mean)

    if dr > 20:
        score += 40
    elif dr > 10:
        score += 25
    elif dr > 0:
        score += 10
    else:
        score -= 10

    return min(score, 100), dr

# =========================
# ANALYZE
# =========================

def analyze(urls):

    results = []

    # まず全部パース
    for url in urls:
        html = fetch(url)
        model, kva, price = parse(html)
        results.append({
            "url": url,
            "model": model,
            "kva": kva,
            "price": price
        })

    # 市場平均
    prices = [r["price"] for r in results]
    mean = market_mean(prices)

    # スコア付与
    for r in results:
        score, dr = omi_score(r["kva"], r["price"], mean)
        r["score"] = score
        r["discount"] = dr

        if score >= 80:
            r["decision"] = "🟢 BUY"
        elif score >= 60:
            r["decision"] = "🟡 HOLD"
        else:
            r["decision"] = "🔴 SKIP"

    return sorted(results, key=lambda x: x["score"], reverse=True), mean

# =========================
# UI
# =========================

st.title("OMI Market Scanner v3.0 - Market Distortion Engine")

urls_input = st.text_area("URLを改行で入力")

if st.button("ANALYZE") and urls_input:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    results, mean = analyze(urls)

    st.subheader("📊 MARKET STATE")
    st.write("Market Mean Price:", round(mean, 2))

    st.subheader("🏆 RANKING")

    for i, r in enumerate(results, 1):

        st.markdown(f"""
### #{i} {r['model']}

- URL: {r['url']}
- kVA: {r['kva']}
- Price: {r['price']}
- Discount: {round(r['discount'], 2)}%
- Score: {r['score']}
- Decision: {r['decision']}
""")

    st.subheader("🔥 BEST PICK")
    best = results[0]
    st.write(best["model"])
    st.metric("OMI SCORE", best["score"])
    st.write(best["decision"])
