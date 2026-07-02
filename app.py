import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

# ------------------------
# 型番抽出
# ------------------------

def extract_model(text):
    match = re.search(r'[A-Z]{2,5}-?\d{2,4}[A-Z0-9-]*', text.upper())
    return match.group(0) if match else "UNKNOWN"

# ------------------------
# kVA抽出
# ------------------------

def extract_kva(text):
    match = re.search(r'(\d{2,3})\s?KVA', text.upper())
    return int(match.group(1)) if match else 50

# ------------------------
# 価格抽出（複数想定）
# ------------------------

def extract_price(text):
    prices = re.findall(r'¥\s?([\d,]+)', text)
    prices = [int(p.replace(",", "")) for p in prices]
    return prices

# ------------------------
# ブランドスコア
# ------------------------

def brand_score(text):
    t = text.upper()
    if "DENYO" in t:
        return 10
    if "AIRMAN" in t:
        return 9
    if "YAMAHA" in t:
        return 8
    return 7

# ------------------------
# 市場レンジ生成
# ------------------------

def market_range(prices):
    if not prices:
        return (0, 0, 0)

    prices = sorted(prices)
    low = prices[0]
    high = prices[-1]
    median = prices[len(prices)//2]

    return low, median, high

# ------------------------
# スコアリング
# ------------------------

def omi_score(kva, brand, price):
    score = 0

    # kVA帯評価
    if 50 <= kva <= 100:
        score += 40
    elif 100 < kva <= 150:
        score += 35
    else:
        score += 25

    score += brand * 2

    if price:
        if price < 1_000_000:
            score += 15
        elif price < 2_000_000:
            score += 10
        else:
            score -= 5

    return min(score, 100)

# ------------------------
# 判断ロジック
# ------------------------

def decision(score):
    if score >= 80:
        return "🟢 BUY"
    elif score >= 60:
        return "🟡 HOLD"
    return "🔴 SKIP"

# ------------------------
# fetch
# ------------------------

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, headers=headers, timeout=10).text

# ------------------------
# parse
# ------------------------

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    model = extract_model(text)
    kva = extract_kva(text)
    prices = extract_price(text)
    brand = brand_score(text)

    return model, kva, prices, brand, text[:800]

# ------------------------
# UI
# ------------------------

st.title("OMI Market Scanner v2.6")

url = st.text_input("URL")

if st.button("ANALYZE") and url:

    try:
        html = fetch(url)
        model, kva, prices, brand, raw = parse(html)

        score = omi_score(kva, brand, prices[0] if prices else None)
        low, median, high = market_range(prices)

        st.subheader("MODEL")
        st.write(model)

        st.subheader("MARKET RANGE")
        st.write(f"Low: {low}")
        st.write(f"Median: {median}")
        st.write(f"High: {high}")

        st.metric("OMI SCORE", score)
        st.write(decision(score))

        st.subheader("RAW")
        st.text(raw)

    except Exception as e:
        st.error(e)
