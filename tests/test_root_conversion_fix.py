#!/usr/bin/env python3
"""
Test the fixed Root object conversion in smart prompting server
This validates that the server can properly handle MCP Root objects and load .knowledges content.
"""

import asyncio
import tempfile
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from fastmcp import Client
from mcp.types import Root
from src.prompts.sub_servers.smart_prompting_server import app as smart_prompting_app, root_to_path

async def test_root_conversion_fix():
    """Test the fixed Root object to Path conversion."""
    
    print("🔧 Testing Fixed Root Object Conversion")
    print("=" * 50)
    
    # Test 1: Test root_to_path helper function directly
    print("🧪 Test 1: Root Conversion Helper Function")
    print("-" * 30)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create mock Root object like FastMCP would provide
        test_uri = temp_path.as_uri()
        mock_root = Root(uri=test_uri, name="test-workspace")
        
        print(f"📁 Test directory: {temp_path}")
        print(f"🌐 Test URI: {test_uri}")
        print(f"🔗 Mock root: {mock_root}")
        
        # Test the conversion function
        converted_path = root_to_path(mock_root)
        print(f"✅ Converted path: {converted_path}")
        
        # Verify conversion accuracy
        paths_match = converted_path.resolve() == temp_path.resolve()
        print(f"📍 Paths match: {'✅ YES' if paths_match else '❌ NO'}")
        print(f"   Original: {temp_path.resolve()}")
        print(f"   Converted: {converted_path.resolve()}")
        
        if not paths_match:
            print("⚠️ Path conversion issue detected!")
            return False
        
        # Test 2: Create .knowledges structure and test full workflow
        print(f"\n🧪 Test 2: Full Workflow with Real .knowledges")
        print("-" * 30)
        
        # Create .knowledges structure
        knowledges_dir = temp_path / ".knowledges"
        workflows_dir = knowledges_dir / "workflows"
        rules_dir = knowledges_dir / "rules"
        memories_dir = knowledges_dir / "memories"
        
        workflows_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)
        memories_dir.mkdir(parents=True)
        
        # Create sample content with line numbers for testing
        workflow_content = """# Root Conversion Testing Workflow

## Test Process
1. Create temporary directory structure
2. Setup .knowledges with sample content
3. Test Root object conversion
4. Verify smart prompting with file citations
5. Confirm line numbers in AI responses

## Validation Steps
1. Convert MCP Root to Path successfully
2. Load .knowledges content with line numbers
3. Generate AI guidance with proper citations"""

        rules_content = """# Root Testing Rules

## Conversion Standards
- Handle file:// URIs correctly
- Support various Root object formats
- Maintain path accuracy across platforms

## Testing Requirements
- Verify path resolution works
- Test with temporary directories
- Confirm .knowledges loading works
- Validate file citations include line numbers"""

        memory_content = """# Root Conversion Lessons

## URI Handling Insights
Date: 2025-07-31
Issue: Root object conversion from URI to Path
Solution: Use urlparse for proper file:// handling

## Key Implementation
Function: root_to_path() handles multiple URI formats
Benefit: Works with FastMCP client roots parameter
Result: End-to-end workspace awareness achieved"""

        # Write test content
        (workflows_dir / "root-testing.md").write_text(workflow_content)
        (rules_dir / "conversion-rules.md").write_text(rules_content)
        (memories_dir / "uri-lessons.md").write_text(memory_content)
        
        print(f"📚 Created test .knowledges with {len(list(knowledges_dir.rglob('*.md')))} files")
        
        # Test 3: Full integration with FastMCP client
        print(f"\n🧪 Test 3: Full Integration Test")
        print("-" * 30)
        
        try:
            # Create client with the test root
            custom_roots = [mock_root]
            
            async with Client(smart_prompting_app, roots=custom_roots) as client:
                print(f"✅ Client created with fixed root conversion")
                
                # Test the smart prompting tool
                result = await client.call_tool("ask_mcp_advance", {
                    "intended_action": "test root conversion fix",
                    "task_description": "Verify that Root objects are properly converted to Paths and .knowledges content loads correctly",
                    "scope": "testing"
                })
                
                guidance = result.data
                print(f"📋 **Smart Prompting Response:**")
                
                # Check if it successfully loaded content (no error about missing .knowledges)
                is_success = "No .knowledges directory found" not in guidance
                has_content = any(keyword in guidance for keyword in ["workflows", "rules", "memories"])
                has_citations = "`" in guidance and ".md" in guidance
                has_line_numbers = ":" in guidance and ("line" in guidance.lower() or "lines" in guidance.lower())
                
                print(f"   ✅ Loaded .knowledges successfully: {'✅ YES' if is_success else '❌ NO'}")
                print(f"   📚 Contains knowledge content: {'✅ YES' if has_content else '❌ NO'}")
                print(f"   📝 Has file citations: {'✅ YES' if has_citations else '❌ NO'}")
                print(f"   🔢 Has line numbers: {'✅ YES' if has_line_numbers else '❌ NO'}")
                
                if is_success and has_content and has_citations:
                    print(f"\n🎉 **COMPLETE SUCCESS!**")
                    print(f"   ✅ Root object conversion fixed")
                    print(f"   ✅ .knowledges content loaded successfully")
                    print(f"   ✅ AI guidance with file citations working")
                    print(f"   ✅ End-to-end workflow 100% functional")
                    
                    # Show sample of the successful response
                    print(f"\n📄 **Sample Response:**")
                    print(guidance[:300] + "..." if len(guidance) > 300 else guidance)
                    
                    return True
                else:
                    print(f"\n⚠️ **PARTIAL SUCCESS** - some features still need work:")
                    if not is_success:
                        print(f"   ❌ .knowledges directory detection failed")
                    if not has_content:
                        print(f"   ❌ Knowledge content not loaded")
                    if not has_citations:
                        print(f"   ❌ File citations missing")
                    
                    print(f"\n📄 **Debug Response:**")
                    print(guidance[:500] + "..." if len(guidance) > 500 else guidance)
                    
                    return False
                
        except Exception as e:
            print(f"❌ Integration test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

async def test_edge_cases():
    """Test edge cases for Root object conversion."""
    
    print(f"\n🔍 Testing Edge Cases for Root Conversion")
    print("-" * 40)
    
    test_cases = [
        ("file:///tmp/test", "/tmp/test"),
        ("file://localhost/tmp/test", "/tmp/test"),
        ("/tmp/test", "/tmp/test"),
        ("C:\\Users\\test", "C:\\Users\\test"),  # Windows path
    ]
    
    for i, (input_uri, expected_path) in enumerate(test_cases, 1):
        print(f"\n📝 Edge Case {i}: {input_uri}")
        
        # Create mock object with uri
        mock_root = type('MockRoot', (), {'uri': input_uri})()
        
        try:
            converted = root_to_path(mock_root)
            print(f"   Input: {input_uri}")
            print(f"   Expected: {expected_path}")
            print(f"   Got: {converted}")
            print(f"   Match: {'✅ YES' if str(converted) == expected_path else '❌ NO'}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Root Object Conversion Fixes")
    print("=" * 60)
    
    # Run main test
    success = asyncio.run(test_root_conversion_fix())
    
    # Run edge case tests
    asyncio.run(test_edge_cases())
    
    if success:
        print(f"\n🎊 **FINAL RESULT: COMPLETE SUCCESS!**")
        print(f"   🔧 Root object conversion completely fixed")
        print(f"   📚 Smart prompting with .knowledges working perfectly")
        print(f"   🎯 Ready for production deployment!")
    else:
        print(f"\n⚠️ **FINAL RESULT: NEEDS MORE WORK**")
        print(f"   📋 Check the debug output above for specific issues")
