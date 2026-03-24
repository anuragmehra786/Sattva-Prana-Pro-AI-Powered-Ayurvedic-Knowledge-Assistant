# utils.py
import re
from data import DOSHA_KEYWORDS

def preprocess_text(text):
    """Clean and lowercase user input."""
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text

def detect_dosha(user_input):
    """
    Analyze text to detect primary dosha based on keyword matching.
    Returns dosha percentages, the dominant dosha, and total keyword matches.
    """
    processed_input = preprocess_text(user_input)
    words = set(processed_input.split())
    
    scores = {"Vata": 0, "Pitta": 0, "Kapha": 0}
    
    for dosha, keywords in DOSHA_KEYWORDS.items():
        for keyword in keywords:
            # Handle multi-word keywords
            if " " in keyword:
                if keyword in processed_input:
                    scores[dosha] += 2  # Higher weight for multi-word exact matches
            else:
                if keyword in words:
                    scores[dosha] += 1
                    
    total_matches = sum(scores.values())
    
    if total_matches == 0:
        return scores, "Balanced / Undetermined", 0
        
    # Calculate percentages
    percentages = {d: (s / total_matches) * 100 for d, s in scores.items()}
    dominant_dosha = max(percentages, key=percentages.get)
    
    return percentages, dominant_dosha, total_matches

def calculate_wellness_score(total_issues_matched):
    """
    Calculate a wellness score based on number of symptoms detected.
    Fewer symptoms = higher wellness score.
    """
    if total_issues_matched == 0:
        return 100
        
    # Simple heuristic: penalize 5 points per matched symptom, capping at a 60 point penalty (min score 40)
    # This provides a realistic-looking score for the dashboard
    max_penalty = 60
    penalty = min(total_issues_matched * 5, max_penalty)
    base_score = 100
    
    wellness_score = base_score - penalty
    return int(wellness_score)
