import os
import requests
from bs4 import BeautifulSoup
from .base_loader import BaseLoader

class WebScraper(BaseLoader):
    """
    Enterprise-grade web scraper using Decodo API.
    Bypasses bot detection, with a smart fallback to BeautifulSoup if the API fails.
    """
    def __init__(self):
        self.decodo_api_key = os.getenv("DECODO_API_KEY")

    def _fallback_extract(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text(separator=' ', strip=True)

    def load(self, source: str) -> list:
        if self.decodo_api_key:
            try:
                # Mocking Decodo API call logic as Decodo setup
                headers = {"Authorization": f"Bearer {self.decodo_api_key}"}
                api_url = "https://api.decodo.io/scrape" 
                response = requests.post(api_url, json={"url": source}, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
                text = data.get("text", "")
                if text:
                    return [{"text": text, "metadata": {"source": source, "method": "decodo_api"}}]
            except Exception as e:
                print(f"Decodo API failed for {source}: {e}. Falling back to BeautifulSoup.")
        
        # Fallback
        text = self._fallback_extract(source)
        return [{"text": text, "metadata": {"source": source, "method": "beautifulsoup_fallback"}}]
