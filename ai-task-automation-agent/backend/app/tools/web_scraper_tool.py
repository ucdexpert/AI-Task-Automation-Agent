from app.tools.base import BaseTool
from typing import Any, Dict
import requests
from bs4 import BeautifulSoup
import re

class WebScraperTool(BaseTool):
    name = "web_scraper"
    description = "Scrape content from websites. Extract text, links, or specific information from a URL."
    
    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "url": {
                "type": "string",
                "description": "URL to scrape content from"
            },
            "extract_type": {
                "type": "string",
                "description": "Type of extraction: 'text' for all text, 'links' for all links, 'summary' for page summary",
                "enum": ["text", "links", "summary"]
            },
            "target_selector": {
                "type": "string",
                "description": "CSS selector for specific elements (optional)"
            }
        }
    
    def get_required_parameters(self) -> list:
        return ["url"]
    
    async def execute(self, url: str, extract_type: str = "text", target_selector: str = None, **kwargs) -> Dict[str, Any]:
        """
        Scrape web content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (AI Task Automation Agent)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if extract_type == "links":
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                return {
                    "success": True,
                    "url": url,
                    "links": links[:50],  # Limit to 50 links
                    "total_links": len(links)
                }
            
            elif extract_type == "summary":
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get title and first paragraph
                title = soup.title.string if soup.title else ""
                paragraphs = soup.find_all('p')
                summary = paragraphs[0].get_text()[:500] if paragraphs else ""
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "summary": summary
                }
            
            else:  # text
                if target_selector:
                    elements = soup.select(target_selector)
                    content = ' '.join([elem.get_text() for elem in elements])
                else:
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    content = soup.get_text()
                
                # Clean up whitespace
                content = re.sub(r'\s+', ' ', content).strip()
                
                return {
                    "success": True,
                    "url": url,
                    "content": content[:2000],  # Limit content
                    "content_length": len(content)
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to scrape URL: {str(e)}"
            }
