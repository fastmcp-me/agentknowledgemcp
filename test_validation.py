#!/usr/bin/env python3
"""
Demo script để test document validation system.
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_schema import (
    validate_document_structure, 
    create_document_template,
    DocumentValidationError
)

def test_valid_document():
    """Test với document hợp lệ theo format của user."""
    print("=" * 60)
    print("🧪 TEST 1: Document hợp lệ theo format của user")
    print("=" * 60)
    
    valid_doc = {
        "id": "auth-jwt-001",
        "title": "JWT Authentication Implementation", 
        "summary": "Brief description of JWT implementation with security considerations",
        "file_path": "/Users/nguyenkimchung/ElasticSearch/backend/workflows/auth/jwt.md",
        "file_name": "jwt.md",
        "directory": "backend/workflows/auth",
        "last_modified": "2025-01-04T10:30:00Z",
        "priority": "high",
        "tags": ["authentication", "JWT", "security"],
        "related": ["auth-refresh-token-002"],
        "source_type": "markdown",
        "key_points": ["Must validate tokens", "Use refresh tokens", "Secure storage"]
    }
    
    try:
        validated = validate_document_structure(valid_doc)
        print("✅ VALIDATION SUCCESSFUL!")
        print("\nValidated document:")
        print(json.dumps(validated, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"❌ VALIDATION FAILED: {e}")
        return False

def test_invalid_document():
    """Test với document không hợp lệ."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Document không hợp lệ")
    print("=" * 60)
    
    invalid_doc = {
        "id": "test-123",
        "title": "Test Document",
        "summary": "Test summary",
        "priority": "invalid_priority",  # Invalid priority
        "tags": "should_be_array",       # Invalid type
        "source_type": "invalid_type"    # Invalid source type
        # Missing required fields
    }
    
    try:
        validated = validate_document_structure(invalid_doc)
        print("❌ UNEXPECTED SUCCESS!")
        print(json.dumps(validated, indent=2, ensure_ascii=False))
        return False
    except DocumentValidationError as e:
        print("✅ VALIDATION CORRECTLY FAILED!")
        print(f"Error details: {e}")
        return True
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        return False

def test_create_template():
    """Test tạo template."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Tạo document template")
    print("=" * 60)
    
    try:
        template = create_document_template(
            title="API Error Handling Best Practices",
            file_path="/Users/nguyenkimchung/ElasticSearch/backend/api/error-handling.md",
            priority="medium",
            source_type="documentation",
            tags=["API", "error handling", "best practices"],
            summary="Comprehensive guide for handling API errors properly",
            key_points=[
                "Use proper HTTP status codes",
                "Provide meaningful error messages", 
                "Log errors for debugging",
                "Handle edge cases gracefully"
            ],
            related=["api-design-001", "logging-best-practices-003"]
        )
        
        print("✅ TEMPLATE CREATED SUCCESSFULLY!")
        print("\nGenerated template:")
        print(json.dumps(template, indent=2, ensure_ascii=False))
        
        # Validate the created template
        print("\n🔍 Validating generated template...")
        validated = validate_document_structure(template)
        print("✅ Generated template is valid!")
        return True
        
    except Exception as e:
        print(f"❌ TEMPLATE CREATION FAILED: {e}")
        return False

def demo_usage():
    """Demo cách sử dụng trong MCP server."""
    print("\n" + "=" * 60)
    print("📚 USAGE DEMO: Cách sử dụng trong MCP server")
    print("=" * 60)
    
    print("""
🔧 CÁCH SỬ DỤNG:

1. Tạo document template:
   Tool: create_document_template
   Input: {
     "title": "Your Document Title",
     "file_path": "/path/to/your/file.md",
     "priority": "high|medium|low",
     "source_type": "markdown|code|config|documentation|tutorial",
     "tags": ["tag1", "tag2"],
     "summary": "Brief description",
     "key_points": ["Point 1", "Point 2"],
     "related": ["related-doc-id"]
   }

2. Validate document trước khi index:
   Tool: validate_document_schema
   Input: {
     "document": { ... your document ... }
   }

3. Index document với validation:
   Tool: index_document
   Input: {
     "index": "knowledge_base",
     "document": { ... your document ... },
     "validate_schema": true  // Mặc định là true
   }

🎯 KẾT QUẢ:
- Nếu document đúng format → Index thành công
- Nếu document sai format → Hiển thị lỗi chi tiết và ví dụ format đúng

🔍 SCHEMA REQUIREMENTS:
- Required fields: id, title, summary, file_path, file_name, directory, 
                  last_modified, priority, tags, related, source_type, key_points
- Priority: high, medium, low
- Source types: markdown, code, config, documentation, tutorial
- Tags, related, key_points: must be arrays of strings
- ID: alphanumeric with hyphens/underscores only
- Timestamp: ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
""")

def main():
    """Chạy tất cả tests."""
    print("🚀 DOCUMENT VALIDATION SYSTEM DEMO")
    print("Kiểm tra validation cho knowledge base documents")
    
    tests_passed = 0
    total_tests = 3
    
    if test_valid_document():
        tests_passed += 1
    
    if test_invalid_document():
        tests_passed += 1
        
    if test_create_template():
        tests_passed += 1
    
    demo_usage()
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Validation system is working correctly.")
        print("\n✅ MCP Server ready with document validation!")
        print("Agent sẽ validate documents trước khi tạo index.")
    else:
        print("❌ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()
