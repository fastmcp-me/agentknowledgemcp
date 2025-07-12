#!/usr/bin/env python3
"""
Simple test to verify our pattern matching works with exact error message.
"""

def test_pattern_matching_with_real_error():
    """Test pattern matching with the exact error we received."""
    
    print("🧪 TESTING PATTERN MATCHING WITH REAL ERROR")
    print("=" * 55)
    
    # The exact error message from our test
    real_error = "NotFoundError(404, 'index_not_found_exception', 'no such index [definitely_nonexistent_index_test_12345]', definitely_nonexistent_index_test_12345, index_or_alias)"
    index = "definitely_nonexistent_index_test_12345"
    
    # Simulate the exact logic from handle_search
    error_message = "❌ Search failed:\n\n"
    error_str = str(real_error).lower()
    
    print(f"Testing with error: {real_error}")
    print(f"Lowercase version: {error_str}")
    print()
    
    # Apply the exact same logic as in handle_search
    if "connection" in error_str or "refused" in error_str:
        error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
        result = "Connection Error Path"
    elif ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str:
        error_message += f"📁 **Index Error**: Index '{index}' does not exist\n"
        error_message += f"📍 The search index has not been created yet\n"
        error_message += f"💡 **Suggestions for agents**:\n"
        error_message += f"   1. Use 'list_indices' tool to see all available indices\n"
        error_message += f"   2. Check which indices contain your target data\n"
        error_message += f"   3. Use the correct index name from the list\n"
        error_message += f"   4. If no suitable index exists, create one with 'create_index' tool\n\n"
        result = "Index Error Path (SUCCESS!)"
    elif "timeout" in error_str:
        error_message += "⏱️ **Timeout Error**: Search query timed out\n"
        result = "Timeout Error Path"
    elif "parse" in error_str or "query" in error_str:
        error_message += f"🔍 **Query Error**: Invalid search query format\n"
        result = "Query Error Path"
    else:
        error_message += f"⚠️ **Unknown Error**: {str(real_error)}\n\n"
        result = "Unknown Error Path (PROBLEM!)"
    
    print(f"🎯 RESULT: {result}")
    print()
    print("📄 GENERATED ERROR MESSAGE:")
    print("-" * 40)
    print(error_message)
    
    # Check for key components
    has_suggestions = "Suggestions for agents" in error_message
    has_4_steps = all(step in error_message for step in ["1.", "2.", "3.", "4."])
    has_list_indices = "list_indices" in error_message
    
    print("✅ VALIDATION:")
    print(f"   Has agent suggestions: {'✅' if has_suggestions else '❌'}")
    print(f"   Has 4-step guidance: {'✅' if has_4_steps else '❌'}")
    print(f"   Mentions list_indices: {'✅' if has_list_indices else '❌'}")
    
    success = result == "Index Error Path (SUCCESS!)" and has_suggestions and has_4_steps
    print(f"   Overall success: {'✅' if success else '❌'}")

if __name__ == "__main__":
    test_pattern_matching_with_real_error()
