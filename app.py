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
# DOMAIN ROUTER
# =========================

def parse_by_domain(url, html):
    if "usedmachinery.bz" in url:
        return parse_usedmachinery(html)

    elif "rs-sangyo" in url:
        return parse_rs_sangyo(html)

    elif "toku-world" in url:
        return parse_tokuworld(html)

    else:
        return parse_generic(html)


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


def parse_rs_sangyo(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    model = re.search(r'[A-Z]{2,5}-\d+[A-Z0-9-]*', text.upper())
    model = model.group(0) if model else "UNKNOWN"

    price = re.search(r'¥\s?([\d,]+)', text)
    price = int(price.group(1).replace(",", "")) if price else None

    kva = re.search(r'(\d{2,3})\s?KVA', text.upper())
    kva = int(kva.group(1)) if kva else 50

    return model, kva, price


def parse_tokuworld(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    price = re.search(r'¥\s?([\d,]+)', text)
    price = int(price.group(1).replace(",", "")) if price else None

    return "UNKNOWN", 50, price


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


# =========================
# SCORING ENGINE
# =========================

def omi_score(kva, price):
    score = 0

    # kVA帯
    if 50 <= kva <= 100:
        score += 40
    elif 100 < kva <= 150:
        score += 35
    else:
        score += 25

    # 価格帯
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
# MAIN ANALYSIS
# =========================

def analyze(url):
    html = fetch(url)
    model, kva, price = parse_by_domain(url, html)
    score = omi_score(kva, price)
    return model, kva, price, score, html[:800]


# =========================
# STREAMLIT UI
# =========================

st.title("OMI Market Scanner v2.7")

url = st.text_input("URLを入力してください")

if st.button("ANALYZE") and url:

    try:
        model, kva, price, score, raw = analyze(url)

        st.subheader("MODEL")
        st.write(model)

        st.subheader("RESULTS")
        st.write("kVA:", kva)
        st.write("Price:", price)

        st.metric("OMI SCORE", score)
        st.write(decision(score))

        st.subheader("RAW SAMPLE")
        st.text(raw)

    except Exception as e:
        st.error(e)
