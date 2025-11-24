"""Test script to verify agent implementations."""

from Agents import (
    CrisisAgent,
    CrisisResult,
    SentimentAgent,
    ChatAgent,
    ContextAgent,
    Orchestrator
)


def test_crisis_agent():
    """Test CrisisAgent with various messages."""
    print("=" * 60)
    print("TESTING CRISIS AGENT")
    print("=" * 60)
    
    agent = CrisisAgent(config={"enable_semantic": False})
    
    test_messages = [
        "Ciao, oggi mi sento un po' triste",
        "Voglio morire, non ce la faccio più",
        "Muoio dal ridere! Che giornata fantastica!",
        "Ho pensieri suicidi ultimamente",
        "Mi sento davvero giù oggi",
    ]
    
    for msg in test_messages:
        result = agent.run(msg)
        print(f"\nMessage: {msg}")
        if result:
            print(f"[!] CRISIS DETECTED!")
            print(f"Response: {result.response_text[:100]}...")
        else:
            print("[OK] No crisis detected - message safe to proceed")



def test_sentiment_agent():
    """Test SentimentAgent."""
    print("\n" + "=" * 60)
    print("TESTING SENTIMENT AGENT")
    print("=" * 60)
    
    agent = SentimentAgent()
    entry = "Oggi è stata una giornata difficile. Mi sento sopraffatto dal lavoro."
    
    result = agent.run(entry)
    print(f"\nEntry: {entry}")
    print(f"Sentiment scores: {result}")


def test_chat_agent():
    """Test ChatAgent."""
    print("\n" + "=" * 60)
    print("TESTING CHAT AGENT")
    print("=" * 60)
    
    agent = ChatAgent()
    message = "Mi sento molto ansioso ultimamente"
    
    response = agent.run(message)
    print(f"\nUser: {message}")
    print(f"Agent: {response}")


def test_orchestration():
    """Test basic orchestration flow."""
    print("\n" + "=" * 60)
    print("TESTING ORCHESTRATION")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = Orchestrator()
    
    # Register agents
    crisis_agent = CrisisAgent(config={"enable_semantic": False})
    chat_agent = ChatAgent()
    
    orchestrator.register_agent(crisis_agent)
    orchestrator.register_agent(chat_agent)
    
    # Test with crisis message
    crisis_msg = "Non voglio più vivere"
    print(f"\nProcessing crisis message: '{crisis_msg}'")
    crisis_result = crisis_agent.run(crisis_msg)
    
    if crisis_result:
        print("[STOPPED] Crisis detected - blocking ChatAgent")
        print(f"Response: {crisis_result.response_text[:100]}...")
    else:
        print("[OK] No crisis - proceeding to ChatAgent")
        chat_response = chat_agent.run(crisis_msg)
        print(f"ChatAgent response: {chat_response}")
    
    # Test with safe message
    safe_msg = "Oggi mi sento un po' triste"
    print(f"\nProcessing safe message: '{safe_msg}'")
    crisis_result = crisis_agent.run(safe_msg)
    
    if crisis_result:
        print("[STOPPED] Crisis detected - blocking ChatAgent")
    else:
        print("[OK] No crisis - proceeding to ChatAgent")
        chat_response = chat_agent.run(safe_msg)
        print(f"ChatAgent response: {chat_response}")


if __name__ == "__main__":
    test_crisis_agent()
    test_sentiment_agent()
    test_chat_agent()
    test_orchestration()
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)
