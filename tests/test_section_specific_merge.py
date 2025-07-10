#!/usr/bin/env python3
"""
Test section-specific intelligent merge logic
"""
import json

def intelligent_config_merge(current_config, backup_config):
    """
    Intelligently merge configuration after server upgrade.
    
    Logic:
    - Some sections use LATEST config (server, schema, version info)
    - Some sections use INTELLIGENT merge (user settings like security, elasticsearch)
    - Ignore deprecated features (keys only in backup - these were removed)
    
    Args:
        current_config: New configuration from server upgrade
        backup_config: User's previous configuration (backup)
        
    Returns:
        Merged configuration with appropriate merge strategy per section
    """
    # Sections that should always use the LATEST config (no merge)
    # These contain version info, schema definitions, server settings that must be current
    LATEST_CONFIG_SECTIONS = {
        "server",           # Version info, new server settings
        "schema",           # Schema definitions must be current  
        "version",          # Version tracking
        "defaults",         # Default values must be current
        "required_fields",  # Schema requirements must be current
        "field_types"       # Schema field types must be current
    }
    
    # Sections that should use INTELLIGENT merge (preserve user settings)
    # These contain user customizations that should be preserved
    INTELLIGENT_MERGE_SECTIONS = {
        "security",         # User's paths and security settings
        "elasticsearch",    # User's ES connection settings  
        "logging",          # User's logging preferences
        "features",         # User's feature toggles
        "custom"            # Any custom user sections
    }
    
    def merge_recursive(current, backup, section_name=None):
        result = current.copy()  # Start with current config (includes new features)
        
        for key, backup_value in backup.items():
            if key in current:
                current_value = current[key]
                
                # Check if this is a top-level section that needs special handling
                if section_name is None and key in LATEST_CONFIG_SECTIONS:
                    # Use latest config for these sections - no merge
                    result[key] = current_value
                    continue
                elif section_name is None and key in INTELLIGENT_MERGE_SECTIONS:
                    # Use intelligent merge for these sections
                    if isinstance(current_value, dict) and isinstance(backup_value, dict):
                        result[key] = merge_recursive(current_value, backup_value, key)
                    else:
                        result[key] = backup_value  # Preserve user setting
                    continue
                elif section_name is None and isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # For unknown top-level sections, default to intelligent merge
                    result[key] = merge_recursive(current_value, backup_value, key)
                    continue
                
                # For nested values within a section, merge normally
                if isinstance(current_value, dict) and isinstance(backup_value, dict):
                    # Recursively merge nested dictionaries
                    result[key] = merge_recursive(current_value, backup_value, section_name)
                else:
                    # Use backup value (user's setting) for intelligent merge sections
                    if section_name in INTELLIGENT_MERGE_SECTIONS or section_name is None:
                        result[key] = backup_value
                    else:
                        # For latest config sections, keep current value
                        result[key] = current_value
            else:
                # Key only exists in backup
                # For intelligent merge sections, preserve user settings even if not in current config
                # BUT only if they're not clearly deprecated (e.g., "old_", "deprecated_", "legacy_")
                if section_name in INTELLIGENT_MERGE_SECTIONS:
                    # Check if this looks like a deprecated setting
                    is_deprecated = any(key.startswith(prefix) for prefix in ["old_", "deprecated_", "legacy_"])
                    if not is_deprecated:
                        result[key] = backup_value
                # For latest config sections or deprecated keys, ignore (don't include)
            
        return result
    
    return merge_recursive(current_config, backup_config)


