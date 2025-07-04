#!/usr/bin/env python3
"""
Comprehensive test version control system functionality.
"""
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil


def test_version_control():
    """Test the version control system setup and functionality."""
    print("🧪 Testing Version Control System")
    print("=" * 50)
    
    # Create temporary test environment
    test_dir = Path(tempfile.mkdtemp(prefix="vcs_test_"))
    print(f"📁 Test directory: {test_dir}")
    
    try:
        # Setup test environment
        setup_test_environment(test_dir)
        
        # Test Git setup
        print("\n1️⃣ Testing Git setup...")
        test_git_setup(test_dir)
        
        # Test file operations
        print("\n2️⃣ Testing file commit...")
        test_file_operations(test_dir)
        
        # Test file history
        print("\n3️⃣ Testing file history...")
        test_file_history(test_dir)
        
        print("\n✅ All version control tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    finally:
        # Cleanup
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")


def setup_test_environment(test_dir: Path):
    """Setup test environment with config and sample files."""
    # Create src directory structure
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
    
    import json
    config_path = src_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Create sample files
    sample_file = test_dir / "test_document.md"
    sample_file.write_text("# Test Document\n\nThis is a test document for version control.\n")
    
    print(f"✅ Created test environment in {test_dir}")
    print(f"   - Config: {config_path}")
    print(f"   - Sample file: {sample_file}")


def test_git_setup(test_dir: Path):
    """Test Git repository setup."""
    # Change to test directory
    original_dir = Path.cwd()
    try:
        import os
        os.chdir(test_dir)
        
        # Initialize Git repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Add and commit files
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial test commit"], check=True)
        
        # Verify repository
        result = subprocess.run(["git", "status"], capture_output=True, text=True, check=True)
        if "working tree clean" in result.stdout:
            print("✅ Git repository setup successful")
        else:
            raise Exception("Git working tree not clean after setup")
            
    finally:
        os.chdir(original_dir)


def test_file_operations(test_dir: Path):
    """Test file commit operations."""
    original_dir = Path.cwd()
    try:
        import os
        os.chdir(test_dir)
        
        # Modify existing file
        sample_file = test_dir / "test_document.md"
        content = sample_file.read_text()
        new_content = content + "\n## New Section\n\nAdded some new content.\n"
        sample_file.write_text(new_content)
        
        # Stage and commit changes
        subprocess.run(["git", "add", "test_document.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Added new section"], check=True)
        
        # Create new file
        new_file = test_dir / "another_document.md"
        new_file.write_text("# Another Document\n\nThis is another test document.\n")
        
        subprocess.run(["git", "add", "another_document.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Added another document"], check=True)
        
        # Verify commits
        result = subprocess.run(["git", "log", "--oneline"], capture_output=True, text=True, check=True)
        commits = result.stdout.strip().split('\n')
        
        if len(commits) >= 3:  # Initial + 2 new commits
            print(f"✅ File operations successful - {len(commits)} commits found")
        else:
            raise Exception(f"Expected at least 3 commits, found {len(commits)}")
            
    finally:
        os.chdir(original_dir)


def test_file_history(test_dir: Path):
    """Test file history retrieval."""
    original_dir = Path.cwd()
    try:
        import os
        os.chdir(test_dir)
        
        # Get file history
        result = subprocess.run(
            ["git", "log", "--oneline", "test_document.md"], 
            capture_output=True, text=True, check=True
        )
        commits = result.stdout.strip().split('\n')
        
        if len(commits) >= 2:
            # Get previous version
            second_commit = commits[1].split()[0]
            result = subprocess.run(
                ["git", "show", f"{second_commit}:test_document.md"],
                capture_output=True, text=True, check=True
            )
            previous_content = result.stdout
            
            # Verify it's different from current
            current_content = (test_dir / "test_document.md").read_text()
            
            if previous_content != current_content:
                print("✅ File history retrieval successful")
                print(f"   - Current file: {len(current_content)} chars")
                print(f"   - Previous version: {len(previous_content)} chars")
            else:
                raise Exception("Previous version identical to current")
        else:
            raise Exception(f"Expected at least 2 commits for test_document.md, found {len(commits)}")
            
    finally:
        os.chdir(original_dir)


def main():
    """Main test function."""
    try:
        # Check if Git is available
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        
        # Run tests
        test_version_control()
        
        print("\n🎉 Version control system is working correctly!")
        
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
