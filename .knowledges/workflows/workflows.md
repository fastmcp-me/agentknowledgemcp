# AgentKnowledgeMCP Workflows

This file contains all workflows for the AgentKnowledgeMCP project.

---

# Release Publishing Workflow {#wf_001}

**WorkflowId**: WF_001
**Description**: Complete workflow for publishing new releases to PyPI with version management and quality checks
**Created**: 2025-08-01
**Updated**: 2025-08-01

## Workflow Logic
```
BEGIN release_publishing_workflow
    # 1. Version Management
    DO check_current_version_in_all_files
    DO determine_new_version_based_on_changes
    
    IF major_breaking_changes
        DO increment_major_version  # X+1.0.0
    ELSE IF new_features_added
        DO increment_minor_version  # X.Y+1.0
    ELSE IF bugfixes_only
        DO increment_patch_version  # X.Y.Z+1
    END IF
    
    # 2. 5-File Consistency
    DO update_version_in_pyproject_toml
    DO update_version_in_src_init_py
    DO update_version_in_src_config_json
    DO update_version_in_src_config_default_json
    DO update_version_in_changelog_md
    
    WHILE version_consistency_check_fails
        DO identify_inconsistent_files
        DO fix_version_mismatches
        DO verify_all_files_match
    END WHILE
    
    # 3. Build Process
    DO clean_previous_build_artifacts
    DO remove_dist_build_directories
    DO clean_python_cache_files
    
    DO run_python_build_command
    
    IF build_fails
        DO check_build_error_logs
        DO fix_syntax_or_dependency_issues
        GOTO run_python_build_command
    END IF
    
    DO verify_wheel_and_source_generated
    
    # 4. Quality Checks
    DO run_twine_check_on_dist_files
    
    IF quality_check_fails
        DO review_package_structure
        DO fix_metadata_issues
        GOTO run_twine_check_on_dist_files
    END IF
    
    # 5. PyPI Publishing
    DO upload_packages_to_pypi
    DO verify_package_appears_on_pypi
    DO test_installation_from_pypi
    
    # 6. Final Verification
    DO verify_pypi_installation_works
    DO update_documentation_if_needed
    DO close_related_issues
    
END release_publishing_workflow
```

## References
- **Related Rules**: [RULE_001](rules.md#rule_001) - Version consistency requirements
- **Related Memories**: [MEM_001](memories.md#mem_001) - Previous release lessons learned

---
*Last updated: 2025-08-01*
