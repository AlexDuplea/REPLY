from .base_agent import BaseAgent
from typing import Dict, Optional
import json


class SentimentAgent(BaseAgent):
    """Agent for analyzing sentiment from journal entries using LLM.
    
    Replaces keyword-based emotion detection with qualitative LLM analysis.
    Handles negations ("Non sono triste"), understands nuances ("Sono al settimo cielo").
    
    Returns structured emotion scores (0-10) for:
    - Stress
    - Happiness  
    - Anger
    - Energy
    - Calm
    - Motivation
    """
    
    def __init__(self, name: str = "SentimentAgent", config: dict | None = None):
        super().__init__(name, config)
        self.model_name = self.config.get("model", "gemini-2.0-flash-lite")
        
    def analyze_entry(self, entry_text: str) -> dict:
        """Analyze a journal entry and extract sentiment scores using LLM.
        
        Args:
            entry_text: The journal entry text to analyze
            
        Returns:
            Dictionary with sentiment scores:
            {
                'stress': float (0-10),
                'happiness': float (0-10),
                'anger': float (0-10),
                'energy': float (0-10),
                'calm': float (0-10),
                'motivation': float (0-10)
            }
        """
        try:
            import google.generativeai as genai
            import os
            from dotenv import load_dotenv
            
            # Load API key
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                # Fallback to default/neutral scores
                print("[WARNING] GEMINI_API_KEY not found, returning neutral scores")
                return self._get_neutral_scores()
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Create model for sentiment analysis
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.3,  # Fairly consistent scoring
                    "max_output_tokens": 100,  # Just need JSON response
                }
            )
            
            # Prompt for JSON sentiment analysis
            prompt = f"""Analizza il seguente testo di diario e valuta le emozioni dell'utente.

Testo: "{entry_text}"

Valuta da 0 a 10 (dove 0 = assente, 10 = molto intenso):
- Stress: livello di stress/ansia
- Happiness: felicità/gioia
- Anger: rabbia/frustrazione
- Energy: energia fisica/mentale
- Calm: calma/serenità
- Motivation: motivazione/determinazione

IMPORTANTE:
- Comprendi le negazioni ("Non sono felice" = bassa felicità)
- Comprendi le sfumature ("al settimo cielo" = alta felicità)
- Considera il contesto complessivo, non solo le parole

Rispondi SOLO con un oggetto JSON valido in questo formato:
{{"stress": 5, "happiness": 7, "anger": 2, "energy": 6, "calm": 5, "motivation": 7}}

JSON:"""
            
            # Make API call
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean response (remove markdown if present)
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            scores = json.loads(response_text)
            
            # Validate and clamp scores to 0-10 range
            validated_scores = {}
            for emotion in ['stress', 'happiness', 'anger', 'energy', 'calm', 'motivation']:
                value = scores.get(emotion, 5)
                validated_scores[emotion] = max(0, min(10, float(value)))
            
            return validated_scores
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] SentimentAgent JSON parse failed: {e}")
            print(f"[ERROR] Response was: {response_text[:200]}")
            return self._get_neutral_scores()
            
        except Exception as e:
            print(f"[ERROR] SentimentAgent analysis failed: {e}")
            return self._get_neutral_scores()
    
    def _get_neutral_scores(self) -> dict:
        """Return neutral/default scores when analysis fails."""
        return {
            'stress': 5.0,
            'happiness': 6.0,
            'anger': 2.0,
            'energy': 5.5,
            'calm': 5.0,
            'motivation': 6.0
        }
    
    def analyze_text_with_context(self, entry_text: str, previous_scores: Optional[Dict] = None) -> dict:
        """Analyze entry with optional context from previous analysis.
        
        Args:
            entry_text: Entry text to analyze
            previous_scores: Optional previous day's scores for context
            
        Returns:
            Sentiment scores dictionary
        """
        # For now, simply analyze without context
        # Future enhancement: include previous_scores in prompt for better continuity
        return self.analyze_entry(entry_text)
    
    def run(self, entry_text: str, *args, **kwargs) -> dict:
        """Process an entry and return sentiment analysis.
        
        Args:
            entry_text: Journal entry text
            
        Returns:
            Dictionary with emotion scores (0-10)
        """
        return self.analyze_entry(entry_text)

