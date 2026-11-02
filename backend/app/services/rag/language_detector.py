import re

# Distinct Hinglish vocabulary that does not collide with standard English words
DISTINCT_HINGLISH = {
    'kya', 'hai', 'hain', 'hoga', 'hogi', 'honge', 'kaise', 'kese', 'kaisey',
    'kab', 'kbb', 'kaha', 'kahan', 'kyu', 'kyun', 'kisme', 'kisko', 'kisne',
    'meri', 'mera', 'mere', 'mujhe', 'mujko', 'hum', 'hume', 'tum', 'tumhe',
    'aap', 'aapka', 'aapke', 'aapki', 'batao', 'bataiye', 'batayein', 'bata',
    'karo', 'karna', 'karein', 'kare', 'karne', 'chahiye', 'chahie', 'sakta',
    'sakti', 'sakte', 'nahi', 'nhi', 'nai', 'tha', 'thi', 'bhi',
    'yeh', 'konsa', 'konsi', 'konse', 'accha', 'achha',
    'theek', 'thik', 'shuru', 'khatam', 'padhai', 'dijiye', 'dijiyega',
    'dekh', 'dekho', 'suno', 'samjhao', 'baat', 'kitna', 'kitne', 'kitni',
    'lagta', 'lagti', 'lagte', 'bataona', 'btao', 'kyahai', 'kabse', 'kabsy',
    'wali', 'wale', 'wala', 'velle', 'kuch', 'hona', 'honi', 'hone', 'raha',
    'rahi', 'rahe', 'gaya', 'gayi', 'gaye', 'paas', 'bhai', 'yaar',
    'batado', 'chale', 'jao', 'aayega', 'aayegi', 'dena', 'kripya',
    'milega', 'milegi', 'rahega', 'rahegi', 'pata', 'bhi', 'kro', 'krna'
}

class LanguageDetector:
    """
    Language detector restricted strictly to:
    - 'hindi' (Devanagari script)
    - 'hinglish' (Roman Hindi)
    - 'english' (Standard English)
    Never returns Afrikaans, Dutch, Somali or any other foreign language.
    """
    def detect(self, text: str) -> dict:
        if not text or not text.strip():
            return {"language_code": "english", "confidence": 1.0}
            
        # 1. Hindi Devanagari Script check
        if re.search(r'[\u0900-\u097F]', text):
            return {
                "language_code": "hindi",
                "confidence": 0.99
            }
            
        # 2. Hinglish (Roman Hindi) check
        words = set(re.findall(r'[a-zA-Z]+', text.lower()))
        hinglish_matches = words.intersection(DISTINCT_HINGLISH)
        if len(hinglish_matches) > 0:
            return {
                "language_code": "hinglish",
                "confidence": 0.95
            }
            
        # 3. Default to English
        return {
            "language_code": "english",
            "confidence": 0.90
        }

language_detector = LanguageDetector()
