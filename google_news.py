import gnews

gn = gnews.GNews(
    language="id",
    country="ID",
    max_results=20,
)


def get_google_top_news():
    articles = gn.get_top_news()
    results = []
    for article in articles:
        formatted_article = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "publisher": article.get("publisher", {}).get("title", ""),
            "published_date": article.get("published date", ""),
            "description": article.get("description", ""),
        }
        results.append(formatted_article)
    return results
