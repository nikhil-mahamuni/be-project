import os

def get_file_extension(filepath: str) -> str:
    _, ext = os.path.splitext(filepath)
    return ext.lower()

def is_pdf(filepath: str) -> bool:
    return get_file_extension(filepath) == '.pdf'
