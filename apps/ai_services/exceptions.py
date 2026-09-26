class AIProviderError(Exception):
    """Raised when an AI provider fails."""
    pass

class AIConfigurationError(Exception):
    """Raised when no AI providers are configured properly."""
    pass

class AIGenerationError(Exception):
    """Raised when the AI fails to generate the requested content."""
    pass
