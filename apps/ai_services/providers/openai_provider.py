import os
import logging
from .base import BaseAIProvider, AIResult

logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:
    openai = None

class OpenAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "openai"

    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY') or os.environ.get('GET_API_KEY')
        self.model = os.environ.get('OPENAI_MODEL', 'openai/gpt-oss-120b')
        if openai and self.api_key:
            openai.api_key = self.api_key
            self.client = openai
        else:
            self.client = None

    def health_check(self) -> bool:
        return self.client is not None

    def generate_text(self, prompt: str, system_message: str = "") -> AIResult:
        if not self.health_check():
            return AIResult(success=False, error="OpenAI API key not configured or package missing.")

        # Size checks similar to GroqProvider
        MAX_TOTAL_INPUT = 8000
        MAX_PROMPT_ONLY = 6000
        if len(prompt) > MAX_PROMPT_ONLY:
            prompt = prompt[:MAX_PROMPT_ONLY] + "... [PROMPT TRUNCATED]"
        combined_len = len(system_message) + len(prompt)
        if combined_len > MAX_TOTAL_INPUT:
            excess = combined_len - MAX_TOTAL_INPUT
            prompt = prompt[:-excess] + "... [TRUNCATED DUE TO TOTAL INPUT]"

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=1200,
            )
            raw = response.choices[0].message.content or ""
            return AIResult(success=True, content=raw, provider=self.provider_name, model=self.model)
        except Exception as e:
            logger.warning(f"OpenAI generation failed with model {self.model}: {e}")
            return AIResult(success=False, error=str(e), provider=self.provider_name, model=self.model)
