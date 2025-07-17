# MCP Server package
import asyncio
from . import main_server

__version__ = "1.0.28"

def main():
    """Main entry point for the package."""
    main_server.cli_main()

# Optionally expose other important items at package level
__all__ = ['main', 'main_server', '__version__']