#!/usr/bin/env python3
"""
Run all tests for Elasticsearch MCP Server
"""
import subprocess
import sys
from pathlib import Path
import time


def run_test(test_file):
    """Run a single test file."""
    print(f"\n{'='*60}")
    print(f"🧪 Running: {test_file.name}")
    print('='*60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=test_file.parent.parent,
            capture_output=False,
            text=True
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {test_file.name} PASSED ({duration:.2f}s)")
            return True
        else:
            print(f"❌ {test_file.name} FAILED ({duration:.2f}s)")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {test_file.name} ERROR: {e} ({duration:.2f}s)")
        return False


def main():
    """Run all tests."""
    print("🚀 Elasticsearch MCP Server - Test Suite")
    print("=" * 60)
    
    tests_dir = Path(__file__).parent
    
    # Find all test files
    test_files = sorted(tests_dir.glob("test_*.py"))
    
    if not test_files:
        print("❌ No test files found!")
        sys.exit(1)
    
    print(f"📋 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"   • {test_file.name}")
    
    # Run all tests
    results = []
    start_time = time.time()
    
    for test_file in test_files:
        success = run_test(test_file)
        results.append((test_file.name, success))
    
    total_duration = time.time() - start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {status}: {test_name}")
    
    print(f"\n📈 Results: {passed}/{len(results)} tests passed")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        sys.exit(0)
    else:
        print(f"\n💥 {failed} test(s) failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
