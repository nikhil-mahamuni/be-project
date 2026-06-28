import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../green_summarizer')))

from summarizers.factory import SummarizerFactory

def test_all_summarizers():
    sample_text = """
    Green AI is a crucial research direction in artificial intelligence. It focuses on making models more efficient and reducing their carbon footprint.
    Many modern deep learning models consume enormous amounts of energy during both training and inference phases.
    By using lighter algorithms, we can provide decent performance on mobile devices without relying on cloud APIs.
    This saves internet data, preserves user privacy, and extends battery life significantly.
    Furthermore, tracking these metrics helps raise user awareness about the hidden costs of AI.
    """

    models = SummarizerFactory.get_available_models()

    for model_name in models:
        summarizer = SummarizerFactory.get_summarizer(model_name)
        result = summarizer.summarize(sample_text, ratio=0.4)

        assert result.output_word_count > 0
        assert result.output_word_count < result.input_word_count
        assert len(result.keywords) > 0
