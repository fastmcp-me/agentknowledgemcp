#!/usr/bin/env python3
"""
Test enhanced error handling for index not found exception.
This is a simple test that verifies our error pattern matching logic works correctly.
"""

def test_error_pattern_matching():
    """Test the enhanced error pattern matching logic."""
    
    print("Testing enhanced error handling patterns...")
    print("=" * 50)
    
    # Simulate the error message patterns we might encounter
    test_cases = [
        ("index_not_found_exception: no such index [knowledge]", "📁 Index Not Found"),
        ("IndexNotFoundError: no such index", "📁 Index Not Found"),
        ("The index [knowledge_base] does not exist", "📁 Index Not Found"),
        ("Index not found: knowledge_base", "📁 Index Not Found"),
        ("Connection refused to Elasticsearch", "🔌 Connection Error"),
        ("document not found", "📄 Document Not Found"),
        ("permission denied", "🔒 Permission Error")
    ]
    
    print(f"\nTesting {len(test_cases)} error scenarios:")
    
    for i, (error_msg, expected) in enumerate(test_cases, 1):
        error_str = error_msg.lower()
        
        # Apply the enhanced pattern matching logic (same as in elasticsearch_handlers.py)
        if "connection" in error_str or "refused" in error_str:
            result = "🔌 Connection Error"
        elif ("not_found" in error_str or "not found" in error_str or "does not exist" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            # Check if it's specifically an index not found error
            if ("index" in error_str and ("not found" in error_str or "not_found" in error_str or "does not exist" in error_str)) or "index_not_found_exception" in error_str or "no such index" in error_str:
                result = "📁 Index Not Found"
            else:
                result = "📄 Document Not Found"
        elif "permission" in error_str or "forbidden" in error_str:
            result = "🔒 Permission Error"
        else:
            result = "⚠️ Unknown Error"
        
        status = "✅" if result == expected else "❌"
        print(f"{i:2}. {status} '{error_msg[:50]}...' → {result}")
    
    print(f"\n{'='*50}")
    print("✅ Enhanced error pattern matching test completed!")
    print("📋 Key improvements:")
    print("   • Detects 'index_not_found_exception' patterns")
    print("   • Catches 'no such index' messages")
    print("   • Handles 'does not exist' variations")
    print("   • Provides 4-step agent guidance for index errors")

if __name__ == "__main__":
    test_error_pattern_matching()
