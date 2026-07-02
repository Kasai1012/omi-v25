import streamlit as st

# =========================
# SESSION DB（仮想DB）
# =========================

if "items" not in st.session_state:
    st.session_state.items = []

# =========================
# SCORE ENGINE
# =========================

def score(item):

    s = 0

    kva = item["kva"]
    price = item["price"]

    if 50 <= kva <= 100:
        s += 40
    elif 100 < kva <= 150:
        s += 35
    else:
        s += 20

    if price < 1000000:
        s += 20
    elif price < 2000000:
        s += 10
    else:
        s -= 5

    return s

# =========================
# UI
# =========================

st.title("OMI v4.0 - Marketplace MVP")

tab1, tab2, tab3 = st.tabs(["🧾 出品", "🔍 検索", "🏆 ランキング"])

# =========================
# ① SELLER INPUT
# =========================

with tab1:

    st.subheader("出品登録")

    name = st.text_input("モデル名")
    kva = st.number_input("kVA", value=50)
    price = st.number_input("価格", value=1000000)

    if st.button("出品する"):

        st.session_state.items.append({
            "name": name,
            "kva": kva,
            "price": price
        })

        st.success("登録完了")

    st.write("現在の出品数:", len(st.session_state.items))

# =========================
# ② SEARCH
# =========================

with tab2:

    st.subheader("検索")

    min_kva = st.number_input("Min KVA", value=0)
    max_kva = st.number_input("Max KVA", value=200)

    min_price = st.number_input("Min Price", value=0)
    max_price = st.number_input("Max Price", value=10000000)

    results = []

    for i in st.session_state.items:

        if min_kva <= i["kva"] <= max_kva and min_price <= i["price"] <= max_price:
            i["score"] = score(i)
            results.append(i)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    st.subheader("検索結果")

    for i, r in enumerate(results, 1):
        st.markdown(f"""
### #{i} {r['name']}
- kVA: {r['kva']}
- Price: {r['price']}
- Score: {r['score']}
""")

# =========================
# ③ RANKING
# =========================

with tab3:

    st.subheader("TOPランキング")

    ranked = []

    for i in st.session_state.items:
        i["score"] = score(i)
        ranked.append(i)

    ranked = sorted(ranked, key=lambda x: x["score"], reverse=True)

    for i, r in enumerate(ranked[:30], 1):
        st.markdown(f"""
### #{i} {r['name']}
- kVA: {r['kva']}
- Price: {r['price']}
- Score: {r['score']}
""")
