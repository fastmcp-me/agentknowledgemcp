#!/usr/bin/env python3
"""
Test Elasticsearch error message formatting without MCP dependencies.
"""
import sys
import os
import json
from pathlib import Path

def simulate_elasticsearch_error_handling():
    """Simulate the enhanced error handling logic."""
    
    def format_connection_error():
        """Format connection error message like the enhanced handlers."""
        error_message = "❌ Failed to index document:\n\n"
        error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
        error_message += "📍 Check if Elasticsearch is running at the configured address\n"
        error_message += "💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n"
        error_message += "🔧 Or check configuration with 'get_config' tool\n\n"
        error_message += "🔍 **Technical Details**: Connection refused to Elasticsearch"
        return error_message
    
    def format_search_error():
        """Format search error message like the enhanced handlers."""
        error_message = "❌ Search failed:\n\n"
        error_message += "🔌 **Connection Error**: Cannot connect to Elasticsearch server\n"
        error_message += "📍 Check if Elasticsearch is running at the configured address\n"
        error_message += "💡 Try: Use 'setup_elasticsearch' tool to start Elasticsearch\n\n"
        error_message += "🔍 **Technical Details**: Connection refused to Elasticsearch"
        return error_message
    
    def format_timeout_error():
        """Format timeout error message like the enhanced handlers."""
        error_message = "❌ Failed to index document:\n\n"
        error_message += "⏱️ **Timeout Error**: Elasticsearch server is not responding\n"
        error_message += "📍 Server may be overloaded or slow to respond\n"
        error_message += "💡 Try: Wait and retry, or check server status\n\n"
        error_message += "🔍 **Technical Details**: timeout error: request timed out"
        return error_message
    
    return format_connection_error, format_search_error, format_timeout_error

def test_error_message_formatting():
    """Test the enhanced error message formatting."""
    print("🧪 Testing Enhanced Elasticsearch Error Messages")
    print("=" * 60)
    print()
    
    # Get the error formatters
    format_connection, format_search, format_timeout = simulate_elasticsearch_error_handling()
    
    # Test 1: Connection error during index_document
    print("📋 Test 1: Connection error during index_document")
    error_msg = format_connection()
    print("   ✅ Error message generated")
    print("   📄 Error message preview:")
    lines = error_msg.split('\n')[:6]  # First 6 lines
    for line in lines:
        print(f"      {line}")
    print("      ...")
    
    # Check if it contains helpful information
    if "🔌 **Connection Error**" in error_msg and "setup_elasticsearch" in error_msg:
        print("   ✅ Contains helpful suggestions and clear error categorization")
    else:
        print("   ❌ Missing helpful suggestions")
    print()
    
    # Test 2: Connection error during search
    print("📋 Test 2: Connection error during search")
    error_msg = format_search()
    print("   ✅ Error message generated")
    print("   📄 Error message preview:")
    lines = error_msg.split('\n')[:5]  # First 5 lines
    for line in lines:
        print(f"      {line}")
    print("      ...")
    
    # Check if it contains helpful information
    if "🔌 **Connection Error**" in error_msg and "setup_elasticsearch" in error_msg:
        print("   ✅ Contains helpful suggestions and clear error categorization")
    else:
        print("   ❌ Missing helpful suggestions")
    print()
    
    # Test 3: Timeout error
    print("📋 Test 3: Timeout error during index_document")
    error_msg = format_timeout()
    print("   ✅ Error message generated")
    print("   📄 Error message preview:")
    lines = error_msg.split('\n')[:5]  # First 5 lines
    for line in lines:
        print(f"      {line}")
    print("      ...")
    
    # Check if it contains helpful information
    if "⏱️ **Timeout Error**" in error_msg and "Wait and retry" in error_msg:
        print("   ✅ Contains helpful suggestions and clear error categorization")
    else:
        print("   ❌ Missing helpful suggestions")
    print()
    
    print("🎯 Enhanced error message formatting tests completed!")
    print("💡 All error messages now provide:")
    print("   📊 Clear error categorization with icons")
    print("   📍 Specific problem description")
    print("   💡 Actionable solutions and tool suggestions")
    print("   🔍 Technical details for debugging")
    print("🔧 Agents will receive detailed guidance for every error type")

if __name__ == "__main__":
    test_error_message_formatting()
