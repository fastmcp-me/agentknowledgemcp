# Tests Directory

This directory contains all test files and demo scripts for the Elasticsearch MCP Server.

## Test Files

### Core Functionality Tests
- **`test_file_paths.py`** - Tests file path normalization and cross-platform compatibility
- **`test_validation.py`** - Tests document schema validation and error handling
- **`test_version_control.py`** - Comprehensive version control system tests
- **`test_simple_vcs.py`** - Simple VCS functionality demonstration

### Demo Scripts
- **`demo_agent_workflow.py`** - Complete agent workflow demonstration
- **`demo_version_control.py`** - Version control features demo (with import issues)

### Utility Tests
- **`quick_test.py`** - Quick functionality check script

## Running Tests

### Individual Tests
```bash
# Test file operations and path handling
python3 tests/test_file_paths.py

# Test document validation
python3 tests/test_validation.py

# Test version control (comprehensive)
python3 tests/test_version_control.py

# Test version control (simple demo)
python3 tests/test_simple_vcs.py

# Quick functionality check
python3 tests/quick_test.py
```

### Demo Scripts
```bash
# Run complete workflow demo
python3 tests/demo_agent_workflow.py

# Run version control demo (may have import issues)
python3 tests/demo_version_control.py
```

### Run All Tests
```bash
# From project root
for test in tests/test_*.py; do
    echo "Running $test..."
    python3 "$test"
    echo "---"
done
```

## Test Coverage

### ✅ File System Operations
- Path normalization (Windows/Unix)
- Relative path conversion
- Directory traversal protection
- Cross-platform compatibility
- File operations (read, write, move, copy)

### ✅ Document Validation
- Schema enforcement
- Required field validation
- Type checking
- Error message formatting
- Template generation

### ✅ Version Control
- Git repository setup
- SVN repository setup
- File commit operations
- History retrieval
- Multi-VCS support

### ✅ Integration Testing
- End-to-end workflows
- Error handling
- Performance validation
- Cross-platform testing

## Expected Results

All tests should pass with ✅ indicators. Common test outputs:

```
🧪 Testing File Path Normalization
==================================================
✅ All path normalization tests passed! (4/4 test suites)

🧪 Testing Version Control System
==================================================
✅ Git repository setup successful
✅ File operations successful - 3 commits found
✅ File history retrieval successful
🎉 Version control system is working correctly!
```

## Test Environment

- **Python**: 3.8+ required
- **Git**: Required for version control tests
- **SVN**: Optional, for SVN-specific tests
- **Elasticsearch**: Optional, server will work without it

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're running from project root
2. **Git not found**: Install Git for version control tests
3. **Permission errors**: Check file system permissions
4. **Path issues**: Tests create temporary directories automatically

### Debug Mode

Set environment variable for verbose output:
```bash
export TEST_DEBUG=1
python3 tests/test_file_paths.py
```

## Adding New Tests

When adding new functionality:

1. Create test file: `tests/test_new_feature.py`
2. Follow existing test patterns
3. Include both positive and negative test cases
4. Test error handling and edge cases
5. Update this README with new test description
