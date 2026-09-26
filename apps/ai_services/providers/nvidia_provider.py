import os
import logging
from .base import BaseAIProvider, AIResult

logger = logging.getLogger(__name__)

try:
    import openai
except ImportError:
    openai = None

class NvidiaProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "nvidia"

    def __init__(self):
        self.api_key = os.environ.get('NVIDIA_API_KEY')
        self.model = os.environ.get('NVIDIA_MODEL', 'nvidia/nemotron-3.5-lightning-30b-a3b')
        if openai and self.api_key:
            self.client = openai
        else:
            self.client = None

    def health_check(self) -> bool:
        return self.client is not None

    def generate_text(self, prompt: str, system_message: str = "") -> AIResult:
        if not self.health_check():
            return AIResult(success=False, error="NVIDIA API key not configured or openai package missing.")

        # Size checks – same limits as other providers
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

        # Save original openai settings so we can restore them after the call
        original_api_key = self.client.api_key
        original_api_base = self.client.api_base

        try:
            # Point openai at NVIDIA's OpenAI-compatible endpoint
            self.client.api_key = self.api_key
            self.client.api_base = "https://integrate.api.nvidia.com/v1"

            response = self.client.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )
            content = response.choices[0].message.content or ""
            return AIResult(success=True, content=content, provider=self.provider_name, model=self.model)
        except Exception as e:
            logger.warning(f"NVIDIA generation failed with model {self.model}: {e}")
            return AIResult(success=False, error=str(e), provider=self.provider_name, model=self.model)
        finally:
            # Restore original settings so other providers aren't affected
            self.client.api_key = original_api_key
            self.client.api_base = original_api_base
