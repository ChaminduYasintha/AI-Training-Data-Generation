import os
from .local_loader import LocalDocumentLoader
from .web_scraper import WebScraper

class UnifiedLoader:
    """
    The Unified Loader acts as a dispatch center for handling incoming tasks.
    It automatically routes URLs to the WebScraper and paths/files to the LocalDocumentLoader.
    """
    def __init__(self):
        self.local_loader = LocalDocumentLoader()
        self.web_scraper = WebScraper()

    def load_resource(self, resource_path: str):
        if resource_path.startswith("http://") or resource_path.startswith("https://"):
            return self.web_scraper.load(resource_path)
        elif os.path.exists(resource_path):
            return self.local_loader.load(resource_path)
        else:
            raise ValueError(f"Resource {resource_path} is neither a valid URL nor a valid file path.")
