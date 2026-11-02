import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.provider = settings.AI_PROVIDER.lower()
        if self.provider == "gemini":
            try:
                from google import genai
                self.client = genai.Client(api_key=settings.AI_API_KEY)
            except ImportError:
                self.client = None
        else:
            self.client = None
                
    async def generate(self, prompt: str, system_instruction: str = "") -> str:
        if self.provider == "mock":
            return "This is a mock answer generated using the retrieved context."
            
        elif self.provider == "gemini" and self.client:
            models_to_try = [
                settings.LLM_MODEL,
                "gemini-3-flash-preview",
                "gemini-3.5-flash"
            ]
            full_prompt = f"{system_instruction}\n\n{prompt}"
            last_err = None
            for model_name in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=full_prompt
                    )
                    return response.text
                except Exception as e:
                    logger.warning(f"Gemini model {model_name} failed: {e}")
                    last_err = e
            logger.error(f"All Gemini generation models failed: {last_err}")
            raise Exception("The AI service is temporarily unavailable. Please try again.")
        else:
            raise Exception("Unsupported or unconfigured LLM provider")

llm_provider = LLMProvider()
