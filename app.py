from flask import Flask, render_template
from youtube import get_youtube_trends
from google_news import get_google_top_news, get_topic_news
from google_trends import get_google_trends_indonesia
from yahoo_finance import get_asia_and_indonesia_stock_exchange_info
from wikipedia_random import get_random_wikipedia_articles
from huggingface_trends import get_trending_ml_models

app = Flask(__name__)


@app.route("/")
def index():
    youtube_trends = get_youtube_trends()
    google_top_news = get_google_top_news()
    topic_news = get_topic_news()
    google_trends = get_google_trends_indonesia()
    asia_markets, ihsg_data = get_asia_and_indonesia_stock_exchange_info()
    wiki_articles = get_random_wikipedia_articles(10)
    huggingface_data = get_trending_ml_models()
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


if __name__ == "__main__":
    app.run()
