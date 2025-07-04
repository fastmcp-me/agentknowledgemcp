"""
Test helpers for loading configuration and setting up test environment.
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def load_test_config():
    """Load test configuration."""
    config_path = Path(__file__).parent / "test_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)

def get_test_directories():
    """Get test directories from config."""
    config = load_test_config()
    return config["test_directories"]

def get_test_files():
    """Get test file paths from config."""
    config = load_test_config()
    return config["test_files"]

def get_expected_results():
    """Get expected test results from config."""
    config = load_test_config()
    return config["expected_results"]

def get_base_dir():
    """Get base directory for tests."""
    dirs = get_test_directories()
    return dirs["docs_dir"]

def setup_test_environment():
    """Setup test environment and return important paths."""
    config = load_test_config()
    return {
        "base_dir": config["test_directories"]["docs_dir"],
        "knowledge_base": config["test_directories"]["base_dir"],
        "sample_file": config["test_files"]["jwt_relative"]
    }
