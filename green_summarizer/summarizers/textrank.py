import time
import math
import networkx as nx
from summarizers.base import BaseSummarizer
from storage.models import SummaryResult
from utils.text_utils import word_count, extract_sentences
from summarizers.frequency_rank import FrequencyRankSummarizer

class TextRankSummarizer(BaseSummarizer):
    name = "TextRank"
    description = "Graph-based ranking model using PageRank algorithm on sentence similarity. Slower but more coherent."

    def _sentence_similarity(self, sent1: list, sent2: list) -> float:
        if not sent1 or not sent2:
            return 0.0

        set1 = set(sent1)
        set2 = set(sent2)

        intersection = len(set1.intersection(set2))

        # Log length penalty to avoid promoting long sentences excessively
        denom = math.log10(len(sent1)) + math.log10(len(sent2))

        if denom == 0.0:
            return 0.0

        return intersection / denom

    def summarize(self, text: str, ratio: float) -> SummaryResult:
        start_time = time.time()

        input_words = word_count(text)
        sentences = extract_sentences(text)

        if not sentences:
            return self._empty_result()

        target_sentences = max(1, math.ceil(len(sentences) * ratio))
        if target_sentences >= len(sentences):
             target_sentences = len(sentences) - 1 if len(sentences) > 1 else 1

        # Tokenize
        sentence_words = []
        all_words = []
        for sentence in sentences:
            words = sentence.lower().replace('.', ' ').replace(',', ' ').split()
            words = [w for w in words if w not in FrequencyRankSummarizer.STOPWORDS and len(w) > 1]
            sentence_words.append(words)
            all_words.extend(words)

        # Build similarity matrix
        num_sentences = len(sentences)
        graph = nx.Graph()
        graph.add_nodes_from(range(num_sentences))

        for i in range(num_sentences):
            for j in range(i + 1, num_sentences):
                sim = self._sentence_similarity(sentence_words[i], sentence_words[j])
                if sim > 0:
                    graph.add_edge(i, j, weight=sim)

        # Apply PageRank
        try:
            scores = nx.pagerank(graph, weight='weight')
        except:
            # Fallback if convergence fails (rare for small graphs)
            scores = {i: 1.0/num_sentences for i in range(num_sentences)}

        # Select top sentences
        sentence_scores = list(scores.items())
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        top_indices = [x[0] for x in sentence_scores[:target_sentences]]
        top_indices.sort()

        summary_sentences = [sentences[i] for i in top_indices]
        summary_text = " ".join(summary_sentences)

        output_words = word_count(summary_text)
        compression = output_words / input_words if input_words > 0 else 0

        # Simple keywords
        from collections import Counter
        top_keywords = [w[0] for w in Counter(all_words).most_common(5)]

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
