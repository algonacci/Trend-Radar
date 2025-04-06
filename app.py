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
import threading
import time
import os

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


if __name__ == "__main__":
    app.run()
