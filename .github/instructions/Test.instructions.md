# Agent Knowledge MCP - AI Assistant Instructions

## 🚨 **MANDATORY 5-PHASE WORKFLOW - MUST FOLLOW - NO EXCEPTIONS**

**THIS IS THE REQUIRED EXECUTION PROCESS FOR ALL TASKS - VIOLATION = FAILED TASK**

### **📊 PHASE 1: RESEARCH**
**RULE 1**: Always start with "Let me check the knowledge base first..."

**Required Actions:**
```
1. ✅ Search knowledge base with `search` command for relevant information
2. ✅ If not found → search other available indices 
3. ✅ Check `get_config` for current settings if needed
4. ✅ Report findings: "Found: [detailed summary]" or "Not found: [what was searched]"
```

**Goal**: Understand task context and gather existing knowledge

---

### **🎯 PHASE 2: PLANNING**
**RULE 2**: After research completed, analyze and get project guidance

**Required Actions:**
```
1. ✅ Analyze what needs to be done based on research findings
2. ✅ MANDATORY: Call `ask_mcp_advance` with intended action and task description
3. ✅ Use returned guidance to inform approach
4. ✅ ONLY call ask_mcp_advance ONCE - do not call again for same task
```

**Goal**: Get project-specific guidance before implementation

---

### **⚡ PHASE 3: EXECUTION**
**RULE 3**: Implement with guidance, ask for help when uncertain

**Required Actions:**
```
1. ✅ Execute task following guidance from Phase 2
2. ✅ If uncertain or stuck → MANDATORY: Call `ask_user_advice` tool
3. ✅ Continue until task is completed successfully
```

**Goal**: Complete task effectively with available guidance

---

### **📚 PHASE 4: DOCUMENTATION**
**RULE 4**: After task completion, preserve knowledge

**Required Actions:**
```
1. ✅ Create knowledge base document for task/solution/discovery
2. ✅ Include: problem, solution steps, lessons learned, user feedback
3. ✅ Index document with appropriate tags for searchability
4. ✅ Verify indexing by searching for the new content
```

**Goal**: Preserve knowledge for future tasks

---

### **🔄 PHASE 5: CONTINUATION**
**RULE 5**: Get direction for next steps

**Required Actions:**
```
1. ✅ MANDATORY: Call `ask_user_advice` tool to get direction for next steps
2. ✅ Wait for user guidance before proceeding with new tasks
```

**Goal**: Ensure proper workflow continuation