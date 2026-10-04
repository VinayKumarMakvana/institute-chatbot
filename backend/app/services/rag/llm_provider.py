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
            try:
                full_prompt = f"{system_instruction}\n\n{prompt}"
                response = self.client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=full_prompt
                )
                return response.text
            except Exception as e:
                logger.error(f"Gemini generation failed: {e}")
                raise Exception("The AI service is temporarily unavailable. Please try again.")
        else:
            raise Exception("Unsupported or unconfigured LLM provider")

llm_provider = LLMProvider()
