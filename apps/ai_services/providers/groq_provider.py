import os
import re
import time
import logging
from .base import BaseAIProvider, AIResult

logger = logging.getLogger(__name__)

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "groq"

    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            self.api_key = os.environ.get('GET_API_KEY')

        model_env = os.environ.get('GROQ_MODEL', '')
        if model_env:
            self.model = model_env
        else:
            self.model = 'openai/gpt-oss-120b'

        if Groq and self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

    def health_check(self) -> bool:
        return self.client is not None

    def _strip_think_blocks(self, text: str) -> str:
        """Remove <think>...</think> blocks, including unclosed ones truncated by token limits."""
        import re
        # Remove fully closed <think>...</think> blocks
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Remove unclosed <think> blocks (everything from <think> to end of string)
        cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL)
        return cleaned.strip()

    def generate_text(self, prompt: str, system_message: str = "") -> AIResult:
        if not self.health_check():
            return AIResult(success=False, error="Groq API key not configured or package missing.")

        # Robust size checks to avoid 413 errors
        # Define safe limits (character counts). Adjust as needed based on model limits.
        MAX_TOTAL_INPUT = 8000  # combined system_message and prompt
        MAX_PROMPT_ONLY = 6000
        # Truncate prompt if it alone exceeds its limit
        if len(prompt) > MAX_PROMPT_ONLY:
            prompt = prompt[:MAX_PROMPT_ONLY] + "... [PROMPT TRUNCATED]"
        # Ensure combined size stays within safe total limit
        combined_len = len(system_message) + len(prompt)
        if combined_len > MAX_TOTAL_INPUT:
            # Truncate the prompt further to fit the total budget
            excess = combined_len - MAX_TOTAL_INPUT
            prompt = prompt[:-excess] + "... [TRUNCATED DUE TO TOTAL INPUT]"

        # Build the effective system message
        effective_system = system_message

        # Models to try (supported models on this Groq endpoint)
        candidate_models = [self.model, 'openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'qwen/qwen3.8-27b']
        # Remove duplicates while preserving order
        candidate_models = list(dict.fromkeys(candidate_models))

        for model_name in candidate_models:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    chat_completion = self.client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": effective_system},
                            {"role": "user", "content": prompt}
                        ],
                        model=model_name,
                        temperature=0.5,
                        max_tokens=1200,  # Reduced to keep response size modest
                    )
                    raw = chat_completion.choices[0].message.content or ""
                    content = self._strip_think_blocks(raw)

                    if not content:
                        return AIResult(
                            success=False,
                            error="Model returned an empty response after stripping think blocks.",
                            provider=self.provider_name,
                            model=model_name
                        )

                    return AIResult(
                        success=True,
                        content=content,
                        provider=self.provider_name,
                        model=model_name
                    )

                except Exception as e:
                    error_str = str(e)
                    # Check for rate limit (429) errors and wait briefly before retrying
                    if '429' in error_str and attempt < max_retries - 1:
                        wait_time = 2 * (attempt + 1)
                        logger.warning(
                            f"Groq rate limit hit (attempt {attempt + 1}/{max_retries}). "
                            f"Waiting {wait_time}s before retry..."
                        )
                        time.sleep(wait_time)
                        continue
                    
                    logger.warning(f"Groq generation failed with model {model_name}: {error_str}")
                    break  # Try next candidate model if available

        return AIResult(success=False, error="All candidate Groq models failed.", provider=self.provider_name, model=self.model)
