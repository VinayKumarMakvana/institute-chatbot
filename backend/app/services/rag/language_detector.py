from langdetect import detect, detect_langs, LangDetectException

class LanguageDetector:
    def detect(self, text: str) -> dict:
        try:
            lang_code = detect(text)
            langs = detect_langs(text)
            confidence = langs[0].prob if langs else 0.0
            
            return {
                "language_code": lang_code,
                "confidence": confidence
            }
        except LangDetectException:
            return {
                "language_code": "unknown",
                "confidence": 0.0
            }

language_detector = LanguageDetector()
