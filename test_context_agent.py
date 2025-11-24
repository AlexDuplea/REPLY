"""Test ContextAgent implementation."""

from Agents import ContextAgent
from storage import Storage
from datetime import date, timedelta


def test_context_agent():
    """Test ContextAgent context building and summarization."""
    print("=" * 70)
    print("TESTING CONTEXT AGENT")
    print("=" * 70)
    
    # Initialize
    storage = Storage()
    agent = ContextAgent(config={"max_entries": 5})
    
    # Test 1: Get context for chat
    print("\n[Test 1] Getting context for chat (last 3 days)...")
    try:
        context = agent.get_context_for_chat(storage, num_days=3)
        
        if context:
            print("[OK] Context retrieved successfully")
            print(f"\nContext preview (first 300 chars):")
            print("-" * 70)
            print(context[:300] + "..." if len(context) > 300 else context)
            print("-" * 70)
        else:
            print("[INFO] No recent entries found (empty context)")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    # Test 2: Prepare system prompt context
    print("\n[Test 2] Preparing system prompt context...")
    try:
        prompt_context = agent.prepare_system_prompt_context(storage, num_days=3)
        
        if prompt_context:
            print("[OK] System prompt context prepared")
            print(f"\nPrompt context preview (first 400 chars):")
            print("-" * 70)
            print(prompt_context[:400] + "..." if len(prompt_context) > 400 else prompt_context)
            print("-" * 70)
        else:
            print("[INFO] No context to prepare (no recent entries)")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    # Test 3: Run method (convenience wrapper)
    print("\n[Test 3] Testing run() method...")
    try:
        result = agent.run(storage, num_days=3)
        
        if result:
            print("[OK] Run method executed successfully")
            print(f"Result length: {len(result)} characters")
        else:
            print("[INFO] Run returned empty (no recent entries)")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    # Test 4: Check token savings
    print("\n[Test 4] Estimating token savings...")
    try:
        entries = storage.get_recent_entries(num_days=3)
        
        if entries:
            # Calculate raw text length vs summarized length
            raw_length = sum(len(e['entry']) for e in entries)
            summarized_length = len(context) if context else 0
            
            savings_percent = ((raw_length - summarized_length) / raw_length * 100) if raw_length > 0 else 0
            
            print(f"[OK] Token savings analysis:")
            print(f"  Raw entries total: ~{raw_length} chars")
            print(f"  Summarized context: ~{summarized_length} chars")
            print(f"  Savings: ~{savings_percent:.1f}%")
            print(f"  Estimated token reduction: ~{(raw_length - summarized_length) / 4:.0f} tokens")
        else:
            print("[INFO] No entries to analyze")
            
    except Exception as e:
        print(f"[FAIL] Error: {e}")
    
    print("\n" + "=" * 70)
    print("CONTEXT AGENT TESTING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    test_context_agent()
