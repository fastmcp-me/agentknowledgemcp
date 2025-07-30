"""
Elasticsearch Search FastMCP Server
Search operations extracted from main elasticsearch server.
Handles advanced document search operations.
"""
import json
from typing import List, Dict, Any, Optional, Annotated
from datetime import datetime

from fastmcp import FastMCP, Context
from pydantic import Field

from ..elasticsearch_client import get_es_client
from ..elasticsearch_helper import (
    parse_time_parameters,
    analyze_search_results_for_reorganization
)
from ...config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Search",
    version="1.0.0",
    instructions="Elasticsearch search tools for advanced document queries"
)

# ================================
# CLI ENTRY POINT
# ================================

def cli_main():
    """CLI entry point for Elasticsearch Search FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Elasticsearch Search FastMCP server...")
    print("🔍 Tools: search")
    print("🎯 Purpose: Advanced document search operations")
    print("✅ Status: 1 Search tool completed - Ready for production!")

    app.run()

    app.run()

if __name__ == "__main__":
    cli_main()
