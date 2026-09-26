import os
import requests
from .base import BaseAIProvider, AIResult

class HuggingFaceProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "huggingface"

    def __init__(self):
        self.api_key = os.environ.get('HF_TOKEN')
        # We can use a powerful model like Mixtral or Meta-Llama from HF Inference API
        self.model = os.environ.get('HF_TEXT_MODEL', 'meta-llama/Meta-Llama-3-8B-Instruct')

    def health_check(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, system_message: str = "") -> AIResult:
        if not self.health_check():
            return AIResult(success=False, error="Hugging Face API token not configured.")

        url = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Format for Llama 3 / Instruct models
        formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n{system_message}<|eot_id|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Hugging Face sometimes returns a list, sometimes a dict
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get('generated_text', '')
            elif isinstance(data, dict):
                content = data.get('generated_text', '')
            else:
                return AIResult(success=False, error="Invalid response format from Hugging Face.")
                
            return AIResult(
                success=True,
                content=content.strip(),
                provider=self.provider_name,
                model=self.model
            )
        except Exception as e:
            return AIResult(success=False, error=str(e), provider=self.provider_name, model=self.model)

    def generate_image(self, prompt: str) -> bytes:
        if not self.health_check():
            raise Exception("Hugging Face API token not configured.")
            
        model = os.environ.get('HF_IMAGE_MODEL', 'stabilityai/stable-diffusion-xl-base-1.0')
        url = f"https://router.huggingface.co/hf-inference/models/{model}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=60)
        
        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to generate image: {response.text}")
