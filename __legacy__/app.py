import streamlit as st
import feedparser
import time

# ページ設定
st.set_page_config(
    page_title="AI News Aggregator",
    page_icon="🤖",
    layout="wide"
)

# カスタムCSS
st.markdown("""
<style>
    .news-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #484b5c;
        transition: transform 0.2s;
    }
    .news-card:hover {
        transform: scale(1.01);
        border-color: #ff4b4b;
    }
    .news-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-decoration: none;
    }
    .news-date {
        color: #aaaaaa;
        font-size: 0.8rem;
        margin-bottom: 10px;
    }
    .news-summary {
        color: #e0e0e0;
        font-size: 0.95rem;
    }
    .news-link {
        display: inline-block;
        margin-top: 15px;
        padding: 5px 15px;
        background-color: #ff4b4b;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .news-link:hover {
        background-color: #ff3333;
        color: white;
    }
    /* サイドバーのスタイル調整 */
    .css-1d391kg {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def get_news(query):
    """
    Google News RSSからニュースを取得する関数
    """
    # URLエンコーディングはfeedparserが内部で処理するが、念の為スペースを+に置換
    formatted_query = query.replace(" ", "+")
    # 日本語ロケールでの検索URL
    rss_url = f"https://news.google.com/rss/search?q={formatted_query}&hl=jp&gl=JP&ceid=JP:ja"
    
    try:
        feed = feedparser.parse(rss_url)
        return feed.entries
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        return []

def main():
    st.title("🤖 AI News Aggregator Dashboard")
    st.markdown("最新のAI関連ニュースをGoogle Newsから収集して表示します。")

    # サイドバー
    with st.sidebar:
        st.header("Search Settings")
        query = st.text_input(
            "検索キーワード",
            value="Artificial Intelligence",
            help="興味のあるトピックを入力してください（例: OpenAI, Machine Learning）"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info(
            "このダッシュボードはfeedparserを使用して"
            "Google NewsのRSSフィードから"
            "最新の記事を取得しています。"
        )

    # メインコンテンツ
    if query:
        with st.spinner(f"「{query}」に関するニュースを取得中..."):
            entries = get_news(query)
            
        if entries:
            st.success(f"{len(entries)} 件のニュースが見つかりました")
            
            # グリッドレイアウトの作成（2列）
            cols = st.columns(2)
            
            for check, entry in enumerate(entries):
                # 2列に交互に配置
                col = cols[check % 2]
                
                with col:
                    # 日付の整形
                    published = entry.get('published', '日付不明')
                    
                    # HTMLを含むサマリーのクリーニング（簡易的）
                    summary = entry.get('summary', '')
                    # 画像タグなどを除去してテキストのみにする処理があれば尚良いが、
                    # Google News RSSのsummaryはHTMLを含むことが多い。
                    # ここではシンプルに表示する。
                    
                    # カード表示
                    st.markdown(f"""
                    <div class="news-card">
                        <div class="news-date">{published}</div>
                        <a href="{entry.link}" target="_blank" class="news-title">{entry.title}</a>
                        <div class="news-summary" style="margin-top: 10px; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;">
                            {summary}
                        </div>
                        <a href="{entry.link}" target="_blank" class="news-link">元記事を読む ➜</a>
                    </div>
                    """, unsafe_allow_html=True)
                    
        else:
            st.warning("ニュースが見つかりませんでした。別のキーワードで試してください。")
    else:
        st.info("サイドバーの検索ボックスにキーワードを入力してください。")

if __name__ == "__main__":
    main()
