"""Text normalization shared by keyword and composition extraction."""
import re

def normalize(text):
    return re.sub(r'[\s\-–—]+', ' ', text.casefold()).strip()


def phrase(pattern):
    return re.compile(r'(?<!\w)' + re.escape(normalize(pattern)).replace(r'\ ', r'\s+') + r'(?!\w)')
