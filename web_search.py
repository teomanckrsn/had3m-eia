"""Web Arama — İnternetten bilgi çekme (DuckDuckGo + opsiyonel Tavily)."""

import os
import json

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


def _get_tavily_key() -> str:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("tavily_api_key", "")
    return ""


def search_duckduckgo(query: str, max_results: int = 5) -> list[dict]:
    """DuckDuckGo ile arama yap. API key gerekmez, ücretsiz."""
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                    "source": "DuckDuckGo",
                })
        return results
    except Exception as e:
        return [{"title": "Hata", "url": "", "snippet": str(e), "source": "DuckDuckGo"}]


def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Tavily ile arama yap. AI için optimize, özetli sonuçlar."""
    api_key = _get_tavily_key()
    if not api_key:
        return [{"title": "Tavily API key yok",
                 "url": "", "snippet": "Ayarlardan Tavily API key girin.",
                 "source": "Tavily"}]
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
                "source": "Tavily",
            })
        return results
    except Exception as e:
        return [{"title": "Hata", "url": "", "snippet": str(e), "source": "Tavily"}]


def search(query: str, max_results: int = 5) -> list[dict]:
    """Otomatik: Tavily key varsa Tavily, yoksa DuckDuckGo."""
    if _get_tavily_key():
        return search_tavily(query, max_results)
    return search_duckduckgo(query, max_results)


def search_and_summarize(query: str, max_results: int = 5) -> str:
    """Arama yap ve sonuçları düz metin olarak formatla."""
    results = search(query, max_results)
    if not results:
        return "Sonuç bulunamadı."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}")
        if r['snippet']:
            lines.append(f"   {r['snippet'][:200]}")
        if r['url']:
            lines.append(f"   {r['url']}")
        lines.append("")

    return "\n".join(lines)
