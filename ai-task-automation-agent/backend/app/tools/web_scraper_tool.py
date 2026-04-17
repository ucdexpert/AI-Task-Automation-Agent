from app.tools.base import BaseTool
from typing import Any, Dict
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import ipaddress
import socket
import logging
from app.services.http_client import http_client
import json

logger = logging.getLogger(__name__)

class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = "Scrape content from websites. Extract text, links, or specific information from a URL. Handles deep data extraction from dynamic sites."
    
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

    async def execute(self, url: str, extract_type: str = "text", target_selector: str = None, **kwargs) -> Dict[ Any, Any]:
        """
        Deep Scraper: Extracts visible text AND hidden JSON-LD/Metadata for dynamic content support.
        """
        if not self._is_safe_url(url):
            return {"success": False, "message": "Security error: URL is blocked."}

        try:
            client = await http_client.get_client()
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'https://www.google.com/',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            response = await client.get(url, headers=headers, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # --- DEEP EXTRACTION LOGIC ---
            # 1. Extract JSON-LD (Often contains full content even if scroll is needed)
            structured_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    structured_data.append(json.loads(script.string))
                except: pass

            # 2. Handle Lazy Loading (Replace data-src with src)
            for img in soup.find_all('img'):
                if img.get('data-src'):
                    img['src'] = img.get('data-src')

            if extract_type == "links":
                links = []
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if href.startswith('http'):
                        links.append({"text": a.text.strip(), "url": href})
                return {"success": True, "links": links[:50], "url": url}
            
            # Clean unwanted tags
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()

            # Target specific selector or fallback to main content
            content_node = soup.select_one(target_selector) if target_selector else (
                soup.select_one('main') or soup.select_one('article') or soup.select_one('#content') or soup.body
            )
            
            text = content_node.get_text(separator='\n', strip=True) if content_node else soup.get_text(separator='\n', strip=True)
            
            # Truncate to avoid LLM token limits but keep enough info
            clean_text = re.sub(r'\n+', '\n', text)[:12000]
            
            # Combine structured data with main text for richness
            final_report = f"SOURCE: {url}\n\n"
            if structured_data:
                final_report += "METADATA SUMMARY:\n"
                for item in structured_data:
                    if isinstance(item, dict):
                        final_report += f"- {item.get('headline', item.get('name', ''))}: {item.get('description', '')}\n"
                final_report += "\n---\n\n"
            
            final_report += clean_text

            return {
                "success": True,
                "content": final_report,
                "url": url,
                "data_richness": "high" if structured_data else "standard"
            }
            
        except Exception as e:
            logger.error(f"Scrape failed for {url}: {e}")
            return {"success": False, "message": f"Scrape failed: {str(e)}"}