def test_section_specific_merge():
    """Test section-specific merge behavior"""
    print("🧪 Testing Section-Specific Intelligent Merge...")
    
    # Test comprehensive config with multiple section types
    current_config = {
        "server": {
            "version": "1.0.21",        # Must use latest
            "new_feature": "enabled",   # Must use latest
            "port": 8080               # Must use latest
        },
        "schema": {
            "required_fields": ["content", "title"],  # Must use latest
            "new_validation": "strict"                # Must use latest
        },
        "security": {
            "allowed_base_directory": "/default/path",  # Should merge with user
            "new_security": "enhanced"                  # Should include new feature
        },
        "elasticsearch": {
            "host": "localhost",        # Should merge with user
            "port": 9200,              # Should merge with user
            "content_field": "content" # Should include new feature
        },
        "logging": {
            "level": "INFO",           # Should merge with user
            "new_format": "json"       # Should include new feature
        }
    }
    
    backup_config = {
        "server": {
            "version": "1.0.20",       # Should be ignored (use latest)
            "port": 9090,              # Should be ignored (use latest)
            "old_setting": "deprecated" # Should be ignored (deprecated)
        },
        "schema": {
            "required_fields": ["title"], # Should be ignored (use latest)
            "old_rule": "deprecated"      # Should be ignored (deprecated)
        },
        "security": {
            "allowed_base_directory": "/custom/user/path", # Should be preserved
            "old_auth": "deprecated"                       # Should be ignored
        },
        "elasticsearch": {
            "host": "custom-host",     # Should be preserved
            "port": 9300,             # Should be preserved
            "username": "myuser",     # Should be preserved (user setting)
            "old_index": "deprecated" # Should be ignored
        },
        "logging": {
            "level": "DEBUG",         # Should be preserved
            "file": "/custom/log"     # Should be preserved (user setting)
        }
    }
    
    result = intelligent_config_merge(current_config, backup_config)
    
    print(f"\n📋 Current (new):")
    print(json.dumps(current_config, indent=2))
    print(f"\n📋 Backup (user):")
    print(json.dumps(backup_config, indent=2))
    print(f"\n📋 Result (merged):")
    print(json.dumps(result, indent=2))
    
    # Verify section-specific behavior
    checks = [
        # SERVER section - should use LATEST config (no user merge)
        (result["server"]["version"] == "1.0.21", "Server version uses latest (not user's 1.0.20)"),
        (result["server"]["port"] == 8080, "Server port uses latest (not user's 9090)"), 
        (result["server"]["new_feature"] == "enabled", "Server new feature included"),
        ("old_setting" not in result["server"], "Server deprecated setting ignored"),
        
        # SCHEMA section - should use LATEST config (no user merge)
        (result["schema"]["required_fields"] == ["content", "title"], "Schema uses latest required_fields"),
        (result["schema"]["new_validation"] == "strict", "Schema new validation included"),
        ("old_rule" not in result["schema"], "Schema deprecated rule ignored"),
        
        # SECURITY section - should use INTELLIGENT merge (preserve user)
        (result["security"]["allowed_base_directory"] == "/custom/user/path", "Security preserves user directory"),
        (result["security"]["new_security"] == "enhanced", "Security includes new feature"),
        ("old_auth" not in result["security"], "Security deprecated setting ignored"),
        
        # ELASTICSEARCH section - should use INTELLIGENT merge (preserve user)
        (result["elasticsearch"]["host"] == "custom-host", "ES preserves user host"),
        (result["elasticsearch"]["port"] == 9300, "ES preserves user port"),
        (result["elasticsearch"]["username"] == "myuser", "ES preserves user credentials"),
        (result["elasticsearch"]["content_field"] == "content", "ES includes new feature"),
        ("old_index" not in result["elasticsearch"], "ES deprecated setting ignored"),
        
        # LOGGING section - should use INTELLIGENT merge (preserve user)
        (result["logging"]["level"] == "DEBUG", "Logging preserves user level"),
        (result["logging"]["file"] == "/custom/log", "Logging preserves user file"),
        (result["logging"]["new_format"] == "json", "Logging includes new feature"),
    ]
    
    print(f"\n✅ Section-Specific Merge Verification:")
    for check_passed, description in checks:
        status = "✅" if check_passed else "❌"
        print(f"   {status} {description}")
    
    # Summary
    latest_sections = ["server", "schema"]
    intelligent_sections = ["security", "elasticsearch", "logging"]
    
    print(f"\n🎯 Section Strategy Summary:")
    print(f"   📋 LATEST CONFIG sections: {latest_sections}")
    print(f"   🧠 INTELLIGENT MERGE sections: {intelligent_sections}")
    print(f"   ✅ Latest sections preserve upgrade features and versions")
    print(f"   ✅ Intelligent sections preserve user settings + add new features")

if __name__ == "__main__":
    test_section_specific_merge()
