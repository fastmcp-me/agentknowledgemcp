#!/usr/bin/env python3
"""
Demo script showing the new config management features.
"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from admin_handlers import handle_get_config, handle_update_config, handle_validate_config
import asyncio

async def demo_config_management():
    """Demo the new config management features."""
    print("🚀 Demo: New Config Management Features")
    print("=" * 50)
    
    # Demo 1: Get current config
    print("\n📋 1. Getting current configuration:")
    config_result = await handle_get_config({})
    print(config_result[0].text)
    
    # Demo 2: Show current validation settings
    config = load_config()
    validation_config = config.get("document_validation", {})
    print(f"\n⚙️  Current validation settings:")
    print(f"   strict_schema_validation: {validation_config.get('strict_schema_validation', False)}")
    print(f"   allow_extra_fields: {validation_config.get('allow_extra_fields', True)}")
    print(f"   required_fields_only: {validation_config.get('required_fields_only', False)}")
    print(f"   auto_correct_paths: {validation_config.get('auto_correct_paths', True)}")
    
    # Demo 3: Try to update config with strict mode disabled
    print(f"\n📝 3. Updating config to disable strict validation:")
    new_config = config.copy()
    new_config["document_validation"]["strict_schema_validation"] = False
    new_config["document_validation"]["allow_extra_fields"] = True
    
    try:
        update_result = await handle_update_config({"config": new_config})
        print(update_result[0].text)
    except Exception as e:
        print(f"❌ Update failed: {e}")
    
    # Demo 4: Validate a config before applying
    print(f"\n🔍 4. Validating config before applying:")
    test_config = {
        "server": {"name": "Test Server", "version": "1.0.0"},
        "elasticsearch": {"host": "localhost", "port": 9200},
        "security": {"allowed_base_directory": "/tmp"},
        "document_validation": {
            "strict_schema_validation": True,
            "allow_extra_fields": False,
            "required_fields_only": True,
            "auto_correct_paths": True
        }
    }
    
    try:
        validate_result = await handle_validate_config({"config": test_config})
        print(validate_result[0].text)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
    
    print("\n✅ Demo completed! The new config management system allows:")
    print("   • Full config viewing and modification")
    print("   • Strict schema validation control")
    print("   • Config validation before applying")
    print("   • Backward compatibility with old tools")

if __name__ == "__main__":
    asyncio.run(demo_config_management())
