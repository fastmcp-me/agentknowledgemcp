#!/usr/bin/env python3
"""
Comprehensive test script for file path handling in document validation.
"""
import sys
import json
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from document_schema import (
    normalize_file_path,
    validate_document_structure, 
    create_document_template,
    DocumentValidationError
)

# Import test helpers
sys.path.append(str(Path(__file__).parent / "tests"))
from test_helpers import get_test_directories, get_test_files, get_expected_results, get_base_dir

def test_normalize_file_path():
    """Test file path normalization in various scenarios."""
    print("=" * 70)
    print("🧪 TEST FILE PATH NORMALIZATION")
    print("=" * 70)
    
    # Test cases with base directory
    base_dir = "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs"
    
    test_cases = [
        {
            "name": "Absolute path within base directory",
            "input": "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs/auth/jwt.md",
            "base_dir": base_dir,
            "expected_file_path": "auth/jwt.md",
            "expected_file_name": "jwt.md",
            "expected_directory": "auth"
        },
        {
            "name": "Absolute path outside base directory",
            "input": "/Users/nguyenkimchung/ElasticSearch/backend/auth/jwt.md",
            "base_dir": base_dir,
            "expected_file_path": "/Users/nguyenkimchung/ElasticSearch/backend/auth/jwt.md",
            "expected_file_name": "jwt.md", 
            "expected_directory": "/Users/nguyenkimchung/ElasticSearch/backend/auth"
        },
        {
            "name": "Relative path with ./",
            "input": "./auth/jwt.md",
            "base_dir": base_dir,
            "expected_file_path": "auth/jwt.md",
            "expected_file_name": "jwt.md",
            "expected_directory": "auth"
        },
        {
            "name": "Relative path without ./",
            "input": "auth/jwt.md",
            "base_dir": base_dir,
            "expected_file_path": "auth/jwt.md",
            "expected_file_name": "jwt.md",
            "expected_directory": "auth"
        },
        {
            "name": "File in root directory",
            "input": "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs/readme.md",
            "base_dir": base_dir,
            "expected_file_path": "readme.md",
            "expected_file_name": "readme.md",
            "expected_directory": ""
        },
        {
            "name": "Windows-style path",
            "input": "auth\\jwt.md",
            "base_dir": None,
            "expected_file_path": "auth/jwt.md",
            "expected_file_name": "jwt.md",
            "expected_directory": "auth"
        },
        {
            "name": "No base directory provided",
            "input": "/absolute/path/file.md",
            "base_dir": None,
            "expected_file_path": "/absolute/path/file.md",
            "expected_file_name": "file.md",
            "expected_directory": "/absolute/path"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        print(f"   Base dir: {test_case['base_dir']}")
        
        try:
            result = normalize_file_path(test_case['input'], test_case['base_dir'])
            
            # Check results
            checks = [
                ("file_path", result['file_path'], test_case['expected_file_path']),
                ("file_name", result['file_name'], test_case['expected_file_name']),
                ("directory", result['directory'], test_case['expected_directory'])
            ]
            
            all_correct = True
            for field, actual, expected in checks:
                if actual != expected:
                    print(f"   ❌ {field}: expected '{expected}', got '{actual}'")
                    all_correct = False
                else:
                    print(f"   ✅ {field}: '{actual}'")
            
            if all_correct:
                passed += 1
                print(f"   ✅ PASSED")
            else:
                print(f"   ❌ FAILED")
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 File Path Normalization: {passed}/{total} tests passed")
    return passed == total

def test_document_with_paths():
    """Test document validation with different path scenarios."""
    print("\n" + "=" * 70)
    print("🧪 TEST DOCUMENT VALIDATION WITH PATHS")
    print("=" * 70)
    
    base_dir = "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs"
    
    test_cases = [
        {
            "name": "Document with absolute path in base directory",
            "document": {
                "id": "test-001",
                "title": "Test Document",
                "summary": "Test summary",
                "file_path": "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs/auth/jwt.md",
                "file_name": "wrong_name.md",  # Will be corrected
                "directory": "wrong_dir",      # Will be corrected
                "last_modified": "2025-07-04T15:00:00Z",
                "priority": "high",
                "tags": ["test"],
                "related": [],
                "source_type": "markdown",
                "key_points": ["Point 1"]
            },
            "expected_corrections": {
                "file_path": "auth/jwt.md",
                "file_name": "jwt.md",
                "directory": "auth"
            }
        },
        {
            "name": "Document with relative path",
            "document": {
                "id": "test-002",
                "title": "Test Document 2",
                "summary": "Test summary 2",
                "file_path": "./config/database.json",
                "file_name": "database.json",
                "directory": "config",
                "last_modified": "2025-07-04T15:00:00Z",
                "priority": "medium",
                "tags": ["config"],
                "related": [],
                "source_type": "config",
                "key_points": ["Configuration"]
            },
            "expected_corrections": {
                "file_path": "config/database.json",
                "file_name": "database.json",
                "directory": "config"
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        try:
            validated = validate_document_structure(test_case['document'], base_dir)
            
            all_correct = True
            for field, expected in test_case['expected_corrections'].items():
                actual = validated[field]
                if actual != expected:
                    print(f"   ❌ {field}: expected '{expected}', got '{actual}'")
                    all_correct = False
                else:
                    print(f"   ✅ {field}: '{actual}'")
            
            if all_correct:
                passed += 1
                print(f"   ✅ VALIDATION PASSED")
            else:
                print(f"   ❌ VALIDATION FAILED")
                
        except Exception as e:
            print(f"   ❌ VALIDATION ERROR: {e}")
    
    print(f"\n📊 Document Validation: {passed}/{total} tests passed")
    return passed == total

def test_template_creation():
    """Test template creation with path normalization."""
    print("\n" + "=" * 70)
    print("🧪 TEST TEMPLATE CREATION WITH PATH NORMALIZATION")
    print("=" * 70)
    
    base_dir = "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs"
    
    test_cases = [
        {
            "name": "Template with absolute path",
            "params": {
                "title": "JWT Authentication Guide",
                "file_path": "/Users/nguyenkimchung/AgentKnowledgeMCP/.knowledges/docs/auth/jwt-guide.md",
                "priority": "high",
                "source_type": "documentation",
                "tags": ["auth", "JWT"],
                "summary": "Comprehensive JWT authentication guide",
                "key_points": ["Token validation", "Security best practices"],
                "related": ["auth-basics-001"],
                "base_directory": base_dir
            },
            "expected": {
                "file_path": "auth/jwt-guide.md",
                "file_name": "jwt-guide.md",
                "directory": "auth"
            }
        },
        {
            "name": "Template with relative path",
            "params": {
                "title": "API Error Handling",
                "file_path": "api/error-handling.md",
                "priority": "medium",
                "source_type": "markdown",
                "tags": ["API", "errors"],
                "summary": "How to handle API errors properly",
                "key_points": ["HTTP status codes", "Error messages"],
                "related": [],
                "base_directory": base_dir
            },
            "expected": {
                "file_path": "api/error-handling.md",
                "file_name": "error-handling.md",
                "directory": "api"
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input path: {test_case['params']['file_path']}")
        
        try:
            template = create_document_template(**test_case['params'])
            
            all_correct = True
            for field, expected in test_case['expected'].items():
                actual = template[field]
                if actual != expected:
                    print(f"   ❌ {field}: expected '{expected}', got '{actual}'")
                    all_correct = False
                else:
                    print(f"   ✅ {field}: '{actual}'")
            
            # Check that ID is generated correctly
            expected_id_prefix = {
                "documentation": "doc-",
                "markdown": "md-"
            }.get(test_case['params']['source_type'], "doc-")
            
            if template['id'].startswith(expected_id_prefix):
                print(f"   ✅ ID: '{template['id']}'")
            else:
                print(f"   ❌ ID should start with '{expected_id_prefix}', got '{template['id']}'")
                all_correct = False
            
            if all_correct:
                passed += 1
                print(f"   ✅ TEMPLATE CREATION PASSED")
            else:
                print(f"   ❌ TEMPLATE CREATION FAILED")
                
        except Exception as e:
            print(f"   ❌ TEMPLATE CREATION ERROR: {e}")
    
    print(f"\n📊 Template Creation: {passed}/{total} tests passed")
    return passed == total

def test_edge_cases():
    """Test edge cases and error conditions."""
    print("\n" + "=" * 70)
    print("🧪 TEST EDGE CASES")
    print("=" * 70)
    
    edge_cases = [
        {
            "name": "Empty file path",
            "test": lambda: normalize_file_path(""),
            "should_fail": True
        },
        {
            "name": "Path with special characters",
            "test": lambda: normalize_file_path("docs/file with spaces & symbols.md"),
            "should_fail": False
        },
        {
            "name": "Very long path",
            "test": lambda: normalize_file_path("a/" * 100 + "file.md"),
            "should_fail": False
        },
        {
            "name": "Path with Unicode characters",
            "test": lambda: normalize_file_path("docs/tài-liệu-việt-nam.md"),
            "should_fail": False
        }
    ]
    
    passed = 0
    total = len(edge_cases)
    
    for i, case in enumerate(edge_cases, 1):
        print(f"\n{i}. {case['name']}")
        
        try:
            result = case['test']()
            if case['should_fail']:
                print(f"   ❌ Expected failure but got: {result}")
            else:
                print(f"   ✅ SUCCESS: {result}")
                passed += 1
        except Exception as e:
            if case['should_fail']:
                print(f"   ✅ Expected failure: {e}")
                passed += 1
            else:
                print(f"   ❌ Unexpected failure: {e}")
    
    print(f"\n📊 Edge Cases: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run comprehensive file path tests."""
    print("🚀 COMPREHENSIVE FILE PATH HANDLING TESTS")
    print("Testing file path normalization, validation, and template creation")
    
    tests = [
        ("File Path Normalization", test_normalize_file_path),
        ("Document Validation", test_document_with_paths),
        ("Template Creation", test_template_creation),
        ("Edge Cases", test_edge_cases)
    ]
    
    passed_tests = 0
    
    for test_name, test_func in tests:
        if test_func():
            passed_tests += 1
    
    print("\n" + "=" * 70)
    print(f"📊 FINAL RESULTS: {passed_tests}/{len(tests)} test suites passed")
    print("=" * 70)
    
    if passed_tests == len(tests):
        print("🎉 ALL TESTS PASSED! File path handling is working correctly.")
        print("\n✅ Key Features Validated:")
        print("   • Absolute to relative path conversion")
        print("   • Cross-platform path handling (Windows/Unix)")
        print("   • Base directory validation")
        print("   • Automatic file_name and directory extraction")
        print("   • Path normalization with forward slashes")
        print("   • Template creation with proper paths")
        print("\n🚀 MCP Server ready for file path operations!")
    else:
        print("❌ Some tests failed. Please review the implementation.")

if __name__ == "__main__":
    main()
