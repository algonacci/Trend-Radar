from flask import Flask, render_template, jsonify
from flask_caching import Cache
from youtube import get_youtube_trends
from google_news import get_google_top_news, get_topic_news
from google_trends import get_google_trends_indonesia
from yahoo_finance import get_asia_and_indonesia_stock_exchange_info
from wikipedia_random import get_random_wikipedia_articles
from huggingface_trends import (
    get_huggingface_collections,
    get_trending_datasets,
    get_trending_spaces,
    get_daily_papers,
)
from arxiv_papers import get_trending_arxiv_papers
from hacker_news import get_hot_hn_stories, get_rising_hn_stories, get_new_hn_stories, get_hn_insights, format_story
from reddit_post import get_reddit_indonesia_posts
import threading
import time
import datetime
from dotenv import load_dotenv

# Memuat variabel environment dari file .env
load_dotenv()

app = Flask(__name__)

# Konfigurasi cache
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",  # Simpan cache di memory, bisa ganti ke FileCache jika perlu
    "CACHE_DEFAULT_TIMEOUT": 3600,  # Cache selama 1 jam (dalam detik)
}
app.config.from_mapping(cache_config)
cache = Cache(app)


# Variabel fallback untuk data awal (jika cache kosong)
EMPTY_DATA = {"collections": [], "datasets": [], "spaces": [], "papers": []}


# Fungsi-fungsi dengan cache dan timeout yang aman
@cache.cached(timeout=3600, key_prefix="youtube_trends")
def cached_youtube_trends():
    print("Fetching fresh YouTube trends data")
    try:
        return get_youtube_trends()
    except Exception as e:
        print(f"Error fetching YouTube trends: {e}")
        return []


@cache.cached(timeout=3600, key_prefix="google_top_news")
def cached_google_top_news():
    print("Fetching fresh Google top news data")
    try:
        return get_google_top_news()
    except Exception as e:
        print(f"Error fetching Google top news: {e}")
        return []


@cache.cached(timeout=3600, key_prefix="topic_news")
def cached_topic_news():
    print("Fetching fresh topic news data")
    try:
        return get_topic_news()
    except Exception as e:
        print(f"Error fetching topic news: {e}")
        return []


@cache.cached(timeout=3600, key_prefix="google_trends")
def cached_google_trends():
    print("Fetching fresh Google trends data")
    try:
        return get_google_trends_indonesia()
    except Exception as e:
        print(f"Error fetching Google trends: {e}")
        return []


@cache.cached(timeout=1800, key_prefix="asia_markets")
def cached_asia_markets():
    print("Fetching fresh market data")
    try:
        return get_asia_and_indonesia_stock_exchange_info()
    except Exception as e:
        print(f"Error fetching market data: {e}")
        return [], {}


@cache.cached(timeout=7200, key_prefix="wiki_articles")
def cached_wiki_articles():
    print("Fetching fresh Wikipedia articles")
    try:
        return get_random_wikipedia_articles(10)
    except Exception as e:
        print(f"Error fetching Wikipedia articles: {e}")
        return []


# Cache individual HuggingFace components separately to avoid timeouts
@cache.cached(timeout=7200, key_prefix="huggingface_collections")
def cached_huggingface_collections():
    print("Fetching fresh HuggingFace collections")
    try:
        return get_huggingface_collections()
    except Exception as e:
        print(f"Error fetching HuggingFace collections: {e}")
        return []


@cache.cached(timeout=7200, key_prefix="huggingface_datasets")
def cached_huggingface_datasets():
    print("Fetching fresh HuggingFace datasets")
    try:
        return get_trending_datasets()
    except Exception as e:
        print(f"Error fetching HuggingFace datasets: {e}")
        return []


@cache.cached(timeout=7200, key_prefix="huggingface_spaces")
def cached_huggingface_spaces():
    print("Fetching fresh HuggingFace spaces")
    try:
        return get_trending_spaces()
    except Exception as e:
        print(f"Error fetching HuggingFace spaces: {e}")
        return []


@cache.cached(timeout=7200, key_prefix="huggingface_papers")
def cached_huggingface_papers():
    print("Fetching fresh HuggingFace papers")
    try:
        return get_daily_papers()
    except Exception as e:
        print(f"Error fetching HuggingFace papers: {e}")
        return []


# Cache ArXiv papers with different sorting methods
@cache.cached(timeout=7200, key_prefix="arxiv_hot_papers")
def cached_arxiv_hot_papers():
    print("Fetching fresh ArXiv HOT papers")
    try:
        return get_trending_arxiv_papers(sort_method="hot", max_results=10)
    except Exception as e:
        print(f"Error fetching ArXiv hot papers: {e}")
        return []


