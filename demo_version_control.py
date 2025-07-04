#!/usr/bin/env python3
"""
Demo script để test version control tools trong MCP server.
"""
import asyncio
import json
from pathlib import Path
import tempfile
import shutil
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment variable for config path
original_cwd = os.getcwd()

from src.config import load_config
from src.version_control_handlers import (
    handle_setup_version_control, 
    handle_commit_file, 
    handle_get_previous_file_version
)


async def demo_version_control():
    """Demo version control functionality."""
    print("🚀 Demo Version Control Tools")
    print("=" * 50)
    
    # Create temporary test environment
    test_dir = Path(tempfile.mkdtemp(prefix="vcs_demo_"))
    print(f"📁 Demo directory: {test_dir}")
    
    try:
        # Setup demo environment
        await setup_demo_environment(test_dir)
        
        # Test 1: Setup version control
        print("\n1️⃣ Testing setup_version_control...")
        result = await handle_setup_version_control({
            "vcs_type": "git",
            "force": True,
            "initial_commit": True
        })
        print("Result:", result[0].text)
        
        # Test 2: Create and commit a file
        print("\n2️⃣ Testing commit_file...")
        
        # Create a test file
        test_file = test_dir / "demo_document.md"
        test_file.write_text("# Demo Document\n\nThis is a demo document.\n")
        
        result = await handle_commit_file({
            "file_path": "demo_document.md",
            "message": "Add demo document",
            "add_if_new": True
        })
        print("Result:", result[0].text)
        
        # Test 3: Modify file and commit again
        print("\n3️⃣ Testing file modification and commit...")
        
        content = test_file.read_text()
        new_content = content + "\n## New Section\n\nAdded some content.\n"
        test_file.write_text(new_content)
        
        result = await handle_commit_file({
            "file_path": "demo_document.md",
            "message": "Added new section to demo document",
            "add_if_new": False
        })
        print("Result:", result[0].text)
        
        # Test 4: Get previous version
        print("\n4️⃣ Testing get_previous_file_version...")
        
        result = await handle_get_previous_file_version({
            "file_path": "demo_document.md",
            "commits_back": 1
        })
        print("Result:", result[0].text[:200] + "..." if len(result[0].text) > 200 else result[0].text)
        
        print("\n✅ All version control demos completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up demo directory: {test_dir}")


async def setup_demo_environment(test_dir: Path):
    """Setup demo environment."""
    # Create src directory
    src_dir = test_dir / "src"
    src_dir.mkdir()
    
    # Create config.json
    config = {
        "elasticsearch": {"enabled": False},
        "security": {"allowed_base_directory": str(test_dir)},
        "version_control": {
            "enabled": True,
            "type": "git",
            "auto_commit": False
        }
    }
    
    config_path = src_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Temporarily change the config module's path
    import src.config as config_module
    original_get_config_path = getattr(config_module, 'get_config_path', None)
    
    def mock_get_config_path():
        return config_path
    
    config_module.get_config_path = mock_get_config_path
    
    print(f"✅ Created demo environment in {test_dir}")


async def main():
    """Main demo function."""
    try:
        await demo_version_control()
        print("\n🎉 Version control demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
