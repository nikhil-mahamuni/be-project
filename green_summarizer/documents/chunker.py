import re
from typing import List

class DocumentChunker:
    @staticmethod
    def chunk_text(text: str, max_words_per_chunk: int = 500) -> List[str]:
        """
        Splits text into chunks of approximately max_words_per_chunk,
        preferring to split on sentence boundaries or paragraphs.
        """
        if not text:
            return []

        words = text.split()
        if len(words) <= max_words_per_chunk:
            return [text]

        # Split by paragraph first
        paragraphs = re.split(r'\n\s*\n', text)

        chunks = []
        current_chunk = []
        current_word_count = 0

        for para in paragraphs:
            para_words = para.split()
            para_word_count = len(para_words)

            # If paragraph itself is too big, split it by sentences or even raw words
            if para_word_count > max_words_per_chunk:
                sentences = re.split(r'(?<=[.!?]) +', para)
                # If there's no punctuation, it might just return the whole paragraph as one sentence
                if len(sentences) == 1 and len(sentences[0].split()) > max_words_per_chunk:
                    # Fallback: split by raw words
                    for word in para_words:
                        if current_word_count + 1 > max_words_per_chunk and current_chunk:
                            chunks.append(" ".join(current_chunk))
                            current_chunk = [word]
                            current_word_count = 1
                        else:
                            current_chunk.append(word)
                            current_word_count += 1
                    continue

                for sent in sentences:
                    sent_words = sent.split()
                    sent_word_count = len(sent_words)

                    if current_word_count + sent_word_count > max_words_per_chunk and current_chunk:
                        chunks.append(" ".join(current_chunk))
                        current_chunk = sent_words
                        current_word_count = sent_word_count
                    else:
                        current_chunk.extend(sent_words)
                        current_word_count += sent_word_count
            else:
                if current_word_count + para_word_count > max_words_per_chunk and current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = para_words
                    current_word_count = para_word_count
                else:
                    current_chunk.extend(para_words)
                    current_word_count += para_word_count

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
