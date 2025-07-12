#!/usr/bin/env python3
"""Test script to verify error pattern matching improvements."""

def test_error_patterns():
    """Test the enhanced error pattern matching logic."""
    
    # Test cases for different error message formats
    test_errors = [
        "index_not_found_exception: no such index [my_index]",
        "IndexNotFoundError: no such index",
        "The index [knowledge_base] does not exist",
        "Index not found: knowledge_base",
        "NOT_FOUND exception in elasticsearch",
        "Connection refused",
        "permission denied",
        "mapping error occurred"
    ]
    
    print("🧪 Testing Enhanced Error Pattern Matching")
    print("=" * 50)
    
    for i, error_msg in enumerate(test_errors, 1):
        print(f"\n{i}. Testing error: '{error_msg}'")
        error_str = error_msg.lower()
        
        # Apply the enhanced pattern matching logic
        if "connection" in error_str or "refused" in error_str:
            result = "🔌 Connection Error detected"
        elif ("not_found" in error_str or "not found" in error_str or "does not exist" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
            # Check if it's specifically an index not found error
            if ("index" in error_str and ("not found" in error_str or "not_found" in error_str or "does not exist" in error_str)) or "index_not_found_exception" in error_str or "no such index" in error_str:
                result = "📁 Index Not Found detected (with 4-step guidance)"
            else:
                result = "📄 Document Not Found detected"
        elif "permission" in error_str or "forbidden" in error_str:
            result = "🔒 Permission Error detected"
        elif "mapping" in error_str or "invalid" in error_str:
            result = "📝 Mapping Error detected"
        else:
            result = "⚠️ Unknown Error (fallback)"
            
        print(f"   → {result}")
    
    print(f"\n✅ Pattern matching test completed!")
    print("📋 Summary: Enhanced patterns now detect:")
    print("   • index_not_found_exception")
    print("   • no such index")
    print("   • traditional not_found/not found patterns")
    print("   • proper index vs document error distinction")

if __name__ == "__main__":
    test_error_patterns()
