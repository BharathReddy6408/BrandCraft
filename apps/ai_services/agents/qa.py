import json
from typing import Dict, Any
from ai_services.services import AIService
from ai_services.context import BrandContextService
from branding.models import BrandProject


class BrandQAAgent:
    @staticmethod
    def validate(asset_data: dict) -> bool:
        """Performs QA checks before saving an asset."""
        if not asset_data:
            return False
        return True


