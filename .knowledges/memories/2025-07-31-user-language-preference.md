# Memory: User Language Preference - Updated Rules

## Date
2025-07-31 (Updated)

## Context
User has clarified language preference rules during workflow management session. Previous understanding was incomplete.

## Details
**IMPORTANT DISTINCTION:**
- **Communication Language**: Vietnamese (Tiếng Việt) for all conversations, explanations, and user interactions
- **Code Language**: English for ALL code-related content (variable names, function names, comments, documentation strings, etc.)

**User's Exact Statement**: "ngôn ngữ yêu thích của tôi là tiếng việt thì đúng rồi, tuy nhiên trong code thì bạn phải dùng tiếng anh toàn bộ nha"

**Translation**: "My favorite language is Vietnamese, that's correct, however in code you must use English entirely"

## Impact
This creates a clear separation:

### Vietnamese Usage:
- All conversational responses
- Explanations and guidance  
- Error messages and feedback
- Documentation creation
- Workflow instructions
- User interaction

### English Usage (MANDATORY):
- Variable names
- Function names
- Class names
- Code comments
- Docstrings
- API endpoints
- Configuration keys
- Technical documentation within code
- File names (when code-related)
- Database schema
- Log messages

## Key Takeaways
- User wants Vietnamese for human communication
- User requires English for ALL code-related content
- This is a strict rule with no exceptions for code
- Separation between human communication and technical implementation
- Professional coding standards require English

## Related
- Smart prompting assistant development
- Template refactoring session  
- AgentKnowledgeMCP feature development
- Release process workflow management
- Code vs Communication language distinction

## Follow-up Actions
- [x] Use Vietnamese in all future responses to this user
- [x] Use English for ALL code-related content (mandatory)
- [ ] Consider adding language preference support to AgentKnowledgeMCP features
- [ ] Document this as a user experience best practice
- [ ] Ensure all team members understand code-English requirement

## Examples

### ✅ Correct Usage:
```python
# English code with Vietnamese explanation
def generate_smart_doc_id(title: str, content: str) -> str:
    """Generate smart document ID with collision detection."""
    # Implementation in English
    pass
```

**Vietnamese Explanation**: "Hàm này tạo ID thông minh cho document với tính năng tránh trùng lặp"

### ❌ Incorrect Usage:
```python
# Vietnamese in code - NOT ALLOWED
def tao_id_thong_minh(tieu_de: str, noi_dung: str) -> str:
    """Tạo ID thông minh cho tài liệu"""
    pass
```

---
*Recorded: 2025-07-31 18:30:00 (Updated: 19:15:00)*
