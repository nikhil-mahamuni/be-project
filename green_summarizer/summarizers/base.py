from storage.models import SummaryResult

class BaseSummarizer:
    name: str = "Base Summarizer"
    description: str = "Base interface for summarization models."

    def summarize(self, text: str, ratio: float) -> SummaryResult:
        """
        Summarizes the given text down to approximately the given ratio (e.g., 0.3 for 30%).
        Should return a SummaryResult object.
        """
        raise NotImplementedError("Summarizer must implement 'summarize' method.")
