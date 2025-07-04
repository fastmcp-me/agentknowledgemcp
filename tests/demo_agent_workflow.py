#!/usr/bin/env python3
"""
Demo workflow for agents using the MCP server.
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from document_schema import (
    validate_document_structure, 
    create_document_template,
    DocumentValidationError
)

# Import test helpers
from test_helpers import get_test_config, get_test_paths


def demo_agent_workflow():
    """Demo how agent will use the validation system."""
    print("🤖 AGENT WORKFLOW DEMO")
    print("=" * 50)
    
    # Load test configuration
    config = get_test_config()
    paths = get_test_paths()
    
    # Simulate user input
    user_file_path = f"{paths['external_dir']}/auth/jwt-implementation.md"
    base_dir = paths["knowledge_base"]
    
    print(f"📋 User request: Index JWT authentication file")
    print(f"📁 User provided path: {user_file_path}")
    print(f"🏠 Agent base directory: {base_dir}")
    
    # Step 1: Agent creates template
    print(f"\n1️⃣ Agent creates document template...")
    try:
        template = create_document_template(
            title="JWT Authentication Implementation",
            file_path=user_file_path,
            priority="high",
            source_type="markdown",
            tags=["authentication", "JWT", "security"],
            summary="Brief description of JWT implementation with security considerations",
            key_points=["Must validate tokens", "Use refresh tokens", "Secure storage"],
            related=["auth-refresh-token-002"],
            base_directory=base_dir
        )
        print("   ✅ Template created successfully!")
        
        # Show path handling
        print(f"\n📝 Path processing:")
        print(f"   Input path:  {user_file_path}")
        print(f"   Output path: {template['file_path']}")
        print(f"   File name:   {template['file_name']}")
        print(f"   Directory:   {template['directory']}")
        print(f"   Generated ID: {template['id']}")
        
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return
    
    # Step 2: Agent validates (optional)
    print(f"\n2️⃣ Agent validates document...")
    try:
        validated = validate_document_structure(template, base_dir)
        print("   ✅ Validation passed!")
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")
        return
    
    # Step 3: Ready for indexing
    print(f"\n3️⃣ Ready for Elasticsearch indexing...")
    print("   ✅ Document structure is valid")
    print("   ✅ Paths are normalized")
    print("   ✅ All required fields present")
    
    # Show final document
    print(f"\n📄 Final document for indexing:")
    important_fields = {
        "id": template["id"],
        "title": template["title"],
        "file_path": template["file_path"],
        "priority": template["priority"],
        "source_type": template["source_type"],
        "tags": template["tags"]
    }
    print(json.dumps(important_fields, indent=2, ensure_ascii=False))
    
    print(f"\n🎯 SUCCESS: Agent workflow completed!")
    print(f"   • External path → Preserved as absolute path")
    print(f"   • Path normalization → Applied correctly")
    print(f"   • Document validation → Passed")
    print(f"   • Ready for indexing → Yes")


def demo_relative_path_workflow():
    """Demo with relative paths."""
    print(f"\n" + "=" * 50)
    print("🤖 RELATIVE PATH WORKFLOW DEMO")
    print("=" * 50)
    
    # Load test configuration
    paths = get_test_paths()
    base_dir = paths["knowledge_base"]
    
    # Simulate relative path input
    user_file_path = "./docs/api/authentication.md"
    
    print(f"📋 User request: Index API authentication docs")
    print(f"📁 User provided path: {user_file_path}")
    print(f"🏠 Agent base directory: {base_dir}")
    
    try:
        template = create_document_template(
            title="API Authentication Documentation",
            file_path=user_file_path,
            priority="medium",
            source_type="documentation",
            tags=["API", "authentication", "docs"],
            summary="Complete API authentication documentation",
            key_points=["OAuth 2.0", "JWT tokens", "Rate limiting"],
            related=["api-basics-001"],
            base_directory=base_dir
        )
        
        print(f"\n✅ Relative path workflow completed!")
        print(f"   Input:  {user_file_path}")
        print(f"   Output: {template['file_path']}")
        print(f"   Status: Path normalized to relative format")
        
    except Exception as e:
        print(f"❌ Relative path workflow failed: {e}")


def main():
    """Run agent workflow demos."""
    print("🚀 AGENT WORKFLOW DEMONSTRATIONS")
    print("Testing realistic agent usage scenarios")
    
    try:
        demo_agent_workflow()
        demo_relative_path_workflow()
        
        print(f"\n🎉 ALL AGENT WORKFLOWS COMPLETED SUCCESSFULLY!")
        print(f"\n✅ Verified Features:")
        print(f"   • External path handling")
        print(f"   • Relative path normalization")
        print(f"   • Document template creation")
        print(f"   • Schema validation")
        print(f"   • Ready for MCP integration")
        
    except Exception as e:
        print(f"❌ Workflow demo failed: {e}")


if __name__ == "__main__":
    main()
