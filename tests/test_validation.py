#!/usr/bin/env python3
"""
Document Validation Test
Tests document validation and processing features
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from test_helpers import load_test_config

def test_document_validation():
    """Test basic document validation"""
    print("🧪 Document Validation Test")
    print("=" * 50)
    
    # Load configuration
    config = load_test_config()
    
    # Create test documents
    test_docs = [
        {
            "name": "valid_markdown.md",
            "content": "# Valid Document\n\nThis is a valid markdown document.\n\n## Section 1\nContent here.",
            "expected": "valid"
        },
        {
            "name": "empty_document.md", 
            "content": "",
            "expected": "empty"
        },
        {
            "name": "json_config.json",
            "content": json.dumps({"key": "value", "number": 42}, indent=2),
            "expected": "valid"
        },
        {
            "name": "invalid_json.json",
            "content": '{"key": value, invalid}',
            "expected": "invalid"
        }
    ]
    
    with tempfile.TemporaryDirectory(prefix="validation_test_") as temp_dir:
        temp_path = Path(temp_dir)
        print(f"📁 Test directory: {temp_path}")
        
        results = {}
        
        for doc in test_docs:
            file_path = temp_path / doc["name"]
            
            # Write test file
            with open(file_path, 'w') as f:
                f.write(doc["content"])
            
            # Validate document
            validation_result = validate_document(file_path)
            results[doc["name"]] = validation_result
            
            print(f"📄 {doc['name']}: {validation_result['status']}")
            if validation_result.get('errors'):
                print(f"   ⚠️ Errors: {validation_result['errors']}")
        
        print("\n📊 Validation Summary:")
        for name, result in results.items():
            status_icon = "✅" if result['status'] != 'invalid' else "❌"
            print(f"   {status_icon} {name}: {result['status']}")
        
        return results

def validate_document(file_path):
    """Simple document validation function"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Basic validations
        if not content.strip():
            return {"status": "empty", "errors": ["Document is empty"]}
        
        # JSON validation
        if file_path.suffix == '.json':
            try:
                json.loads(content)
                return {"status": "valid", "type": "json"}
            except json.JSONDecodeError as e:
                return {"status": "invalid", "errors": [f"Invalid JSON: {str(e)}"]}
        
        # Markdown validation
        if file_path.suffix == '.md':
            if content.startswith('#'):
                return {"status": "valid", "type": "markdown"}
            else:
                return {"status": "warning", "warnings": ["No markdown headers found"]}
        
        # Default validation
        return {"status": "valid", "type": "text"}
        
    except Exception as e:
        return {"status": "error", "errors": [f"Could not read file: {str(e)}"]}

def test_content_analysis():
    """Test content analysis features"""
    print("\n🔍 Content Analysis Test")
    print("=" * 50)
    
    sample_texts = [
        "This is a simple test document with basic content.",
        "# Important Document\n\nThis document contains **bold** and *italic* text.",
        "Configuration: server_port=8080, debug=true, workers=4",
        ""
    ]
    
    for i, text in enumerate(sample_texts, 1):
        analysis = analyze_content(text)
        print(f"📝 Text {i}:")
        print(f"   Length: {analysis['length']} chars")
        print(f"   Words: {analysis['words']}")
        print(f"   Lines: {analysis['lines']}")
        if analysis.get('features'):
            print(f"   Features: {', '.join(analysis['features'])}")
        print()

def analyze_content(text):
    """Simple content analysis"""
    if not text:
        return {"length": 0, "words": 0, "lines": 0}
    
    lines = text.split('\n')
    words = len(text.split())
    
    features = []
    if '#' in text:
        features.append("headers")
    if '**' in text or '__' in text:
        features.append("bold")
    if '*' in text or '_' in text:
        features.append("italic")
    if '=' in text and any(word in text.lower() for word in ['config', 'setting', 'port']):
        features.append("configuration")
    
    return {
        "length": len(text),
        "words": words, 
        "lines": len(lines),
        "features": features
    }

if __name__ == "__main__":
    try:
        print("🚀 Starting document validation tests...")
        print()
        
        # Run validation tests
        validation_results = test_document_validation()
        
        # Run content analysis tests
        test_content_analysis()
        
        print("✅ All validation tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)
