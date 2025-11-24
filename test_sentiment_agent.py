"""Test SentimentAgent LLM-based emotion analysis."""

from Agents import SentimentAgent


def test_sentiment_analysis():
    """Test SentimentAgent with various text examples including negations."""
    print("=" * 70)
    print("TESTING SENTIMENT AGENT - LLM-BASED ANALYSIS")
    print("=" * 70)
    
    agent = SentimentAgent()
    
    test_cases = [
        {
            "text": "Oggi è stata una giornata fantastica! Sono al settimo cielo, tutto è andato benissimo.",
            "expected": {"happiness": "high", "stress": "low", "energy": "high"},
            "description": "Positive day - should detect high happiness"
        },
        {
            "text": "Non sono per niente felice. Mi sento triste e abbattuto.",
            "expected": {"happiness": "low", "stress": "medium-high"},
            "description": "Negation test - 'non felice' should = low happiness"
        },
        {
            "text": "Sono stressatissimo, pieno di ansia e non riesco a dormire.",
            "expected": {"stress": "high", "calm": "low", "energy": "low"},
            "description": "High stress - should detect anxiety"
        },
        {
            "text": "Mi sento arrabbiato e frustrato per come sono andate le cose.",
            "expected": {"anger": "high", "stress": "medium-high"},
            "description": "Anger - should detect frustration"
        },
        {
            "text": "Giornata tranquilla, ho lavorato con calma e costanza.",
            "expected": {"calm": "high", "stress": "low", "motivation": "medium"},
            "description": "Calm day - should detect serenity"
        },
        {
            "text": "Sono esausto, non ho più energie. Vorrei solo dormire.",
            "expected": {"energy": "low", "stress": "medium"},
            "description": "Low energy - exhaustion"
        },
    ]
    
    print("\nAnalyzing test cases...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"[Test {i}] {test_case['description']}")
        print(f"Text: \"{test_case['text'][:70]}...\"" if len(test_case['text']) > 70 else f"Text: \"{test_case['text']}\"")
        
        try:
            scores = agent.analyze_entry(test_case['text'])
            
            print(f"Results:")
            print(f"  Stress:      {scores['stress']:.1f}/10")
            print(f"  Happiness:   {scores['happiness']:.1f}/10")
            print(f"  Anger:       {scores['anger']:.1f}/10")
            print(f"  Energy:      {scores['energy']:.1f}/10")
            print(f"  Calm:        {scores['calm']:.1f}/10")
            print(f"  Motivation:  {scores['motivation']:.1f}/10")
            
            # Validate expectations
            expected = test_case['expected']
            validation_passed = True
            
            for emotion, level in expected.items():
                score = scores[emotion]
                if level == "high" and score < 6:
                    print(f"  [!] Expected high {emotion} (>6), got {score:.1f}")
                    validation_passed = False
                elif level == "low" and score > 4:
                    print(f"  [!] Expected low {emotion} (<4), got {score:.1f}")
                    validation_passed = False
                elif level == "medium-high" and score < 5:
                    print(f"  [!] Expected medium-high {emotion} (>5), got {score:.1f}")
                    validation_passed = False
            
            status = "[OK]" if validation_passed else "[REVIEW]"
            print(f"{status} Analysis completed")
            
        except Exception as e:
            print(f"[FAIL] Error: {e}")
        
        print()
    
    print("=" * 70)
    print("SENTIMENT AGENT TESTING COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    test_sentiment_analysis()
