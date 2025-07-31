#!/usr/bin/env python3
"""
Test script for enhanced smart prompting with file citations
Creates sample .knowledges content and tests the enhanced citation functionality.
"""

from pathlib import Path
import tempfile
import asyncio
import sys

# Add src to path for testing
sys.path.append(str(Path(__file__).parent.parent))

async def test_enhanced_smart_prompting():
    """Test the enhanced smart prompting with file citations."""
    
    # Import the enhanced function
    from src.prompts.sub_servers.smart_prompting_server import load_knowledges_content
    
    print("🧪 Testing Enhanced Smart Prompting with File Citations")
    print("=" * 60)
    
    # Create temporary .knowledges directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        knowledges_dir = temp_path / ".knowledges"
        
        # Create subdirectories
        workflows_dir = knowledges_dir / "workflows"
        rules_dir = knowledges_dir / "rules"
        memories_dir = knowledges_dir / "memories"
        
        workflows_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)
        memories_dir.mkdir(parents=True)
        
        # Create sample workflow file
        workflow_content = """# Deployment Process

## Pre-deployment Checklist
1. Run all tests
2. Update version number
3. Create release notes

## Deployment Steps
1. Build production image
2. Deploy to staging
3. Run smoke tests
4. Deploy to production
5. Monitor for issues

## Post-deployment
1. Verify all services
2. Update documentation
3. Notify team"""
        
        workflow_file = workflows_dir / "deployment.md"
        workflow_file.write_text(workflow_content)
        
        # Create sample rules file
        rules_content = """# Python Coding Standards

## Code Style
- Use black formatter
- Follow PEP 8 guidelines
- Maximum line length: 88 characters

## Documentation
- All functions must have docstrings
- Use type hints for parameters
- Include examples in docstrings

## Testing
- Write unit tests for all functions
- Achieve minimum 80% coverage
- Use pytest for testing framework"""
        
        rules_file = rules_dir / "python-style.md"
        rules_file.write_text(rules_content)
        
        # Create sample memory file
        memory_content = """# Database Migration Lessons

## Issue with Migration Order
Date: 2024-01-15
Problem: Migrations failed due to dependency order

Solution: Always check foreign key dependencies before creating migrations

## Performance Issue with Large Tables
Date: 2024-02-20
Problem: Migration took 6 hours on production

Solution: Use batch processing for large data migrations
- Process in chunks of 1000 records
- Add progress monitoring
- Plan for downtime windows"""
        
        memory_file = memories_dir / "migration-issues.md"
        memory_file.write_text(memory_content)
        
        print(f"📁 Created test .knowledges structure in: {knowledges_dir}")
        print(f"   📄 Workflow: {workflow_file.name} ({len(workflow_content.split(chr(10)))} lines)")
        print(f"   📄 Rules: {rules_file.name} ({len(rules_content.split(chr(10)))} lines)")
        print(f"   📄 Memory: {memory_file.name} ({len(memory_content.split(chr(10)))} lines)")
        
        # Test the enhanced load function
        print(f"\n🔍 Testing enhanced load_knowledges_content function...")
        content = await load_knowledges_content(knowledges_dir, "project")
        
        print(f"\n📋 Enhanced Content Output:")
        print("-" * 40)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("-" * 40)
        
        # Verify key enhancements
        print(f"\n✅ **Enhancement Verification:**")
        
        # Check for file paths
        has_file_paths = "**File**:" in content and ".knowledges/" in content
        print(f"   📁 File paths included: {'✅ YES' if has_file_paths else '❌ NO'}")
        
        # Check for line numbers
        has_line_numbers = "Lines 1-" in content and "```" in content
        print(f"   📊 Line numbers included: {'✅ YES' if has_line_numbers else '❌ NO'}")
        
        # Check for numbered content
        has_numbered_content = ": #" in content or ":   1." in content
        print(f"   🔢 Numbered content lines: {'✅ YES' if has_numbered_content else '❌ NO'}")
        
        # Verify all files are included
        has_all_files = all(filename in content for filename in ["deployment", "python-style", "migration-issues"])
        print(f"   📄 All files included: {'✅ YES' if has_all_files else '❌ NO'}")
        
        print(f"\n🎯 **Expected Citation Format in AI Response:**")
        print(f"   ✅ Follow deployment process in `workflows/deployment.md:6-10`")
        print(f"   ✅ Apply coding standards from `rules/python-style.md:4-6`") 
        print(f"   ✅ Remember migration lesson in `memories/migration-issues.md:15-18`")
        
        # Calculate enhancement metrics
        total_lines = len(content.split('\n'))
        file_count = content.count("**File**:")
        code_blocks = content.count("```") // 2  # Each file has start and end markers
        
        print(f"\n📊 **Enhancement Metrics:**")
        print(f"   📏 Total content lines: {total_lines}")
        print(f"   📁 Files processed: {file_count}")
        print(f"   💻 Code blocks with line numbers: {code_blocks}")
        print(f"   📐 Content length: {len(content)} characters")
        
        return True

if __name__ == "__main__":
    asyncio.run(test_enhanced_smart_prompting())
