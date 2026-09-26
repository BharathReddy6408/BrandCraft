# ai_services/module_registry.py

MODULE_REGISTRY = {
    "branding": {
        "keywords": ["brand", "identity", "brand identity", "brand kit", "board"],
        "route": "branding:brand_identity",
        "actions": ["create", "update", "redesign", "generate"]
    },
    "logo_generator": {
        "keywords": ["logo", "brand mark", "symbol", "icon"],
        "route": "branding:logo_studio"
    },
    "creative": {
        "keywords": ["design", "creative", "visual", "poster", "banner", "ui", "mockup", "presentation"],
        "route": "branding:creative_studio"
    },
    "marketing": {
        "keywords": ["marketing", "advertisement", "ad", "copy", "promotion"],
        "route": "branding:marketing_studio"
    },
    "socialmedia": {
        "keywords": ["instagram", "facebook", "linkedin", "social media", "post", "social"],
        "route": "branding:social_studio"
    },
    "campaigns": {
        "keywords": ["campaign", "campaign plan", "marketing campaign"],
        "route": "branding:campaign_studio"
    },
    "brand_reports": {
        "keywords": ["report", "brand report", "guidelines", "strategy", "brand guidelines"],
        "route": "branding:reports"
    },
    "analytics": {
        "keywords": ["analytics", "performance", "statistics"],
        "route": "branding:analytics"
    }
}
