#!/usr/bin/env python3
"""
Real-world test: Search a non-existent index to verify server returns suggestions.
"""

import asyncio
import sys
import os

# Add the parent directory to the Python path to access src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.elasticsearch_handlers import handle_search

async def test_real_search_nonexistent_index():
    """Test real search with non-existent index to verify suggestions are returned."""
    
    print("🧪 REAL-WORLD TEST: Search Non-Existent Index")
    print("=" * 60)
    print("Testing if server returns 4-step agent guidance for non-existent index...")
    print()
    
    # Test with completely non-existent index
    test_index = "nonexistent_test_index_12345"
    
    print(f"📍 Testing search with non-existent index: '{test_index}'")
    print(f"🔍 Query: 'test search'")
    print()
    
    try:
        # Perform the actual search
        result = await handle_search({
            "index": test_index,
            "query": "test search",
            "size": 10
        })
        
        print("📄 SERVER RESPONSE:")
        print("-" * 40)
        for content in result:
            response_text = content.text
            print(response_text)
            
            # Check if response contains the expected 4-step guidance
            has_suggestions = "Suggestions for agents" in response_text
            has_4_steps = all(step in response_text for step in ["1.", "2.", "3.", "4."])
            has_list_indices = "list_indices" in response_text
            has_index_error = "Index Error" in response_text or "Index Not Found" in response_text
            
            print()
            print("✅ VALIDATION RESULTS:")
            print(f"   🎯 Contains agent suggestions: {'✅' if has_suggestions else '❌'}")
            print(f"   📝 Has 4-step guidance: {'✅' if has_4_steps else '❌'}")
            print(f"   🛠️  Mentions list_indices tool: {'✅' if has_list_indices else '❌'}")
            print(f"   📁 Identifies as index error: {'✅' if has_index_error else '❌'}")
            
            all_checks_pass = has_suggestions and has_4_steps and has_list_indices and has_index_error
            print(f"   🏆 OVERALL TEST RESULT: {'✅ PASS' if all_checks_pass else '❌ FAIL'}")
            
            if all_checks_pass:
                print()
                print("🎉 SUCCESS: Server correctly returns 4-step agent guidance!")
                print("📋 Error handling enhancement is working as expected.")
            else:
                print()
                print("⚠️  WARNING: Some expected suggestions are missing.")
                print("📋 Error handling may need further improvement.")
    
    except Exception as e:
        print(f"❌ TEST ERROR: {str(e)}")
        print("📋 Could not complete the test due to technical issues.")
    
    print()
    print("=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_real_search_nonexistent_index())
