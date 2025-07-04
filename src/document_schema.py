"""
Document schema validation for knowledge base documents.
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# Document schema definition
DOCUMENT_SCHEMA = {
    "required_fields": [
        "id", "title", "summary", "file_path", "file_name", 
        "directory", "last_modified", "priority", "tags", 
        "related", "source_type", "key_points"
    ],
    "field_types": {
        "id": str,
        "title": str,
        "summary": str,
        "file_path": str,
        "file_name": str,
        "directory": str,
        "last_modified": str,
        "priority": str,
        "tags": list,
        "related": list,
        "source_type": str,
        "key_points": list
    },
    "priority_values": ["high", "medium", "low"],
    "source_types": ["markdown", "code", "config", "documentation", "tutorial"],
}

class DocumentValidationError(Exception):
    """Exception raised when document validation fails."""
    pass

def validate_document_structure(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate document structure against schema.
    
    Args:
        document: Document to validate
        
    Returns:
        Validated and normalized document
        
    Raises:
        DocumentValidationError: If validation fails
    """
    errors = []
    
    # Check required fields
    for field in DOCUMENT_SCHEMA["required_fields"]:
        if field not in document:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    # Validate field types
    for field, expected_type in DOCUMENT_SCHEMA["field_types"].items():
        if field in document:
            if not isinstance(document[field], expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}, got {type(document[field]).__name__}")
    
    # Validate priority values
    if document.get("priority") not in DOCUMENT_SCHEMA["priority_values"]:
        errors.append(f"Priority must be one of {DOCUMENT_SCHEMA['priority_values']}, got '{document.get('priority')}'")
    
    # Validate source_type
    if document.get("source_type") not in DOCUMENT_SCHEMA["source_types"]:
        errors.append(f"Source type must be one of {DOCUMENT_SCHEMA['source_types']}, got '{document.get('source_type')}'")
    
    # Validate ID format (should be alphanumeric with hyphens)
    if document.get("id") and not re.match(r'^[a-zA-Z0-9-_]+$', document["id"]):
        errors.append("ID must contain only alphanumeric characters, hyphens, and underscores")
    
    # Validate timestamp format
    if document.get("last_modified"):
        try:
            datetime.fromisoformat(document["last_modified"].replace('Z', '+00:00'))
        except ValueError:
            errors.append("last_modified must be in ISO 8601 format (e.g., '2025-01-04T10:30:00Z')")
    
    # Validate file_path exists (relative to base directory)
    if document.get("file_path"):
        # Convert absolute path to relative if needed
        file_path = document["file_path"]
        if file_path.startswith("/"):
            # Make it relative to current working directory or base directory
            document["file_path"] = file_path
        
        # Extract file_name from file_path if not provided correctly
        path = Path(file_path)
        if document.get("file_name") != path.name:
            document["file_name"] = path.name
        
        # Extract directory from file_path if not provided correctly
        if document.get("directory") != str(path.parent):
            document["directory"] = str(path.parent)
    
    # Validate tags (must be non-empty strings)
    if document.get("tags"):
        for i, tag in enumerate(document["tags"]):
            if not isinstance(tag, str) or not tag.strip():
                errors.append(f"Tag at index {i} must be a non-empty string")
    
    # Validate related documents (must be strings)
    if document.get("related"):
        for i, related_id in enumerate(document["related"]):
            if not isinstance(related_id, str) or not related_id.strip():
                errors.append(f"Related document ID at index {i} must be a non-empty string")
    
    # Validate key_points (must be non-empty strings)
    if document.get("key_points"):
        for i, point in enumerate(document["key_points"]):
            if not isinstance(point, str) or not point.strip():
                errors.append(f"Key point at index {i} must be a non-empty string")
    
    if errors:
        raise DocumentValidationError("Validation failed: " + "; ".join(errors))
    
    return document

def generate_document_id(title: str, source_type: str = "markdown") -> str:
    """
    Generate a document ID from title.
    
    Args:
        title: Document title
        source_type: Type of source document
        
    Returns:
        Generated ID
    """
    # Convert title to lowercase, replace spaces with hyphens
    base_id = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    base_id = re.sub(r'\s+', '-', base_id.strip())
    
    # Add source type prefix
    type_prefix = {
        "markdown": "md",
        "code": "code", 
        "config": "cfg",
        "documentation": "doc",
        "tutorial": "tut"
    }.get(source_type, "doc")
    
    return f"{type_prefix}-{base_id}"

def create_document_template(
    title: str,
    file_path: str,
    priority: str = "medium",
    source_type: str = "markdown",
    tags: Optional[List[str]] = None,
    summary: str = "",
    key_points: Optional[List[str]] = None,
    related: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a document template with proper structure.
    
    Args:
        title: Document title
        file_path: Path to the source file
        priority: Priority level (high/medium/low)
        source_type: Type of source
        tags: List of tags
        summary: Brief description
        key_points: List of key points
        related: List of related document IDs
        
    Returns:
        Properly structured document
    """
    path = Path(file_path)
    
    document = {
        "id": generate_document_id(title, source_type),
        "title": title,
        "summary": summary or f"Brief description of {title}",
        "file_path": str(path),
        "file_name": path.name,
        "directory": str(path.parent),
        "last_modified": datetime.now().isoformat() + "Z",
        "priority": priority,
        "tags": tags or [],
        "related": related or [],
        "source_type": source_type,
        "key_points": key_points or []
    }
    
    return validate_document_structure(document)
