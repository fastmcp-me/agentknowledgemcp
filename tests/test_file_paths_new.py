#!/usr/bin/env python3
"""
Comprehensive test script for file path handling in document validation.
Uses generic paths from test_config.json to avoid hardcoded personal paths.
"""
import sys
import json
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from document_schema import (
    normalize_file_path,
    validate_document_structure, 
    create_document_template,
    DocumentValidationError
)


def load_test_config():
    """Load test configuration with generic paths."""
    config_path = Path(__file__).parent / "test_config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def test_normalize_file_path():
    """Test file path normalization with various input formats."""
    print("🧪 TEST FILE PATH NORMALIZATION")
    print("=" * 70)
    
    config = load_test_config()
    base_dir = config["test_directories"]["docs_dir"]
    
    test_cases = [
        {
            "name": "Absolute path within base directory",
            "input": config["test_files"]["jwt_absolute"],
            "base_dir": base_dir,
            "expected": config["expected_results"]["jwt_from_absolute"]
        },
        {
            "name": "Absolute path outside base directory",
            "input": config["test_files"]["outside_base"],
            "base_dir": base_dir,
            "expected": config["expected_results"]["outside_base_unchanged"]
        },
        {
            "name": "Relative path with ./",
            "input": "./" + config["test_files"]["jwt_relative"],
            "base_dir": base_dir,
            "expected": config["expected_results"]["jwt_from_absolute"]
        },
        {
            "name": "Relative path without ./",
            "input": config["test_files"]["jwt_relative"],
            "base_dir": base_dir,
            "expected": config["expected_results"]["jwt_from_absolute"]
        },
        {
            "name": "File in root directory",
            "input": config["test_files"]["readme_absolute"],
            "base_dir": base_dir,
            "expected": config["expected_results"]["readme_from_absolute"]
        },
        {
            "name": "Windows-style path",
            "input": "auth\\jwt.md",
            "base_dir": base_dir,
            "expected": {
                "file_path": "auth/jwt.md",
                "file_name": "jwt.md",
                "directory": "auth"
            }
        },
        {
            "name": "No base directory provided",
            "input": "/absolute/path/file.md",
            "base_dir": None,
            "expected": {
                "file_path": "/absolute/path/file.md",
                "file_name": "file.md",
                "directory": "/absolute/path"
            }
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"   Input: {test_case['input']}")
        print(f"   Base:  {test_case['base_dir']}")
        
        try:
            result = normalize_file_path(test_case['input'], test_case['base_dir'])
            expected = test_case['expected']
            
            # Check all expected fields
            all_correct = True
            for key, expected_value in expected.items():
                if result.get(key) != expected_value:
                    print(f"   ❌ {key}: got '{result.get(key)}', expected '{expected_value}'")
                    all_correct = False
            
            if all_correct:
                print(f"   ✅ PASSED")
                print(f"      file_path: {result['file_path']}")
                print(f"      file_name: {result['file_name']}")
                print(f"      directory: {result['directory']}")
                passed += 1
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total


def test_document_with_paths():
    """Test document validation with different path scenarios."""
    print("\n" + "=" * 70)
    print("🧪 TEST DOCUMENT VALIDATION WITH PATHS")
    print("=" * 70)
    
    config = load_test_config()
    base_dir = config["test_directories"]["docs_dir"]
    
    test_cases = [
        {
            "name": "Document with absolute path in base directory",
            "document": {
                "id": "test-001",
                "title": "JWT Authentication Guide",
                "summary": "Comprehensive guide for JWT implementation",
                "file_path": config["test_files"]["jwt_absolute"],
                "file_name": "wrong_name.md",  # Will be corrected
                "directory": "wrong_dir",      # Will be corrected
                "last_modified": "2025-07-04T15:00:00Z",
                "priority": "high",
                "tags": ["authentication", "JWT", "security"],
                "related": [],
                "source_type": "markdown",
                "key_points": ["Token validation", "Secure storage", "Refresh tokens"]
            },
            "expected_corrections": config["expected_results"]["jwt_from_absolute"]
        },
        {
            "name": "Document with relative path",
            "document": {
                "id": "test-002",
                "title": "Database Configuration",
                "summary": "Database connection settings and configuration",
                "file_path": config["test_files"]["config_relative"],
                "file_name": "database.json",
                "directory": "config",
                "last_modified": "2025-07-04T15:00:00Z",
                "priority": "medium",
                "tags": ["configuration", "database"],
                "related": [],
                "source_type": "config",
                "key_points": ["Connection strings", "Pool settings"]
            },
            "expected_corrections": config["expected_results"]["config_from_relative"]
        },
        {
            "name": "Document with external path (should remain unchanged)",
            "document": {
                "id": "test-003",
                "title": "External Documentation",
                "summary": "Documentation stored outside knowledge base",
                "file_path": config["test_files"]["outside_base"],
                "file_name": "external-file.md",
                "directory": "/some/external/path",
                "last_modified": "2025-07-04T15:00:00Z",
                "priority": "low",
                "tags": ["external"],
                "related": [],
                "source_type": "markdown",
                "key_points": ["External reference"]
            },
            "expected_corrections": config["expected_results"]["outside_base_unchanged"]
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        try:
            validated = validate_document_structure(test_case['document'], base_dir)
            
            all_correct = True
            expected = test_case['expected_corrections']
            
            for key, expected_value in expected.items():
                actual_value = validated.get(key)
                if actual_value != expected_value:
                    print(f"   ❌ {key}: got '{actual_value}', expected '{expected_value}'")
                    all_correct = False
            
            if all_correct:
                print(f"   ✅ PASSED - Path corrections applied correctly")
                print(f"      file_path: {validated['file_path']}")
                print(f"      file_name: {validated['file_name']}")
                print(f"      directory: {validated['directory']}")
                passed += 1
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total


def test_template_creation():
    """Test document template creation with path normalization."""
    print("\n" + "=" * 70)
    print("🧪 TEST TEMPLATE CREATION")
    print("=" * 70)
    
    config = load_test_config()
    base_dir = config["test_directories"]["docs_dir"]
    
    test_cases = [
        {
            "name": "Template with absolute path",
            "params": {
                "title": "API Error Handling Best Practices",
                "file_path": config["test_files"]["api_guide_absolute"],
                "priority": "high",
                "source_type": "documentation",
                "tags": ["API", "error handling", "best practices"],
                "summary": "Comprehensive guide for handling API errors properly",
                "key_points": [
                    "Use proper HTTP status codes",
                    "Provide meaningful error messages", 
                    "Log errors for debugging",
                    "Handle edge cases gracefully"
                ],
                "related": ["api-design-001", "logging-best-practices-003"],
                "base_directory": base_dir
            },
            "expected_path": "api/error-handling.md"
        },
        {
            "name": "Template with relative path",
            "params": {
                "title": "Database Configuration Guide",
                "file_path": config["test_files"]["config_relative"],
                "priority": "medium",
                "source_type": "configuration",
                "tags": ["database", "configuration"],
                "summary": "Database setup and configuration guidelines",
                "key_points": [
                    "Connection pool settings",
                    "Security configurations",
                    "Performance tuning"
                ],
                "related": ["setup-guide-001"],
                "base_directory": base_dir
            },
            "expected_path": "config/database.json"
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        
        try:
            template = create_document_template(**test_case['params'])
            
            if template['file_path'] == test_case['expected_path']:
                print(f"   ✅ PASSED")
                print(f"      Generated ID: {template['id']}")
                print(f"      File path: {template['file_path']}")
                print(f"      File name: {template['file_name']}")
                print(f"      Directory: {template['directory']}")
                passed += 1
            else:
                print(f"   ❌ FAILED - Expected path: {test_case['expected_path']}, got: {template['file_path']}")
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    return passed == total


def test_error_scenarios():
    """Test error handling scenarios."""
    print("\n" + "=" * 70)
    print("🧪 TEST ERROR SCENARIOS")
    print("=" * 70)
    
    config = load_test_config()
    base_dir = config["test_directories"]["docs_dir"]
    
    # Test invalid document
    print("\n1. Invalid document structure")
    invalid_doc = {
        "id": "test-invalid",
        "title": "Invalid Document",
        "summary": "Test invalid document",
        "priority": "invalid_priority",  # Invalid priority
        "tags": "should_be_array",       # Invalid type
        "source_type": "invalid_type"    # Invalid source type
        # Missing required fields
    }
    
    try:
        validated = validate_document_structure(invalid_doc, base_dir)
        print("   ❌ UNEXPECTED SUCCESS!")
        return False
    except DocumentValidationError as e:
        print("   ✅ VALIDATION CORRECTLY FAILED!")
        print(f"      Error: {e}")
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        return False
    
    # Test missing required fields
    print("\n2. Missing required fields")
    incomplete_doc = {
        "id": "test-incomplete",
        "title": "Incomplete Document"
        # Missing summary, priority, tags, etc.
    }
    
    try:
        validated = validate_document_structure(incomplete_doc, base_dir)
        print("   ❌ UNEXPECTED SUCCESS!")
        return False
    except DocumentValidationError as e:
        print("   ✅ VALIDATION CORRECTLY FAILED!")
        print(f"      Error: {e}")
    except Exception as e:
        print(f"   ❌ UNEXPECTED ERROR: {e}")
        return False
    
    print("\n📊 Error scenarios: 2/2 tests passed")
    return True


def main():
    """Run all file path tests."""
    print("🚀 FILE PATH HANDLING TESTS")
    print("=" * 70)
    
    config = load_test_config()
    print(f"📁 Using test base directory: {config['test_directories']['docs_dir']}")
    print(f"📝 Test configuration loaded from: test_config.json")
    
    # Run all tests
    results = []
    
    print("\n" + "🔬" * 35)
    results.append(("Path Normalization", test_normalize_file_path()))
    
    print("\n" + "🔬" * 35)
    results.append(("Document Validation", test_document_with_paths()))
    
    print("\n" + "🔬" * 35)
    results.append(("Template Creation", test_template_creation()))
    
    print("\n" + "🔬" * 35)
    results.append(("Error Scenarios", test_error_scenarios()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 FINAL SUMMARY")
    print("=" * 70)
    
    total_passed = 0
    total_tests = len(results)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status}: {test_name}")
        if passed:
            total_passed += 1
    
    print(f"\n🎯 Overall Results: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! File path handling is working correctly!")
        return True
    else:
        print("💥 Some tests failed! Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
