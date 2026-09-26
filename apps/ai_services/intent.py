# ai_services/intent.py

import json
from ai_services.services import AIService
from ai_services.router import Intent
from ai_services.module_registry import MODULE_REGISTRY

class IntentDetector:
    @staticmethod
    def detect_intent(message_content: str, conversation_history: list = None) -> dict:
        """
        Uses an LLM call to classify the user's message into an Intent, target module, and asset_type.
        """
        intents_list = [
            "CREATE_BRAND", "GENERATE_BRAND_VISUAL", "GENERATE_LOGO", "GENERATE_BRAND_BOARD", 
            "GENERATE_BRAND_GUIDELINES", "GENERATE_MARKETING_CONTENT", "GENERATE_SOCIAL_MEDIA", 
            "GENERATE_CAMPAIGN", "GENERATE_PROMOTIONAL_ASSET", "REDESIGN_BRAND", "CHANGE_COLORS", 
            "CHANGE_TYPOGRAPHY", "REDESIGN_UI", "UPDATE_BRAND_IDENTITY", "VIEW_BRAND_ASSETS", 
            "VIEW_ANALYTICS", "GENERATE_REPORT", "GENERAL_BRAND_CHAT", "OUT_OF_DOMAIN"
        ]
        intents_str = ", ".join(intents_list)
        
        modules_str = ", ".join(MODULE_REGISTRY.keys())
        
        system_prompt = (
            f"You are the Intent Classification Engine for the BrandCraft AI Copilot.\n"
            f"Your job is to analyze the user's request and classify it.\n"
            f"Supported Intents: {intents_str}\n"
            f"Supported Modules: {modules_str}\n\n"
            f"RULES:\n"
            f"1. Respond ONLY with a valid JSON object.\n"
            f"2. The JSON object must match this structure:\n"
            f"   {{\n"
            f"     \"intent\": \"one of the exact intent strings above\",\n"
            f"     \"module\": \"the matching module name from the list above\",\n"
            f"     \"action\": \"create|update|redesign|generate|view\",\n"
            f"     \"asset_type\": \"specific asset type requested (e.g. logo, brand_board, business_card, etc.) or null\",\n"
            f"     \"requires_image\": boolean,\n"
            f"     \"requires_text\": boolean,\n"
            f"     \"requires_database_update\": boolean\n"
            f"   }}\n"
            f"3. CRITICAL STRICT RESTRICTION: This platform ONLY handles brand names, redesigning text colors, generating UI designs, and brand identities. If the user asks for ANYTHING OTHER THAN THIS, you MUST return intent: OUT_OF_DOMAIN.\n"
            f"4. If they are just chatting normally about their brand, return GENERAL_BRAND_CHAT.\n"
        )
        
        try:
            data = AIService.generate_structured(prompt=message_content, system_message=system_prompt)
            if data and isinstance(data, dict):
                return data
            return {"intent": "GENERAL_BRAND_CHAT"}
        except Exception:
            return {"intent": "GENERAL_BRAND_CHAT"}
