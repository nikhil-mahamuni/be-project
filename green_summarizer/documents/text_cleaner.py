import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """
        Removes weird characters, multiple spaces, and normalizes text.
        """
        if not text:
            return ""

        # Replace non-breaking spaces
        text = text.replace('\xa0', ' ')

        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)

        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Replace multiple spaces with a single space
        text = re.sub(r' +', ' ', text)

        return text.strip()