@cache.cached(timeout=7200, key_prefix="arxiv_rising_papers")
def cached_arxiv_rising_papers():
    print("Fetching fresh ArXiv RISING papers")
    try:
        return get_trending_arxiv_papers(sort_method="rising", max_results=10)
    except Exception as e:
        print(f"Error fetching ArXiv rising papers: {e}")
        return []


@cache.cached(timeout=7200, key_prefix="arxiv_new_papers")
def cached_arxiv_new_papers():
    print("Fetching fresh ArXiv NEW papers")
    try:
        return get_trending_arxiv_papers(sort_method="new", max_results=10)
    except Exception as e:
        print(f"Error fetching ArXiv new papers: {e}")
        return []


# Cache Hacker News stories with different sorting methods
@cache.cached(timeout=1800, key_prefix="hn_hot_stories")
def cached_hn_hot_stories():
    print("Fetching fresh Hacker News HOT stories")
    try:
        stories_with_scores = get_hot_hn_stories(10)
        return [format_story(story, score) for story, score in stories_with_scores]
    except Exception as e:
        print(f"Error fetching Hacker News hot stories: {e}")
        return []


@cache.cached(timeout=1800, key_prefix="hn_rising_stories")
def cached_hn_rising_stories():
    print("Fetching fresh Hacker News RISING stories")
    try:
        stories_with_scores = get_rising_hn_stories(10)
        return [format_story(story, score) for story, score in stories_with_scores]
    except Exception as e:
        print(f"Error fetching Hacker News rising stories: {e}")
        return []


@cache.cached(timeout=1800, key_prefix="hn_new_stories")
def cached_hn_new_stories():
    print("Fetching fresh Hacker News NEW stories")
    try:
        stories_with_scores = get_new_hn_stories(10)
        return [format_story(story, score) for story, score in stories_with_scores]
    except Exception as e:
        print(f"Error fetching Hacker News new stories: {e}")
        return []


@cache.cached(timeout=3600, key_prefix="hn_insights")
def cached_hn_insights():
    print("Fetching fresh Hacker News insights")
    try:
        return get_hn_insights()
    except Exception as e:
        print(f"Error fetching Hacker News insights: {e}")
        return {}


# Cache Reddit posts untuk r/indonesia dengan berbagai kategori
@cache.cached(timeout=1800, key_prefix="reddit_hot_posts")
def cached_reddit_hot_posts():
    print("Fetching fresh Reddit HOT posts from r/indonesia")
    try:
        return get_reddit_indonesia_posts(category="hot", limit=10)
    except Exception as e:
        print(f"Error fetching Reddit hot posts: {e}")
        return []


@cache.cached(timeout=1800, key_prefix="reddit_new_posts")
def cached_reddit_new_posts():
    print("Fetching fresh Reddit NEW posts from r/indonesia")
    try:
        return get_reddit_indonesia_posts(category="new", limit=10)
    except Exception as e:
        print(f"Error fetching Reddit new posts: {e}")
        return []


@cache.cached(timeout=1800, key_prefix="reddit_top_posts")
def cached_reddit_top_posts():
    print("Fetching fresh Reddit TOP posts from r/indonesia")
    try:
        return get_reddit_indonesia_posts(category="top", limit=10)
    except Exception as e:
        print(f"Error fetching Reddit top posts: {e}")
        return []


# Thread untuk mengupdate cache di background
def update_cache_in_background():
    while True:
        try:
            print("Background thread: updating cache...")
            # Update semua cache secara berurutan
            cached_youtube_trends()
            cached_google_top_news()
            cached_topic_news()
            cached_google_trends()
            cached_asia_markets()
            cached_wiki_articles()
            cached_huggingface_collections()
            cached_huggingface_datasets()
            cached_huggingface_spaces()
            cached_huggingface_papers()
            # Update ArXiv papers cache
            cached_arxiv_hot_papers()
            cached_arxiv_rising_papers()
            cached_arxiv_new_papers()
            # Update Hacker News cache
            cached_hn_hot_stories()
            cached_hn_rising_stories()
            cached_hn_new_stories()
            cached_hn_insights()
            # Update Reddit cache
            cached_reddit_hot_posts()
            cached_reddit_new_posts()
            cached_reddit_top_posts()
            print("Background thread: cache update complete")
        except Exception as e:
            print(f"Error in background cache update: {e}")
        # Tunggu 1 jam sebelum memperbarui cache lagi
        time.sleep(3600)


