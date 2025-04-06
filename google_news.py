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


def get_news_by_topic(topic):
    # Create a new GNews instance with 10 results max
    topic_gn = gnews.GNews(
        language="id",
        country="ID",
        max_results=10,
    )

    articles = topic_gn.get_news_by_topic(topic)
    results = []
    for article in articles:
        formatted_article = {
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "publisher": article.get("publisher", {}).get("title", ""),
            "published_date": article.get("published date", ""),
            "description": article.get("description", ""),
            "topic": topic,
        }
        results.append(formatted_article)
    return results


def get_topic_news():
    topics = {
        "BUSINESS": "Business",
        "TECHNOLOGY": "Technology",
        "SCIENCE": "Science",
        "SPORTS": "Sports",
        "POLITICS": "Politics",
    }

    topic_news = {}
    for topic_key, topic_name in topics.items():
        topic_news[topic_name] = get_news_by_topic(topic_key)

    return topic_news
