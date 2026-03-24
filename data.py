# data.py
"""
Contains reference data for Doshas, their symptoms, characteristics, and recommendations.
"""

DOSHA_KEYWORDS = {
    "Vata": [
        "anxiety", "dry skin", "constipation", "bloating", "insomnia",
        "cold hands", "cold feet", "fatigue", "restless", "thin",
        "irregular appetite", "joint cracking", "nervous", "light sleeper",
        "worried", "fear", "dryness", "gassy", "tremors"
    ],
    "Pitta": [
        "acne", "heartburn", "acid reflux", "anger", "irritability",
        "sweating", "hot flashes", "inflammation", "diarrhea", "intense",
        "sharp hunger", "competitiveness", "perfectionist", "warm body",
        "red skin", "rash", "burning", "impatient", "fever"
    ],
    "Kapha": [
        "weight gain", "lethargy", "congestion", "sinus", "depression",
        "sluggish", "oily skin", "heavy sleep", "water retention", "calm",
        "slow digestion", "stubborn", "sweet tooth", "thick hair",
        "mucus", "cold", "attachment", "greed", "lazy"
    ]
}

RECOMMENDATIONS = {
    "Vata": {
        "diet": ["Warm, cooked, nourishing foods", "Healthy fats (ghee, olive oil)", "Sweet, sour, and salty tastes", "Avoid raw vegetables and cold drinks"],
        "lifestyle": ["Establish a regular daily routine", "Gentle exercise like yoga or walking", "Keep warm", "Daily warm oil massage (Abhyanga)"]
    },
    "Pitta": {
        "diet": ["Cooling foods like cucumber, melon, and coconut", "Sweet, bitter, and astringent tastes", "Avoid spicy, fried, and fermented foods", "Reduce caffeine and alcohol"],
        "lifestyle": ["Avoid midday sun and extreme heat", "Practice moderation and avoid overworking", "Meditation and cooling breathwork (Sheetali)", "Spend time in nature and near water"]
    },
    "Kapha": {
        "diet": ["Warm, light, and spicy foods", "Pungent, bitter, and astringent tastes", "Avoid heavy, oily, and overly sweet foods", "Reduce dairy and cold drinks"],
        "lifestyle": ["Vigorous, daily exercise to break a sweat", "Stimulating activities and seeking variety", "Wake up early (before sunrise)", "Dry skin brushing (Garshana)"]
    }
}