# Mulai thread background di startup aplikasi
background_thread = threading.Thread(target=update_cache_in_background, daemon=True)
background_thread.start()


@app.route("/")
def index():
    # Get current year for the footer
    current_year = datetime.datetime.now().year

    # Gunakan individual cached functions dengan fallback (tidak timeout)
    try:
        youtube_trends = cached_youtube_trends()
    except Exception:
        youtube_trends = []

    try:
        google_top_news = cached_google_top_news()
    except Exception:
        google_top_news = []

    try:
        topic_news = cached_topic_news()
    except Exception:
        topic_news = []

    try:
        google_trends = cached_google_trends()
    except Exception:
        google_trends = []

    try:
        asia_markets, ihsg_data = cached_asia_markets()
    except Exception:
        asia_markets, ihsg_data = [], {}

    try:
        wiki_articles = cached_wiki_articles()
    except Exception:
        wiki_articles = []

    # Ambil data HuggingFace secara individual dengan fallback
    try:
        huggingface_collections = cached_huggingface_collections()
    except Exception:
        huggingface_collections = []

    try:
        huggingface_datasets = cached_huggingface_datasets()
    except Exception:
        huggingface_datasets = []

    try:
        huggingface_spaces = cached_huggingface_spaces()
    except Exception:
        huggingface_spaces = []

    try:
        huggingface_papers = cached_huggingface_papers()
    except Exception:
        huggingface_papers = []

    # Ambil ArXiv papers dengan berbagai algoritma scoring
    try:
        arxiv_hot_papers = cached_arxiv_hot_papers()
    except Exception:
        arxiv_hot_papers = []

    try:
        arxiv_rising_papers = cached_arxiv_rising_papers()
    except Exception:
        arxiv_rising_papers = []

    try:
        arxiv_new_papers = cached_arxiv_new_papers()
    except Exception:
        arxiv_new_papers = []
        
    # Ambil data Hacker News dengan fallback
    try:
        hn_hot_stories = cached_hn_hot_stories()
    except Exception:
        hn_hot_stories = []
        
    try:
        hn_rising_stories = cached_hn_rising_stories()
    except Exception:
        hn_rising_stories = []
        
    try:
        hn_new_stories = cached_hn_new_stories()
    except Exception:
        hn_new_stories = []
    
    # Menghapus insights karena sudah tidak digunakan
    hn_insights = {}
    
    # Ambil data Reddit dengan fallback
    try:
        reddit_hot_posts = cached_reddit_hot_posts()
    except Exception:
        reddit_hot_posts = []
        
    try:
        reddit_new_posts = cached_reddit_new_posts()
    except Exception:
        reddit_new_posts = []
        
    try:
        reddit_top_posts = cached_reddit_top_posts()
    except Exception:
        reddit_top_posts = []
    
    # Menggabungkan semua cerita Hacker News dan menghapus duplikat berdasarkan judul
    all_hn_stories = []
    seen_titles = set()
    
    # Fungsi untuk tambahkan cerita ke daftar gabungan jika judulnya belum ada
    def add_unique_story(story):
        title = story.get('title', '')
        if title and title not in seen_titles:
            seen_titles.add(title)
            all_hn_stories.append(story)
    
    # Tambahkan cerita dari masing-masing kategori
    for story in hn_hot_stories:
        add_unique_story(story)
    
    for story in hn_rising_stories:
        add_unique_story(story)
    
    for story in hn_new_stories:
        add_unique_story(story)
    
    # Urutkan berdasarkan skor (dari tertinggi ke terendah) dan ambil 16 teratas
    all_hn_stories.sort(key=lambda x: x.get('score', 0), reverse=True)
    all_hn_stories = all_hn_stories[:16]
    
    # Hapus array terpisah karena sudah digabungkan
    hn_hot_stories = all_hn_stories
    hn_rising_stories = []
    hn_new_stories = []

    # Buat cache status endpoint
    status = {
        "youtube": len(youtube_trends) > 0,
        "google_news": len(google_top_news) > 0,
        "topic_news": len(topic_news) > 0,
        "google_trends": len(google_trends) > 0,
        "wiki": len(wiki_articles) > 0,
        "huggingface_collections": len(huggingface_collections) > 0,
        "huggingface_datasets": len(huggingface_datasets) > 0,
        "huggingface_spaces": len(huggingface_spaces) > 0,
        "huggingface_papers": len(huggingface_papers) > 0,
        "arxiv_hot": len(arxiv_hot_papers) > 0,
        "arxiv_rising": len(arxiv_rising_papers) > 0,
        "arxiv_new": len(arxiv_new_papers) > 0,
        "hn_hot": len(hn_hot_stories) > 0,
        "hn_rising": len(hn_rising_stories) > 0,
        "hn_new": len(hn_new_stories) > 0,
        "hn_insights": bool(hn_insights),
        "reddit_hot": len(reddit_hot_posts) > 0,
        "reddit_new": len(reddit_new_posts) > 0,
        "reddit_top": len(reddit_top_posts) > 0,
    }
    print(f"Data status: {status}")

    return render_template(
        "pages/index.html",
        youtube_trends=youtube_trends,
        google_top_news=google_top_news,
        topic_news=topic_news,
        google_trends=google_trends,
        asia_markets=asia_markets,
        ihsg_data=ihsg_data,
        wiki_articles=wiki_articles,
        huggingface_collections=huggingface_collections,
        huggingface_datasets=huggingface_datasets,
        huggingface_spaces=huggingface_spaces,
        huggingface_papers=huggingface_papers,
        arxiv_hot_papers=arxiv_hot_papers,
        arxiv_rising_papers=arxiv_rising_papers,
        arxiv_new_papers=arxiv_new_papers,
        hn_hot_stories=hn_hot_stories,
        hn_rising_stories=hn_rising_stories,
        hn_new_stories=hn_new_stories,
        hn_insights=hn_insights,
        reddit_hot_posts=reddit_hot_posts,
        reddit_new_posts=reddit_new_posts,
        reddit_top_posts=reddit_top_posts,
        current_year=current_year,
    )


