# Agent Knowledge MCP - AI Assistant Instructions

## ⚠️ HARD REQUIREMENT - NOT OPTIONAL

**YOU MUST ALWAYS CHECK KNOWLEDGE BASE FIRST - NO EXCEPTIONS**

This is a **HARD RULE**, not a suggestion. Violation = Failed Task.

## 📋 MANDATORY CHECKLIST - NEVER SKIP

Before ANY action, you MUST verbally confirm:

```
- [ ] "Let me check the knowledge base for: [specific query]"
- [ ] "Searching for: [keywords/concepts/files]"  
- [ ] "Found: [detailed summary of results]"
- [ ] "Based on knowledge base findings: [how it influences approach]"
- [ ] "Proceeding with: [specific action plan]"
```

## 🔄 REQUIRED WORKFLOW - NO SHORTCUTS

**Step 1: ALWAYS start with "Let me check the knowledge base first..."**
**Step 2: Use these MCP tools to search:**
   ```
   - Search for existing information: `search` command
   - Check project documents: `get_document` for specific files
   - Review configuration: `get_config` for current settings
   - Find related content: search by keywords, concepts, topics
   ```

**Step 3: Report findings in detail:**
   - ✅ What you searched for
   - ✅ What you found (or didn't find)  
   - ✅ How findings influence your approach
   - ✅ Any conflicts or dependencies discovered

**Step 4: Only then proceed with task**

## 🧠 SELF-MONITORING PROTOCOL

**If you catch yourself about to act without checking knowledge base:**
- STOP immediately
- Say "Wait, I need to check knowledge base first"
- Execute the mandatory checklist above
- This happens to everyone - the key is catching yourself

## � Knowledge Base Usage Protocol

**When asked to help with anything:**

1. **Start with Search:**
   ```
   "Let me check the knowledge base for relevant information about [topic]..."
   ```

2. **Document Your Process:**
   - What you searched for
   - What you found (or didn't find)
   - How it influences your approach

3. **Smart Knowledge Management:**
   - Index new information with appropriate status: `predicted`, `confirmed`, `draft`
   - Update status of existing information rather than content: `outdated`, `superseded`, `verified`
   - Track information lifecycle with timestamps and confidence levels
   - Link related information through references, not duplication
   - Document lessons learned with clear status indicators

## 🔍 Effective Search Strategies

**Search Queries to Try:**
- Function/feature names you're working with
- Error messages or issues encountered
- Related concepts and keywords
- File paths and module names
- Configuration settings and requirements

**Multiple Search Approaches:**
- Broad searches first, then narrow down
- Try synonyms and related terms
- Search by different aspects (technical, functional, historical)
- Look for patterns and connections

## 📚 Knowledge Management Best Practices

**When Working with Information:**
- Always verify against knowledge base first
- Document new discoveries immediately
- Create structured, searchable content
- Link related concepts together
- Update outdated information

**Document Everything:**
- Decisions made and reasoning behind them
- Solutions that worked (and didn't work)
- Patterns discovered during work
- Configuration changes and their effects

## � Learning from Mistakes

**Important Reminder:**
- Never assume without checking knowledge base
- Previous work may contain valuable insights
- Mistakes are learning opportunities to document
- Knowledge base is the source of truth, not assumptions

**Example of Good Practice:**
```
Before implementing X, let me search for:
- Existing implementations of X
- Related functionality 
- Known issues with X
- Configuration requirements for X
```

**Remember: The knowledge base contains valuable context about decisions, patterns, and gotchas. Always consult it first to avoid repeating mistakes and build on existing knowledge!**
