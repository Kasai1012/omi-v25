import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import json
import os

# =========================
# DB FILE
# =========================

DB_FILE = "omi_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


# =========================
# FETCH
# =========================

def fetch(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    return requests.get(url, headers=headers, timeout=10).text


# =========================
# PARSER
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
# SCORE
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

st.title("OMI Market Scanner v2.9 - Memory Edition")

db = load_db()

urls_input = st.text_area("URL（複数OK・改行区切り）")

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

    # SORT
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # SAVE TO DB
    db.extend(results)
    save_db(db)

    st.success("Saved to memory DB")

    # DISPLAY
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
# HISTORY VIEW
# =========================

st.subheader("📦 HISTORY")

if db:
    db_sorted = sorted(db, key=lambda x: x["score"], reverse=True)

    for i, r in enumerate(db_sorted[:10], 1):
        st.write(f"{i}. {r['model']} | {r['score']} | {r['decision']}")

else:
    st.write("No history yet")
