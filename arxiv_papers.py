import arxiv
from datetime import datetime, timezone
from collections import defaultdict
import time

# List of selected ArXiv categories from various fields
CATEGORIES = [
    # Computer Science
    "cs",
    # Biology
    "q-bio.BM",  # Biomolecules
    "q-bio.NC",  # Neurons and Cognition
    # Economics & Finance
    "econ.GN",  # General Economics
    "q-fin.ST",  # Statistical Finance
    # Mathematics
    "math.NT",  # Number Theory
    "math.PR",  # Probability
    # Physics
    "physics",  # Atmospheric and Oceanic Physics
    "physics",  # Medical Physics
    "eess"
    "stat"
]

# Global cache duration
CACHE_DURATION = 7200  # 2 hours in seconds

# Store papers globally to avoid redundant API calls
_papers_cache = {}
_last_fetch_time = 0


def get_trending_arxiv_papers(sort_method="hot", max_results=10):
    """
    Get trending papers from ArXiv based on specified sorting method.

    Args:
        sort_method (str): Sorting method - "hot", "rising", or "new"
        max_results (int): Maximum number of results to return

    Returns:
        list: List of trending papers with metadata
    """
    try:
        # Fetch papers from ArXiv (will use cache if available)
        all_papers = fetch_papers()

        if not all_papers:
            print("No papers found")
            return []

        # Calculate scores based on sort method
        print(
            f"Calculating scores for {len(all_papers)} papers using {sort_method} algorithm"
        )
        papers_with_scores = []

        # Extract trending keywords and author activity for scoring
        trending_keywords = extract_trending_keywords(all_papers)
        author_activity = calculate_author_activity(all_papers)

        for paper in all_papers:
            if sort_method.lower() == "hot":
                score = calculate_hot_score(paper, author_activity, trending_keywords)
            elif sort_method.lower() == "rising":
                score = calculate_rising_score(paper, trending_keywords)
            else:  # "new"
                score = calculate_new_score(paper)

            papers_with_scores.append((paper, score))

        # Sort papers by score
        sorted_papers = sorted(papers_with_scores, key=lambda x: x[1], reverse=True)

        # Format top papers for display
        trending_papers = []
        for paper, score in sorted_papers[:max_results]:
            trending_papers.append(format_paper(paper, score))

        print(f"Returning {len(trending_papers)} {sort_method} papers")
        return trending_papers

    except Exception as e:
        print(f"Error in get_trending_arxiv_papers: {e}")
        return []


def fetch_papers():
    """
    Fetch papers from ArXiv API for all categories.
    Uses a simple time-based cache to avoid redundant API calls.

    Returns:
        list: List of paper objects
    """
    global _papers_cache, _last_fetch_time
    current_time = time.time()

    # Return cached papers if they're less than 1 hour old
    if _papers_cache and current_time - _last_fetch_time < 3600:
        print("Using cached ArXiv papers")
        return _papers_cache

    try:
        # Use a combined query to reduce number of API calls
        combined_query = " OR ".join([f"cat:{category}" for category in CATEGORIES])

        print(f"Fetching ArXiv papers with query: {combined_query}")

        # Make a single request with all categories
        search = arxiv.Search(
            query=combined_query,
            max_results=100,  # Limit to 100 papers total
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        papers = list(search.results())
        print(f"Retrieved {len(papers)} papers from ArXiv")

        # Update the cache
        _papers_cache = papers
        _last_fetch_time = current_time

        return papers
    except Exception as e:
        print(f"Error in fetch_papers: {e}")
        # If error occurs but we have cached papers, return those
        if _papers_cache:
            print("Returning cached papers due to fetch error")
            return _papers_cache
        return []


def extract_trending_keywords(papers):
    """
    Extract trending keywords from paper titles and abstracts.

    Args:
        papers (list): List of paper objects

    Returns:
        list: List of trending keywords
    """
    keyword_counts = defaultdict(int)
    for paper in papers:
        # Combine title and abstract for keyword extraction
        text = (paper.title + " " + paper.summary).lower()
        # Simple word tokenization and filtering
        words = [word.strip(".,;:()[]{}\"''") for word in text.split()]
        for word in words:
            if (
                len(word) > 4 and word not in STOPWORDS
            ):  # Only consider words longer than 4 letters
                keyword_counts[word] += 1

    # Get the top 50 keywords
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_keywords[:50]]


def calculate_author_activity(papers):
    """
    Calculate activity score for each author based on number of publications.

    Args:
        papers (list): List of paper objects

    Returns:
        dict: Dictionary mapping author names to activity scores
    """
    author_counts = defaultdict(int)
    for paper in papers:
        for author in paper.authors:
            author_counts[author.name] += 1
    return author_counts


