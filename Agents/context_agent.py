from .base_agent import BaseAgent
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class ContextAgent(BaseAgent):
    """Agent responsible for managing contextual information across sessions.
    
    Centralizes memory management by:
    - Retrieving recent journal entries intelligently
    - Creating structured summaries instead of raw text dumps
    - Preparing context strings for injection into ChatAgent system prompts
    - Saving token usage by summarizing instead of passing full entries
    """
    
    def __init__(self, name: str = "ContextAgent", config: dict | None = None):
        super().__init__(name, config)
        self.max_entries = self.config.get("max_entries", 7)  # Last N days
        self.summary_model = self.config.get("model", "gemini-2.0-flash-lite")
        
    def get_context_for_chat(self, storage, num_days: int = 3) -> str:
        """Get structured context for ChatAgent system prompt.
        
        Args:
            storage: Storage instance to retrieve entries
            num_days: Number of recent days to include
            
        Returns:
            Formatted context string ready for injection into system prompt
        """
        # Retrieve recent entries
        entries = storage.get_recent_entries(num_days=num_days)
        
        if not entries:
            return None
            
        # Create structured summary
        summary = self._create_structured_summary(entries)
        
        return summary
    
    def _create_structured_summary(self, entries: List[Dict]) -> str:
        """Create a structured summary of recent entries.
        
        Instead of dumping full text (wastes tokens), creates concise summaries:
        "3 days ago: User anxious about exam (Stress: 8/10). 
         Yesterday: Exam passed, mood high."
        
        Args:
            entries: List of entry dictionaries
            
        Returns:
            Structured summary string
        """
        if not entries:
            return ""
            
        summary_parts = ["Recent context from user's journal:\n"]
        
        # Sort by date (oldest first for chronological order)
        sorted_entries = sorted(entries, key=lambda x: x['date'])
        
        for entry_data in sorted_entries:
            entry_date = entry_data['date']
            entry_text = entry_data['entry']
            metadata = entry_data.get('metadata', {})
            
            # Calculate days ago
            try:
                entry_dt = datetime.fromisoformat(entry_date.split('T')[0])
                today = datetime.now()
                days_ago = (today - entry_dt).days
                
                if days_ago == 0:
                    time_label = "Today"
                elif days_ago == 1:
                    time_label = "Yesterday"
                else:
                    time_label = f"{days_ago} days ago"
            except:
                time_label = entry_date
            
            # Extract key information using AI summarization
            brief_summary = self._summarize_entry(entry_text, metadata)
            
            # Add to context
            summary_parts.append(f"- {time_label}: {brief_summary}")
        
        return "\n".join(summary_parts)
    
    def _summarize_entry(self, entry_text: str, metadata: dict) -> str:
        """Summarize a single entry concisely.
        
        Uses Gemini API to create 1-sentence summary with emotion scores.
        
        Args:
            entry_text: Full entry text
            metadata: Entry metadata (emotions, etc.)
            
        Returns:
            Brief summary (e.g., "Anxious about exam. Stress: 8/10")
        """
        try:
            import google.generativeai as genai
            import os
            from dotenv import load_dotenv
            
            # Load API key
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            
            if not api_key:
                # Fallback: use first sentence + emotions
                first_sentence = entry_text.split('.')[0] + '.'
                emotions = metadata.get('emotions_detected', {})
                if emotions:
                    stress = emotions.get('stress', 0)
                    happiness = emotions.get('happiness', 0)
                    return f"{first_sentence[:100]} (Stress: {stress}, Happy: {happiness})"
                return first_sentence[:150]
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Create model for summarization
            model = genai.GenerativeModel(
                model_name=self.summary_model,
                generation_config={
                    "temperature": 0.3,  # Fairly deterministic
                    "max_output_tokens": 50,  # Very brief
                }
            )
            
            # Prompt for 1-sentence summary
            emotions = metadata.get('emotions_detected', {})
            emotion_context = ""
            if emotions:
                emotion_context = f"\nEmotions detected: {emotions}"
            
            prompt = f"""Summarize this journal entry in ONE sentence (max 15 words).
Focus on the main topic/feeling.

Entry: "{entry_text[:300]}"
{emotion_context}

Summary:"""
            
            # Make API call
            response = model.generate_content(prompt)
            summary = response.text.strip()
            
            # Add emotion scores if available
            if emotions:
                stress = min(emotions.get('stress', 0) * 2, 10)
                happiness = min(emotions.get('happiness', 0) * 2, 10)
                if stress > 0 or happiness > 0:
                    summary += f" (Stress: {stress}/10" if stress > 0 else ""
                    summary += f", Happy: {happiness}/10" if happiness > 0 else ""
                    summary += ")" if (stress > 0 or happiness > 0) else ""
            
            return summary
            
        except Exception as e:
            # Fallback: use first 2 sentences
            print(f"[WARN] ContextAgent summarization failed: {e}")
            sentences = entry_text.split('.')[:2]
            return '. '.join(sentences) + '.'
    
    def prepare_system_prompt_context(self, storage, num_days: int = 3) -> str:
        """Prepare the exact context string to inject into ChatAgent's system_instruction.
        
        This method relieves ChatAgent from context building responsibility.
        
        Args:
            storage: Storage instance
            num_days: Number of recent days to include
            
        Returns:
            Context string formatted for system prompt injection
        """
        context = self.get_context_for_chat(storage, num_days)
        
        if not context:
            return ""
        
        # Format for system prompt injection
        formatted = f"""
=== USER BACKGROUND ===
{context}

Use this background to provide more personalized, contextual responses.
Reference past entries when relevant, but don't over-do it.
===
"""
        return formatted
    
    def run(self, storage, num_days: int = 3, *args, **kwargs) -> str:
        """Process context retrieval and return formatted string.
        
        Args:
            storage: Storage instance
            num_days: Number of days to include
            
        Returns:
            Formatted context string
        """
        return self.prepare_system_prompt_context(storage, num_days)
