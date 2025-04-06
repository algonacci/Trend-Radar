from flask import Flask, render_template
from flask_caching import Cache
from youtube import get_youtube_trends
from google_news import get_google_top_news, get_topic_news
from google_trends import get_google_trends_indonesia
from yahoo_finance import get_asia_and_indonesia_stock_exchange_info
from wikipedia_random import get_random_wikipedia_articles
from huggingface_trends import get_trending_ml_models
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


# Fungsi-fungsi dengan cache
@cache.cached(timeout=3600, key_prefix="youtube_trends")
def cached_youtube_trends():
    print("Fetching fresh YouTube trends data")
    return get_youtube_trends()

@cache.cached(timeout=3600, key_prefix="google_top_news")
def cached_google_top_news():
    print("Fetching fresh Google top news data")
    return get_google_top_news()

@cache.cached(timeout=3600, key_prefix="topic_news")
def cached_topic_news():
    print("Fetching fresh topic news data")
    return get_topic_news()

@cache.cached(timeout=3600, key_prefix="google_trends")
def cached_google_trends():
    print("Fetching fresh Google trends data")
    return get_google_trends_indonesia()

@cache.cached(timeout=1800, key_prefix="asia_markets")
def cached_asia_markets():
    print("Fetching fresh market data")
    return get_asia_and_indonesia_stock_exchange_info()

@cache.cached(timeout=7200, key_prefix="wiki_articles")
def cached_wiki_articles():
    print("Fetching fresh Wikipedia articles")
    return get_random_wikipedia_articles(10)

@cache.cached(timeout=7200, key_prefix="huggingface_data")
def cached_huggingface_data():
    print("Fetching fresh HuggingFace data")
    return get_trending_ml_models()

@app.route("/")
def index():
    # Gunakan fungsi-fungsi dengan cache
    youtube_trends = cached_youtube_trends()
    google_top_news = cached_google_top_news()
    topic_news = cached_topic_news()
    google_trends = cached_google_trends()
    asia_markets, ihsg_data = cached_asia_markets()
    wiki_articles = cached_wiki_articles()
    huggingface_data = cached_huggingface_data()
    
    # Tambahkan waktu cache yang tersisa pada cache huggingface untuk debug
    try:
        cache_info = cache.get_dict()
        print(f"Cache info: {len(cache_info)} items")
    except Exception as e:
        print(f"Error getting cache info: {e}")
    
    return render_template(
        "pages/index.html",
        youtube_trends=youtube_trends,
        google_top_news=google_top_news,
        topic_news=topic_news,
        google_trends=google_trends,
        asia_markets=asia_markets,
        ihsg_data=ihsg_data,
        wiki_articles=wiki_articles,
        huggingface_collections=huggingface_data["collections"],
        huggingface_datasets=huggingface_data["datasets"],
        huggingface_spaces=huggingface_data["spaces"],
        huggingface_papers=huggingface_data["papers"],
    )


# Endpoint untuk membersihkan cache (hanya untuk development)
@app.route("/clear-cache")
def clear_cache():
    cache.clear()
    return "Cache cleared successfully!"

if __name__ == "__main__":
    app.run()
