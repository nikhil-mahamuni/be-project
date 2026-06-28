import re
from typing import List

def word_count(text: str) -> int:
    return len(re.findall(r'\b\w+\b', text))

def clean_text(text: str) -> str:
    # Basic cleanup
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_sentences(text: str) -> List[str]:
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?]) +', text)
    return [s.strip() for s in sentences if s.strip()]