# Endpoint untuk membersihkan cache
@app.route("/clear-cache")
def clear_cache():
    try:
        cache.clear()
        return "Cache cleared successfully!"
    except Exception as e:
        return f"Error clearing cache: {e}"


# Endpoint untuk melihat status cache
@app.route("/cache-status")
def cache_status():
    try:
        status = {
            "youtube_trends": cache.has("youtube_trends"),
            "google_top_news": cache.has("google_top_news"),
            "topic_news": cache.has("topic_news"),
            "google_trends": cache.has("google_trends"),
            "asia_markets": cache.has("asia_markets"),
            "wiki_articles": cache.has("wiki_articles"),
            "huggingface_collections": cache.has("huggingface_collections"),
            "huggingface_datasets": cache.has("huggingface_datasets"),
            "huggingface_spaces": cache.has("huggingface_spaces"),
            "huggingface_papers": cache.has("huggingface_papers"),
            "arxiv_hot_papers": cache.has("arxiv_hot_papers"),
            "arxiv_rising_papers": cache.has("arxiv_rising_papers"),
            "arxiv_new_papers": cache.has("arxiv_new_papers"),
            "hn_hot_stories": cache.has("hn_hot_stories"),
            "hn_rising_stories": cache.has("hn_rising_stories"),
            "hn_new_stories": cache.has("hn_new_stories"),
            "hn_insights": cache.has("hn_insights"),
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)})


# Endpoint untuk memulai background refresh cache
@app.route("/refresh-cache")
def refresh_cache():
    try:
        thread = threading.Thread(target=update_cache_in_background)
        thread.daemon = True
        thread.start()
        return "Cache refresh started in background"
    except Exception as e:
        return f"Error starting cache refresh: {e}"


# API Endpoints untuk Hacker News
@app.route("/api/hackernews/hot")
def api_hot_hn_stories():
    """Get hot stories from Hacker News"""
    try:
        return jsonify({"stories": cached_hn_hot_stories()})
    except Exception as e:
        print(f"Error in HN hot API: {e}")
        return jsonify({"error": str(e), "stories": []})


@app.route("/api/hackernews/rising")
def api_rising_hn_stories():
    """Get rising stories from Hacker News"""
    try:
        return jsonify({"stories": cached_hn_rising_stories()})
    except Exception as e:
        print(f"Error in HN rising API: {e}")
        return jsonify({"error": str(e), "stories": []})


@app.route("/api/hackernews/new")
def api_new_hn_stories():
    """Get new stories from Hacker News"""
    try:
        return jsonify({"stories": cached_hn_new_stories()})
    except Exception as e:
        print(f"Error in HN new API: {e}")
        return jsonify({"error": str(e), "stories": []})


@app.route("/api/hackernews/insights")
def api_hn_insights():
    """Get insights from Hacker News"""
    try:
        return jsonify({"insights": cached_hn_insights()})
    except Exception as e:
        print(f"Error in HN insights API: {e}")
        return jsonify({"error": str(e), "insights": {}})


if __name__ == "__main__":
    app.run()
