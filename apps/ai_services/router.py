# ai_services/router.py

from enum import Enum

class Intent(Enum):
    CREATE_BRAND = "CREATE_BRAND"
    MODIFY_BRAND = "MODIFY_BRAND"
    GENERATE_NAME = "GENERATE_NAME"
    GENERATE_LOGO = "GENERATE_LOGO"
    GENERATE_BRAND_VISUAL = "GENERATE_BRAND_VISUAL"
    GENERATE_COLOR_PALETTE = "GENERATE_COLOR_PALETTE"
    GENERATE_BRAND_GUIDELINES = "GENERATE_BRAND_GUIDELINES"
    GENERATE_MARKETING = "GENERATE_MARKETING"
    GENERATE_SOCIAL = "GENERATE_SOCIAL"
    GENERATE_CAMPAIGN = "GENERATE_CAMPAIGN"
    GENERATE_AD = "GENERATE_AD"
    GENERATE_PACKAGING = "GENERATE_PACKAGING"
    GENERATE_POSTER = "GENERATE_POSTER"
    GENERATE_BUSINESS_CARD = "GENERATE_BUSINESS_CARD"
    GENERATE_CONTENT = "GENERATE_CONTENT"
    REFINE_ASSET = "REFINE_ASSET"
    EXPLAIN_MODULE = "EXPLAIN_MODULE"
    CREATE_REPORT = "CREATE_REPORT"
    EXPORT_BRAND = "EXPORT_BRAND"
    OUT_OF_DOMAIN = "OUT_OF_DOMAIN"
    
    # Legacy/Mapping Support
    NAMING_GENERATION = "NAMING_GENERATION"
    SLOGAN_GENERATION = "SLOGAN_GENERATION"
    BRAND_IDENTITY_GENERATION = "BRAND_IDENTITY_GENERATION"
    LOGO_GENERATION = "LOGO_GENERATION"
    MARKETING_GENERATION = "MARKETING_GENERATION"
    SOCIAL_MEDIA_GENERATION = "SOCIAL_MEDIA_GENERATION"
    CAMPAIGN_GENERATION = "CAMPAIGN_GENERATION"
    BRAND_GUIDELINE_GENERATION = "BRAND_GUIDELINE_GENERATION"
    PROMOTIONAL_ASSET = "PROMOTIONAL_ASSET"
    BRAND_CONTEXT_QUERY = "BRAND_CONTEXT_QUERY"
    CAMPAIGN_HISTORY = "CAMPAIGN_HISTORY"
    ANALYTICS_QUERY = "ANALYTICS_QUERY"
    BRAND_INSIGHT = "BRAND_INSIGHT"
    MODULE_NAVIGATION = "MODULE_NAVIGATION"
    GENERAL_CHAT = "GENERAL_CHAT"

BRAND_MODULES = {
    "branding": {
        "name": "Brand Strategy",
        "route": "branding:project_detail",
        "intents": [Intent.BRAND_CONTEXT_QUERY, Intent.BRAND_INSIGHT]
    },
    "naming": {
        "name": "Business Name Generator",
        "route": "branding:project_detail", # Assuming it's part of strategy
        "intents": [Intent.NAMING_GENERATION]
    },
    "logo_generator": {
        "name": "Logo Studio",
        "route": "branding:logo_studio",
        "intents": [Intent.LOGO_GENERATION]
    },
    "brand_identity": {
        "name": "Brand Identity",
        "route": "branding:brand_identity",
        "intents": [Intent.BRAND_IDENTITY_GENERATION, Intent.SLOGAN_GENERATION]
    },
    "marketing": {
        "name": "Marketing Studio",
        "route": "branding:marketing_studio",
        "intents": [Intent.MARKETING_GENERATION, Intent.PROMOTIONAL_ASSET]
    },
    "socialmedia": {
        "name": "Social Studio",
        "route": "branding:social_studio",
        "intents": [Intent.SOCIAL_MEDIA_GENERATION]
    },
    "campaigns": {
        "name": "Campaign Studio",
        "route": "branding:campaign_studio",
        "intents": [Intent.CAMPAIGN_GENERATION, Intent.CAMPAIGN_HISTORY]
    },
    "brand_reports": {
        "name": "Executive Reports",
        "route": "branding:reports",
        "intents": [Intent.BRAND_GUIDELINE_GENERATION]
    },
    "analytics": {
        "name": "Brand Analytics",
        "route": "branding:analytics",
        "intents": [Intent.ANALYTICS_QUERY]
    }
}

class CopilotRouter:
    @staticmethod
    def get_module_for_intent(intent: Intent):
        for module_id, module_info in BRAND_MODULES.items():
            if intent in module_info.get("intents", []):
                return module_id, module_info
        return None, None
