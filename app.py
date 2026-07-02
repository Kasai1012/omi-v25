import streamlit as st

# =========================
# MARKET DATA (仮想だが構造は実運用前提)
# =========================

MARKETS = {
    "Generator": [
        {"name": "DCA-150LSKE", "kva": 150, "price": 3795000},
        {"name": "DCA-60ESH", "kva": 60, "price": 1595000},
        {"name": "DCA-45LSK", "kva": 45, "price": 1210000},
        {"name": "DCA-25LSK", "kva": 25, "price": 900000},
        {"name": "EF5500iS", "kva": 5, "price": 198000},
    ],

    "Survey Equipment": [
        {"name": "TOPCON GT-100", "kva": 10, "price": 850000},
        {"name": "Leica TS06", "kva": 10, "price": 1200000},
        {"name": "SOKKIA CX-105", "kva": 10, "price": 650000},
    ],

    "Construction Machinery": [
        {"name": "Mini Excavator ZX30", "kva": 30, "price": 2500000},
        {"name": "CAT 320D", "kva": 120, "price": 7800000},
        {"name": "Kubota U30", "kva": 30, "price": 2100000},
    ]
}

# =========================
# SCORE ENGINE（v3ロジック流用）
# =========================

def score(item):

    s = 0

    # サイズ価値
    if 50 <= item["kva"] <= 100:
        s += 40
    elif 100 < item["kva"] <= 150:
        s += 35
    else:
        s += 25

    # 価格効率
    if item["price"] < 1000000:
        s += 20
    elif item["price"] < 3000000:
        s += 10
    else:
        s -= 5

    return s

# =========================
# MARKET BUILD
# =========================

def build_market(items):
    for i in items:
        i["score"] = score(i)
    return sorted(items, key=lambda x: x["score"], reverse=True)

# =========================
# UI
# =========================

st.title("OMI v3.2 - Market Shelf Engine")

market = st.selectbox("Marketを選択", list(MARKETS.keys()))

items = build_market(MARKETS[market])

st.subheader(f"🏆 TOP 30 - {market}")

top30 = items[:30]

for i, item in enumerate(top30, 1):

    st.markdown(f"""
### #{i} {item['name']}

- kVA: {item['kva']}
- Price: {item['price']}
- Score: {item['score']}
""")

# =========================
# MARKET SUMMARY
# =========================

st.subheader("📊 Market Summary")

st.write("Total items:", len(items))
st.write("Best score:", items[0]["score"])
