"""
Elasticsearch Helper Functions
Utility functions for AI-enhanced metadata generation and content processing.
"""

import json
from typing import Dict, Any
from fastmcp import Context


async def generate_smart_metadata(title: str, content: str, ctx: Context) -> Dict[str, Any]:
    """Generate intelligent tags, key_points, smart_summary and enhanced_content using LLM sampling."""
    try:
        # Create prompt for generating metadata and smart content
        prompt = f"""Analyze the following document and provide comprehensive smart metadata and content:

Title: {title}

Content: {content[:2000]}{"..." if len(content) > 2000 else ""}

Please provide:
1. Relevant tags (3-8 tags, lowercase, hyphen-separated)
2. Key points (3-6 important points from the content)
3. Smart summary (2-3 sentences capturing the essence)
4. Enhanced content (improved/structured version if content is brief or unclear)

Respond in JSON format:
{{
  "tags": ["tag1", "tag2", "tag3"],
  "key_points": ["Point 1", "Point 2", "Point 3"],
  "smart_summary": "Brief 2-3 sentence summary of the document",
  "enhanced_content": "Improved/structured content if original is brief, otherwise keep original"
}}

Focus on:
- Technical concepts and technologies mentioned
- Main topics and themes
- Document type and purpose
- Key features or functionalities discussed
- Clear, professional language for summary and content
- Maintain accuracy while improving clarity"""

        # Request LLM analysis with controlled parameters and model preferences
        response = await ctx.sample(
            messages=prompt,
            system_prompt="You are an expert document analyzer and content enhancer. Generate accurate, relevant metadata and improve content quality while maintaining original meaning. Always respond with valid JSON.",
            model_preferences=["claude-3-opus", "claude-3-sonnet", "gpt-4"],  # Prefer reasoning models for analysis
            temperature=0.3,  # Low randomness for consistency
            max_tokens=600   # Increased for smart content generation
        )
        
        # Parse the JSON response
        try:
            metadata = json.loads(response.text.strip())
            
            # Validate and clean the response
            tags = metadata.get("tags", [])
            key_points = metadata.get("key_points", [])
            smart_summary = metadata.get("smart_summary", "")
            enhanced_content = metadata.get("enhanced_content", "")
            
            # Ensure we have reasonable limits and clean data
            tags = [tag.lower().strip() for tag in tags[:8] if tag and isinstance(tag, str)]
            key_points = [point.strip() for point in key_points[:6] if point and isinstance(point, str)]
            
            # Clean and validate smart content
            smart_summary = smart_summary.strip() if isinstance(smart_summary, str) else ""
            enhanced_content = enhanced_content.strip() if isinstance(enhanced_content, str) else ""
            
            return {
                "tags": tags,
                "key_points": key_points,
                "smart_summary": smart_summary,
                "enhanced_content": enhanced_content
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            await ctx.warning("LLM response was not valid JSON, using fallback metadata generation")
            return generate_fallback_metadata(title, content)
            
    except Exception as e:
        # Fallback for any sampling errors
        await ctx.warning(f"LLM sampling failed ({str(e)}), using fallback metadata generation")
        return generate_fallback_metadata(title, content)


def generate_fallback_metadata(title: str, content: str) -> Dict[str, Any]:
    """Generate basic metadata when LLM sampling is not available."""
    # Basic tags based on title and content analysis
    title_lower = title.lower()
    content_lower = content.lower()[:1000]  # First 1000 chars for analysis
    
    tags = ["document"]
    
    # Add file type tags
    if any(word in title_lower for word in ["readme", "documentation", "docs"]):
        tags.append("documentation")
    if any(word in title_lower for word in ["config", "configuration", "settings"]):
        tags.append("configuration")
    if any(word in title_lower for word in ["test", "testing", "spec"]):
        tags.append("testing")
    if any(word in content_lower for word in ["python", "def ", "class ", "import "]):
        tags.append("python")
    if any(word in content_lower for word in ["javascript", "function", "const ", "let "]):
        tags.append("javascript")
    if any(word in content_lower for word in ["api", "endpoint", "request", "response"]):
        tags.append("api")
    
    # Basic key points
    key_points = [
        f"Document title: {title}",
        f"Content length: {len(content)} characters"
    ]
    
    # Add content-based points
    if "implementation" in content_lower:
        key_points.append("Contains implementation details")
    if "example" in content_lower or "demo" in content_lower:
        key_points.append("Includes examples or demonstrations")
    if "error" in content_lower or "exception" in content_lower:
        key_points.append("Discusses error handling")
    
    return {
        "tags": tags[:6],  # Limit to 6 tags
        "key_points": key_points[:4],  # Limit to 4 points
        "smart_summary": f"Fallback document: {title}",
        "enhanced_content": content[:500] + "..." if len(content) > 500 else content
    }
