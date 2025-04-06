import feedparser
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import re
from bs4 import BeautifulSoup
import requests
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Try to download NLTK data, handle case where it might already exist
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

# Global cache
_hn_stories_cache = []
_last_fetch_time = 0
CACHE_DURATION = 1800  # 30 minutes in seconds

def fetch_hn_stories(limit=30):
    """
    Fetch top stories from Hacker News RSS feed.
    Uses a simple time-based cache to avoid redundant API calls.
    
    Args:
        limit (int): Maximum number of stories to fetch
        
    Returns:
        list: List of story objects
    """
    global _hn_stories_cache, _last_fetch_time
    current_time = time.time()
    
    # Return cached stories if they're less than 30 minutes old
    if _hn_stories_cache and current_time - _last_fetch_time < CACHE_DURATION:
        print("Using cached Hacker News stories")
        return _hn_stories_cache
    
    try:
        print("Fetching Hacker News stories...")
        feed = feedparser.parse("https://hnrss.org/frontpage")
        
        stories = []
        for entry in feed.entries[:limit]:
            # Extract points and comments count from description
            description = BeautifulSoup(entry.description, 'html.parser')
            points_text = [p.text for p in description.find_all('p') if 'Points:' in p.text]
            comments_text = [p.text for p in description.find_all('p') if 'Comments:' in p.text]
            
            # Safely extract points with error handling
            points = 0
            if points_text:
                try:
                    # Cleanup text and extract the number part
                    clean_points = re.search(r'\d+', points_text[0])
                    if clean_points:
                        points = int(clean_points.group())
                except ValueError:
                    # If conversion fails, use default
                    print(f"Could not parse points from: {points_text[0]}")
                    
            # Safely extract comments count with error handling
            comments = 0
            if comments_text:
                try:
                    # Cleanup text and extract the number part
                    clean_comments = re.search(r'\d+', comments_text[0])
                    if clean_comments:
                        comments = int(clean_comments.group())
                except ValueError:
                    # If conversion fails, use default
                    print(f"Could not parse comments from: {comments_text[0]}")
            
            # Get article URL (not HN discussion URL)
            article_url_tag = description.find('a')
            article_url = article_url_tag['href'] if article_url_tag else entry.link
            
            story = {
                'title': entry.title,
                'url': article_url,
                'hn_url': entry.link,
                'discussion_url': entry.comments if hasattr(entry, 'comments') else None,
                'points': points,
                'comments_count': comments,
                'published': entry.published_parsed,
                'author': entry.author if hasattr(entry, 'author') else None,
            }
            stories.append(story)
        
        # Update cache
        _hn_stories_cache = stories
        _last_fetch_time = current_time
        
        print(f"Retrieved {len(stories)} stories from Hacker News")
        return stories
    except Exception as e:
        print(f"Error fetching Hacker News stories: {e}")
        # Return cached stories if available, otherwise empty list
        return _hn_stories_cache if _hn_stories_cache else []

def get_trending_hn_keywords(stories, min_frequency=2):
    """
    Extract trending keywords from Hacker News story titles.
    
    Args:
        stories (list): List of story objects
        min_frequency (int): Minimum frequency for a keyword to be considered trending
        
    Returns:
        list: List of (keyword, frequency) tuples
    """
    try:
        # Get English stopwords
        stop_words = set(stopwords.words('english'))
        
        # Add custom stopwords relevant to tech news
        custom_stopwords = {'new', 'using', 'use', 'used', 'how', 'what', 'why', 'when',
                           'make', 'made', 'making', 'build', 'built', 'building',
                           'create', 'created', 'creating', 'best', 'top', 'first', 'latest'}
        stop_words.update(custom_stopwords)
        
        # Combine all titles
        all_titles = ' '.join([story['title'] for story in stories])
        
        # Tokenize
        tokens = word_tokenize(all_titles.lower())
        
        # Filter out stopwords, punctuation, and short words
        filtered_tokens = [token for token in tokens 
                          if token not in stop_words 
                          and token.isalnum() 
                          and len(token) > 2]
        
        # Count frequencies
        word_freq = Counter(filtered_tokens)
        
        # Filter by minimum frequency and sort by frequency
        trending_keywords = [(word, freq) for word, freq in word_freq.items() 
                            if freq >= min_frequency]
        trending_keywords.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to dictionary for template compatibility
        trending_dict = {word: freq for word, freq in trending_keywords[:20]}
        
        return trending_dict  # Return top 20 trending keywords as dictionary
    except Exception as e:
        print(f"Error extracting trending keywords: {e}")
        return []

