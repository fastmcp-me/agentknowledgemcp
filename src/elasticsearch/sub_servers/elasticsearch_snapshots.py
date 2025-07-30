"""
Elasticsearch Snapshots FastMCP Server
Snapshot operations extracted from main elasticsearch server.
Handles backup and restore operations.
"""

from typing import Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-Snapshots",
    version="1.0.0",
    instructions="Elasticsearch snapshot operations tools"
)

@app.tool(
    description="Create a snapshot (backup) of Elasticsearch indices with comprehensive options and repository management",
    tags={"elasticsearch", "snapshot", "backup", "repository"}
)
async def create_snapshot(
        snapshot_name: Annotated[str, Field(description="Name for the snapshot (must be unique)")],
        repository: Annotated[str, Field(description="Repository name to store the snapshot")] = "backup_repository",
        indices: Annotated[Optional[str], Field(description="Comma-separated list of indices to backup (default: all indices)")] = None,
        ignore_unavailable: Annotated[bool, Field(description="Whether to ignore unavailable indices")] = True,
        include_global_state: Annotated[bool, Field(description="Whether to include cluster global state")] = True,
        wait_for_completion: Annotated[bool, Field(description="Whether to wait for snapshot completion")] = True,
        description: Annotated[Optional[str], Field(description="Optional description for the snapshot")] = None
) -> str:
    """Create a snapshot (backup) of Elasticsearch indices."""
    return await create_snapshot_operation(
        snapshot_name=snapshot_name,
        repository=repository,
        indices=indices,
        ignore_unavailable=ignore_unavailable,
        include_global_state=include_global_state,
        wait_for_completion=wait_for_completion,
        description=description
    )


# ================================
# TOOL 15: RESTORE_SNAPSHOT
# ================================

@app.tool(
    description="Restore indices from an Elasticsearch snapshot with comprehensive options and conflict resolution",
    tags={"elasticsearch", "snapshot", "restore", "rollback"}
)
async def restore_snapshot(
        snapshot_name: Annotated[str, Field(description="Name of the snapshot to restore from")],
        repository: Annotated[str, Field(description="Repository containing the snapshot")] = "backup_repository",
        indices: Annotated[Optional[str], Field(description="Comma-separated list of indices to restore (default: all from snapshot)")] = None,
        ignore_unavailable: Annotated[bool, Field(description="Whether to ignore unavailable indices")] = True,
        include_global_state: Annotated[bool, Field(description="Whether to restore cluster global state")] = False,
        wait_for_completion: Annotated[bool, Field(description="Whether to wait for restore completion")] = True,
        rename_pattern: Annotated[Optional[str], Field(description="Pattern to rename restored indices (e.g., 'restored_%s')")] = None,
        index_settings: Annotated[Optional[str], Field(description="JSON string of index settings to override")] = None
) -> str:
    """Restore indices from an Elasticsearch snapshot."""
    return await restore_snapshot_operation(
        snapshot_name=snapshot_name,
        repository=repository,
        indices=indices,
        ignore_unavailable=ignore_unavailable,
        include_global_state=include_global_state,
        wait_for_completion=wait_for_completion,
        rename_pattern=rename_pattern,
        index_settings=index_settings
    )

# ================================
# TOOL 16: LIST_SNAPSHOTS
# ================================

@app.tool(
    description="List all snapshots in an Elasticsearch repository with detailed information and status",
    tags={"elasticsearch", "snapshot", "list", "repository"}
)
async def list_snapshots(
        repository: Annotated[str, Field(description="Repository name to list snapshots from")] = "backup_repository",
        verbose: Annotated[bool, Field(description="Whether to show detailed information for each snapshot")] = True
) -> str:
    """List all snapshots in an Elasticsearch repository."""
    return await list_snapshots_operation(
        repository=repository,
        verbose=verbose
    )

# CLI Entry Point
def main():
    """Main entry point for elasticsearch snapshots server."""
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--version":
            print("elasticsearch-snapshots 1.0.0")
            return
        elif sys.argv[1] == "--help":
            print("Elasticsearch Snapshots Server - FastMCP Implementation")
            print("Handles snapshot operations.")
            print("\nTools provided:")
            print("  - [TO BE COPIED FROM BAK FILE]")
            return

    print("🚀 Starting Elasticsearch Snapshots Server...")
    print("🔍 Tools: [TO BE COPIED FROM BAK FILE]")
    app.run()

if __name__ == "__main__":
    main()
