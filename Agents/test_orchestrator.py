#!/usr/bin/env python3
"""
Test WellnessOrchestrator - Full integration test
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment
load_dotenv()

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from Agents.orchestrator import WellnessOrchestrator, create_orchestrator
from storage import Storage

def test_orchestrator():
    """Test complete orchestrator workflow."""
    print("=" * 70)
    print("TESTING WELLNESS ORCHESTRATOR")
    print("=" * 70)
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    # Create orchestrator
    print("\n[Step 1] Creating orchestrator...")
    try:
        orchestrator = create_orchestrator(
            api_key=api_key,
            enable_semantic_crisis=True
        )
        print("✅ Orchestrator created successfully")
    except Exception as e:
        print(f"❌ Failed to create orchestrator: {e}")
        return
    
    # Start session
    print("\n[Step 2] Starting session...")
    try:
        result = orchestrator.start_session(user_name="Alex")
        
        if result['success']:
            print("✅ Session started")
            print(f"📖 Context loaded: {result.get('context_loaded', False)}")
            print(f"\n💬 Greeting:\n{result['greeting']}\n")
        else:
            print(f"❌ Session start failed: {result.get('error')}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        return
    
    # Test messages
    test_messages = [
        "Oggi è stata una giornata produttiva. Ho lavorato sul progetto di refactoring.",
        "Mi sento soddisfatto dei progressi, anche se un po' stanco.",
        "fine"
    ]
    
    print("\n[Step 3] Testing message flow...")
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Message {i} ---")
        print(f"User: {message}")
        
        try:
            result = orchestrator.handle_interaction(message)
            
            if not result.get('success'):
                print(f"❌ Error: {result.get('error')}")
                continue
            
            # Crisis check
            if result.get('crisis_detected'):
                print("⚠️  CRISIS DETECTED")
                print(f"Response: {result['response'][:100]}...")
                break
            
            # Normal response
            print(f"\nAI: {result['response']}\n")
            
            # Check if ending
            if result.get('should_end'):
                print("\n🏁 SESSION ENDING")
                
                if 'journal_entry' in result:
                    print(f"\n📝 Journal Entry Generated:")
                    print("-" * 70)
                    print(result['journal_entry'])
                    print("-" * 70)
                
                if 'emotions' in result:
                    print(f"\n😊 Emotions Detected:")
                    for emotion, score in result['emotions'].items():
                        print(f"  {emotion}: {score:.1f}/10")
                
                if 'streak' in result:
                    print(f"\n🔥 Current Streak: {result['streak']} days")
                
                if result.get('new_milestone'):
                    milestone = result['new_milestone']
                    print(f"\n🎉 MILESTONE ACHIEVED: {milestone['name']} ({milestone['days']} days)!")
                
                break
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            break
    
    # Check session status
    print("\n[Step 4] Checking final session status...")
    status = orchestrator.get_session_status()
    print(f"Session active: {status.get('active', False)}")
    
    print("\n" + "=" * 70)
    print("ORCHESTRATOR TEST COMPLETE")
    print("=" * 70)


def test_crisis_detection():
    """Test crisis detection in orchestrator."""
    print("\n" + "=" * 70)
    print("TESTING CRISIS DETECTION")
    print("=" * 70)
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API key not found")
        return
    
    orchestrator = create_orchestrator(api_key, enable_semantic_crisis=True)
    orchestrator.start_session()
    
    crisis_messages = [
        "Voglio morire, non ce la faccio più",
        "Ho pensieri suicidi",
    ]
    
    safe_messages = [
        "Muoio dal ridere! Che giornata!",
        "Questo esame mi ucciderà",
    ]
    
    print("\n[Testing Crisis Messages]")
    for msg in crisis_messages:
        print(f"\nMessage: '{msg}'")
        result = orchestrator.handle_interaction(msg)
        
        if result.get('crisis_detected'):
            print("✅ CORRECTLY DETECTED AS CRISIS")
        else:
            print("❌ MISSED - Should have been crisis")
    
    print("\n[Testing Safe Messages]")
    # Need to restart session for each test
    for msg in safe_messages:
        orchestrator.start_session()
        print(f"\nMessage: '{msg}'")
        result = orchestrator.handle_interaction(msg)
        
        if not result.get('crisis_detected'):
            print("✅ CORRECTLY IDENTIFIED AS SAFE")
        else:
            print("❌ FALSE POSITIVE - Should have been safe")


if __name__ == "__main__":
    print("\n🚀 WELLNESS ORCHESTRATOR TEST SUITE\n")
    
    # Test 1: Full workflow
    test_orchestrator()
    
    # Test 2: Crisis detection
    test_crisis_detection()
    
    print("\n✅ ALL TESTS COMPLETED\n")