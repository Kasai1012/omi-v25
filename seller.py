import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="SELLER", layout="wide")

# 【重要】先ほど作った secrets.toml からSupabaseの鍵を自動で読み込みます
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

st.title("🛠 SELLER (Supabase連動版)")

user = st.text_input("ユーザー名")
pw = st.text_input("パスワード", type="password")

if user and pw:
    st.success("ログインOK")

    title = st.text_input("商品名")
    maker = st.text_input("メーカー")
    kva = st.selectbox("KVA", [50, 100, 200, 300, 500, 750, 1000])
    price = st.number_input("価格", min_value=0)
    year = st.selectbox("年式", list(range(1990, 2030)))
    note = st.text_area("備考")

    if st.button("登録"):
        # Supabaseの「items」テーブルにデータを直接挿入します
        data, count = supabase.table("items").insert({
            "title": title,
            "maker": maker,
            "kva": kva,
            "price": price,
            "year": year,
            "note": note
        }).execute()
        st.success("🎉 Supabaseへ登録完了！")

    st.write("## 出品一覧")

    # Supabaseからリアルタイムでデータを取得して表示します
    response = supabase.table("items").select("title", "kva", "price", "year").execute()
    rows = response.data

    for r in rows:
        st.write(f"{r['title']} / {r['kva']}KVA / ¥{r['price']} / {r['year']}年")
