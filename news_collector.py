import asyncio
import feedparser

CYBER_RSS_FEEDS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
]

MADRID_RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Madrid&hl=es&gl=ES&ceid=ES:es",
]


def _parse_feed(url: str, limit: int = 5) -> list[dict]:
    feed = feedparser.parse(url)
    return [
        {
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", "")[:400],
        }
        for entry in feed.entries[:limit]
    ]


async def fetch_feed(url: str, limit: int = 5) -> list[dict]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _parse_feed, url, limit)


async def get_cybersecurity_news() -> list[dict]:
    results = await asyncio.gather(
        *[fetch_feed(url) for url in CYBER_RSS_FEEDS],
        return_exceptions=True,
    )
    items = []
    for r in results:
        if not isinstance(r, Exception):
            items.extend(r)
    return items


async def get_madrid_news() -> list[dict]:
    results = await asyncio.gather(
        *[fetch_feed(url) for url in MADRID_RSS_FEEDS],
        return_exceptions=True,
    )
    items = []
    for r in results:
        if not isinstance(r, Exception):
            items.extend(r)
    return items


async def get_news_by_topic(topic: str) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={topic}&hl=es&gl=ES&ceid=ES:es"
    return await fetch_feed(url, limit=10)
