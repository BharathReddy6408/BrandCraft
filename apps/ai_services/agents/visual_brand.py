import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class VisualBrandAgent:
    @staticmethod
    def assemble_specific_asset_prompt(project: BrandProject, asset_type: str) -> str:
        """Builds a dynamic image prompt string using the exact BrandContext."""
        context = BrandContextService.build_context(project)
        system_prompt = (
            "You are an elite Image Prompt Engineer.\n"
            "Construct a detailed text-to-image prompt based on the exact Brand DNA and requested asset_type.\n"
            "CRITICAL RULES:\n"
            "1. The visual MUST strongly reflect the industry.\n"
            "2. If asset_type is 'UI', 'DASHBOARD', or 'APP', you MUST prefix the prompt with 'High-fidelity UI design mockup, mobile app screen, dashboard interface, software application'.\n"
            "3. DO NOT use overly poetic or abstract descriptions (like 'leaf vein patterns' or 'river stones') as the image model will draw actual leaves and stones instead of a UI.\n"
            "4. Keep the description focused on UI elements: cards, charts, buttons, sidebars, typography, and clean layouts.\n"
            "Return ONLY a JSON object with a single key 'prompt'."
        )
        prompt = (
            f"Brand Name: {context.get('business_name')}\n"
            f"Industry: {context.get('industry')}\n"
            f"Style: {context.get('visual_style')}\n"
            f"Asset Type Required: {asset_type}\n"
            f"Create the perfect visual description."
        )
        result = AIService.generate_structured(prompt=prompt, system_message=system_prompt)
        if result and isinstance(result, dict) and 'prompt' in result:
            return result['prompt']
        return f'High quality {asset_type} design for {context.get("business_name")}, industry: {context.get("industry")}.'


