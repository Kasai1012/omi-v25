import streamlit as st
from supabase import create_client, Client

# ==========================================
# 1. ページ全体の初期設定（見た目を少しリッチに）
# ==========================================
st.set_page_config(
    page_title="データ検索システム",
    page_icon="🔍",
    layout="centered"  # 画面中央にすっきり収める
)

# ==========================================
# 2. Supabase 接続設定（st.secrets から読み込み）
# ==========================================
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError:
        st.error("❌ Streamlit Cloudの Secrets 設定が見つかりません。")
        st.stop()

supabase = init_supabase()

# ==========================================
# 3. 画面ヘッダーのデザイン
# ==========================================
st.title("🔍 スマート検索ダッシュボード")
st.caption("Supabase データベースからリアルタイムで情報を検索・表示します")
st.markdown("---")

# ==========================================
# 4. 検索バー（横並びレイアウト）
# ==========================================
# st.columns で入力欄とボタンを 4:1 の黄金比で横並びにします
col1, col2 = st.columns([4, 1])

with col1:
    search_query = st.text_input(
        label="検索キーワード",
        placeholder="検索したいキーワードを入力してください...",
        label_visibility="collapsed"  # 余計なスキマをなくすためラベルを非表示に
    )

with col2:
    # type="primary" でボタンに色をつけ、use_container_width で横幅いっぱいに広げます
    search_button = st.button("検索", type="primary", use_container_width=True)

st.markdown(" ") # 少しスキマを空ける

# ==========================================
# 5. 検索処理 ＆ 結果のカード型表示
# ==========================================
# 入力欄でエンターが押されるか、検索ボタンがクリックされたら実行
if search_query or search_button:
    
    # 🔍 【重要】ここのテーブル名と列名は、ご自身のSupabaseに合わせて書き換えてください！
    # 例：テーブル名が 'users' で、名前の列が 'name' の場合
    TARGET_TABLE = "items"   # あなたのテーブル名
    TARGET_COLUMN = "name"   # 検索対象にしたい列名
    
    with st.spinner("データを検索中..."):
        try:
            # .ilike() で大文字小文字を区別しない「あいまい検索（部分一致）」を行います
            response = (
                supabase.table(TARGET_TABLE)
                .select("*")
                .ilike(TARGET_COLUMN, f"%{search_query}%")
                .execute()
            )
            results = response.data

            # --- 結果の表示 ---
            if results:
                st.success(f"💡 {len(results)} 件のデータが見つかりました！")
                st.markdown(" ")
                
                # 取得したデータを1件ずつ、枠線付きの「カード風」にして並べる
                for item in results:
                    with st.container(border=True):
                        # タイトル部分（太字で少し大きく）
                        st.subheader(f"📦 {item.get(TARGET_COLUMN, '名称なし')}")
                        
                        # 中身（データに合わせて自由に変えてください）
                        st.markdown(f"**詳細説明:** {item.get('description', '未設定')}")
                        
                        # 数字（価格など）がある場合はカンマ区切りにして右側に目立たせるなど
                        if "price" in item:
                            st.metric(label="価格", value=f"{item.get('price', 0):,} 円")
            else:
                st.info("該当するデータが見つかりませんでした。別のキーワードを試してください。")
                
        except Exception as e:
            st.error("❌ 検索中にエラーが発生しました。")
            st.exception(e) # 開発用に詳しいエラー内容も表示します
