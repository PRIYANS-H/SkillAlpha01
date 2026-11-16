import time
import re
import json
import hashlib
import logging
import datetime
import urllib.parse
from typing import Dict, Any, Optional, List
import httpx
from app.config import settings

# Two-tier TTL cache (7 days): an in-process dict in front of the resource_match_cache table,
# so YouTube API quota is not spent again after a restart or on another worker.
_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 7 * 24 * 3600 # 7 days
logger = logging.getLogger("skillalpha.resource_matcher")


def _db_key(cache_key: str) -> str:
    if len(cache_key) <= 200:
        return cache_key
    return "sha256_" + hashlib.sha256(cache_key.encode("utf-8")).hexdigest()


def _utcnow_naive() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def get_from_cache(cache_key: str) -> Optional[Any]:
    entry = _CACHE.get(cache_key)
    if entry:
        if time.time() <= entry["expires_at"]:
            return entry["value"]
        _CACHE.pop(cache_key, None)

    try:
        from app.models.db import SessionLocal
        from app.models.models import ResourceMatchCache
        db = SessionLocal()
        try:
            row = db.query(ResourceMatchCache).filter(ResourceMatchCache.cache_key == _db_key(cache_key)).first()
            if row is None:
                return None
            if row.expires_at <= _utcnow_naive():
                db.delete(row)
                db.commit()
                return None
            value = json.loads(row.payload_json)
            remaining = (row.expires_at - _utcnow_naive()).total_seconds()
            _CACHE[cache_key] = {"value": value, "expires_at": time.time() + remaining}
            return value
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Resource cache read failed: {e}")
        return None


def set_in_cache(cache_key: str, value: Any, ttl: int = CACHE_TTL_SECONDS):
    _CACHE[cache_key] = {
        "value": value,
        "expires_at": time.time() + ttl
    }
    try:
        from app.models.db import SessionLocal
        from app.models.models import ResourceMatchCache
        db = SessionLocal()
        try:
            db.merge(ResourceMatchCache(
                cache_key=_db_key(cache_key),
                payload_json=json.dumps(value),
                expires_at=_utcnow_naive() + datetime.timedelta(seconds=ttl),
            ))
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Resource cache write failed: {e}")


def clear_cache():
    """Clears both cache tiers (used by tests)."""
    _CACHE.clear()
    try:
        from app.models.db import SessionLocal
        from app.models.models import ResourceMatchCache
        db = SessionLocal()
        try:
            db.query(ResourceMatchCache).delete()
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Resource cache clear failed: {e}")

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

def extract_youtube_video_id(url: Optional[str]) -> Optional[str]:
    """Video id from a watch or youtu.be URL; None for playlists, channels and non-YouTube URLs."""
    if not url:
        return None
    try:
        parsed = urllib.parse.urlparse(url)
    except ValueError:
        return None
    host = (parsed.netloc or "").lower()
    video_id = None
    if host.endswith("youtu.be"):
        video_id = parsed.path.strip("/")
    elif "youtube.com" in host and parsed.path == "/watch":
        video_id = (urllib.parse.parse_qs(parsed.query).get("v") or [None])[0]
    return video_id if video_id and re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id) else None


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
        # A curated resource that points at one specific video plays exactly that video:
        # no search, no API quota, and the learner sees what the plan promised.
        direct_id = extract_youtube_video_id(url)
        if direct_id:
            return {
                "resource_id": resource_id,
                "type": "youtube",
                "title": title,
                "provider": provider or "YouTube",
                "matches": [{
                    "video_id": direct_id,
                    "title": title,
                    "thumbnail_url": f"https://img.youtube.com/vi/{direct_id}/hqdefault.jpg",
                    "channel_title": provider or "YouTube",
                    "duration": ""
                }],
                "fallback": False
            }
        if "list=" in (url or ""):
            # Playlists open on YouTube rather than being replaced by a search result
            return {
                "resource_id": resource_id,
                "type": "fallback",
                "title": title,
                "provider": provider,
                "url": url,
                "resource_type": resource_type,
                "matches": [],
                "fallback": False
            }
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
