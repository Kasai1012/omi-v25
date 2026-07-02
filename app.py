import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="OMI Market - Used Japanese Generator", layout="wide")

# 1. 堅牢なクラウドDB接続（データが100%飛ばない仕組み）
# StreamlitのSecrets（環境変数）から安全にキーを読み込みます
@st.cache_resource
def init_supabase():
    # 本番環境ではStreamlit CloudのSecretsに、ローカルでは .streamlit/secrets.toml に保存します
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_supabase()
except Exception as e:
    st.error("Database connection failed. Please check your Secrets configuration.")
    st.stop()

st.title("🏭 OMI Market - Used Japanese Generator")

# 2. 環境に依存しないリンク設計
# 自分のドメインや本番URLに自動追従するようにMarkdownではなくst.link_buttonなどを推奨（後述）
st.info("💡 Looking for the Seller Dashboard? Contact the administrator.")

# 3. 検索機能
search = st.text_input("🔍 Search Products (e.g., Denyo, 25kVA)", placeholder="Type brand or capacity...")

# 4. データ取得（クラウドから安全に取得）
try:
    # Supabaseの'items'テーブルから全件取得
    response = supabase.table("items").select("title, kva, price, year").execute()
    rows = response.data
except Exception as e:
    st.error(f"Error fetching data: {e}")
    rows = []

# 5. フロントエンドでのフィルタリング（大文字小文字を区別しない）
if search:
    items = [r for r in rows if search.lower() in str(r.get("title", "")).lower()]
else:
    items = rows

st.write("## 📦 Live Inventory")

# 6. 将来のSEOとユーザー体験を意識したレイアウト表示
if not items:
    st.warning("No products found matching your search.")
else:
    for i in items:
        # プレースホルダーから安全にデータを取得
        title = i.get("title", "N/A")
        kva = i.get("kva", "-")
        price = i.get("price", "0")
        year = i.get("year", "-")
        
        # 将来の海外バイヤー向けに英語表記をベースにしつつ、見やすいカード型（コンテナ）に変更
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"### **{title}**")
            with col2:
                st.markdown(f"**Capacity:** {kva} KVA  \n**Year:** {year}")
            with col3:
                # 通貨表記も海外向けに追々USDなどに変えられるように準備
                st.markdown(f"### ¥{int(price):,}")
