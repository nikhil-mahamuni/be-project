import time

def get_current_timestamp() -> float:
    return time.time()

def format_duration(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 1:
        return f"{seconds:.3f} s"
    else:
        return f"{seconds:.2f} s"
