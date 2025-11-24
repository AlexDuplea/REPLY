"""Test semantic check (Level 2) implementation for CrisisAgent."""

from Agents import CrisisAgent

def test_semantic_check():
    """Test Level 2 semantic check with Gemini API."""
    print("=" * 70)
    print("TESTING CRISIS AGENT - LEVEL 2 SEMANTIC CHECK")
    print("=" * 70)
    
    # Enable semantic check
    agent = CrisisAgent(config={"enable_semantic": True})
    
    test_cases = [
        # Should be detected as crisis
        ("Voglio morire, non ce la faccio più", True, "Real suicidal intent"),
        ("Ho pensieri suicidi ultimamente", True, "Explicit suicidal thoughts"),
        ("Non voglio più vivere", True, "Clear intent to die"),
        
        # Should NOT be detected as crisis (false positives)
        ("Muoio dal ridere! Che giornata fantastica!", False, "Figurative expression"),
        ("Questo esame mi ucciderà", False, "Metaphorical expression"),
        ("Sono stanchissimo, muoio di sonno", False, "Common figure of speech"),
        
        # Edge cases
        ("Mi sento molto triste e solo", False, "Sadness without suicidal intent"),
        ("Non riesco più a farcela con questo stress", False, "Stress without crisis"),
    ]
    
    print("\nTesting messages with Level 2 semantic check enabled...\n")
    
    correct = 0
    total = len(test_cases)
    
    for message, expected_crisis, description in test_cases:
        print(f"Test: {description}")
        print(f"Message: \"{message}\"")
        
        result = agent.run(message)
        detected_crisis = result is not None
        
        status = "[OK]" if detected_crisis == expected_crisis else "[FAIL]"
        outcome = "CRISIS" if detected_crisis else "SAFE"
        expected = "CRISIS" if expected_crisis else "SAFE"
        
        print(f"{status} Expected: {expected}, Got: {outcome}")
        
        if detected_crisis == expected_crisis:
            correct += 1
        else:
            print(f"  [!] MISMATCH - Review this case!")
        
        print()
    
    print("=" * 70)
    print(f"RESULTS: {correct}/{total} correct ({(correct/total)*100:.1f}%)")
    print("=" * 70)


if __name__ == "__main__":
    test_semantic_check()
