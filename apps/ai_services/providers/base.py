from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class AIResult:
    success: bool
    content: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAIProvider:
    @property
    def provider_name(self) -> str:
        raise NotImplementedError

    def generate_text(self, prompt: str, system_message: str = "") -> AIResult:
        raise NotImplementedError

    def health_check(self) -> bool:
        """Returns True if configured and reachable."""
        raise NotImplementedError
