import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class SocialMediaAgent:
    @staticmethod
    def execute(project: BrandProject, user_request: str) -> list:
        context = BrandContextService.build_context(project)
        system_prompt = "You are a Social Media Manager. Return JSON with a list of 'posts', each containing 'platform', 'content', and 'visual_concept'."
        prompt = f"Context: {json.dumps(context)}\nRequest: {user_request}"
        result = AIService.generate_structured(prompt=prompt, system_message=system_prompt)
        return result.get("posts", []) if result else []


