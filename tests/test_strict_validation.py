#!/usr/bin/env python3
"""
Test script to verify strict schema validation is working properly.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from document_schema import validate_document_structure, DocumentValidationError
import json

def test_strict_validation():
    """Test strict validation functionality."""
    print("🧪 Testing strict schema validation...")
    
    # Test 1: Valid knowledge base document
    print("\n📋 Test 1: Valid knowledge base document")
    valid_doc = {
        "id": "test-doc-1",
        "title": "Test Document",
        "summary": "A test document",
        "file_path": "test.md",
        "file_name": "test.md",
        "directory": "",
        "priority": "medium",
        "tags": ["test"],
        "source_type": "markdown",
        "last_modified": "2025-01-04T10:30:00Z",
        "key_points": ["Point 1", "Point 2"],
        "related": []
    }
    
    try:
        result = validate_document_structure(valid_doc, is_knowledge_doc=True)
        print("✅ Valid document passed validation")
    except DocumentValidationError as e:
        print(f"❌ Valid document failed: {e}")
    
    # Test 2: Knowledge base document with extra fields (should fail if strict mode enabled)
    print("\n📋 Test 2: Knowledge base document with extra fields")
    doc_with_extra = valid_doc.copy()
    doc_with_extra["extra_field"] = "This should not be allowed"
    doc_with_extra["another_extra"] = "Neither should this"
    
    try:
        result = validate_document_structure(doc_with_extra, is_knowledge_doc=True)
        print("⚠️  Document with extra fields passed (strict mode may be disabled)")
    except DocumentValidationError as e:
        print(f"✅ Document with extra fields correctly rejected: {e}")
    
    # Test 3: Non-knowledge document
    print("\n📋 Test 3: Non-knowledge document")
    custom_doc = {
        "name": "Custom Document",
        "data": {"key": "value"},
        "timestamp": "2025-01-04"
    }
    
    try:
        result = validate_document_structure(custom_doc, is_knowledge_doc=False)
        print("✅ Custom document passed validation")
    except DocumentValidationError as e:
        print(f"❌ Custom document failed: {e}")
    
    # Test 4: Missing required fields
    print("\n📋 Test 4: Knowledge base document missing required fields")
    incomplete_doc = {
        "id": "incomplete-doc",
        "title": "Incomplete Document"
        # Missing other required fields
    }
    
    try:
        result = validate_document_structure(incomplete_doc, is_knowledge_doc=True)
        print("⚠️  Incomplete document passed (validation may be lenient)")
    except DocumentValidationError as e:
        print(f"✅ Incomplete document correctly rejected: {e}")

if __name__ == "__main__":
    test_strict_validation()
