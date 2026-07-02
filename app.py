import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

# =========================
# FETCH
# =========================

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, headers=headers, timeout=10).text


# =========================
# PARSERS
# =========================

def parse_usedmachinery(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    model = re.search(r'DCA-\d+[A-Z0-9-]*|SDG\d+[A-Z0-9-]*', text.upper())
    model = model.group(0) if model else "UNKNOWN"

    price = re.search(r'本体価格[^\d]*(¥\s?[\d,]+)', text)
    if price:
        price = int(price.group(1).replace("¥", "").replace(",", "").strip())
    else:
        price = None

    kva = re.search(r'(\d{2,3})\s?KVA', text.upper())
    kva = int(kva.group(1)) if kva else 50

    return model, kva, price


def parse_generic(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    model = re.search(r'[A-Z]{2,5}-?\d+[A-Z0-9-]*', text.upper())
    model = model.group(0) if model else "UNKNOWN"

    price = re.search(r'¥\s?([\d,]+)', text)
    price = int(price.group(1).replace(",", "")) if price else None

    kva = re.search(r'(\d{2,3})\s?KVA', text.upper())
    kva = int(kva.group(1)) if kva else 50

    return model, kva, price


def parse_by_domain(url, html):
    if "usedmachinery.bz" in url:
        return parse_usedmachinery(html)
    else:
        return parse_generic(html)


# =========================
# OMI SCORE
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
# ANALYZE SINGLE
# =========================

def analyze(url):
    html = fetch(url)
    model, kva, price = parse_by_domain(url, html)
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
# STREAMLIT UI
# =========================

st.title("OMI Market Scanner v2.8")
st.write("複数URLを貼ってランキング化します（改行区切り）")

urls_input = st.text_area("URLを複数入力（1行1URL）")

if st.button("ANALYZE") and urls_input:

    urls = [u.strip() for u in urls_input.split("\n") if u.strip()]
    results = []

    for url in urls:
        try:
            result = analyze(url)
            results.append(result)
        except Exception as e:
            results.append({
                "url": url,
                "model": "ERROR",
                "kva": None,
                "price": None,
                "score": 0,
                "decision": f"ERROR: {e}"
            })

    # =========================
    # SORT (核心)
    # =========================

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # =========================
    # OUTPUT
    # =========================

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
    # BEST PICK
    # =========================

    best = results[0]

    st.subheader("🔥 BEST PICK")

    st.write(best["model"])
    st.metric("OMI SCORE", best["score"])
    st.write(best["decision"])
