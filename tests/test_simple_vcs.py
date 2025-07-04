#!/usr/bin/env python3
"""
Simple VCS test without dependencies.
"""
import subprocess
import json
from pathlib import Path
import tempfile
import shutil


def create_test_repo():
    """Create test repository for VCS testing."""
    # Create test directory
    test_dir = Path(tempfile.mkdtemp(prefix="vcs_test_"))
    print(f"📁 Test directory: {test_dir}")
    
    try:
        # Create directory structure
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
        
        # Create test files
        test_files = [
            ("document1.md", "# Document 1\n\nFirst document content.\n"),
            ("document2.md", "# Document 2\n\nSecond document content.\n"),
            ("notes.txt", "Some notes here.\n")
        ]
        
        for filename, content in test_files:
            file_path = test_dir / filename
            file_path.write_text(content)
        
        # Setup Git repository
        print("\n🔧 Setting up Git repository...")
        subprocess.run(["git", "init"], cwd=test_dir, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=test_dir, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=test_dir, check=True)
        
        # Add and commit files
        subprocess.run(["git", "add", "."], cwd=test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=test_dir, check=True)
        
        print("✅ Git repository setup complete")
        
        # Test file modifications
        print("\n📝 Testing file modifications...")
        
        # Modify document1.md
        doc1_path = test_dir / "document1.md"
        content = doc1_path.read_text()
        new_content = content + "\n## New Section\n\nAdded some new content.\n"
        doc1_path.write_text(new_content)
        
        # Commit changes
        subprocess.run(["git", "add", "document1.md"], cwd=test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Updated document1 with new section"], cwd=test_dir, check=True)
        
        # Create new file
        new_file = test_dir / "document3.md"
        new_file.write_text("# Document 3\n\nThis is a new document.\n")
        
        subprocess.run(["git", "add", "document3.md"], cwd=test_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Added document3"], cwd=test_dir, check=True)
        
        print("✅ File modifications and commits complete")
        
        # Test history retrieval
        print("\n📚 Testing history retrieval...")
        
        # Get commit history
        result = subprocess.run(
            ["git", "log", "--oneline"], 
            cwd=test_dir, capture_output=True, text=True, check=True
        )
        commits = result.stdout.strip().split('\n')
        print(f"Found {len(commits)} commits:")
        for i, commit in enumerate(commits):
            print(f"  {i+1}. {commit}")
        
        # Get previous version of document1.md
        if len(commits) >= 2:
            second_commit = commits[1].split()[0]
            result = subprocess.run(
                ["git", "show", f"{second_commit}:document1.md"],
                cwd=test_dir, capture_output=True, text=True, check=True
            )
            previous_content = result.stdout
            
            print(f"\n📄 Previous version of document1.md:")
            print("-" * 40)
            print(previous_content)
            print("-" * 40)
            
            print(f"\n📄 Current version of document1.md:")
            print("-" * 40)
            print(doc1_path.read_text())
            print("-" * 40)
        
        print("\n✅ Version control test completed successfully!")
        print(f"\n📊 Summary:")
        print(f"   - Repository: {test_dir}")
        print(f"   - Commits: {len(commits)}")
        print(f"   - Files: {len(list(test_dir.glob('*.md')))} markdown, {len(list(test_dir.glob('*.txt')))} text")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        # Cleanup
        input(f"\nPress Enter to cleanup test directory: {test_dir}")
        shutil.rmtree(test_dir)
        print(f"🧹 Cleaned up: {test_dir}")


def main():
    """Main function."""
    print("🧪 Version Control System Test")
    print("=" * 50)
    
    try:
        # Check Git availability
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✅ Git is available")
        
        # Run test
        create_test_repo()
        
        print("\n🎉 All tests passed!")
        
    except FileNotFoundError:
        print("❌ Git is not installed or not in PATH")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main()
