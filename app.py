import streamlit as st
from PIL import Image
import io

# =========================
# SESSION DB
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

    # kVA評価
    if 50 <= kva <= 100:
        s += 40
    elif 100 < kva <= 150:
        s += 35
    else:
        s += 20

    # 価格効率
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

st.title("OMI v4.2 - Market UI (Full Product View)")

tab1, tab2, tab3 = st.tabs(["🧾 出品", "🔍 検索", "🏆 ランキング"])

# =========================
# ① 出品（強化版）
# =========================

with tab1:

    st.subheader("商品出品")

    name = st.text_input("モデル名")
    maker = st.text_input("メーカー")
    kva = st.number_input("kVA", value=50)
    year = st.number_input("年式", value=2015)
    hours = st.number_input("稼働時間", value=3000)
    price = st.number_input("価格", value=1000000)

    images = st.file_uploader(
        "写真アップロード（複数可）",
        type=["jpg", "png"],
        accept_multiple_files=True
    )

    if st.button("出品する"):

        img_list = []

        for img in images:
            img_list.append(img.read())

        item = {
            "name": name,
            "maker": maker,
            "kva": kva,
            "year": year,
            "hours": hours,
            "price": price,
            "images": img_list,
        }

        item["score"] = score(item)

        st.session_state.items.append(item)

        st.success("出品完了")

# =========================
# ② 検索
# =========================

with tab2:

    st.subheader("検索")

    min_kva = st.number_input("Min KVA", value=0)
    max_kva = st.number_input("Max KVA", value=200)

    results = []

    for i in st.session_state.items:

        if min_kva <= i["kva"] <= max_kva:
            i["score"] = score(i)
            results.append(i)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    for i, r in enumerate(results, 1):

        st.markdown(f"""
---

## #{i} {r['name']}（{r['maker']}）

**🔥 Score:** {r['score']}

- kVA: {r['kva']}
- 年式: {r['year']}
- 稼働時間: {r['hours']}
- 価格: ¥{r['price']:,}
""")

        if r["images"]:
            cols = st.columns(len(r["images"]))

            for idx, img_bytes in enumerate(r["images"]):
                cols[idx].image(img_bytes)

# =========================
# ③ ランキング
# =========================

with tab3:

    st.subheader("TOPランキング")

    ranked = sorted(
        st.session_state.items,
        key=lambda x: x["score"],
        reverse=True
    )

    for i, r in enumerate(ranked[:30], 1):

        st.markdown(f"""
---

## #{i} {r['name']}（{r['maker']}）

**🔥 Score:** {r['score']}

- kVA: {r['kva']}
- 年式: {r['year']}
- 稼働時間: {r['hours']}
- 価格: ¥{r['price']:,}
""")

        if r["images"]:
            cols = st.columns(len(r["images"]))

            for idx, img_bytes in enumerate(r["images"]):
                cols[idx].image(img_bytes)
