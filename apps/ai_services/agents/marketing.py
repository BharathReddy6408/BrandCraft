import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class MarketingAgent:
    @staticmethod
    def execute(project: BrandProject, user_request: str) -> Dict[str, Any]:
        context = BrandContextService.build_context(project)
        system_prompt = "You are a Marketing Copywriter. Return JSON with 'marketing_copy' and 'title'."
        prompt = f"Context: {json.dumps(context)}\nRequest: {user_request}"
        return AIService.generate_structured(prompt=prompt, system_message=system_prompt) or {}


