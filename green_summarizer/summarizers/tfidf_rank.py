import time
import math
from collections import Counter
from summarizers.base import BaseSummarizer
from storage.models import SummaryResult
from utils.text_utils import word_count, extract_sentences
from summarizers.frequency_rank import FrequencyRankSummarizer

class TFIDFRankSummarizer(BaseSummarizer):
    name = "TF-IDF Rank"
    description = "Extractive summarization using Term Frequency-Inverse Document Frequency weighting on sentences."

    def summarize(self, text: str, ratio: float) -> SummaryResult:
        start_time = time.time()

        input_words = word_count(text)
        sentences = extract_sentences(text)

        if not sentences:
            return self._empty_result()

        target_sentences = max(1, math.ceil(len(sentences) * ratio))

        # Tokenize sentences and compute TF
        sentence_words = []
        doc_freq = Counter()

        for sentence in sentences:
            words = sentence.lower().replace('.', ' ').replace(',', ' ').split()
            words = [w for w in words if w not in FrequencyRankSummarizer.STOPWORDS and len(w) > 1]
            sentence_words.append(words)

            # Count document frequency (number of sentences containing the word)
            unique_words = set(words)
            for word in unique_words:
                doc_freq[word] += 1

        num_sentences = len(sentences)

        # Compute IDF
        idf = {}
        for word, count in doc_freq.items():
            idf[word] = math.log10(num_sentences / float(count))

        # Score sentences
        sentence_scores = []
        for i, words in enumerate(sentence_words):
            score = 0.0
            tf = Counter(words)
            total_words = len(words)

            if total_words > 0:
                for word, count in tf.items():
                    tf_val = count / float(total_words)
                    score += tf_val * idf.get(word, 0)

            sentence_scores.append((i, score))

        # Select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [x[0] for x in sentence_scores[:target_sentences]]
        top_indices.sort()

        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = " ".join(summary_sentences)

        output_words = word_count(summary_text)
        compression = output_words / input_words if input_words > 0 else 0

        # Keywords based on highest IDF
        top_keywords = [w[0] for w in sorted(idf.items(), key=lambda x: x[1], reverse=True)[:5]]

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
