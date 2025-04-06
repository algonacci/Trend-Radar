from flask import Flask, render_template
from youtube import get_youtube_trends
from google_news import get_google_top_news
from google_trends import get_google_trends_indonesia

app = Flask(__name__)


@app.route("/")
def index():
    youtube_trends = get_youtube_trends()
    google_top_news = get_google_top_news()
    google_trends = get_google_trends_indonesia()
    return render_template(
        "pages/index.html",
        youtube_trends=youtube_trends,
        google_top_news=google_top_news,
        google_trends=google_trends,
    )


if __name__ == "__main__":
    app.run()
