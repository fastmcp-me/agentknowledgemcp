#!/usr/bin/env python3
"""
Quick debug test for path normalization
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from document_schema import normalize_file_path

# Test simple case
base_dir = "/tmp/knowledge_base_test"
test_path = "/tmp/knowledge_base_test/auth/jwt.md"

print(f"Base directory: {base_dir}")
print(f"Test path: {test_path}")

# Debug Path logic
from pathlib import Path
base_path = Path(base_dir).resolve()
path = Path(test_path)

print(f"\nPath analysis:")
print(f"  base_path.resolve(): {base_path}")
print(f"  path: {path}")
print(f"  path.is_absolute(): {path.is_absolute()}")

try:
    relative_path = path.relative_to(base_path)
    print(f"  relative_path: {relative_path}")
except ValueError as e:
    print(f"  relative_to failed: {e}")

# Test our function
result = normalize_file_path(test_path, base_dir)
print(f"\nResult: {result}")
