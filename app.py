import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

# =========================
# FETCH
# =========================

def fetch(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        return r.text
    except:
        return ""

# =========================
# EXTRACTION
# =========================

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
            return m.group(0), 0.9

    return "UNKNOWN", 0.3


def extract_kva(html):
    text = html.upper()

    patterns = [
        (r'(\d{2,3})\s?KVA', 0.9),
        (r'(\d{2,3})KVA', 0.8),
        (r'出力[^0-9]{0,10}(\d{2,3})', 0.6)
    ]

    for p, conf in patterns:
        m = re.search(p, text)
        if m:
            return int(m.group(1)), conf

    return 50, 0.2


def extract_price(html):
    text = html

    # 本体価格優先
    m = re.search(r'本体価格[^¥]{0,50}¥\s?([\d,]+)', text)
    if m:
        return int(m.group(1).replace(",", "")), 0.95

    # 税込
    m = re.search(r'税込価格[^¥]{0,50}¥\s?([\d,]+)', text)
    if m:
        return int(m.group(1).replace(",", "")), 0.8

    # fallback
    m = re.findall(r'¥\s?([\d,]+)', text)
    if m:
        return int(m[0].replace(",", "")), 0.4

    return None, 0.0

# =========================
# SCORE ENGINE
# =========================

def omi_score(kva, price):
    score = 0

    if 50 <= kva <= 100:
        score += 40
    elif 100 < kva <= 150:
        score += 35
    else:
        score += 25

    if price:
        if price < 1_000_000:
            score += 15
        elif price < 2_000_000:
            score += 10
        else:
            score -= 5

    return min(score, 100)

# =========================
# DATA QUALITY SCORE
# =========================

def data_score(model_c, kva_c, price_c):
    return round((model_c + kva_c + price_c) / 3 * 100, 1)

# =========================
# ANALYZE
# =========================

def analyze(url):
    html = fetch(url)

    model, model_c = extract_model(html)
    kva, kva_c = extract_kva(html)
    price, price_c = extract_price(html)

    score = omi_score(kva, price)
    dscore = data_score(model_c, kva_c, price_c)

    return {
        "url": url,
        "model": model,
        "kva": kva,
        "price": price,
        "omi_score": score,
        "data_score": dscore,
        "confidence": round((model_c + kva_c + price_c) / 3, 2)
    }

# =========================
# UI
# =========================

st.title("OMI Market Scanner v3.1 - Data Quality Engine")

urls_input = st.text_area("URLを改行で入力")

if st.button("ANALYZE") and urls_input:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    for url in urls:
        results.append(analyze(url))

    # OMIスコア順
    results = sorted(results, key=lambda x: x["omi_score"], reverse=True)

    st.subheader("📊 RESULTS")

    for i, r in enumerate(results, 1):

        st.markdown(f"""
### #{i} {r['model']}

- URL: {r['url']}
- kVA: {r['kva']}
- Price: {r['price']}
- OMI Score: {r['omi_score']}
- Data Score: {r['data_score']}
- Confidence: {r['confidence']}
""")

    best = results[0]

    st.subheader("🔥 BEST PICK")
    st.write(best["model"])
    st.metric("OMI SCORE", best["omi_score"])
    st.metric("DATA QUALITY", best["data_score"])
