#!/usr/bin/env python3
"""
Development helper script for AgentKnowledgeMCP.
"""
import subprocess
import sys
from pathlib import Path

def start_dev_server():
    """Start the MCP server in development mode."""
    project_root = Path(__file__).parent.parent
    server_path = project_root / "src" / "server.py"
    
    print("🚀 Starting AgentKnowledgeMCP development server...")
    try:
        subprocess.run([sys.executable, str(server_path)], check=True)
    except KeyboardInterrupt:
        print("\n✅ Development server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

def run_tests():
    """Run all tests."""
    project_root = Path(__file__).parent.parent
    test_dir = project_root / "tests"
    
    print("🧪 Running tests...")
    try:
        # Run specific test files
        test_files = [
            "test_validation.py",
            "test_strict_validation.py", 
            "demo_config_management.py"
        ]
        
        for test_file in test_files:
            test_path = test_dir / test_file
            if test_path.exists():
                print(f"Running {test_file}...")
                subprocess.run([sys.executable, str(test_path)], check=True)
        
        print("✅ All tests passed!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        sys.exit(1)

def build_package():
    """Build the package for distribution."""
    print("📦 Building package...")
    try:
        subprocess.run([sys.executable, "-m", "build"], check=True)
        print("✅ Package built successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)

def deploy_pypi():
    """Deploy to PyPI using twine."""
    print("🚀 Deploying to PyPI...")
    try:
        # Build first
        build_package()
        
        # Upload with twine
        subprocess.run([
            sys.executable, "-m", "twine", "upload", 
            "dist/*", "--repository", "pypi"
        ], check=True)
        print("✅ Successfully deployed to PyPI!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AgentKnowledgeMCP development tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Dev server command
    subparsers.add_parser("dev", help="Start development server")
    
    # Test command
    subparsers.add_parser("test", help="Run tests")
    
    # Build command
    subparsers.add_parser("build", help="Build package")
    
    # Deploy command
    subparsers.add_parser("deploy", help="Deploy to PyPI")
    
    args = parser.parse_args()
    
    if args.command == "dev":
        start_dev_server()
    elif args.command == "test":
        run_tests()
    elif args.command == "build":
        build_package()
    elif args.command == "deploy":
        deploy_pypi()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
