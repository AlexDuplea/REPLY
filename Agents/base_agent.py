class BaseAgent:
    """Base class for all agents providing common configuration.
    
    Attributes:
        name (str): Identifier for the agent.
        config (dict): Configuration dictionary, e.g., Gemini settings.
    """
    def __init__(self, name: str = "BaseAgent", config: dict | None = None):
        self.name = name
        self.config = config or {}

    def configure(self, **kwargs):
        """Update configuration parameters."""
        self.config.update(kwargs)

    def run(self, *args, **kwargs):
        """Placeholder run method to be overridden by subclasses."""
        raise NotImplementedError("Subclasses should implement this method.")