def identify_trending_domains(stories):
    """
    Identify trending domains from Hacker News stories.
    
    Args:
        stories (list): List of story objects
        
    Returns:
        list: List of (domain, frequency) tuples
    """
    try:
        domain_counter = Counter()
        
        for story in stories:
            if 'url' in story and story['url']:
                # Extract domain from URL
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', story['url'])
                if domain_match:
                    domain = domain_match.group(1)
                    domain_counter[domain] += 1
        
        # Get domains with counts and sort by frequency
        domain_counts = [(domain, count) for domain, count in domain_counter.items()]
        domain_counts.sort(key=lambda x: x[1], reverse=True)
        
        # Convert to dictionary for template compatibility
        domains_dict = {domain: count for domain, count in domain_counts[:10]}
        
        return domains_dict  # Return top 10 domains as dictionary
    except Exception as e:
        print(f"Error identifying trending domains: {e}")
        return []

def get_hot_hn_stories(max_results=10):
    """
    Get hot stories from Hacker News based on a scoring algorithm.
    
    Args:
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of hot stories with scores
    """
    stories = fetch_hn_stories(limit=30)
    
    if not stories:
        return []
    
    # Score stories based on points, comments, and recency
    current_time = time.mktime(datetime.now().timetuple())
    scored_stories = []
    
    for story in stories:
        # Skip stories with no points
        if story['points'] == 0:
            continue
            
        # Calculate time difference in hours
        story_time = time.mktime(story['published'])
        time_diff_hours = max((current_time - story_time) / 3600, 1)  # in hours, min 1
        
        # Calculate hot score - similar to HN's own algorithm but simplified
        # Gravity factor reduces score as time passes
        gravity = 1.8  # gravity factor
        score = (story['points'] + story['comments_count']) / (time_diff_hours ** gravity)
        
        # Normalize score to 0-100 range for consistency with other metrics
        # We'll use a dynamic scaling approach here
        scored_stories.append((story, score))
    
    # Sort by score
    sorted_stories = sorted(scored_stories, key=lambda x: x[1], reverse=True)
    
    # Normalize top scores to 0-100 range if we have stories
    if sorted_stories:
        max_score = sorted_stories[0][1]  # Highest score
        normalized_stories = []
        
        for story, score in sorted_stories:
            normalized_score = min(100, (score / max_score) * 100)
            normalized_stories.append((story, normalized_score))
            
        return normalized_stories[:max_results]
    
    return []

def get_rising_hn_stories(max_results=10):
    """
    Get rising stories from Hacker News that are gaining comments quickly.
    
    Args:
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of rising stories with scores
    """
    stories = fetch_hn_stories(limit=30)
    
    if not stories:
        return []
    
    # Score stories based on comments-to-points ratio and recency
    scored_stories = []
    
    for story in stories:
        # Skip stories with very few points
        if story['points'] < 5:
            continue
            
        # Calculate rising score based on comments/points ratio and recency
        # Rising stories have high engagement relative to their points
        comment_ratio = story['comments_count'] / max(story['points'], 1)
        
        # Prefer newer stories with high comment ratios
        current_time = time.mktime(datetime.now().timetuple())
        story_time = time.mktime(story['published'])
        hours_old = (current_time - story_time) / 3600
        
        # Rising score favors newer stories with high comment engagement
        # Cap ratio at 2.0 to prevent outliers
        capped_ratio = min(comment_ratio, 2.0)
        rising_score = (capped_ratio * 50) * (24 / (hours_old + 6))
        
        scored_stories.append((story, rising_score))
    
    # Sort by score
    sorted_stories = sorted(scored_stories, key=lambda x: x[1], reverse=True)
    
    # Normalize scores to 0-100
    if sorted_stories:
        max_score = max(1, sorted_stories[0][1])  # Highest score, min 1
        normalized_stories = []
        
        for story, score in sorted_stories:
            normalized_score = min(100, (score / max_score) * 100)
            normalized_stories.append((story, normalized_score))
            
        return normalized_stories[:max_results]
    
    return []

