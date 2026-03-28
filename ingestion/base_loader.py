from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLoader(ABC):
    """
    Abstract base class for all data loaders.
    Strictly follows the single responsibility principle.
    """
    @abstractmethod
    def load(self, source: str) -> List[Dict[str, Any]]:
        """
        Loads data from a given source and returns a list of chunk dictionaries or raw text.
        Each dictionary should minimally contain:
        - 'text': the extracted raw text
        - 'metadata': dict with source information
        """
        pass
