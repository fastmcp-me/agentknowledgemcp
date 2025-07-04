#!/usr/bin/env python3
"""
Quick demo for agent workflow with document validation.
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_schema import create_document_template, validate_document_structure

def demo_agent_workflow():
    """Demo how agent will use the validation system."""
    print("🤖 AGENT WORKFLOW DEMO")
    print("=" * 50)
    
    # Simulate agent getting user request with JWT path
    user_file_path = "/Users/nguyenkimchung/ElasticSearch/backend/workflows/auth/jwt.md"
    base_dir = "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs"
    
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
    print(f"   • User path outside base directory → Warning shown")
    print(f"   • Path normalized for consistency")
    print(f"   • Document ready for knowledge base")

def demo_validation_error():
    """Demo what happens with invalid document."""
    print(f"\n" + "=" * 50)
    print("❌ VALIDATION ERROR DEMO")
    print("=" * 50)
    
    # Invalid document missing required fields
    invalid_doc = {
        "id": "test-invalid",
        "title": "Incomplete Document",
        "summary": "Missing fields",
        "priority": "invalid_priority",  # Wrong value
        "tags": "should_be_array"        # Wrong type
        # Missing: file_path, file_name, directory, etc.
    }
    
    print("🧪 Testing invalid document...")
    try:
        validate_document_structure(invalid_doc)
        print("❌ Unexpected success!")
    except Exception as e:
        print("✅ Validation correctly failed!")
        print(f"   Error: {str(e)[:100]}...")
        print("   → Agent gets clear error message")
        print("   → Agent knows exactly what to fix")

if __name__ == "__main__":
    demo_agent_workflow()
    demo_validation_error()
    
    print(f"\n🚀 SYSTEM READY!")
    print("Agent can now:")
    print("  • Create templates with any file path")
    print("  • Auto-normalize paths to relative format")
    print("  • Validate documents before indexing")
    print("  • Get clear error messages for fixes")
    print("  • Handle cross-platform paths (Windows/Unix)")
