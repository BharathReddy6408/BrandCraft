from ai_services.services import AIService
from ai_services.image_service import BrandAssetGenerationService
from ai_services.agents import MarketingAgent, SocialMediaAgent, CampaignAgent

class CopilotTools:
    @staticmethod
    def execute_generation(project, user, intent: str, module: str, request: str, asset_type: str):
        """
        Dynamically executes the correct generation pipeline based on the intent and module.
        """
        if intent == "CREATE_BRAND":
            # Generate a full suite of brand assets
            assets_to_gen = ['logo', 'brand_board', 'business_card']
            return BrandAssetGenerationService.generate_multi_asset_package(project, user, assets_to_gen)
            
        elif intent in ["GENERATE_BRAND_VISUAL", "GENERATE_LOGO", "GENERATE_BRAND_BOARD", "GENERATE_PROMOTIONAL_ASSET", "REDESIGN_UI", "REFINE_ASSET"]:
            assets_to_gen = [asset_type] if asset_type else ['brand_board']
            return BrandAssetGenerationService.generate_multi_asset_package(project, user, assets_to_gen)
            
        elif intent in ["GENERATE_MARKETING_CONTENT"]:
            return MarketingAgent.execute(project, request)
            
        elif intent in ["GENERATE_SOCIAL_MEDIA"]:
            return SocialMediaAgent.execute(project, request)
            
        elif intent in ["GENERATE_CAMPAIGN"]:
            return CampaignAgent.execute(project, request)
            
        return {"error": "Unsupported generation request"}
