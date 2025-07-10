#!/usr/bin/env python3
"""
Test intelligent_config_merge function
"""
import json
import sys
from pathlib import Path

# Add src to path for imports  
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from admin_handlers import intelligent_config_merge

def test_intelligent_merge():
    """Test intelligent configuration merge algorithm"""
    print("🧪 Testing intelligent_config_merge function...")
    
    # Test Case 1: Basic merge with new features and user settings
    print("\n📋 Test Case 1: Basic merge")
    
    current_config = {
        "security": {
            "allowed_base_directory": "/default/path"
        },
        "elasticsearch": {
            "host": "localhost",
            "port": 9200,
            "new_feature": "enabled"  # New feature in upgrade
        },
        "server": {
            "version": "1.0.21",
            "new_setting": "default"  # New setting in upgrade
        }
    }
    
    backup_config = {
        "security": {
            "allowed_base_directory": "/custom/user/path"  # User's setting
        },
        "elasticsearch": {
            "host": "custom-host",  # User's setting
            "port": 9300,  # User's setting
            "old_deprecated": "should_be_ignored"  # Deprecated - only in backup
        },
        "server": {
            "version": "1.0.20"  # Old version
        }
    }
    
    expected_result = {
        "security": {
            "allowed_base_directory": "/custom/user/path"  # User's setting preserved (intelligent merge)
        },
        "elasticsearch": {
            "host": "custom-host",  # User's setting preserved (intelligent merge)
            "port": 9300,  # User's setting preserved (intelligent merge)
            "new_feature": "enabled"  # New feature included
        },
        "server": {
            "version": "1.0.21",  # Latest config used (no merge for server section)
            "new_setting": "default"  # Latest config used (no merge for server section)
        }
    }
    
    result = intelligent_config_merge(current_config, backup_config)
    
    print(f"   Current (new): {json.dumps(current_config, indent=2)}")
    print(f"   Backup (user): {json.dumps(backup_config, indent=2)}")
    print(f"   Result (merged): {json.dumps(result, indent=2)}")
    
    # Verify key aspects
    checks = [
        (result["security"]["allowed_base_directory"] == "/custom/user/path", "User's directory preserved (intelligent merge)"),
        (result["elasticsearch"]["host"] == "custom-host", "User's elasticsearch host preserved (intelligent merge)"),
        (result["elasticsearch"]["port"] == 9300, "User's elasticsearch port preserved (intelligent merge)"),
        (result["elasticsearch"]["new_feature"] == "enabled", "New feature included"),
        (result["server"]["version"] == "1.0.21", "Server version uses latest config (no merge)"),
        (result["server"]["new_setting"] == "default", "Server new setting uses latest config (no merge)"),
        ("old_deprecated" not in result["elasticsearch"], "Deprecated setting ignored"),
    ]
    
    for check_passed, description in checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    # Test Case 2: Nested merge
    print("\n📋 Test Case 2: Nested configuration merge")
    
    current_nested = {
        "level1": {
            "level2": {
                "setting1": "default1",
                "setting2": "default2",
                "new_setting": "new_value"
            }
        }
    }
    
    backup_nested = {
        "level1": {
            "level2": {
                "setting1": "user1",
                "deprecated_setting": "old_value"
            }
        }
    }
    
    result_nested = intelligent_config_merge(current_nested, backup_nested)
    
    print(f"   Result nested: {json.dumps(result_nested, indent=2)}")
    
    nested_checks = [
        (result_nested["level1"]["level2"]["setting1"] == "user1", "Nested user setting preserved"),
        (result_nested["level1"]["level2"]["setting2"] == "default2", "Nested new setting included"),
        (result_nested["level1"]["level2"]["new_setting"] == "new_value", "Nested new feature included"),
        ("deprecated_setting" not in result_nested["level1"]["level2"], "Nested deprecated setting ignored"),
    ]
    
    for check_passed, description in nested_checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")

if __name__ == "__main__":
    test_intelligent_merge()
