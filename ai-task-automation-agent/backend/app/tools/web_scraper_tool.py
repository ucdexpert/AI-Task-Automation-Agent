from app.tools.base import BaseTool
from typing import Any, Dict
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import ipaddress
import socket
import logging
from app.services.http_client import http_client

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = "Scrape content from websites. Extract text, links, or specific information from a URL."
    
    def _is_safe_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ["http", "https"]: return False
            hostname = parsed.hostname
            if not hostname: return False
            if hostname.lower() in ["localhost", "127.0.0.1", "::1", "0.0.0.0"]: return False
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)
            return not (ip_obj.is_loopback or ip_obj.is_private or ip_obj.is_link_local)
        except Exception: return False

    async def execute(self, url: str, extract_type: str = "text", target_selector: str = None, **kwargs) -> Dict[str, Any]:
        if not self._is_safe_url(url):
            return {"success": False, "message": "Security error: URL is blocked."}

        try:
            client = await http_client.get_client()
            
            # Advanced headers to mimic a real modern browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
                'Referer': 'https://www.google.com/'
            }
            
            response = await client.get(
                url, 
                headers=headers, 
                follow_redirects=True, 
                timeout=30.0
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]): script.decompose()
            
            if extract_type == "links":
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                return {"success": True, "links": links[:50], "total": len(links)}
            
            content = soup.get_text()
            content = re.sub(r'\s+', ' ', content).strip()
            return {"success": True, "url": url, "content": content[:2000]}
                
        except Exception as e:
            return {"success": False, "message": f"Scrape failed: {str(e)}"}
