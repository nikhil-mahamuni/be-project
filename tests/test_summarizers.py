import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from summarizers.factory import SummarizerFactory
from summarizers.frequency_rank import FrequencyRankSummarizer
from summarizers.tfidf_rank import TFIDFRankSummarizer
from summarizers.textrank import TextRankSummarizer
from summarizers.hybrid_green import HybridGreenSummarizer

def test_summarizers_general():
    sample_text = """
    Green AI is a crucial research direction in artificial intelligence. It focuses on making models more efficient and reducing their carbon footprint.
    Many modern deep learning models consume enormous amounts of energy during both training and inference phases.
    By using lighter algorithms, we can provide decent performance on mobile devices without relying on cloud APIs.
    This saves internet data, preserves user privacy, and extends battery life significantly.
    Furthermore, tracking these metrics helps raise user awareness about the hidden costs of AI.
    """
    models = SummarizerFactory.get_available_models()
    assert len(models) == 4

    for model_name in models:
        summarizer = SummarizerFactory.get_summarizer(model_name)
        result = summarizer.summarize(sample_text, ratio=0.4)

        assert result.output_word_count > 0
        assert result.output_word_count < result.input_word_count
        assert len(result.keywords) > 0

def test_empty_input():
    for model_name in SummarizerFactory.get_available_models():
        summarizer = SummarizerFactory.get_summarizer(model_name)
        result = summarizer.summarize("", ratio=0.5)
        assert result.output_word_count == 0
        assert result.summary_text == ""
        assert result.compression_ratio == 0.0

def test_short_input():
    text = "Hello world."
    for model_name in SummarizerFactory.get_available_models():
        summarizer = SummarizerFactory.get_summarizer(model_name)
        result = summarizer.summarize(text, ratio=0.5)
        # Should just return the short text or handle it without crashing
        assert isinstance(result.summary_text, str)

def test_duplicate_sentence_removal():
    text = "This is a test. This is a test. This is a test."
    summarizer = TFIDFRankSummarizer()
    result = summarizer.summarize(text, ratio=0.3)
    # The algorithms pick top N sentences based on ratio. 3 sentences * 0.3 ratio -> ~1 sentence
    assert result.sentence_count == 1
