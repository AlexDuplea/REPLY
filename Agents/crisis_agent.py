import re
from dataclasses import dataclass
from .base_agent import BaseAgent


@dataclass
class CrisisResult:
    """Structured result for crisis detection."""
    is_crisis: bool
    response_text: str


class CrisisAgent(BaseAgent):
    """Agent handling crisis detection and response.

    Level 1: Regex-based quick detection to catch crisis keywords.
    Level 2 (optional): Semantic check via Gemini API for context verification.
    
    This agent acts as the first absolute filter - no message reaches ChatAgent
    if this agent detects a genuine crisis.
    """
    
    def __init__(self, name: str = "CrisisAgent", config: dict | None = None):
        super().__init__(name, config)
        # Configuration flags
        self.enable_semantic: bool = self.config.get("enable_semantic", False)
        self.semantic_model: str = self.config.get("semantic_model", "gemini-2.0-flash-lite")
        
        # Compile regex patterns for level 1 detection
        # These patterns are designed to avoid false positives like "muoio dal ridere"
        self.regex_patterns = [
            r"\b(voglio\s+(morire|uccidermi|farla finita))\b",
            r"\b(pensieri?\s+suicid[aei])\b",
            r"\b(non\s+voglio\s+(più\s+)?vivere)\b",
            r"\b(suicid(io|armi))\b",
            r"\b(farla\s+finita)\b",
        ]
        self.compiled_regex = [re.compile(p, re.IGNORECASE) for p in self.regex_patterns]

    def _regex_check(self, message: str) -> bool:
        """Level 1: Quick regex-based detection.
        
        Returns True if any crisis pattern is detected.
        """
        return any(pattern.search(message) for pattern in self.compiled_regex)

    def _semantic_check(self, message: str) -> bool:
        """Level 2: AI-powered semantic check for crisis verification.
        
        Makes a quick API call to Gemini with temperature=0 to determine
        if the message expresses genuine self-harm or suicidal intent.
        
        Args:
            message: The user's message to analyze
            
        Returns:
            True if genuine crisis detected, False otherwise
        """
        try:
            import google.generativeai as genai
            import os
            from dotenv import load_dotenv
            
            # Load API key
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                # Fallback to keyword check if API key not available
                print("[WARNING] GEMINI_API_KEY not found, falling back to keyword check")
                keywords = [
                    "suicidio",
                    "non voglio vivere",
                    "voglio morire",
                    "pensieri suicidi",
                    "non riesco a farcela",
                ]
                lowered = message.lower()
                return any(k in lowered for k in keywords)
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Create model with temperature=0 for deterministic responses
            model = genai.GenerativeModel(
                model_name=self.semantic_model,
                generation_config={
                    "temperature": 0,  # Deterministic output
                    "max_output_tokens": 10,  # Just need "SI" or "NO"
                }
            )
            
            # Prompt for yes/no crisis detection
            prompt = f"""Analizza il seguente testo scritto da un utente.

L'utente esprime una REALE intenzione di autolesionismo o suicidio?

Rispondi SOLO con "SI" o "NO". Nient'altro.

IMPORTANTE:
- "SI" solo se c'è chiara intenzione di farsi del male
- "NO" se è un'espressione figurata (es. "muoio dal ridere")
- "NO" se esprime solo tristezza o difficoltà senza intenti suicidi

Testo: "{message}"

Risposta:"""
            
            # Make API call
            response = model.generate_content(prompt)
            answer = response.text.strip().upper()
            
            # Parse response
            is_crisis = "SI" in answer or "SÌ" in answer or "YES" in answer
            
            print(f"[DEBUG] Semantic check for '{message[:50]}...': {answer} -> {'CRISIS' if is_crisis else 'SAFE'}")
            
            return is_crisis
            
        except Exception as e:
            # Log error and fallback to safe default (assume crisis to be safe)
            print(f"[ERROR] Semantic check failed: {e}")
            # When in doubt, treat as crisis for safety
            return True

    def detect_crisis(self, message: str) -> CrisisResult:
        """Run the two-level detection pipeline and return a CrisisResult.
        
        Args:
            message: The user's input message to analyze
            
        Returns:
            CrisisResult with is_crisis flag and appropriate response text
        """
        # Level 1: Regex check
        level1_triggered = self._regex_check(message)
        is_crisis = False
        
        if level1_triggered:
            # If semantic check is enabled, verify with AI
            if self.enable_semantic:
                is_crisis = self._semantic_check(message)
            else:
                # Without semantic check, trust regex detection
                is_crisis = True
        
        # Generate appropriate response
        if is_crisis:
            response = (
                "[!] Sei in pericolo. Ti preghiamo di contattare immediatamente:\n\n"
                "[IT] Numero di emergenza: 112\n"
                "[HELP] Telefono Amico: 02 2327 2327\n"
                "[SOS] Supporto salute mentale: 800-822-132\n\n"
                "Non sei solo/a. Chiedi aiuto ora."
            )
        else:
            response = ""
            
        return CrisisResult(is_crisis=is_crisis, response_text=response)

    def run(self, message: str, *args, **kwargs) -> CrisisResult | None:
        """Process a message through crisis detection.
        
        If a crisis is detected, returns a CrisisResult that should block
        further processing by other agents (ChatAgent, etc.).
        
        Args:
            message: User's input message
            
        Returns:
            CrisisResult if crisis detected, None otherwise
        """
        result = self.detect_crisis(message)
        if result.is_crisis:
            # Block further agent processing
            return result
        # Allow message to proceed to other agents
        return None
