import streamlit as st
import requests
import re

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
# PARSE ENGINE（軽量版）
# =========================

def parse(html):

    text = html.upper()

    # model
    model = re.search(r'DCA-\d+[A-Z0-9-]*|SDG\d+[A-Z0-9-]*|EF\d+[A-Z0-9-]*', text)
    model = model.group(0) if model else "UNKNOWN"

    # kva
    kva = re.search(r'(\d{2,3})\s?KVA', text)
    kva = int(kva.group(1)) if kva else None

    # price
    price = re.search(r'¥\s?([\d,]+)', html)
    price = int(price.group(1).replace(",", "")) if price else None

    return model, kva, price

# =========================
# SCORE
# =========================

def score(kva, price):

    s = 0

    if kva:
        if 50 <= kva <= 100:
            s += 40
        elif 100 < kva <= 150:
            s += 35
        else:
            s += 20

    if price:
        if price < 1000000:
            s += 20
        elif price < 2000000:
            s += 10
        else:
            s -= 5

    return s

# =========================
# FILTER
# =========================

def process(urls, min_kva, max_kva):

    results = []

    for url in urls:
        html = fetch(url)
        model, kva, price = parse(html)

        if kva is None:
            continue

        if min_kva <= kva <= max_kva:

            results.append({
                "url": url,
                "model": model,
                "kva": kva,
                "price": price,
                "score": score(kva, price)
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)

# =========================
# UI
# =========================

st.title("OMI v3.4 - Live Generator Market Scanner")

st.subheader("🔗 URL INPUT")

urls_input = st.text_area("発電機URLを改行で入力")

col1, col2 = st.columns(2)

with col1:
    min_kva = st.number_input("Min KVA", value=20)

with col2:
    max_kva = st.number_input("Max KVA", value=150)

if st.button("ANALYZE"):

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]

    results = process(urls, min_kva, max_kva)

    st.subheader("🏆 TOP RESULTS")

    if not results:
        st.write("No valid items found")

    for i, r in enumerate(results, 1):

        st.markdown(f"""
### #{i} {r['model']}

- URL: {r['url']}
- KVA: {r['kva']}
- Price: {r['price']}
- Score: {r['score']}
""")
