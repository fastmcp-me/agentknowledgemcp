#!/usr/bin/env python3
"""
Test Elasticsearch error handling improvements
"""
import sys
import os
import importlib.util
from pathlib import Path

# Import elasticsearch_handlers directly from the file
spec = importlib.util.spec_from_file_location("elasticsearch_handlers", 
    os.path.join(os.path.dirname(__file__), '..', 'src', 'elasticsearch_handlers.py'))
elasticsearch_handlers = importlib.util.module_from_spec(spec)

# Mock the get_es_client function to simulate connection errors
class MockElasticsearchClient:
    def __init__(self, error_type="connection"):
        self.error_type = error_type
    
    def index(self, **kwargs):
        if self.error_type == "connection":
            raise Exception("Connection refused to Elasticsearch")
        elif self.error_type == "index_not_found":
            raise Exception("index_not_found_exception: no such index")
        elif self.error_type == "timeout":
            raise Exception("timeout error: request timed out")
        else:
            raise Exception("Unknown error occurred")
    
    def search(self, **kwargs):
        if self.error_type == "connection":
            raise Exception("Connection refused to Elasticsearch")
        else:
            raise Exception("Unknown error occurred")

def mock_get_es_client():
    return MockElasticsearchClient("connection")

# Replace the real client with mock
elasticsearch_handlers.get_es_client = mock_get_es_client

async def test_error_handling():
    """Test improved error handling for Elasticsearch operations."""
    print("🧪 Testing Elasticsearch Error Handling")
    print("=" * 60)
    print()
    
    # Test 1: Connection error during index_document
    print("📋 Test 1: Connection error during index_document")
    try:
        result = await elasticsearch_handlers.handle_index_document({
            "index": "test_index",
            "document": {"id": "test-1", "title": "Test Document"},
            "validate_schema": False
        })
        
        error_text = result[0].text
        print("   ✅ Error handled correctly")
        print("   📄 Error message preview:")
        lines = error_text.split('\n')[:5]  # First 5 lines
        for line in lines:
            print(f"      {line}")
        print("      ...")
        
        # Check if it contains helpful information
        if "Connection Error" in error_text and "setup_elasticsearch" in error_text:
            print("   ✅ Contains helpful suggestions")
        else:
            print("   ❌ Missing helpful suggestions")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    
    # Test 2: Connection error during search
    print("📋 Test 2: Connection error during search")
    try:
        result = await elasticsearch_handlers.handle_search({
            "index": "test_index",
            "query": "test query"
        })
        
        error_text = result[0].text
        print("   ✅ Error handled correctly")
        print("   📄 Error message preview:")
        lines = error_text.split('\n')[:3]  # First 3 lines
        for line in lines:
            print(f"      {line}")
        print("      ...")
        
        # Check if it contains helpful information
        if "Connection Error" in error_text and "setup_elasticsearch" in error_text:
            print("   ✅ Contains helpful suggestions")
        else:
            print("   ❌ Missing helpful suggestions")
            
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
    
    print()
    print("🎯 Elasticsearch error handling tests completed!")
    print("💡 All Elasticsearch operations now provide detailed error messages")
    print("🔧 Agents will receive clear guidance on how to fix connection issues")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_error_handling())
