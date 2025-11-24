"""
Orchestrator - Coordinates all agents in Mental Wellness Journal
Responsabilità: Gestire il flusso sequenziale delle chiamate agli agenti
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Agents.base_agent import BaseAgent
from Agents.crisis_agent import CrisisAgent, CrisisResult
from Agents.context_agent import ContextAgent
from Agents.chat_agent import ChatAgent
from Agents.sentiment_agent import SentimentAgent
from storage import Storage
from typing import Dict, Optional, List
from datetime import date
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WellnessOrchestrator(BaseAgent):
    """Orchestrates the complete mental wellness interaction flow.
    
    Workflow:
    1. Safety Check (CrisisAgent) - BLOCKING
    2. Context Building (ContextAgent) 
    3. Response Generation (ChatAgent)
    4. Emotion Analysis (SentimentAgent) - Can be async
    5. Persistence (Storage)
    
    This keeps app.py clean by centralizing agent coordination logic.
    """
    
    def __init__(self, name: str = "WellnessOrchestrator", config: dict | None = None):
        super().__init__(name, config)
        
        # Extract configuration
        api_key = self.config.get("api_key")
        enable_semantic_crisis = self.config.get("enable_semantic_crisis", True)
        
        if not api_key:
            raise ValueError("API key required in config")
        
        # Initialize storage
        self.storage = Storage()
        
        # Initialize agents
        self.crisis_agent = CrisisAgent(config={
            "enable_semantic": enable_semantic_crisis
        })
        
        self.context_agent = ContextAgent(config={
            "max_entries": 7,
            "model": "gemini-2.0-flash-lite"
        })
        
        self.chat_agent = ChatAgent(config={
            "api_key": api_key,
            "model": "gemini-2.0-flash-lite",
            "temperature": 0.7,
            "max_tokens": 500
        })
        
        self.sentiment_agent = SentimentAgent(config={
            "model": "gemini-2.0-flash-lite"
        })
        
        # Session state
        self.session_active = False
        self.user_name = None
        
        logger.info(f"✅ {self.name} initialized with all agents")
    
    def start_session(self, user_name: Optional[str] = None) -> Dict:
        """Start a new wellness journal session.
        
        Args:
            user_name: Optional user name for personalization
            
        Returns:
            Dict with:
                - success: bool
                - greeting: str (AI greeting message)
                - context_loaded: bool
        """
        logger.info(f"🚀 Starting session for user: {user_name or 'Anonymous'}")
        
        try:
            self.user_name = user_name
            
            # 1. Build context from recent entries
            logger.info("📖 Loading context from recent entries...")
            context = self.context_agent.prepare_system_prompt_context(
                self.storage, 
                num_days=3
            )
            
            context_loaded = bool(context)
            
            # 2. Start chat session with context
            logger.info("💬 Initializing chat agent...")
            greeting = self.chat_agent.start_session(
                user_name=user_name,
                system_context=context
            )
            
            self.session_active = True
            
            logger.info("✅ Session started successfully")
            
            return {
                "success": True,
                "greeting": greeting,
                "context_loaded": context_loaded
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting session: {e}")
            return {
                "success": False,
                "error": str(e),
                "greeting": "Ciao! Come è andata la giornata?"  # Fallback
            }
    
    def handle_interaction(self, user_message: str) -> Dict:
        """Process user message through complete agent pipeline.
        
        This is the MAIN method that coordinates all agents.
        
        Args:
            user_message: User's input text
            
        Returns:
            Dict with:
                - success: bool
                - crisis_detected: bool
                - response: str (AI response or crisis message)
                - should_end: bool (if conversation should terminate)
                - journal_entry: str (if session ended)
                - emotions: dict (if session ended)
                - metadata: dict (additional info)
        """
        if not self.session_active:
            return {
                "success": False,
                "error": "Session not started. Call start_session() first."
            }
        
        logger.info(f"📨 Processing message: '{user_message[:50]}...'")
        
        # ===== STEP 1: SAFETY CHECK (BLOCKING) =====
        logger.info("🚨 Step 1: Crisis detection...")
        crisis_result = self.crisis_agent.run(user_message)
        
        if crisis_result:
            logger.warning("⚠️  CRISIS DETECTED - Stopping pipeline")
            
            # End session immediately
            self.session_active = False
            
            return {
                "success": True,
                "crisis_detected": True,
                "response": crisis_result.response_text,
                "should_end": True,
                "metadata": {
                    "blocked_by": "CrisisAgent",
                    "reason": "Safety concern detected"
                }
            }
        
        logger.info("✅ Message cleared by CrisisAgent")
        
        # ===== STEP 2: CONTEXT REFRESH (OPTIONAL) =====
        # For now, context is loaded at session start
        # Future: Could refresh context mid-conversation if needed
        
        # ===== STEP 3: GENERATE RESPONSE =====
        logger.info("💬 Step 2: Generating conversational response...")
        
        try:
            response = self.chat_agent.chat(user_message)
        except Exception as e:
            logger.error(f"❌ Error in ChatAgent: {e}")
            return {
                "success": False,
                "error": f"Failed to generate response: {str(e)}"
            }
        
        # ===== STEP 4: CHECK IF SESSION ENDING =====
        should_end = user_message.lower().strip() in ["fine", "basta", "stop", "termina"]
        
        if should_end:
            logger.info("🏁 Session ending - generating journal entry...")
            return self._end_session(response)
        
        # ===== STEP 5: EMOTION ANALYSIS (ASYNC - for stats) =====
        # Run sentiment analysis in background for real-time stats
        # This doesn't block the response
        try:
            emotions = self.sentiment_agent.analyze_entry(user_message)
            logger.info(f"😊 Emotions detected: {emotions}")
        except Exception as e:
            logger.warning(f"⚠️  Sentiment analysis failed: {e}")
            emotions = {}
        
        # ===== RETURN RESPONSE =====
        return {
            "success": True,
            "crisis_detected": False,
            "response": response,
            "should_end": False,
            "emotions": emotions,
            "metadata": {
                "message_count": len([m for m in self.chat_agent.get_conversation_history() 
                                     if m["role"] == "user"])
            }
        }
    
    def _end_session(self, final_response: str) -> Dict:
        """Handle session termination: generate journal, analyze emotions, save.
        
        Args:
            final_response: The AI's final summary/goodbye message
            
        Returns:
            Dict with session end results
        """
        logger.info("📝 Ending session - generating journal entry and saving...")
        
        today = date.today().isoformat()
        
        try:
            # 1. Check if entry exists today
            existing_entry = self.storage.get_today_entry_text()
            
            # 2. Generate journal entry
            logger.info("📖 Generating journal entry...")
            journal_entry = self.chat_agent.generate_journal_entry(
                existing_entry=existing_entry
            )
            
            # 3. Analyze emotions from journal entry
            logger.info("😊 Analyzing emotions...")
            emotions = self.sentiment_agent.analyze_entry(journal_entry)
            
            # 4. Save conversation
            logger.info("💾 Saving conversation history...")
            conversation = self.chat_agent.get_conversation_history()
            self.storage.save_conversation(conversation, today)
            
            # 5. Save journal entry with emotions
            logger.info("💾 Saving journal entry...")
            metadata = {
                "source": "chat",
                "emotions_detected": emotions,
                "message_count": len([m for m in conversation if m["role"] == "user"])
            }
            self.storage.save_entry(journal_entry, metadata=metadata, entry_date=today)
            
            # 6. Update streak
            logger.info("🔥 Updating streak...")
            streak_info = self.storage.update_streak()
            
            # 7. Reset session
            self.session_active = False
            self.chat_agent.reset_session()
            
            logger.info("✅ Session ended successfully")
            
            return {
                "success": True,
                "crisis_detected": False,
                "response": final_response,
                "should_end": True,
                "journal_entry": journal_entry,
                "emotions": emotions,
                "streak": streak_info['current_streak'],
                "new_milestone": streak_info.get('new_milestone'),
                "metadata": {
                    "entries_saved": 1,
                    "streak_continued": streak_info.get('streak_continued', False)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error ending session: {e}")
            
            # Still try to end gracefully
            self.session_active = False
            
            return {
                "success": False,
                "error": f"Failed to save session: {str(e)}",
                "response": final_response,
                "should_end": True
            }
    
    def force_end_session(self) -> Dict:
        """Force end current session (for emergency/cleanup).
        
        Returns:
            Dict with minimal session data
        """
        logger.warning("⚠️  Force ending session (no save)")
        
        self.session_active = False
        self.chat_agent.reset_session()
        
        return {
            "success": True,
            "message": "Session force-ended without saving"
        }
    
    def get_session_status(self) -> Dict:
        """Get current session status.
        
        Returns:
            Dict with session info
        """
        if not self.session_active:
            return {
                "active": False,
                "message": "No active session"
            }
        
        conversation = self.chat_agent.get_conversation_history()
        user_messages = [m for m in conversation if m["role"] == "user"]
        
        return {
            "active": True,
            "user_name": self.user_name,
            "message_count": len(user_messages),
            "conversation_length": len(conversation)
        }
    
    def run(self, user_message: str, *args, **kwargs) -> Dict:
        """Standard run method for BaseAgent compatibility.
        
        Args:
            user_message: User's input
            
        Returns:
            Result dict from handle_interaction
        """
        if not self.session_active:
            # Auto-start session if needed
            self.start_session()
        
        return self.handle_interaction(user_message)


# ===== CONVENIENCE FUNCTIONS =====

def create_orchestrator(api_key: str, enable_semantic_crisis: bool = True) -> WellnessOrchestrator:
    """Factory function to create configured orchestrator.
    
    Args:
        api_key: Gemini API key
        enable_semantic_crisis: Enable Level 2 semantic crisis detection
        
    Returns:
        Configured WellnessOrchestrator instance
    """
    return WellnessOrchestrator(config={
        "api_key": api_key,
        "enable_semantic_crisis": enable_semantic_crisis
    })