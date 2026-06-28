import time
import math
from collections import Counter
from summarizers.base import BaseSummarizer
from storage.models import SummaryResult
from utils.text_utils import word_count, extract_sentences

class FrequencyRankSummarizer(BaseSummarizer):
    name = "Frequency Rank"
    description = "A fast, lightweight statistical summarizer. Scores sentences based on the frequency of non-stop words."

    # Simple builtin stopword list to keep it offline and pure python
    STOPWORDS = set([
        "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
        "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
        "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
        "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
        "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
        "while", "of", "at", "by", "for", "with", "about", "against", "between", "into",
        "through", "during", "before", "after", "above", "below", "to", "from", "up", "down",
        "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here",
        "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
        "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
        "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"
    ])

    def summarize(self, text: str, ratio: float) -> SummaryResult:
        start_time = time.time()

        input_words = word_count(text)
        sentences = extract_sentences(text)

        if not sentences:
            return self._empty_result()

        target_sentences = max(1, math.ceil(len(sentences) * ratio))

        # Tokenize and get word frequencies
        words = text.lower().replace('.', ' ').replace(',', ' ').replace('!', ' ').replace('?', ' ').split()
        words = [w for w in words if w not in self.STOPWORDS and len(w) > 1]
        freq_dist = Counter(words)

        if not freq_dist:
             return self._empty_result()

        max_freq = max(freq_dist.values())
        for word in freq_dist:
            freq_dist[word] = freq_dist[word] / max_freq # Normalize

        # Score sentences
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = 0.0
            sentence_words = sentence.lower().replace('.', ' ').replace(',', ' ').split()
            valid_words = 0
            for word in sentence_words:
                if word in freq_dist:
                    score += freq_dist[word]
                    valid_words += 1

            # length normalization
            if valid_words > 0:
                 score = score / valid_words

            sentence_scores.append((i, score))

        # Select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [x[0] for x in sentence_scores[:target_sentences]]
        top_indices.sort()

        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = " ".join(summary_sentences)

        output_words = word_count(summary_text)
        compression = output_words / input_words if input_words > 0 else 0

        top_keywords = [w[0] for w in freq_dist.most_common(5)]

        return SummaryResult(
            summary_text=summary_text,
            model_name=self.name,
            input_word_count=input_words,
            output_word_count=output_words,
            compression_ratio=compression,
            sentence_count=len(summary_sentences),
            keywords=top_keywords,
            processing_time_seconds=time.time() - start_time
        )

    def _empty_result(self) -> SummaryResult:
        return SummaryResult(
            summary_text="",
            model_name=self.name,
            input_word_count=0,
            output_word_count=0,
            compression_ratio=0.0,
            sentence_count=0,
            keywords=[],
            processing_time_seconds=0.0
        )
