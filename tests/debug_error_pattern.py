#!/usr/bin/env python3
"""
Debug test: Analyze the actual error message to understand why pattern matching fails.
"""

def debug_error_pattern():
    """Debug the error message pattern matching."""
    
    # This is the actual error message we received:
    error_message = "NotFoundError(404, 'index_not_found_exception', 'no such index [definitely_nonexistent_index_test_12345]', definitely_nonexistent_index_test_12345, index_or_alias)"
    
    print("🔍 ERROR MESSAGE ANALYSIS")
    print("=" * 50)
    print(f"Original error: {error_message}")
    print()
    
    error_str = str(error_message).lower()
    print(f"Lowercase error: {error_str}")
    print()
    
    # Test each pattern condition
    print("📋 PATTERN MATCHING TESTS:")
    print("-" * 30)
    
    # Test individual conditions
    has_connection = "connection" in error_str or "refused" in error_str
    print(f"Connection error: {'✅' if has_connection else '❌'} - {'connection' in error_str} or {'refused' in error_str}")
    
    has_index_not_found = "index" in error_str and "not found" in error_str
    print(f"Index not found: {'✅' if has_index_not_found else '❌'} - {'index' in error_str} and {'not found' in error_str}")
    
    has_index_exception = "index_not_found_exception" in error_str
    print(f"Index exception: {'✅' if has_index_exception else '❌'} - {'index_not_found_exception' in error_str}")
    
    has_no_such_index = "no such index" in error_str
    print(f"No such index: {'✅' if has_no_such_index else '❌'} - {'no such index' in error_str}")
    
    # Test the combined condition
    combined_condition = ("index" in error_str and "not found" in error_str) or "index_not_found_exception" in error_str or "no such index" in error_str
    print(f"Combined condition: {'✅' if combined_condition else '❌'}")
    
    print()
    print("🔧 RECOMMENDED FIX:")
    if has_index_exception or has_no_such_index:
        print("✅ Pattern should match! The error contains the expected patterns.")
        print("📍 Issue might be in the order of conditions or logic flow.")
    else:
        print("❌ Pattern doesn't match. Need to add new patterns.")
        print(f"📍 Consider adding pattern for: {error_str}")

if __name__ == "__main__":
    debug_error_pattern()
