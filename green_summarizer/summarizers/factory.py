from summarizers.base import BaseSummarizer
from summarizers.frequency_rank import FrequencyRankSummarizer
from summarizers.tfidf_rank import TFIDFRankSummarizer
from summarizers.textrank import TextRankSummarizer
from summarizers.hybrid_green import HybridGreenSummarizer

class SummarizerFactory:
    _models = {
        "Frequency Rank": FrequencyRankSummarizer,
        "TF-IDF Rank": TFIDFRankSummarizer,
        "TextRank": TextRankSummarizer,
        "Hybrid Green Mode": HybridGreenSummarizer
    }

    @classmethod
    def get_summarizer(cls, model_name: str) -> BaseSummarizer:
        model_class = cls._models.get(model_name)
        if not model_class:
            # fallback to hybrid green
            model_class = HybridGreenSummarizer
        return model_class()

    @classmethod
    def get_available_models(cls) -> list:
        return list(cls._models.keys())
