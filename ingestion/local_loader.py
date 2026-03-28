import os
import PyPDF2
from .base_loader import BaseLoader

class LocalDocumentLoader(BaseLoader):
    """
    Loads raw text from local documents like PDF and TXT.
    """
    def load(self, source: str) -> list:
        ext = os.path.splitext(source)[1].lower()
        if ext == '.pdf':
            text = self._load_pdf(source)
        elif ext == '.txt':
            text = self._load_txt(source)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
        
        return [{"text": text, "metadata": {"source": source, "method": "local_loader"}}]

    def _load_txt(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_pdf(self, path: str) -> str:
        text = ""
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
