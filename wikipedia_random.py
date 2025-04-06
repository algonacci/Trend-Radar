import wikipedia

# Set language to Indonesian
wikipedia.set_lang("id")


def get_random_wikipedia_articles(count=10):
    """Get multiple random Wikipedia articles with their summaries."""
    articles = []
    for _ in range(count):
        try:
            # Get a random article title
            title = wikipedia.random()

            # Get a summary of the article
            try:
                summary = wikipedia.summary(title, sentences=2)
            except wikipedia.exceptions.DisambiguationError as e:
                # If disambiguation page, use the first option
                if e.options:
                    title = e.options[0]
                    summary = wikipedia.summary(title, sentences=2)
                else:
                    summary = "Summary not available"
            except Exception:
                summary = "Summary not available"

            # Get the URL
            url = wikipedia.page(title).url

            # Create article object
            article = {"title": title, "summary": summary, "url": url}

            articles.append(article)
        except Exception as e:
            # If any error occurs, just continue to the next article
            print(f"Error fetching Wikipedia article: {e}")
            continue

    return articles
