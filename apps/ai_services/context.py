from typing import Dict, Any

from ai_services.services import AIService

class BrandContextService:
    @staticmethod
    def extract_from_message(message_content: str) -> Dict[str, Any]:
        """
        Uses an LLM to extract potential brand name, industry, and style from user message.
        """
        system_prompt = (
            "Extract brand information from the user request.\n"
            "Respond ONLY with a JSON object containing keys: 'business_name', 'industry', 'style', 'colors'.\n"
            "If a key is not found, leave its value as null."
        )
        data = AIService.generate_structured(prompt=message_content, system_message=system_prompt)
        return data if isinstance(data, dict) else {}

    @staticmethod
    def build_context(project) -> Dict[str, Any]:
        """
        Builds a standardized dictionary of the Brand DNA that all 
        AI prompts and agents will consume.
        """
        # Fetch selected or generated assets for enriched context
        selected_logo = project.assets.filter(asset_type='LOGO', is_selected=True).first()
        color_asset = project.assets.filter(asset_type='COLOR').first()
        font_asset = project.assets.filter(asset_type='TYPOGRAPHY').first()
        
        # Override project fields with asset fields if they exist
        colors = {
            "primary": project.primary_color,
            "secondary": project.secondary_color,
            "accent": project.accent_color,
            "background": project.background_color
        }
        if color_asset and isinstance(color_asset.content_json, dict):
            colors.update(color_asset.content_json)
            
        fonts = {
            "heading": project.heading_font,
            "body": project.body_font
        }
        if font_asset and isinstance(font_asset.content_json, dict):
            fonts.update(font_asset.content_json)
            
        # Add Marketing & Social Context (Recent 3)
        recent_marketing = project.marketing_contents.filter(status='APPROVED').order_by('-created_at')[:3]
        recent_social = project.social_posts.filter(status='APPROVED').order_by('-created_at')[:3]
            
        return {
            "business_name": project.business_name or "Unknown",
            "business_idea": project.business_idea or "Unknown",
            "industry": project.industry or "Unknown",
            "target_audience": project.target_audience or "Unknown",
            "business_goal": project.business_goal or "Unknown",
            "personality": project.brand_personality or "Unknown",
            "voice": project.brand_voice or "Unknown",
            "mission": project.brand_mission or "Unknown",
            "vision": project.brand_vision or "Unknown",
            "values": project.brand_values or [],
            "usp": project.usp or "Unknown",
            "keywords": project.keywords or [],
            "visual_style": project.preferred_style or "Unknown",
            "colors": colors,
            "typography": fonts,
            "has_primary_logo": bool(selected_logo),
            "recent_marketing_titles": [m.title for m in recent_marketing],
            "recent_social_topics": [s.title for s in recent_social]
        }
        
    @staticmethod
    def get_context(project_id) -> Dict[str, Any]:
        """
        Helper method to fetch a project by ID and return its context.
        """
        from branding.models import BrandProject
        try:
            project = BrandProject.objects.get(id=project_id)
            return BrandContextService.build_context(project)
        except BrandProject.DoesNotExist:
            return {}

    @staticmethod
    def build_summary_context(project) -> Dict[str, Any]:
        """
        Builds a highly compressed version of the Brand DNA for token-efficient
        chat orchestration.
        """
        return {
            "business_name": project.business_name or "Unknown",
            "industry": project.industry or "Unknown",
            "target_audience": project.target_audience or "Unknown",
            "personality": project.brand_personality or "Unknown",
            "visual_style": project.preferred_style or "Unknown",
            "voice": project.brand_voice or "Unknown",
        }
