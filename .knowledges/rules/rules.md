# Server Restart After Code Changes {#rule_001}

**RuleId**: RULE_001
**When**: After making any code changes to the server (source files, configuration, dependencies)
**Do**: 
- Inform user that server restart is required
- Ask user to restart the server before proceeding with testing
- Wait for user confirmation that server has been restarted
- Only then proceed with testing or validation
**Not Do**: 
- Do not attempt to test without server restart
- Do not assume code changes are loaded in running server
- Do not proceed with validation if unsure about restart status
**Description**: Ensures all code changes are properly loaded into the server runtime environment before testing, preventing false test results due to stale code execution
**Created**: 2025-08-06
**Updated**: 2025-08-06

## References
- **Related Rules**: None yet
- **Related Workflows**: To be integrated into testing and validation workflows
- **Related Memories**: To be created for specific testing scenarios

---
*Last updated: 2025-08-06 11:15:00*
