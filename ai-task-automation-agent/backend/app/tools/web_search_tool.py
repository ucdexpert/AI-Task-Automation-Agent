import logging
import json
import urllib.request
import urllib.parse
from typing import Any, Dict, List
from googlesearch import search
from app.tools.base import BaseTool
from app.services.http_client import http_client

logger = logging.getLogger(__name__)

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the internet for real-time information, news, or specific topics."

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "query": {
                "type": "string",
                "description": "The search query to look up on the web."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default 5).",
                "default": 5
            }
        }

    def get_required_parameters(self) -> list:
        return ["query"]

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Search with multiple fallbacks: Google -> Wikipedia -> DuckDuckGo Lite
        """
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        
        if not query:
            return {"success": False, "message": "Search tool requires a 'query' parameter."}
            
        results = []
        logger.info(f"🔍 Searching for: {query}")
        
        # 1. Try Google Search
        try:
            search_results = search(query, num_results=max_results, advanced=True)
            for r in search_results:
                results.append({
                    "title": r.title,
                    "link": r.url,
                    "snippet": r.description
                })
            if results: logger.info("✅ Results found via Google")
        except Exception as e:
            logger.warning(f"Google search failed: {e}")

        # 2. Try DuckDuckGo Lite Fallback (Highly Reliable for Bots)
        if not results:
            try:
                encoded_query = urllib.parse.quote(query)
                # DDG Lite is very bot-friendly
                url = f"https://duckduckgo.com/html/?q={encoded_query}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                
                with urllib.request.urlopen(req) as response:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.read(), 'html.parser')
                    # DDG Lite uses 'result__a' for links
                    for i, link in enumerate(soup.find_all('a', class_='result__a')[:max_results]):
                        snippet = soup.find_all('a', class_='result__snippet')[i].text if i < len(soup.find_all('a', class_='result__snippet')) else ""
                        results.append({
                            "title": link.text,
                            "link": link.get('href'),
                            "snippet": snippet
                        })
                if results: logger.info("✅ Results found via DuckDuckGo Lite")
            except Exception as e:
                logger.warning(f"DuckDuckGo Lite fallback failed: {e}")

        # 3. Last Resort: Wikipedia API
        if not results:
            try:
                wiki_query = urllib.parse.quote(query)
                wiki_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={wiki_query}&limit={max_results}&namespace=0&format=json"
                req = urllib.request.Request(wiki_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
                    for i in range(len(data[1])):
                        results.append({
                            "title": data[1][i],
                            "link": data[3][i],
                            "snippet": data[2][i]
                        })
                if results: logger.info("✅ Results found via Wikipedia API")
            except Exception as e:
                logger.error(f"Wikipedia fallback failed: {e}")

        if not results:
            return {
                "success": False, 
                "message": f"All search methods failed for '{query}'. Please try a different query."
            }
            
        return {
            "success": True,
            "results": results,
            "query": query
        }
