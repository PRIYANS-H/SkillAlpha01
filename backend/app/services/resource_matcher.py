import time
import re
import urllib.parse
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings

# In-memory TTL cache with 7-day expiration
_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 7 * 24 * 3600 # 7 days

def get_from_cache(cache_key: str) -> Optional[Any]:
    entry = _CACHE.get(cache_key)
    if not entry:
        return None
    if time.time() > entry["expires_at"]:
        _CACHE.pop(cache_key, None)
        return None
    return entry["value"]

def set_in_cache(cache_key: str, value: Any, ttl: int = CACHE_TTL_SECONDS):
    _CACHE[cache_key] = {
        "value": value,
        "expires_at": time.time() + ttl
    }

def clear_cache():
    """Utility for testing cache invalidation."""
    _CACHE.clear()

KNOWN_DOMAINS = {
    "fastapi": "fastapi.tiangolo.com",
    "scikit-learn": "scikit-learn.org",
    "pytorch": "pytorch.org",
    "react": "react.dev",
    "python": "docs.python.org",
    "postgresql": "postgresql.org",
    "docker": "docs.docker.com",
    "pandas": "pandas.pydata.org",
    "numpy": "numpy.org",
    "leetcode": "leetcode.com",
    "hackerrank": "hackerrank.com",
    "kaggle": "kaggle.com",
    "github": "github.com",
    "mdn": "developer.mozilla.org"
}

def extract_domain(url: str, provider: str) -> str:
    if url:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc.lower()
        if netloc and not any(g in netloc for g in ["google.com", "bing.com"]):
            return netloc
    
    prov_lower = (provider or "").lower()
    for key, domain in KNOWN_DOMAINS.items():
        if key in prov_lower:
            return domain
    return "docs.python.org"

def search_youtube_videos(query: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    key = api_key if api_key is not None else settings.YOUTUBE_DATA_API_KEY
    if not key:
        return []

    cache_key = f"yt_{query.strip().lower()}"
    cached = get_from_cache(cache_key)
    if cached is not None:
        return cached

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 3,
        "key": key
    }

    try:
        with httpx.Client(timeout=6.0) as client:
            resp = client.get(url, params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
            items = data.get("items", [])
            videos = []
            for item in items:
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})
                if not video_id:
                    continue
                thumbs = snippet.get("thumbnails", {})
                thumb_url = (
                    thumbs.get("medium", {}).get("url") or
                    thumbs.get("high", {}).get("url") or
                    thumbs.get("default", {}).get("url") or
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                )
                videos.append({
                    "video_id": video_id,
                    "title": snippet.get("title", "YouTube Video"),
                    "thumbnail_url": thumb_url,
                    "channel_title": snippet.get("channelTitle", "YouTube Creator"),
                    "duration": "15 min"
                })

            set_in_cache(cache_key, videos)
            return videos
    except Exception:
        return []

def resolve_resource_matches(
    resource_id: str,
    title: str,
    resource_type: str,
    provider: str,
    url: str,
    description: Optional[str] = None,
    search_hint: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolves stored resource metadata into real playable/readable content:
    - youtube_channel / VIDEO -> YouTube Data API v3 top 3 matches with 7-day TTL cache
    - docs / practice_site -> Scoped Google search URL and direct deep-link
    - book -> Structured chapter/topic guidance without illegal download/purchase links
    - fallback -> Raw resource representation
    """
    clean_type = (resource_type or "").upper()
    provider_lower = (provider or "").lower()
    hint = search_hint.strip() if search_hint and search_hint.strip() else title

    # 1. YouTube Channel / Video
    is_youtube = (
        clean_type in ["VIDEO", "YOUTUBE_CHANNEL", "YOUTUBE"] or
        "youtube" in provider_lower or
        "youtube.com" in (url or "") or
        "youtu.be" in (url or "")
    )

    if is_youtube:
        search_query = f"{provider} {hint}" if "youtube" not in provider_lower and provider else hint
        videos = search_youtube_videos(search_query, api_key=api_key)
        if videos:
            return {
                "resource_id": resource_id,
                "type": "youtube",
                "title": title,
                "provider": provider or "YouTube",
                "matches": videos,
                "fallback": False
            }
        # Fallback if external API returned no matches or failed
        return {
            "resource_id": resource_id,
            "type": "fallback",
            "title": title,
            "provider": provider,
            "url": url,
            "resource_type": resource_type,
            "matches": [],
            "fallback": True
        }

    # 2. Docs or Practice Site
    is_docs_or_practice = (
        clean_type in ["DOCUMENTATION", "DOCS", "PRACTICE", "PRACTICE_SITE", "TUTORIAL", "ARTICLE", "GITHUB"] or
        any(k in provider_lower for k in ["docs", "tutorial", "practice", "code", "guide"])
    )

    if is_docs_or_practice:
        domain = extract_domain(url, provider)
        scoped_query = f"site:{domain} {hint}"
        search_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(scoped_query)}"
        sub_type = "practice" if clean_type in ["PRACTICE", "PRACTICE_SITE"] else "docs"
        return {
            "resource_id": resource_id,
            "type": sub_type,
            "title": title,
            "provider": provider,
            "search_url": search_url,
            "deep_link": url,
            "fallback": False
        }

    # 3. Book
    if clean_type in ["BOOK", "TEXTBOOK"]:
        # Extract topics or chapters from title & description
        topics = []
        if description:
            clean_desc = re.sub(r'[^\w\s,]', '', description)
            words = [w.strip() for w in clean_desc.split(',') if len(w.strip()) > 3]
            topics = words[:4]
        if not topics:
            topics = ["Core Concepts", "Implementation Architecture", "Case Studies", "Review Questions"]

        return {
            "resource_id": resource_id,
            "type": "book",
            "title": title,
            "author": provider or "Technical Author",
            "topics": topics,
            "description": description or f"Structured reference manual covering {title}.",
            "fallback": False
        }

    # 4. Fallback for any other type
    return {
        "resource_id": resource_id,
        "type": "fallback",
        "title": title,
        "provider": provider,
        "url": url,
        "resource_type": resource_type,
        "matches": [],
        "fallback": True
    }
