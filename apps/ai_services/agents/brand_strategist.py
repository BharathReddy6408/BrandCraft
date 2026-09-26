import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class BrandStrategistAgent:
    @staticmethod
    def execute(project: BrandProject, user_request: str) -> Dict[str, Any]:
        """Creates the foundational strategy."""
        system_prompt = (
            "You are an elite Brand Strategist AI. Extract core brand strategy from the user's idea.\n"
            "Return JSON: business_name, tagline, brand_mission, brand_vision, target_audience, "
            "brand_personality, brand_voice, primary_color, secondary_color, typography_style."
        )
        prompt = f"User Request: {user_request}\nGenerate strategy."
        result = AIService.generate_structured(prompt=prompt, system_message=system_prompt)
        
        if result and isinstance(result, dict):
            project.business_name = result.get('business_name', project.business_name)
            project.business_idea = user_request
            project.brand_mission = result.get('brand_mission', '')
            project.brand_vision = result.get('brand_vision', '')
            project.target_audience = result.get('target_audience', '')
            project.brand_personality = result.get('brand_personality', '')
            project.brand_voice = result.get('brand_voice', '')
            project.primary_color = result.get('primary_color', '')
            project.secondary_color = result.get('secondary_color', '')
            project.save()
            return result
        return {}


class BrandModificationAgent:
    @staticmethod
    def execute(project: BrandProject, user_request: str) -> Dict[str, Any]:
        """Modifies an existing brand context based on user feedback."""
        context = BrandContextService.build_context(project)
        context_str = json.dumps(context, indent=2)
        system_prompt = (
            "You are a Brand Modification AI. The user wants to change an aspect of their current brand.\n"
            "Analyze the current brand context and the user's request.\n"
            "Update ONLY the fields that need to change. Preserve the rest.\n"
            "Return ONLY a valid JSON object matching the BrandContext schema:\n"
            "business_name, tagline, brand_story, brand_mission, brand_vision, "
            "target_audience, brand_personality, brand_voice, "
            "primary_color, secondary_color, typography_style."
        )
        prompt = f"Current Brand Context:\n{context_str}\n\nUser Request: {user_request}\n\nReturn the updated JSON."
        result = AIService.generate_structured(prompt=prompt, system_message=system_prompt)
        
        if result and isinstance(result, dict):
            project.business_name = result.get('business_name', project.business_name)
            project.brand_mission = result.get('brand_mission', project.brand_mission)
            project.brand_vision = result.get('brand_vision', project.brand_vision)
            project.target_audience = result.get('target_audience', project.target_audience)
            project.brand_personality = result.get('brand_personality', project.brand_personality)
            project.brand_voice = result.get('brand_voice', project.brand_voice)
            project.primary_color = result.get('primary_color', project.primary_color)
            project.secondary_color = result.get('secondary_color', project.secondary_color)
            project.save()
            return result
        return {"error": "Failed to modify brand strategy"}


