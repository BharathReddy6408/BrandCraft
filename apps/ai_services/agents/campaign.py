import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class CampaignAgent:
    @staticmethod
    def execute(project: BrandProject, user_request: str) -> Dict[str, Any]:
        context = BrandContextService.build_context(project)
        system_prompt = "You are a Campaign Manager. Return JSON: 'campaign_name', 'objective', 'theme', 'content_plan'."
        prompt = f"Context: {json.dumps(context)}\nRequest: {user_request}"
        return AIService.generate_structured(prompt=prompt, system_message=system_prompt) or {}


