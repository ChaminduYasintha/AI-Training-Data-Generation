from typing import List

class SmartChunker:
    """
    Cuts text into optimized portions with overlapping slices 
    to perfectly preserve semantic context between chunks.
    """
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        
        if not words:
            return chunks

        i = 0
        while i < len(words):
            chunk = words[i: i + self.chunk_size]
            chunks.append(" ".join(chunk))
            i += (self.chunk_size - self.overlap)
            
            # Prevent infinite loop if overlap >= chunk_size
            if self.chunk_size - self.overlap <= 0:
                break
                
        return chunks
