#!/usr/bin/env python3
"""
QRAG (Query-Augmented Retrieval Generation) System Demo

This script demonstrates the complete workflow of the QRAG system.
"""

import os
from qrag_system import QRAGSystem

def run_demo():
    """Run QRAG system demo."""
    
    print("🚀 Starting QRAG System Demo!")
    print("=" * 50)
    
    # Initialize QRAG system
    qrag = QRAGSystem()
    
    # Check system status
    print("\n📊 System Status Check:")
    status = qrag.get_system_status()
    for key, value in status.items():
        status_icon = "✅" if value else "❌"
        print(f"  {status_icon} {key}: {value}")
    
    # Test queries
    test_queries = [
        "Generate two Evaluate-level questions about AI in Education based on Bloom's Taxonomy.",
        "Create three Analyze questions for critical thinking in mathematics.",
        "Make one Remember question about reading comprehension.",
        "Design four Apply problems for science education."
    ]
    
    print(f"\n🧪 Testing system with {len(test_queries)} test queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*20} Test {i} {'='*20}")
        print(f"Query: {query}")
        
        # Test query parsing only (works without API keys)
        parsed = qrag.query_parser.parse_query(query)
        print(f"Parsing result:")
        print(f"  - Bloom's Level: {parsed.get('bloom_level', 'N/A')}")
        print(f"  - Topic: {parsed.get('topic', 'N/A')}")
        print(f"  - Quantity: {parsed.get('quantity', 'N/A')}")
        print(f"  - Confidence: {parsed.get('confidence', 0):.2f}")
        
        retrieval_query = qrag.query_parser.generate_retrieval_query(parsed)
        print(f"Retrieval query: {retrieval_query}")
        
        # Test full process if API keys are configured
        if status["openai_configured"] and status["pinecone_configured"]:
            print("\n🔍 Running full QRAG process...")
            result = qrag.process_query(query, top_k=3)
            
            if result["success"]:
                print("✅ Success!")
                print("Generated questions:")
                for j, question in enumerate(result["formatted_questions"], 1):
                    print(f"  {j}. {question}")
            else:
                print(f"❌ Failed: {result['error']}")
        else:
            print("\n⚠️ API keys not configured, skipping full process.")
    
    print(f"\n{'='*50}")
    print("🎉 QRAG System Demo Completed!")
    
    # Usage instructions
    print("\n📖 Usage Instructions:")
    print("1. Create .env file referring to env_example.txt.")
    print("2. Set up OpenAI API key and Pinecone API key.")
    print("3. Run python qrag_system.py to test the complete system.")

def interactive_demo():
    """Run interactive demo."""
    
    print("🎯 QRAG System Interactive Demo")
    print("=" * 40)
    
    qrag = QRAGSystem()
    
    while True:
        print("\nEnter your query (type 'quit' to exit):")
        user_input = input("> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Exiting demo!")
            break
        
        if not user_input:
            continue
        
        print(f"\n🔍 Processing query: {user_input}")
        
        # Query parsing
        parsed = qrag.query_parser.parse_query(user_input)
        print(f"📝 Parsing result: {parsed}")
        
        retrieval_query = qrag.query_parser.generate_retrieval_query(parsed)
        print(f"🔎 Retrieval query: {retrieval_query}")
        
        # Run full process if API keys are available
        status = qrag.get_system_status()
        if status["openai_configured"] and status["pinecone_configured"]:
            result = qrag.process_query(user_input)
            
            if result["success"]:
                print("\n✅ Question generation completed!")
                print("Generated questions:")
                for i, question in enumerate(result["formatted_questions"], 1):
                    print(f"{i}. {question}")
            else:
                print(f"\n❌ Error: {result['error']}")
        else:
            print("\n⚠️ API keys not configured, skipping question generation.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        run_demo() 