def calculate_hot_score(paper, author_activity, trending_keywords):
    """
    Calculate hotness score for a paper.

    Args:
        paper: Paper object
        author_activity (dict): Dictionary of author activity scores
        trending_keywords (list): List of trending keywords

    Returns:
        float: Normalized hotness score between 0-100
    """
    # Time decay factor - more recent papers get higher scores
    published_time = paper.published.replace(tzinfo=timezone.utc)
    time_diff = datetime.now(timezone.utc) - published_time
    time_diff_days = max(
        time_diff.total_seconds() / (3600 * 24), 0.1
    )  # In days, minimum 0.1 day
    recency_score = 100 * (1 / (time_diff_days + 1))

    # Author activity score - cap at 100
    author_count = sum(author_activity.get(author.name, 0) for author in paper.authors)
    author_score = min(100, author_count * 5)  # Scale by 5, but cap at 100

    # Keyword relevance score - cap at 100
    text = (paper.title + " " + paper.summary).lower()
    keyword_count = sum(1 for keyword in trending_keywords if keyword in text)
    keyword_score = min(100, keyword_count * 10)  # Scale by 10, but cap at 100

    # Combine scores with weights
    # 50% recency, 30% keyword relevance, 20% author activity
    score = (0.5 * recency_score) + (0.3 * keyword_score) + (0.2 * author_score)

    # Ensure score is between 0-100
    return max(0, min(100, score))


def calculate_rising_score(paper, trending_keywords):
    """
    Calculate rising score for a paper, emphasizing novelty.

    Args:
        paper: Paper object
        trending_keywords (list): List of trending keywords

    Returns:
        float: Normalized rising score between 0-100
    """
    # Time component - papers from last 30 days get higher scores
    published_time = paper.published.replace(tzinfo=timezone.utc)
    time_diff = datetime.now(timezone.utc) - published_time
    time_diff_days = max(
        time_diff.total_seconds() / (3600 * 24), 0.1
    )  # In days, minimum 0.1 day

    # Papers newer than 30 days get high recency score, older papers decay
    if time_diff_days <= 30:
        recency_score = 100 * (1 - (time_diff_days / 30))
    else:
        recency_score = max(
            0, 50 * (1 - ((time_diff_days - 30) / 335))
        )  # Decay to 0 over a year

    # Novelty component - papers with less common keywords score higher
    text = (paper.title + " " + paper.summary).lower()
    words = set(word.strip(".,;:()[]{}\"''") for word in text.split() if len(word) > 4)
    uncommon_keywords = words - set(trending_keywords)
    novelty_score = min(100, len(uncommon_keywords) * 2)  # Scale by 2, but cap at 100

    # Rising score combines recency (60%) and novelty (40%)
    score = (0.6 * recency_score) + (0.4 * novelty_score)

    # Ensure score is between 0-100
    return max(0, min(100, score))


def calculate_new_score(paper):
    """
    Calculate score based purely on recency.

    Args:
        paper: Paper object

    Returns:
        float: Normalized recency score between 0-100
    """
    # Time component - papers from last 90 days get proportional scores
    published_time = paper.published.replace(tzinfo=timezone.utc)
    time_diff = datetime.now(timezone.utc) - published_time
    time_diff_days = max(
        time_diff.total_seconds() / (3600 * 24), 0.1
    )  # In days, minimum 0.1 day

    # Papers from last 30 days get top scores (80-100)
    if time_diff_days <= 30:
        # Scale from 100 (today) to 80 (30 days ago)
        score = 100 - ((time_diff_days / 30) * 20)
    # Papers from 30-90 days get medium scores (30-80)
    elif time_diff_days <= 90:
        # Scale from 80 (30 days ago) to 30 (90 days ago)
        score = 80 - (((time_diff_days - 30) / 60) * 50)
    # Papers older than 90 days get lower scores (0-30)
    else:
        # Scale from 30 (90 days ago) to 0 (365+ days ago)
        days_over_90 = min(time_diff_days - 90, 275)  # Cap at 275 (90+275=365 days)
        score = 30 - ((days_over_90 / 275) * 30)

    # Ensure score is between 0-100
    return max(0, min(100, score))


def format_paper(paper, score):
    """
    Format paper data for display.

    Args:
        paper: Paper object
        score: Calculated score

    Returns:
        dict: Formatted paper data
    """
    return {
        "title": paper.title,
        "url": paper.pdf_url or paper.entry_id,
        "authors": [author.name for author in paper.authors],
        "published": paper.published,
        "summary": paper.summary[:150] + "..."
        if len(paper.summary) > 150
        else paper.summary,
        "categories": paper.categories,
        "score": score,
        "paper_id": paper.entry_id.split("/")[-1],  # Extract paper ID from entry_id
    }


# Common English stopwords to filter out from keyword extraction
STOPWORDS = {
    "about",
    "above",
    "after",
    "again",
    "against",
    "all",
    "and",
    "any",
    "are",
    "aren't",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "cannot",
    "could",
    "couldn't",
    "did",
    "didn't",
    "does",
    "doesn't",
    "doing",
    "don't",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn't",
    "has",
    "hasn't",
    "have",
    "haven't",
    "having",
    "here",
    "how",
    "into",
    "itself",
    "just",
    "more",
    "most",
    "mustn't",
    "not",
    "off",
    "once",
    "only",
    "other",
    "ought",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "same",
    "shan't",
    "she",
    "should",
    "shouldn't",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "thus",
    "too",
    "under",
    "until",
    "very",
    "was",
    "wasn't",
    "were",
    "weren't",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "with",
    "won't",
    "would",
    "wouldn't",
    "your",
    "yours",
    "yourself",
    "yourselves",
}
