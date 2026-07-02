import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

def estimate_kva(text):
    match = re.search(r'(\d{2,3})\s?KVA', text.upper())
    if match:
        return int(match.group(1))
    return 50

def extract_price(text):
    match = re.search(r'¥\s?([\d,]+)', text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None

def brand_score(text):
    if "DENYO" in text.upper():
        return 10
    elif "AIRMAN" in text.upper():
        return 9
    return 7

def kva_score(kva):
    if 50 <= kva <= 100:
        return 10
    elif 100 < kva <= 150:
        return 9
    return 6

def omi_score(kva, brand, price):
    base = kva_score(kva) + brand
    if price:
        if price < 1_000_000:
            base += 2
        elif price < 2_000_000:
            base += 1
        else:
            base -= 1
    return base * 10

def decision(score):
    if score >= 80:
        return "BUY"
    elif score >= 60:
        return "HOLD"
    return "SKIP"

def fetch_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, headers=headers).text

def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ")

    kva = estimate_kva(text)
    price = extract_price(text)
    brand = brand_score(text)

    return kva, price, brand, text[:1000]

st.title("OMI v2.5")

url = st.text_input("URLを貼ってください")

if st.button("ANALYZE"):
    html = fetch_page(url)
    kva, price, brand, raw = parse(html)

    score = omi_score(kva, brand, price)

    st.write("kVA:", kva)
    st.write("Price:", price)
    st.write("Brand:", brand)

    st.metric("OMI SCORE", score)
    st.write(decision(score))

    st.text(raw)