def get_new_hn_stories(max_results=10):
    """
    Get newest stories from Hacker News.
    
    Args:
        max_results (int): Maximum number of results to return
        
    Returns:
        list: List of new stories with recency scores
    """
    stories = fetch_hn_stories(limit=30)
    
    if not stories:
        return []
    
    # Sort by publication date
    sorted_stories = sorted(stories, key=lambda x: time.mktime(x['published']), reverse=True)
    
    # Calculate recency score (0-100)
    current_time = time.mktime(datetime.now().timetuple())
    stories_with_scores = []
    
    for story in sorted_stories[:max_results]:
        story_time = time.mktime(story['published'])
        hours_old = (current_time - story_time) / 3600
        
        # Newer stories get higher scores
        # Scale from 100 (now) to 0 (24+ hours old)
        recency_score = max(0, 100 - (hours_old * 4))
        
        stories_with_scores.append((story, recency_score))
    
    return stories_with_scores[:max_results]

def get_hn_insights():
    """
    Get insights from Hacker News data.
    
    Returns:
        dict: Dictionary with various insights
    """
    stories = fetch_hn_stories(limit=100)
    
    if not stories:
        return {}
        
    # Get trending keywords
    trending_keywords = get_trending_hn_keywords(stories)
    
    # Get trending domains
    trending_domains = identify_trending_domains(stories)
    
    # Calculate average points and comments
    total_points = sum(story['points'] for story in stories)
    total_comments = sum(story['comments_count'] for story in stories)
    avg_points = round(total_points / len(stories), 1)
    avg_comments = round(total_comments / len(stories), 1)
    
    # Find stories with highest points-to-comments ratio (controversial)
    stories_with_ratio = []
    for story in stories:
        if story['comments_count'] >= 5:  # Only consider stories with some discussion
            ratio = story['points'] / max(story['comments_count'], 1)
            stories_with_ratio.append((story, ratio))
    
    # Sort by ratio (descending)
    most_agreed = sorted(stories_with_ratio, key=lambda x: x[1], reverse=True)[:5]
    most_controversial = sorted(stories_with_ratio, key=lambda x: x[1])[:5]
    
    # Format datetime for display
    current_time = datetime.now()
    
    # Compile insights
    insights = {
        'trending_keywords': trending_keywords,
        'trending_domains': trending_domains,
        'avg_points': avg_points,
        'avg_comments': avg_comments,
        'most_agreed': [(s['title'], round(r, 1)) for s, r in most_agreed],
        'most_controversial': [(s['title'], round(r, 1)) for s, r in most_controversial],
        'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    return insights

def format_story(story, score):
    """
    Format a Hacker News story for display.
    
    Args:
        story (dict): Story object
        score (float): Calculated score
        
    Returns:
        dict: Formatted story
    """
    # Convert time struct to datetime for easier formatting
    published_time = datetime(*story['published'][:6])
    
    # Extract domain from URL if available
    domain = ''
    if story.get('url'):
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', story['url'])
        if domain_match:
            domain = domain_match.group(1)
    
    # Format time ago string
    now = datetime.now()
    delta = now - published_time
    if delta.days > 0:
        time_ago = f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        time_ago = f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"
    
    # Extract discussion URL (for comments)
    discussion_url = ''
    if story.get('discussion_url'):
        discussion_url = story['discussion_url']
    elif story.get('comments'):
        discussion_url = story['comments']
    elif story.get('guid') and 'item?id=' in story.get('guid', ''):
        discussion_url = story['guid']
    elif story.get('hn_url'):
        discussion_url = story['hn_url']
    else:
        # Jika tidak ada satupun, buat URL berdasarkan item ID jika ada
        item_id = story.get('id')
        if item_id:
            discussion_url = f'https://news.ycombinator.com/item?id={item_id}'
    
    return {
        'title': story['title'],
        'url': story['url'],
        'hn_url': story['hn_url'],
        'points': story['points'],
        'num_comments': story.get('comments_count', 0),  # Changed key for template compatibility
        'published': published_time.strftime('%Y-%m-%d %H:%M:%S'),
        'by': story['author'] if story.get('author') else 'Anonymous',  # Handle empty author
        'score': round(score, 1),
        'time_ago': time_ago,
        'domain': domain,
        'discussion_url': discussion_url  # URL ke halaman komentar/diskusi
    }
