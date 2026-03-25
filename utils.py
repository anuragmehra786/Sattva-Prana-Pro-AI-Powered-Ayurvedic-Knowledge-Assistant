# utils.py
import re
from data import DOSHA_KEYWORDS

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def detect_dosha(user_input):
    processed = preprocess_text(user_input)
    words = set(processed.split())
    
    scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    
    for dosha, keywords in DOSHA_KEYWORDS.items():
        for kw in keywords:
            if " " in kw:
                if kw in processed:
                    scores[dosha] += 2
            else:
                if kw in words:
                    scores[dosha] += 1
                    
    total = sum(scores.values())
    if total == 0:
        return {"Vata": 33.3, "Pitta": 33.3, "Kapha": 33.3}, "Balanced / Undetected", 0

    percentages = {d: round((s / total) * 100, 1) for d, s in scores.items()}
    dominant = max(percentages, key=percentages.get)
    
    return percentages, dominant, total

def calculate_wellness_score(match_count):
    if match_count == 0:
        return 100
    penalty = min(match_count * 5, 60)
    return int(100 - penalty)
