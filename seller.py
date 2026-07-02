import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="OMI SELLER - Dashboard", layout="wide")

# 1. 堅牢なクラウドDB接続
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("Database connection failed. Please check your Secrets configuration.")
    st.stop()

st.title("🛠️ SELLER 管理画面")

# 2. 簡易的だが破綻しないログイン認証
# パスワードなどをコードに直書きせず、StreamlitのSecretsで一元管理します
col_login1, col_login2 = st.columns(2)
with col_login1:
    user = st.text_input("ユーザー名", placeholder="Enter username")
with col_login2:
    pw = st.text_input("パスワード", type="password", placeholder="Enter password")

# Secretsに設定した正しい認証情報と一致するかチェック
if user and pw:
    if user == st.secrets["SELLER_USER"] and pw == st.secrets["SELLER_PASSWORD"]:
        st.success("🔒 ログイン完了")
        st.divider()

        # 3. 商品登録フォーム
        st.subheader("➕ 新規商品登録")
        
        with st.form("item_registration_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("商品名（英語推奨・検索に直結）", placeholder="Example: Used Denyo DCA-25ESK")
                maker = st.text_input("メーカー", placeholder="Example: Denyo, Shindaiwa, Airman")
                kva = st.selectbox("KVA (定格出力)", [25, 35, 45, 50, 60, 100, 125, 150, 200, 300, 500, 750, 1000])
            with col2:
                price = st.number_input("価格（円）", min_value=0, step=10000)
                year = st.selectbox("年式", list(range(1990, 2027))[::-1]) # 直近の年を上に
                note = st.text_area("備考・スペック（稼働時間やコンディションなど）")

            submit_button = st.form_submit_button("商品を登録する")

        # 4. データ挿入処理
        if submit_button:
            if not title or not maker:
                st.error("❌ 商品名とメーカーは必須入力です。")
            else:
                try:
                    # Supabaseにデータを挿入
                    data = {
                        "title": title,
                        "maker": maker,
                        "kva": kva,
                        "price": price,
                        "year": year,
                        "note": note
                    }
                    supabase.table("items").insert(data).execute()
                    st.success(f"🛢️ 『{title}』をクラウドDBに安全に登録しました！")
                except Exception as e:
                    st.error(f"登録エラーが発生しました: {e}")

        st.divider()

        # 5. 出品一覧の表示
        st.subheader("📦 現在の出品一覧")
        
        try:
            response = supabase.table("items").select("title, kva, price, year").execute()
            rows = response.data
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            rows = []

        if not rows:
            st.info("登録されている商品はありません。")
        else:
            # 管理画面側も見やすいようにテーブルかコンテナで表示
            for r in rows:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.markdown(f"**{r.get('title')}** ({r.get('maker')})")
                    c2.markdown(f"**{r.get('kva')} KVA** / {r.get('year')}年")
                    c3.markdown(f"¥{int(r.get('price', 0)):,}")
                    
    else:
        st.error("❌ ユーザー名またはパスワードが正しくありません。")
