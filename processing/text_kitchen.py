import re

class TextKitchen:
    """
    Cleans up raw text by stripping excessive whitespace, removing too-short lines,
    and normalizing formatting.
    """
    def clean(self, text: str) -> str:
        # Remove consecutive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Filter lines that are just numbers or very short, optionally
        lines = text.split('\n')
        cleaned_lines = [
            line.strip() for line in lines 
            if len(line.strip()) > 10 or line.strip().endswith('.') 
            or (line.strip() and line.strip()[-1].isalnum())
        ]
        
        return "\n".join(cleaned_lines)
