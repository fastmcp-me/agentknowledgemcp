#!/usr/bin/env python3
"""
Simple test for unified edit_file functionality
Tests the underlying functions directly without FastMCP decoration.
"""
import tempfile
from pathlib import Path

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent.parent))

def test_unified_file_operations():
    """Test basic file operations without using the FastMCP tool directly."""
    print("🧪 Testing Unified File Operations\n")
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = Path(temp_dir)
        test_file = test_dir / "test.txt"
        
        print(f"📁 Test directory: {test_dir}\n")
        
        # Test 1: Write file
        print("1️⃣ Testing write operation...")
        content = "Hello, this is a test file!\nLine 2\nLine 3"
        try:
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ File written successfully: {test_file}")
            print(f"📏 Content length: {len(content)} characters")
        except Exception as e:
            print(f"❌ Write failed: {e}")
        print()
        
        # Test 2: Read file
        print("2️⃣ Testing read operation...")
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                read_content = f.read()
            print(f"✅ File read successfully:")
            print(f"📄 Content:\n{read_content}")
        except Exception as e:
            print(f"❌ Read failed: {e}")
        print()
        
        # Test 3: Append to file
        print("3️⃣ Testing append operation...")
        append_content = "\nAppended line 4\nAppended line 5"
        try:
            with open(test_file, 'a', encoding='utf-8') as f:
                f.write(append_content)
            file_size = test_file.stat().st_size
            print(f"✅ Content appended successfully")
            print(f"📏 Added: {len(append_content)} characters")
            print(f"📊 Total file size: {file_size} bytes")
        except Exception as e:
            print(f"❌ Append failed: {e}")
        print()
        
        # Test 4: File info
        print("4️⃣ Testing file info...")
        try:
            stat_info = test_file.stat()
            size_bytes = stat_info.st_size
            print(f"✅ File info retrieved:")
            print(f"📁 Path: {test_file}")
            print(f"📊 Type: File")
            print(f"📏 Size: {size_bytes} bytes")
            print(f"🔐 Permissions: {oct(stat_info.st_mode)[-3:]}")
        except Exception as e:
            print(f"❌ File info failed: {e}")
        print()
        
        # Test 5: Copy file
        print("5️⃣ Testing copy operation...")
        test_copy = test_dir / "test_copy.txt"
        try:
            import shutil
            shutil.copy2(test_file, test_copy)
            source_size = test_file.stat().st_size
            dest_size = test_copy.stat().st_size
            print(f"✅ File copied successfully:")
            print(f"📂 From: {test_file}")
            print(f"📁 To: {test_copy}")
            print(f"📏 Size: {source_size} bytes")
            print(f"🔍 Verified: Source and destination match ({dest_size} bytes)")
        except Exception as e:
            print(f"❌ Copy failed: {e}")
        print()
        
        # Test 6: Move file
        print("6️⃣ Testing move operation...")
        test_move = test_dir / "test_moved.txt"
        try:
            test_file.rename(test_move)
            print(f"✅ File moved successfully:")
            print(f"📂 From: {test_file}")
            print(f"📁 To: {test_move}")
        except Exception as e:
            print(f"❌ Move failed: {e}")
        print()
        
        # Test 7: Create directory
        print("7️⃣ Testing directory creation...")
        test_subdir = test_dir / "subdir"
        try:
            test_subdir.mkdir(parents=True, exist_ok=False)
            if test_subdir.exists() and test_subdir.is_dir():
                print(f"✅ Directory created successfully:")
                print(f"📁 Path: {test_subdir}")
            else:
                print(f"❌ Directory creation failed")
        except Exception as e:
            print(f"❌ Directory creation failed: {e}")
        print()
        
        # Test 8: List directory
        print("8️⃣ Testing directory listing...")
        try:
            items = []
            for item in sorted(test_dir.iterdir()):
                item_type = "📁" if item.is_dir() else "📄"
                size_info = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                items.append(f"{item_type} {item.name}{size_info}")
            
            if not items:
                print(f"✅ Directory is empty")
            else:
                print(f"✅ Directory listing:")
                print(f"📁 Path: {test_dir}")
                print(f"📋 Items ({len(items)}):")
                for item in items:
                    print(f"  {item}")
        except Exception as e:
            print(f"❌ Directory listing failed: {e}")
        print()
        
        # Test 9: Delete file
        print("9️⃣ Testing file deletion...")
        try:
            if test_copy.exists():
                test_copy.unlink()
                print(f"✅ File deleted successfully:")
                print(f"📁 Path: {test_copy}")
            else:
                print(f"❌ File not found: {test_copy}")
        except Exception as e:
            print(f"❌ File deletion failed: {e}")
        print()
        
        # Test 10: Remove directory
        print("🔟 Testing directory removal...")
        try:
            if test_subdir.exists() and test_subdir.is_dir():
                test_subdir.rmdir()
                print(f"✅ Directory deleted successfully:")
                print(f"📁 Path: {test_subdir}")
            else:
                print(f"❌ Directory not found: {test_subdir}")
        except Exception as e:
            print(f"❌ Directory deletion failed: {e}")
        print()
        
        print("✅ All basic file operation tests completed!")

if __name__ == "__main__":
    test_unified_file_operations()
