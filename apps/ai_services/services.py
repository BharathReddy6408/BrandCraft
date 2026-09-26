import json
import logging
from .providers.huggingface import HuggingFaceProvider
from .providers.groq_provider import GroqProvider
from .providers.nvidia_provider import NvidiaProvider
# OpenAI provider removed; using Groq only
from .exceptions import AIConfigurationError, AIGenerationError

logger = logging.getLogger(__name__)

class AIService:
    @staticmethod
    def _get_providers():
        """Returns a list of configured providers in priority order."""
        providers = []
        
        # Primary: Groq (Ultra-fast & reliable)
        groq = GroqProvider()
        if groq.health_check():
            providers.append(groq)

        # NVIDIA provider (placed after Groq)
        from .providers.nvidia_provider import NvidiaProvider
        nvidia = NvidiaProvider()
        if nvidia.health_check():
            providers.append(nvidia)

        # Fallback: Hugging Face
        hf = HuggingFaceProvider()
        if hf.health_check():
            providers.append(hf)

        return providers

    @staticmethod
    def generate_text(prompt, system_message="You are an expert AI branding assistant."):
        providers = AIService._get_providers()
        
        if not providers:
            logger.error("No AI providers configured or healthy.")
            return None

        for provider in providers:
            try:
                result = provider.generate_text(prompt, system_message)
                if result.success and result.content:
                    text = result.content
                    import re
                    # Remove closed <think>...</think> blocks
                    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
                    # Remove unclosed <think> blocks (truncated by token limit)
                    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL).strip()
                    
                    # Clean up raw leaked reasoning (like "Here's a thinking process:")
                    if "Here's a thinking process" in text or "thinking process:" in text.lower():
                        # Often the actual response starts after a divider like --- or ✅ or just "Got it!"
                        if "✅" in text:
                            text = text.split("✅")[-1].strip()
                        elif "\n\nGot it!" in text:
                            text = "Got it!" + text.split("\n\nGot it!")[-1]
                        elif "\n\n**" in text:
                            # Try to find where the real formatting starts
                            parts = text.split("\n\n**", 1)
                            if len(parts) == 2:
                                text = "**" + parts[1]
                                
                    formatted = AIService._format_response(text.strip())
                    return formatted
                else:
                    logger.warning(f"Provider {provider.provider_name} failed: {result.error}")
            except Exception as e:
                logger.warning(f"Exception using provider {provider.provider_name}: {e}")
                
        logger.error("All AI providers failed to generate text.")
        return None

    @staticmethod
    def _format_response(text: str) -> str:
        """Apply consistent markdown formatting to AI-generated text.
        Adds leading and trailing separator lines (---) and ensures headings are preserved.
        """
        text = text.strip()
        # Ensure separator at start
        if not text.startswith('---'):
            text = '---\n' + text
        # Ensure separator at end
        if not text.endswith('---'):
            text = text + '\n---'
        return text

    @staticmethod
    def generate_structured(prompt, system_message="You are an expert AI branding assistant. Return ONLY valid JSON."):
        """Attempts to generate and parse structured JSON output."""
        import re

        text_result = AIService.generate_text(prompt, system_message)

        if not text_result:
            return None

        # --- Multi-strategy JSON extractor ---
        def try_parse(s):
            try:
                return json.loads(s)
            except Exception:
                return None

        cleaned = text_result.strip()

        # 1. Strip any residual <think>...</think> blocks (closed and unclosed)
        cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
        cleaned = re.sub(r'<think>.*', '', cleaned, flags=re.DOTALL).strip()

        # 2. Strip markdown code fences
        cleaned = re.sub(r'^```json\s*', '', cleaned).strip()
        cleaned = re.sub(r'^```\s*', '', cleaned).strip()
        cleaned = re.sub(r'\s*```$', '', cleaned).strip()

        # 3. Direct parse
        result = try_parse(cleaned)
        if result is not None:
            return result

        # 4. Find outermost { ... } block
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            result = try_parse(cleaned[start:end + 1])
            if result is not None:
                return result

        # 5. Handle truncated JSON: find the opening { and try to close it
        if start != -1:
            partial = cleaned[start:]
            # Count braces to find where it gets cut off
            depth = 0
            for i, ch in enumerate(partial):
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        result = try_parse(partial[:i + 1])
                        if result is not None:
                            return result
                        break

        # 6. Key-by-key extraction fallback for common keys
        extracted = {}
        for key in ['prompt', 'strategy', 'caption', 'headline', 'body', 'cta',
                    'subject', 'content', 'title', 'names', 'slogans',
                    'audience_focus', 'meta_description', 'summary', 'image_prompt']:
            m = re.search(r'"' + key + r'"\s*:\s*"((?:\\.|[^"\\])*)"', cleaned)
            if m:
                extracted[key] = m.group(1)

        # Check for list-type keys (slogans, names, etc.)
        for key in ['names', 'slogans', 'hashtags', 'keywords', 'features',
                    'content_pillars', 'strengths', 'weaknesses', 'opportunities', 'priority_actions']:
            m = re.search(r'"' + key + r'"\s*:\s*\[([^\]]*)\]', cleaned, re.DOTALL)
            if m:
                items_raw = m.group(1)
                items = re.findall(r'"((?:\\.|[^"\\])*)"', items_raw)
                if items:
                    extracted[key] = items

        if extracted:
            return extracted

        logger.error(f"Failed to parse structured JSON from AI.\nRaw output: {text_result[:500]}")
        return None


    @staticmethod
    def generate_image(prompt: str) -> bytes:
        """Generates an image from a prompt and returns raw bytes.
        
        Tries in order:
        1. Configured AI providers that support generate_image (e.g. HuggingFace)
        2. Pollinations.ai (flux model) - free, no key needed
        3. Pollinations.ai (turbo model) - lighter fallback
        4. Picsum placeholder (last resort so UI never breaks)
        """
        import urllib.parse
        import requests
        import random

        # 1. Try any configured provider that has image generation
        providers = AIService._get_providers()
        for provider in providers:
            if hasattr(provider, 'generate_image'):
                try:
                    result = provider.generate_image(prompt)
                    if result:
                        return result
                except Exception as e:
                    logger.warning(f"Image generation failed for {provider.provider_name}: {e}")

        # Also try HuggingFace directly even if its health_check failed (no HF_TOKEN)
        # because pollinations is always available as a free fallback
        hf = HuggingFaceProvider()
        if hf.health_check():
            try:
                result = hf.generate_image(prompt)
                if result:
                    logger.info("Image generated via HuggingFace provider.")
                    return result
            except Exception as e:
                logger.warning(f"HuggingFace image generation failed: {e}")

        # 2. Pollinations.ai – flux model (best quality, free, no API key needed)
        logger.info("Trying Pollinations.ai (flux) for image generation.")
        try:
            encoded_prompt = urllib.parse.quote(prompt[:500])  # cap prompt length
            seed = random.randint(1, 9999999)
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
            )
            response = requests.get(url, timeout=60)
            if response.status_code == 200 and len(response.content) > 1000:
                logger.info("Image generated via Pollinations.ai (flux).")
                return response.content
            else:
                logger.warning(f"Pollinations.ai (flux) returned status {response.status_code}, content length {len(response.content)}")
        except Exception as e:
            logger.warning(f"Pollinations.ai (flux) failed: {e}")

        # 3. Pollinations.ai – turbo model (faster, lighter)
        logger.info("Trying Pollinations.ai (turbo) for image generation.")
        try:
            encoded_prompt = urllib.parse.quote(prompt[:400])
            seed = random.randint(1, 9999999)
            url = (
                f"https://image.pollinations.ai/prompt/{encoded_prompt}"
                f"?width=1024&height=1024&nologo=true&seed={seed}&model=turbo"
            )
            response = requests.get(url, timeout=45)
            if response.status_code == 200 and len(response.content) > 1000:
                logger.info("Image generated via Pollinations.ai (turbo).")
                return response.content
            else:
                logger.warning(f"Pollinations.ai (turbo) returned status {response.status_code}")
        except Exception as e:
            logger.warning(f"Pollinations.ai (turbo) failed: {e}")

        # 4. Last resort: return None so the caller can show a friendly error
        logger.error("All providers and fallbacks failed to generate image.")
        return None
