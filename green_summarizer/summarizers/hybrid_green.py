import time
import math
from collections import Counter
from summarizers.base import BaseSummarizer
from storage.models import SummaryResult
from utils.text_utils import word_count, extract_sentences
from summarizers.frequency_rank import FrequencyRankSummarizer

class HybridGreenSummarizer(BaseSummarizer):
    name = "Hybrid Green Mode"
    description = "Optimized for speed and low energy. Combines positional scoring, fast frequency tracking, and length penalties."

    def summarize(self, text: str, ratio: float) -> SummaryResult:
        start_time = time.time()

        input_words = word_count(text)
        sentences = extract_sentences(text)

        if not sentences:
            return self._empty_result()

        target_sentences = max(1, math.ceil(len(sentences) * ratio))
        num_sentences = len(sentences)

        # Fast Tokenization & Global Frequencies
        sentence_words_list = []
        global_counts = Counter()

        for sentence in sentences:
            words = sentence.lower().replace('.', ' ').replace(',', ' ').split()
            words = [w for w in words if w not in FrequencyRankSummarizer.STOPWORDS and len(w) > 1]
            sentence_words_list.append(words)
            global_counts.update(words)

        max_freq = max(global_counts.values()) if global_counts else 1.0

        # Score
        sentence_scores = []
        for i, words in enumerate(sentence_words_list):
            score = 0.0

            # Position Score (sentences early and late in document are often more important)
            position_ratio = i / float(num_sentences) if num_sentences > 1 else 0
            position_weight = 1.0
            if position_ratio < 0.2:
                position_weight = 1.5
            elif position_ratio > 0.8:
                position_weight = 1.2

            # Frequency Score
            freq_score = sum((global_counts[w] / max_freq) for w in words)

            # Length penalty (penalize very short or very long sentences)
            length = len(words)
            length_penalty = 1.0
            if length < 3:
                length_penalty = 0.5
            elif length > 20:
                length_penalty = 0.8

            if length > 0:
                score = (freq_score / length) * position_weight * length_penalty

            sentence_scores.append((i, score))

        # Select top sentences
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [x[0] for x in sentence_scores[:target_sentences]]
        top_indices.sort()

        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = " ".join(summary_sentences)

        output_words = word_count(summary_text)
        compression = output_words / input_words if input_words > 0 else 0

        top_keywords = [w[0] for w in global_counts.most_common(5)]

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
