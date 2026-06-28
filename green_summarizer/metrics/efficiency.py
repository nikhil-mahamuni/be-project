class EfficiencyCalculator:
    @staticmethod
    def calculate_score(duration_seconds: float,
                        energy_joules: float,
                        data_used_bytes: int,
                        compression_ratio: float,
                        output_words: int) -> float:
        """
        Calculates a proprietary Green Efficiency Score (0-100).
        Higher is better.
        """
        score = 100.0

        # Latency Penalty (e.g. lose 5 points per second)
        latency_penalty = duration_seconds * 5.0

        # Energy Penalty (e.g. lose 10 points per joule)
        energy_penalty = energy_joules * 10.0

        # Data Penalty (lose 1 point per 100KB)
        data_penalty = (data_used_bytes / 102400.0) * 1.0

        # Compression Penalty (punish over-compression > 95% or under-compression < 10%)
        compression_penalty = 0.0
        if compression_ratio > 0.95:
            compression_penalty = 20.0
        elif compression_ratio < 0.10:
            compression_penalty = 10.0

        # Empty output penalty
        if output_words == 0:
            return 0.0

        score = score - latency_penalty - energy_penalty - data_penalty - compression_penalty

        # Clamp between 0 and 100
        return max(0.0, min(100.0, score))
