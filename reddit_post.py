import praw
import os
from datetime import datetime
from time import time

# Cache untuk posts
_reddit_posts_cache = {}
_last_fetch_time = {}
CACHE_DURATION = 1800  # 30 minutes in seconds

def get_reddit_posts(subreddit_name="indonesia", category="hot", limit=10):
    """
    Mengambil postingan Reddit dari subreddit tertentu.
    
    Parameters:
    -----------
    subreddit_name : str
        Nama subreddit (default: "indonesia")
    category : str
        Kategori postingan ("hot", "new", "top", "rising")
    limit : int
        Jumlah postingan yang akan diambil
        
    Returns:
    --------
    list
        List berisi postingan Reddit
    """
    # Debug kredensial Reddit
    print(f"Reddit Credentials Check:")
    print(f"CLIENT_ID: {'Set' if os.getenv('REDDIT_CLIENT_ID') else 'Not Set'}")
    print(f"CLIENT_SECRET: {'Set' if os.getenv('REDDIT_SECRET') else 'Not Set'}")
    print(f"USERNAME: {'Set' if os.getenv('REDDIT_USERNAME') else 'Not Set'}")
    # Mengecek cache
    cache_key = f"{subreddit_name}_{category}"
    current_time = time()
    
    # Jika data ada di cache dan masih fresh, gunakan cache
    if (
        cache_key in _reddit_posts_cache
        and cache_key in _last_fetch_time
        and current_time - _last_fetch_time[cache_key] < CACHE_DURATION
    ):
        print(f"Using cached Reddit posts for {cache_key}")
        return _reddit_posts_cache[cache_key]
    
    print(f"Fetching fresh Reddit posts for {cache_key}")
    
    try:
        # Menggunakan Reddit API dengan read-only public access
        try:
            # Coba dengan kredensial dari .env jika tersedia
            if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_SECRET"):
                reddit = praw.Reddit(
                    client_id=os.getenv("REDDIT_CLIENT_ID"),
                    client_secret=os.getenv("REDDIT_SECRET"),
                    user_agent=f"script:trend_radar:v1.0 (by u/{os.getenv('REDDIT_USERNAME') or 'anonymous'})"
                )
            else:
                # Gunakan default public access
                reddit = praw.Reddit(
                    client_id="V0MHCutyw6_MaA",  # Public client ID for read-only
                    client_secret="",
                    user_agent="script:trend_radar:v1.0 (by anonymous)"
                )
            
            print("Reddit connection established successfully")
        except Exception as e:
            print(f"Error connecting to Reddit API: {e}")
            raise
        
        # Pilih subreddit
        subreddit = reddit.subreddit(subreddit_name)
        
        # Ambil postingan berdasarkan kategori
        if category == "hot":
            posts = subreddit.hot(limit=limit)
        elif category == "new":
            posts = subreddit.new(limit=limit)
        elif category == "top":
            posts = subreddit.top(limit=limit)
        elif category == "rising":
            posts = subreddit.rising(limit=limit)
        else:
            raise ValueError("Kategori tidak valid. Gunakan 'hot', 'new', 'top', atau 'rising'")
        
        # Simpan data postingan
        post_data = []
        for post in posts:
            # Tangani kemungkinan author tidak ada
            author_name = 'Deleted'
            try:
                if post.author:
                    author_name = post.author.name
            except:
                pass
                
            post_data.append({
                'title': post.title,
                'author': author_name,
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'id': post.id,
                'url': post.url,
                'permalink': 'https://www.reddit.com' + post.permalink,
                'num_comments': post.num_comments,
                'created_utc': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                'time_ago': get_time_ago(datetime.fromtimestamp(post.created_utc)),
                'is_self': post.is_self,
                'selftext': post.selftext if post.is_self else '',
                'subreddit': post.subreddit.display_name,
                'thumbnail': post.thumbnail if hasattr(post, 'thumbnail') and post.thumbnail.startswith('http') else ''
            })
        
        # Simpan ke cache
        _reddit_posts_cache[cache_key] = post_data
        _last_fetch_time[cache_key] = current_time
        
        return post_data
    except Exception as e:
        print(f"Error fetching Reddit posts: {e}")
        # Jika terjadi error, kembalikan cache lama jika ada
        if cache_key in _reddit_posts_cache:
            return _reddit_posts_cache[cache_key]
        return []

def get_time_ago(timestamp):
    """
    Menghitung waktu "time ago" dari timestamp
    
    Parameters:
    -----------
    timestamp : datetime
        Timestamp yang akan dihitung
        
    Returns:
    --------
    str
        String format "X hours/days ago"
    """
    now = datetime.now()
    delta = now - timestamp
    
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
        hours = delta.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
        minutes = delta.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{delta.seconds} second{'s' if delta.seconds != 1 else ''} ago"

def format_reddit_post(post):
    """
    Format post Reddit untuk ditampilkan di aplikasi
    
    Parameters:
    -----------
    post : dict
        Data post Reddit
        
    Returns:
    --------
    dict
        Post yang sudah diformat
    """
    # Ekstrak domain dari URL
    domain = ''
    if post.get('url'):
        from urllib.parse import urlparse
        try:
            parsed_url = urlparse(post['url'])
            domain = parsed_url.netloc.replace('www.', '')
        except:
            pass
    
    # Potong selftext jika terlalu panjang
    excerpt = ''
    if post.get('selftext'):
        if len(post['selftext']) > 200:
            excerpt = post['selftext'][:197] + '...'
        else:
            excerpt = post['selftext']
    
    return {
        'title': post['title'],
        'author': post['author'],
        'score': post['score'],
        'upvote_ratio': post['upvote_ratio'],
        'permalink': post['permalink'],
        'num_comments': post['num_comments'],
        'created': post['created_utc'],
        'time_ago': post['time_ago'],
        'is_self': post['is_self'],
        'excerpt': excerpt,
        'domain': domain,
        'thumbnail': post['thumbnail'],
        'url': post['url']
    }

def get_reddit_indonesia_posts(category="hot", limit=10):
    """
    Mengambil postingan dari r/indonesia
    
    Parameters:
    -----------
    category : str
        Kategori postingan ("hot", "new", "top", "rising")
    limit : int
        Jumlah postingan yang akan diambil
        
    Returns:
    --------
    list
        List berisi postingan Reddit yang sudah diformat
    """
    posts = get_reddit_posts("indonesia", category, limit)
    return [format_reddit_post(post) for post in posts]
