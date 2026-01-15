import random

def calculate_confidence(text: str) -> float:
    # Phase-1 heuristic
    if len(text) < 50:
        return 0.4
    if len(text) < 150:
        return 0.7
    return round(random.uniform(0.8, 0.95), 2)
