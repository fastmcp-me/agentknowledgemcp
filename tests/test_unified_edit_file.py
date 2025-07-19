#!/usr/bin/env python3
"""
Test script for unified edit_file tool
Tests all operations in the consolidated edit_file tool.
"""
import asyncio
import tempfile
import os
from pathlib import Path

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.file.unified_file_server import edit_file

async def test_unified_edit_file():
    """Test all operations of the unified edit_file tool."""
    print("🧪 Testing Unified edit_file Tool\n")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        test_file = test_dir / "test.txt"
        test_copy = test_dir / "test_copy.txt"
        test_move = test_dir / "test_moved.txt"
        test_subdir = test_dir / "subdir"
        
        print(f"📁 Test directory: {test_dir}\n")
        
        # Test 1: Write a file
        print("1️⃣ Testing WRITE operation...")
        result = await edit_file(
            operation="write",
            path=str(test_file),
            content="Hello, this is a test file!\nLine 2\nLine 3"
        )
        print(result)
        print()
        
        # Test 2: Read the file
        print("2️⃣ Testing READ operation...")
        result = await edit_file(
            operation="read",
            path=str(test_file)
        )
        print(result)
        print()
        
        # Test 3: Append to the file
        print("3️⃣ Testing APPEND operation...")
        result = await edit_file(
            operation="append",
            path=str(test_file),
            content="\nAppended line 4\nAppended line 5"
        )
        print(result)
        print()
        
        # Test 4: Get file info
        print("4️⃣ Testing INFO operation...")
        result = await edit_file(
            operation="info",
            path=str(test_file)
        )
        print(result)
        print()
        
        # Test 5: Copy the file
        print("5️⃣ Testing COPY operation...")
        result = await edit_file(
            operation="copy",
            path=str(test_file),
            destination=str(test_copy)
        )
        print(result)
        print()
        
        # Test 6: Move the original file
        print("6️⃣ Testing MOVE operation...")
        result = await edit_file(
            operation="move",
            path=str(test_file),
            destination=str(test_move)
        )
        print(result)
        print()
        
        # Test 7: Create a directory
        print("7️⃣ Testing MKDIR operation...")
        result = await edit_file(
            operation="mkdir",
            path=str(test_subdir)
        )
        print(result)
        print()
        
        # Test 8: List directory contents
        print("8️⃣ Testing LIST operation...")
        result = await edit_file(
            operation="list",
            path=str(test_dir)
        )
        print(result)
        print()
        
        # Test 9: Create a file in subdirectory
        print("9️⃣ Testing nested file creation...")
        nested_file = test_subdir / "nested.txt"
        result = await edit_file(
            operation="write",
            path=str(nested_file),
            content="This is a nested file"
        )
        print(result)
        print()
        
        # Test 10: Recursive directory listing
        print("🔟 Testing RECURSIVE LIST operation...")
        result = await edit_file(
            operation="list",
            path=str(test_dir),
            recursive=True
        )
        print(result)
        print()
        
        # Test 11: Delete a file
        print("1️⃣1️⃣ Testing DELETE operation...")
        result = await edit_file(
            operation="delete",
            path=str(test_copy)
        )
        print(result)
        print()
        
        # Test 12: Try to delete non-empty directory (should fail)
        print("1️⃣2️⃣ Testing RMDIR operation (non-empty, should fail)...")
        result = await edit_file(
            operation="rmdir",
            path=str(test_subdir)
        )
        print(result)
        print()
        
        # Test 13: Delete directory recursively
        print("1️⃣3️⃣ Testing RMDIR operation (recursive)...")
        result = await edit_file(
            operation="rmdir",
            path=str(test_subdir),
            recursive=True
        )
        print(result)
        print()
        
        # Test 14: Final directory listing
        print("1️⃣4️⃣ Final directory listing...")
        result = await edit_file(
            operation="list",
            path=str(test_dir)
        )
        print(result)
        print()
        
        # Test 15: Error handling - try to read non-existent file
        print("1️⃣5️⃣ Testing ERROR handling (non-existent file)...")
        result = await edit_file(
            operation="read",
            path=str(test_dir / "nonexistent.txt")
        )
        print(result)
        print()
        
        # Test 16: Error handling - invalid operation
        print("1️⃣6️⃣ Testing ERROR handling (invalid operation)...")
        result = await edit_file(
            operation="invalid",  # type: ignore
            path=str(test_file)
        )
        print(result)
        print()

    print("✅ All unified edit_file tests completed!")

if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_unified_edit_file())
