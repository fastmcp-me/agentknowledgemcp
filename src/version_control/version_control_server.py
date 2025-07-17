"""
Version Control Operations FastMCP Server - Step by step migration
Tool-by-tool conversion from handlers to FastMCP tools.
File 4/4: Version Control Server
"""
from pathlib import Path
from typing import List, Optional, Annotated
import subprocess
import json

from fastmcp import FastMCP
from pydantic import Field

from src.config.config import load_config

# Create FastMCP app
app = FastMCP(
    name="AgentKnowledgeMCP-VersionControl",
    version="1.0.0",
    instructions="Version control operations tools for Git and SVN repository management"
)

def _format_vcs_error(e: Exception, operation: str, context: str = None) -> str:
    """Format version control operation errors with detailed guidance for agents."""
    error_message = f"❌ Failed to {operation}:\n\n"

    error_str = str(e).lower()
    if "permission denied" in error_str or "access denied" in error_str:
        error_message += f"🚨 **Permission Error**\n"
        error_message += f"   • Check file system permissions for repository directory\n"
        error_message += f"   • Ensure user has write access to target directory\n"
        error_message += f"   • Try running with elevated permissions if necessary\n"
        error_message += f"   • Verify directory ownership and access rights\n\n"
    elif "file not found" in error_str or "no such file" in error_str:
        error_message += f"🚨 **File Not Found**\n"
        error_message += f"   • Check that all required files exist\n"
        error_message += f"   • Verify correct file paths and working directory\n"
        error_message += f"   • Ensure repository is properly initialized\n"
        error_message += f"   • Check spelling and case sensitivity\n\n"
    elif "not a git repository" in error_str or "not a working copy" in error_str:
        error_message += f"🚨 **Repository Not Initialized**\n"
        error_message += f"   • Run setup_version_control to initialize repository\n"
        error_message += f"   • Verify you're in the correct directory\n"
        error_message += f"   • Check repository type (Git vs SVN) matches configuration\n"
        error_message += f"   • Try force=true to reinitialize if needed\n\n"
    elif "already exists" in error_str or "already a repository" in error_str:
        error_message += f"🚨 **Repository Already Exists**\n"
        error_message += f"   • Repository is already initialized in this directory\n"
        error_message += f"   • Use force=true to reinitialize if needed\n"
        error_message += f"   • Check if you want to work with existing repository\n"
        error_message += f"   • Verify repository type matches your needs\n\n"
    else:
        error_message += f"🚨 **Version Control Error**\n"
        error_message += f"   • Check version control system is properly installed\n"
        error_message += f"   • Verify network connectivity for remote operations\n"
        error_message += f"   • Ensure sufficient disk space for repository operations\n"
        error_message += f"   • Check system performance and memory availability\n\n"

    if context:
        error_message += f"🔍 **Operation Context**: {context}\n"

    error_message += f"🔍 **Technical Details**: {str(e)}"

    return error_message


def get_vcs_type() -> Optional[str]:
    """Get version control type from config."""
    config = load_config()
    vc_config = config.get("version_control", {})
    if not vc_config.get("enabled", False):
        return None
    return vc_config.get("type", "git")


def get_base_directory() -> Path:
    """Get base directory from config."""
    config = load_config()
    base_directory = config.get("security", {}).get("allowed_base_directory", ".")
    return Path(base_directory).resolve()


def run_command(cmd: List[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run command in specified directory."""
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=True
    )


# ================================
# TOOL 1: SETUP_VERSION_CONTROL
# ================================

@app.tool(
    description="Setup version control (Git or SVN) in knowledge base directory with comprehensive repository initialization",
    tags={"version-control", "setup", "git", "svn", "repository", "initialization"}
)
async def setup_version_control(
    vcs_type: Annotated[Optional[str], Field(description="Version control system to use (git or svn). If not provided, uses config default or 'git'", enum=["git", "svn"])] = None,
    force: Annotated[bool, Field(description="Force setup even if VCS already exists")] = False,
    initial_commit: Annotated[bool, Field(description="Create initial commit with existing files")] = True
) -> str:
    """Setup version control system with comprehensive repository initialization and configuration."""
    try:
        base_path = get_base_directory()
        selected_vcs_type = vcs_type or get_vcs_type() or "git"

        # Check if VCS is installed
        try:
            run_command([selected_vcs_type, "--version"], base_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            install_commands = {
                "git": "git (usually pre-installed on macOS/Linux, or use: brew install git)",
                "svn": "SVN (install with: brew install subversion on macOS, apt install subversion on Ubuntu)"
            }
            return f"❌ **{selected_vcs_type.upper()} Not Installed!**\n\n🚨 **Error:** {selected_vcs_type.upper()} is not installed or not available in PATH\n\n🛠️ **Installation Instructions:**\n   • {install_commands.get(selected_vcs_type, f'Install {selected_vcs_type}')}\n   • Restart terminal after installation\n   • Verify installation: `{selected_vcs_type} --version`\n   • Try setup again after installation\n\n💡 **Alternative:** Choose different VCS type if preferred (git or svn)"

        # Check if VCS already exists
        vcs_dir = base_path / f".{selected_vcs_type}"
        if vcs_dir.exists() and not force:
            return f"⚠️ **{selected_vcs_type.upper()} Repository Already Exists!**\n\n📁 **Location:** {base_path}\n🗂️ **Repository Directory:** {vcs_dir}\n\n💡 **Options:**\n   • Use existing repository (no action needed)\n   • Set `force=True` to reinitialize (⚠️ will remove existing history)\n   • Switch to different directory if needed\n   • Check repository status with version control commands\n\n✅ **Current Status:** Repository is ready for use!"

        # Initialize setup message
        setup_message = f"🚀 **Setting up {selected_vcs_type.upper()} Repository**\n\n📁 **Target Directory:** {base_path}\n⚙️ **Configuration:** force={force}, initial_commit={initial_commit}\n\n"

        # Setup VCS based on type
        if selected_vcs_type == "git":
            setup_result = await _setup_git(base_path, force, initial_commit)
        elif selected_vcs_type == "svn":
            setup_result = await _setup_svn(base_path, force, initial_commit)
        else:
            return f"❌ **Unsupported VCS Type!**\n\n🚨 **Error:** '{selected_vcs_type}' is not supported\n\n✅ **Supported Types:**\n   • `git` - Git distributed version control\n   • `svn` - Subversion centralized version control\n\n💡 **Recommendation:** Use 'git' for most modern workflows"

        setup_message += setup_result

        # Update configuration
        try:
            config = load_config()
            config.setdefault("version_control", {})
            config["version_control"]["enabled"] = True
            config["version_control"]["type"] = selected_vcs_type

            # Save configuration
            config_path = Path(__file__).parent / "config.json"
            with open(config_path, "w", encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            setup_message += f"\n🔧 **Configuration Updated:**\n   ✅ Version control enabled: {selected_vcs_type.upper()}\n   📄 Config file: {config_path.name}\n"
        except Exception as e:
            setup_message += f"\n⚠️ **Configuration Update Warning:**\n   🚨 Could not update config.json: {str(e)}\n   💡 You may need to manually enable version control in configuration\n"

        # Final success message
        setup_message += f"\n🎉 **{selected_vcs_type.upper()} Setup Completed Successfully!**\n\n"
        setup_message += f"✅ **Repository Status:** Initialized and ready for use\n"
        setup_message += f"📚 **Next Steps:**\n"
        setup_message += f"   • Start tracking files with commit_file tool\n"
        setup_message += f"   • View previous versions with get_previous_file_version tool\n"
        setup_message += f"   • Use standard {selected_vcs_type} commands for advanced operations\n"
        setup_message += f"   • Check repository status: `{selected_vcs_type} status`\n\n"
        setup_message += f"🔗 **Integration:** Version control is now active in AgentKnowledgeMCP configuration"

        return setup_message

    except subprocess.CalledProcessError as e:
        return _format_vcs_error(e, "setup version control", f"{selected_vcs_type} repository initialization")
    except PermissionError as e:
        return f"❌ **Permission Error!**\n\n🚨 **Error:** Insufficient permissions for repository setup\n🔍 **Details:** {str(e)}\n\n🛠️ **Resolution:**\n   • Check directory permissions for {base_path}\n   • Ensure user has write access to target directory\n   • Try running with elevated permissions if necessary\n   • Verify directory ownership and access rights"
    except FileNotFoundError as e:
        return f"❌ **Directory Error!**\n\n🚨 **Error:** Target directory not found\n🔍 **Details:** {str(e)}\n\n🛠️ **Resolution:**\n   • Verify base directory exists: {base_path}\n   • Check allowed_base_directory in configuration\n   • Create directory if needed: `mkdir -p {base_path}`\n   • Ensure correct path configuration"
    except Exception as e:
        return _format_vcs_error(e, "setup version control", f"repository initialization with {selected_vcs_type}")


async def _setup_git(base_path: Path, force: bool, initial_commit: bool) -> str:
    """Setup Git repository with comprehensive configuration."""
    setup_message = ""

    # Remove existing .git if force
    git_dir = base_path / ".git"
    if git_dir.exists() and force:
        try:
            import shutil
            shutil.rmtree(git_dir)
            setup_message += "🗑️ **Cleanup:** Removed existing Git repository\n"
        except Exception as e:
            setup_message += f"⚠️ **Cleanup Warning:** Could not remove existing .git: {str(e)}\n"

    # Initialize Git repository
    run_command(["git", "init"], base_path)
    setup_message += "✅ **Repository:** Git repository initialized\n"

    # Set user configuration if not set globally
    try:
        result = run_command(["git", "config", "user.name"], base_path)
        if not result.stdout.strip():
            raise subprocess.CalledProcessError(1, ["git", "config", "user.name"])
    except subprocess.CalledProcessError:
        run_command(["git", "config", "user.name", "Knowledge Base User"], base_path)
        run_command(["git", "config", "user.email", "knowledge@base.local"], base_path)
        setup_message += "✅ **User Config:** Git user configuration set\n"

    # Create comprehensive .gitignore
    gitignore_path = base_path / ".gitignore"
    gitignore_content = """# Temporary files
*.tmp
*.temp
*.swp
*.swo
*~
.#*

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Editor files
.vscode/
.idea/
*.sublime-*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Logs
*.log
logs/

# Cache and temp directories
.cache/
.pytest_cache/
.coverage
"""
    try:
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        setup_message += "✅ **GitIgnore:** Comprehensive .gitignore created\n"
    except Exception as e:
        setup_message += f"⚠️ **GitIgnore Warning:** Could not create .gitignore: {str(e)}\n"

    if initial_commit:
        try:
            # Add all files
            run_command(["git", "add", "."], base_path)

            # Create initial commit
            run_command(["git", "commit", "-m", "Initial commit - AgentKnowledgeMCP knowledge base setup"], base_path)
            setup_message += "✅ **Initial Commit:** All files committed to repository\n"

            # Check final status
            result = run_command(["git", "status", "--porcelain"], base_path)
            if result.stdout.strip():
                untracked_count = len(result.stdout.strip().split('\n'))
                setup_message += f"📝 **Status:** {untracked_count} untracked files remain (may be new since commit)\n"
            else:
                setup_message += "📝 **Status:** Working directory is clean\n"
        except subprocess.CalledProcessError as e:
            setup_message += f"⚠️ **Commit Warning:** Initial commit failed: {str(e)}\n"
            setup_message += "💡 **Note:** Repository is initialized but no initial commit created\n"

    return setup_message


async def _setup_svn(base_path: Path, force: bool, initial_commit: bool) -> str:
    """Setup SVN repository with comprehensive configuration."""
    setup_message = ""

    # Create repository directory
    repo_path = base_path.parent / ".svn_repo"
    if repo_path.exists() and force:
        try:
            import shutil
            shutil.rmtree(repo_path)
            setup_message += "🗑️ **Cleanup:** Removed existing SVN repository\n"
        except Exception as e:
            setup_message += f"⚠️ **Cleanup Warning:** Could not remove existing repository: {str(e)}\n"

    if not repo_path.exists():
        run_command(["svnadmin", "create", str(repo_path)], base_path)
        setup_message += f"✅ **Repository:** SVN repository created at {repo_path.name}\n"

    # Remove existing .svn if force
    svn_dir = base_path / ".svn"
    if svn_dir.exists() and force:
        try:
            import shutil
            shutil.rmtree(svn_dir)
            setup_message += "🗑️ **Cleanup:** Removed existing SVN working copy\n"
        except Exception as e:
            setup_message += f"⚠️ **Cleanup Warning:** Could not remove .svn: {str(e)}\n"

    # Checkout working copy
    repo_url = f"file://{repo_path}"
    run_command(["svn", "checkout", repo_url, ".", "--force"], base_path)
    setup_message += f"✅ **Working Copy:** Checked out from {repo_url}\n"

    if initial_commit:
        try:
            # Add all files except hidden directories
            files_to_add = []
            for item in base_path.iterdir():
                if not item.name.startswith('.') and item.is_file():
                    files_to_add.append(item.name)

            if files_to_add:
                run_command(["svn", "add"] + files_to_add, base_path)
                run_command(["svn", "commit", "-m", "Initial commit - AgentKnowledgeMCP knowledge base setup"], base_path)
                setup_message += f"✅ **Initial Commit:** Added and committed {len(files_to_add)} files\n"
            else:
                setup_message += "📝 **Status:** No files found for initial commit\n"
        except subprocess.CalledProcessError as e:
            setup_message += f"⚠️ **Commit Warning:** Initial commit failed: {str(e)}\n"
            setup_message += "💡 **Note:** Working copy is initialized but no initial commit created\n"

    return setup_message


# ================================
# TOOL 2: COMMIT_FILE
# ================================

@app.tool(
    description="Commit file changes to version control (Git or SVN) with automatic staging and comprehensive tracking",
    tags={"version-control", "commit", "git", "svn", "file-tracking", "staging"}
)
async def commit_file(
    file_path: Annotated[str, Field(description="Path to file to commit (relative to knowledge base)")],
    message: Annotated[str, Field(description="Commit message")],
    add_if_new: Annotated[bool, Field(description="Add file to VCS if it's not tracked yet")] = True
) -> str:
    """Commit file changes to version control with comprehensive staging and tracking."""
    try:
        base_path = get_base_directory()
        vcs_type = get_vcs_type()

        if not vcs_type:
            return "❌ **Version Control Not Enabled!**\n\n🚨 **Error:** Version control is not enabled in configuration\n\n🛠️ **Resolution Steps:**\n   1. Run `setup_version_control` tool to initialize repository\n   2. Choose VCS type (git or svn) during setup\n   3. Enable version control in AgentKnowledgeMCP configuration\n   4. Try commit operation again after setup\n\n💡 **Alternative:** Check configuration with admin tools if VCS should already be enabled"

        if not file_path or not message:
            return "❌ **Missing Required Parameters!**\n\n🚨 **Error:** Both file_path and message are required\n\n📝 **Required Parameters:**\n   • `file_path`: Path to file to commit (relative to knowledge base)\n   • `message`: Descriptive commit message\n\n💡 **Example Usage:**\n   ```\n   commit_file(\n       file_path=\"docs/readme.md\",\n       message=\"Update documentation with new features\"\n   )\n   ```"

        # Check if file exists
        full_file_path = base_path / file_path
        if not full_file_path.exists():
            return f"❌ **File Not Found!**\n\n🚨 **Error:** File does not exist: `{file_path}`\n📁 **Full Path:** {full_file_path}\n\n🛠️ **Resolution:**\n   • Verify file path is correct and relative to knowledge base\n   • Check file exists: `{file_path}`\n   • Ensure file hasn't been deleted or moved\n   • Use correct relative path from knowledge base root\n\n💡 **Base Directory:** {base_path}"

        # Route to appropriate VCS handler
        if vcs_type == "git":
            return await _commit_file_git(base_path, file_path, message, add_if_new)
        elif vcs_type == "svn":
            return await _commit_file_svn(base_path, file_path, message, add_if_new)
        else:
            return f"❌ **Unsupported VCS Type!**\n\n🚨 **Error:** '{vcs_type}' is not supported for commit operations\n\n✅ **Supported Types:**\n   • `git` - Git distributed version control\n   • `svn` - Subversion centralized version control\n\n🛠️ **Resolution:**\n   • Check version control configuration\n   • Run `setup_version_control` with supported VCS type\n   • Verify config.json has correct VCS type setting"

    except subprocess.CalledProcessError as e:
        return _format_vcs_error(e, "commit file", f"file tracking and commit for {file_path}")
    except PermissionError as e:
        return f"❌ **Permission Error!**\n\n🚨 **Error:** Insufficient permissions for commit operation\n🔍 **Details:** {str(e)}\n\n🛠️ **Resolution:**\n   • Check file system permissions for {file_path}\n   • Ensure user has write access to repository\n   • Verify repository directory permissions\n   • Try running with elevated permissions if necessary"
    except Exception as e:
        return _format_vcs_error(e, "commit file", f"version control commit operation for {file_path}")


async def _commit_file_git(base_path: Path, file_path: str, message: str, add_if_new: bool) -> str:
    """Commit file using Git with comprehensive staging and status tracking."""
    commit_summary = ""

    try:
        # Check file status with Git
        result = run_command(["git", "status", "--porcelain", file_path], base_path)
        status = result.stdout.strip()

        if not status and not add_if_new:
            # File is already tracked and has no changes
            return f"ℹ️ **No Changes to Commit**\n\n📝 **File:** `{file_path}`\n🔍 **Status:** File is already tracked and up to date\n\n💡 **Note:** No commit created as there are no changes to stage\n\n✅ **Repository Status:** Working directory is clean for this file"

        # Handle different file statuses
        if status.startswith("??"):
            # Untracked file
            if add_if_new:
                run_command(["git", "add", file_path], base_path)
                commit_summary += f"📁 **File Staged:** Added untracked file `{file_path}` to Git\n"
            else:
                return f"⚠️ **Untracked File!**\n\n📝 **File:** `{file_path}`\n🔍 **Status:** File is not tracked by Git\n\n💡 **Options:**\n   • Set `add_if_new=True` to add and commit the file\n   • Manually add file: `git add {file_path}`\n   • Use Git commands to stage file before committing\n\n🛠️ **Next Steps:** Enable add_if_new or manually stage the file"
        elif status.startswith(("M", "A", "D", "R", "C")):
            # Modified, Added, Deleted, Renamed, or Copied file
            run_command(["git", "add", file_path], base_path)
            status_names = {
                "M": "Modified",
                "A": "Added",
                "D": "Deleted",
                "R": "Renamed",
                "C": "Copied"
            }
            status_name = status_names.get(status[0], "Changed")
            commit_summary += f"📝 **File Staged:** {status_name} file `{file_path}` staged for commit\n"
        elif not status:
            # File is tracked but unchanged - still allow commit for explicit intent
            commit_summary += f"📄 **File Status:** `{file_path}` is tracked and current\n"

        # Create commit
        try:
            run_command(["git", "commit", "-m", message, file_path], base_path)
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in str(e).lower():
                return f"ℹ️ **Nothing to Commit**\n\n📝 **File:** `{file_path}`\n💬 **Message:** {message}\n\n🔍 **Status:** No changes detected for commit\n\n✅ **Repository:** File is already up to date in version control"
            else:
                raise e

        # Get commit information
        try:
            result = run_command(["git", "rev-parse", "HEAD"], base_path)
            commit_hash = result.stdout.strip()[:8]

            # Get commit details
            result = run_command(["git", "show", "--no-patch", "--format=%an %ad", commit_hash], base_path)
            commit_info = result.stdout.strip()

            # Build success message
            success_message = f"🎉 **File Committed Successfully!**\n\n"
            success_message += commit_summary
            success_message += f"📝 **Commit Details:**\n"
            success_message += f"   📄 File: `{file_path}`\n"
            success_message += f"   💬 Message: \"{message}\"\n"
            success_message += f"   🔖 Commit: {commit_hash}\n"
            success_message += f"   👤 Author: {commit_info}\n\n"
            success_message += f"✅ **Repository Status:** Changes successfully committed to Git history\n"
            success_message += f"🔗 **Integration:** File changes are now tracked in version control"

            return success_message

        except subprocess.CalledProcessError:
            # Fallback if we can't get commit details
            success_message = f"🎉 **File Committed Successfully!**\n\n"
            success_message += commit_summary
            success_message += f"📝 **Commit Details:**\n"
            success_message += f"   📄 File: `{file_path}`\n"
            success_message += f"   💬 Message: \"{message}\"\n\n"
            success_message += f"✅ **Repository Status:** Changes successfully committed to Git"

            return success_message

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        return f"❌ **Git Commit Failed!**\n\n🚨 **Error:** Git operation failed\n🔍 **Details:** {error_output}\n\n🛠️ **Troubleshooting:**\n   • Check if repository is properly initialized\n   • Verify file exists and is accessible\n   • Ensure commit message is properly formatted\n   • Check Git configuration and user settings\n   • Try manual Git commands to diagnose issue\n\n💡 **Git Status:** Run `git status` to check repository state"


async def _commit_file_svn(base_path: Path, file_path: str, message: str, add_if_new: bool) -> str:
    """Commit file using SVN with comprehensive staging and status tracking."""
    commit_summary = ""

    try:
        # Check file status with SVN
        result = run_command(["svn", "status", file_path], base_path)
        status = result.stdout.strip()

        if not status and not add_if_new:
            # File is already tracked and has no changes
            return f"ℹ️ **No Changes to Commit**\n\n📝 **File:** `{file_path}`\n🔍 **Status:** File is already tracked and up to date\n\n💡 **Note:** No commit created as there are no changes to stage\n\n✅ **Repository Status:** Working copy is clean for this file"

        # Handle different file statuses
        if status.startswith("?"):
            # Untracked file
            if add_if_new:
                run_command(["svn", "add", file_path], base_path)
                commit_summary += f"📁 **File Staged:** Added untracked file `{file_path}` to SVN\n"
            else:
                return f"⚠️ **Untracked File!**\n\n📝 **File:** `{file_path}`\n🔍 **Status:** File is not tracked by SVN\n\n💡 **Options:**\n   • Set `add_if_new=True` to add and commit the file\n   • Manually add file: `svn add {file_path}`\n   • Use SVN commands to add file before committing\n\n🛠️ **Next Steps:** Enable add_if_new or manually add the file"
        elif status.startswith(("M", "A", "D", "R")):
            # Modified, Added, Deleted, or Replaced file
            status_names = {
                "M": "Modified",
                "A": "Added",
                "D": "Deleted",
                "R": "Replaced"
            }
            status_name = status_names.get(status[0], "Changed")
            commit_summary += f"📝 **File Status:** {status_name} file `{file_path}` ready for commit\n"
        elif not status:
            # File is tracked but unchanged
            commit_summary += f"📄 **File Status:** `{file_path}` is tracked and current\n"

        # Create commit
        try:
            result = run_command(["svn", "commit", file_path, "-m", message], base_path)
            svn_output = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if "is up to date" in str(e).lower() or "no changes" in str(e).lower():
                return f"ℹ️ **Nothing to Commit**\n\n📝 **File:** `{file_path}`\n💬 **Message:** {message}\n\n🔍 **Status:** No changes detected for commit\n\n✅ **Repository:** File is already up to date in version control"
            else:
                raise e

        # Extract revision number from SVN output
        revision = "unknown"
        for line in svn_output.split('\n'):
            if "Committed revision" in line:
                try:
                    revision = line.split()[-1].rstrip('.')
                except:
                    pass
                break

        # Build success message
        success_message = f"🎉 **File Committed Successfully!**\n\n"
        success_message += commit_summary
        success_message += f"📝 **Commit Details:**\n"
        success_message += f"   📄 File: `{file_path}`\n"
        success_message += f"   💬 Message: \"{message}\"\n"
        success_message += f"   🔖 Revision: {revision}\n\n"

        if svn_output:
            success_message += f"📋 **SVN Output:**\n```\n{svn_output}\n```\n\n"

        success_message += f"✅ **Repository Status:** Changes successfully committed to SVN history\n"
        success_message += f"🔗 **Integration:** File changes are now tracked in version control"

        return success_message

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        return f"❌ **SVN Commit Failed!**\n\n🚨 **Error:** SVN operation failed\n🔍 **Details:** {error_output}\n\n🛠️ **Troubleshooting:**\n   • Check if working copy is properly initialized\n   • Verify file exists and is accessible\n   • Ensure commit message is properly formatted\n   • Check SVN server connectivity\n   • Try manual SVN commands to diagnose issue\n\n💡 **SVN Status:** Run `svn status` to check working copy state"


# ================================
# TOOL 3: GET_PREVIOUS_FILE_VERSION
# ================================

@app.tool(
    description="Get content of file from previous commit or revision with comprehensive Git and SVN support",
    tags={"version-control", "history", "git", "svn", "file-versions", "previous-commits"}
)
async def get_previous_file_version(
    file_path: Annotated[str, Field(description="Path to file (relative to knowledge base)")],
    commits_back: Annotated[int, Field(description="How many commits to go back (1 = previous commit)", ge=1)] = 1
) -> str:
    """Get content of file from previous commit with comprehensive version history support."""
    try:
        base_path = get_base_directory()
        vcs_type = get_vcs_type()

        if not vcs_type:
            return "❌ **Version Control Not Enabled!**\n\n🚨 **Error:** Version control is not enabled in configuration\n\n🛠️ **Resolution Steps:**\n   1. Run `setup_version_control` tool to initialize repository\n   2. Choose VCS type (git or svn) during setup\n   3. Enable version control in AgentKnowledgeMCP configuration\n   4. Commit some changes to create version history\n   5. Try get_previous_file_version again after setup\n\n💡 **Note:** File history requires existing commits in the repository"

        if not file_path:
            return "❌ **Missing File Path!**\n\n🚨 **Error:** file_path parameter is required\n\n📝 **Required Parameters:**\n   • `file_path`: Path to file (relative to knowledge base)\n   • `commits_back`: Number of commits to go back (optional, default: 1)\n\n💡 **Example Usage:**\n   ```\n   get_previous_file_version(\n       file_path=\"docs/readme.md\",\n       commits_back=2\n   )\n   ```"

        if commits_back < 1:
            return f"❌ **Invalid Commits Back Value!**\n\n🚨 **Error:** commits_back must be 1 or greater\n📊 **Provided Value:** {commits_back}\n\n🛠️ **Valid Options:**\n   • `1` - Previous commit (most recent)\n   • `2` - Two commits ago\n   • `3` - Three commits ago\n   • etc.\n\n💡 **Note:** Higher values require sufficient commit history"

        # Route to appropriate VCS handler
        if vcs_type == "git":
            return await _get_previous_file_version_git(base_path, file_path, commits_back)
        elif vcs_type == "svn":
            return await _get_previous_file_version_svn(base_path, file_path, commits_back)
        else:
            return f"❌ **Unsupported VCS Type!**\n\n🚨 **Error:** '{vcs_type}' is not supported for file history operations\n\n✅ **Supported Types:**\n   • `git` - Git distributed version control\n   • `svn` - Subversion centralized version control\n\n🛠️ **Resolution:**\n   • Check version control configuration\n   • Run `setup_version_control` with supported VCS type\n   • Verify config.json has correct VCS type setting"

    except subprocess.CalledProcessError as e:
        return _format_vcs_error(e, "get file history", f"retrieving previous version of {file_path}")
    except PermissionError as e:
        return f"❌ **Permission Error!**\n\n🚨 **Error:** Insufficient permissions for history operation\n🔍 **Details:** {str(e)}\n\n🛠️ **Resolution:**\n   • Check file system permissions for {file_path}\n   • Ensure user has read access to repository\n   • Verify repository directory permissions\n   • Try running with elevated permissions if necessary"
    except Exception as e:
        return _format_vcs_error(e, "get file history", f"version control history operation for {file_path}")


async def _get_previous_file_version_git(base_path: Path, file_path: str, commits_back: int) -> str:
    """Get previous file version using Git with comprehensive history support."""
    try:
        # Check if file exists in current working directory
        full_file_path = base_path / file_path
        current_exists = full_file_path.exists()

        # Get commit history for the file
        try:
            result = run_command(["git", "log", "--oneline", "-n", str(commits_back + 1), "--", file_path], base_path)
            history_output = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if "does not have any commits yet" in str(e).lower():
                return f"❌ **No Commit History!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** Repository has no commits yet\n\n🛠️ **Resolution:**\n   • Create initial commit with files\n   • Commit some changes to build history\n   • File must be tracked in at least one commit\n\n💡 **Commands to Try:**\n   • `git add {file_path}`\n   • `git commit -m \"Initial commit\"`"
            elif "ambiguous argument" in str(e).lower():
                return f"❌ **File Not Found in History!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** File has never been committed to Git\n\n🛠️ **Resolution:**\n   • Check if file path is correct: `{file_path}`\n   • Add and commit file: `git add {file_path}`\n   • Verify file exists in repository history\n   • Use `git log --name-only` to see tracked files\n\n💡 **Current Status:** File exists in working directory: {current_exists}"
            else:
                raise e

        if not history_output:
            return f"❌ **No History Available!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** No commit history found for this file\n\n🛠️ **Possible Causes:**\n   • File has never been committed\n   • File was added after all existing commits\n   • File path is incorrect\n   • Repository is empty\n\n💡 **Check Commands:**\n   • `git log --name-only` - See all tracked files\n   • `git status` - Check current file status\n   • `git ls-files` - List tracked files"

        # Parse commit history
        commits = [line.split(' ', 1) for line in history_output.split('\n') if line.strip()]
        total_commits = len(commits)

        if commits_back >= total_commits:
            commit_list = "\n".join([f"   {i+1}. {commit[0][:8]} - {commit[1] if len(commit) > 1 else 'No message'}" for i, commit in enumerate(commits)])
            return f"❌ **Not Enough History!**\n\n📝 **File:** `{file_path}`\n📊 **Requested:** Go back {commits_back} commits\n📊 **Available:** Only {total_commits} commits in history\n\n📋 **Available Commits:**\n{commit_list}\n\n🛠️ **Resolution:**\n   • Choose a value between 1 and {total_commits}\n   • Use `git log --oneline {file_path}` to see full history\n   • Create more commits to build longer history"

        # Get the target commit hash
        target_commit = commits[commits_back][0]

        # Get file content from that commit
        try:
            result = run_command(["git", "show", f"{target_commit}:{file_path}"], base_path)
            file_content = result.stdout
        except subprocess.CalledProcessError as e:
            if "does not exist" in str(e).lower() or "path not in" in str(e).lower():
                return f"❌ **File Not Found in Commit!**\n\n📝 **File:** `{file_path}`\n🔖 **Commit:** {target_commit}\n🚨 **Error:** File did not exist in that commit\n\n� **Possible Explanations:**\n   • File was added after this commit\n   • File was deleted before this commit\n   • File was moved/renamed\n   • Different file path was used\n\n🛠️ **Investigation:**\n   • Check file history: `git log --follow {file_path}`\n   • See files in commit: `git show --name-only {target_commit}`\n   • Look for renames: `git log --follow --stat {file_path}`"
            else:
                raise e

        # Get commit information
        try:
            result = run_command(["git", "show", "--no-patch", "--format=%H|%an|%ad|%s", target_commit], base_path)
            commit_info = result.stdout.strip().split('|')
            full_hash = commit_info[0] if len(commit_info) > 0 else target_commit
            author = commit_info[1] if len(commit_info) > 1 else "Unknown"
            date = commit_info[2] if len(commit_info) > 2 else "Unknown"
            message = commit_info[3] if len(commit_info) > 3 else "No message"
        except subprocess.CalledProcessError:
            # Fallback if detailed info fails
            full_hash = target_commit
            author = "Unknown"
            date = "Unknown"
            message = "No message"

        # Build success response
        content_preview = file_content[:200] + "..." if len(file_content) > 200 else file_content
        success_message = f"📜 **Previous File Version Retrieved!**\n\n"
        success_message += f"📝 **File Details:**\n"
        success_message += f"   📄 File: `{file_path}`\n"
        success_message += f"   ⏮️ Commits Back: {commits_back}\n"
        success_message += f"   📊 Total History: {total_commits} commits\n\n"
        success_message += f"🔖 **Commit Information:**\n"
        success_message += f"   🔗 Hash: {full_hash[:8]}\n"
        success_message += f"   👤 Author: {author}\n"
        success_message += f"   📅 Date: {date}\n"
        success_message += f"   💬 Message: {message}\n\n"
        success_message += f"📄 **File Content:** ({len(file_content)} characters)\n"
        success_message += f"```\n{file_content}\n```\n\n"
        success_message += f"✅ **Operation Status:** File content successfully retrieved from Git history"

        return success_message

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        return f"❌ **Git History Failed!**\n\n🚨 **Error:** Git operation failed\n🔍 **Details:** {error_output}\n\n🛠️ **Troubleshooting:**\n   • Check if repository is properly initialized\n   • Verify file has been committed to Git\n   • Ensure commit history exists for file\n   • Check Git configuration and connectivity\n   • Try manual Git commands to diagnose issue\n\n💡 **Git Commands:**\n   • `git log {file_path}` - Check file history\n   • `git ls-files {file_path}` - Verify file is tracked"


async def _get_previous_file_version_svn(base_path: Path, file_path: str, commits_back: int) -> str:
    """Get previous file version using SVN with comprehensive revision support."""
    try:
        # Check if file exists in current working copy
        full_file_path = base_path / file_path
        current_exists = full_file_path.exists()

        # Get revision history for the file using svn log
        try:
            result = run_command(["svn", "log", "-l", str(commits_back + 5), "--quiet", file_path], base_path)
            history_output = result.stdout.strip()
        except subprocess.CalledProcessError as e:
            if "is not a working copy" in str(e).lower():
                return f"❌ **Not an SVN Working Copy!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** Directory is not an SVN working copy\n\n🛠️ **Resolution:**\n   • Run `setup_version_control` with vcs_type='svn'\n   • Check if working copy is properly initialized\n   • Verify you're in the correct directory\n   • Try `svn info` to check working copy status"
            elif "not under version control" in str(e).lower():
                return f"❌ **File Not Under Version Control!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** File is not tracked by SVN\n\n🛠️ **Resolution:**\n   • Add file to SVN: `svn add {file_path}`\n   • Commit file: `svn commit -m \"Add {file_path}\"`\n   • Verify file path is correct\n   • Use `svn status` to see tracked files\n\n💡 **Current Status:** File exists in working copy: {current_exists}"
            else:
                raise e

        if not history_output or "--------" not in history_output:
            return f"❌ **No History Available!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** No revision history found for this file\n\n🛠️ **Possible Causes:**\n   • File has never been committed\n   • File was added after all existing revisions\n   • File path is incorrect\n   • Working copy is not initialized\n\n💡 **Check Commands:**\n   • `svn log {file_path}` - See file history\n   • `svn status` - Check current file status\n   • `svn info` - Verify working copy"

        # Parse revision history - SVN log format includes revision lines starting with 'r'
        revisions = []
        for line in history_output.split('\n'):
            if line.startswith('r') and ' | ' in line:
                rev_number = line.split(' | ')[0].strip()
                revisions.append(rev_number)

        total_revisions = len(revisions)

        if total_revisions == 0:
            return f"❌ **No Revisions Found!**\n\n📝 **File:** `{file_path}`\n🚨 **Error:** Could not parse revision history\n\n🛠️ **Debug Steps:**\n   • Run `svn log {file_path}` manually\n   • Check if file has commit history\n   • Verify SVN log output format\n   • Ensure file is properly tracked"

        if commits_back > total_revisions:
            revision_list = "\n".join([f"   {i+1}. {rev}" for i, rev in enumerate(revisions)])
            return f"❌ **Not Enough History!**\n\n📝 **File:** `{file_path}`\n📊 **Requested:** Go back {commits_back} revisions\n📊 **Available:** Only {total_revisions} revisions in history\n\n📋 **Available Revisions:**\n{revision_list}\n\n🛠️ **Resolution:**\n   • Choose a value between 1 and {total_revisions}\n   • Use `svn log {file_path}` to see full history\n   • Create more revisions to build longer history"

        # Get the target revision number
        target_revision = revisions[commits_back - 1]  # SVN revisions are 0-indexed in our list

        # Get file content from that revision
        try:
            result = run_command(["svn", "cat", f"{file_path}@{target_revision}"], base_path)
            file_content = result.stdout
        except subprocess.CalledProcessError as e:
            if "file not found" in str(e).lower() or "does not exist" in str(e).lower():
                return f"❌ **File Not Found in Revision!**\n\n📝 **File:** `{file_path}`\n🔖 **Revision:** {target_revision}\n🚨 **Error:** File did not exist in that revision\n\n💡 **Possible Explanations:**\n   • File was added after this revision\n   • File was deleted before this revision\n   • File was moved/renamed\n   • Different file path was used\n\n🛠️ **Investigation:**\n   • Check file history: `svn log {file_path}`\n   • See files in revision: `svn log -v {target_revision}`\n   • Look for moves: `svn log -v --stop-on-copy {file_path}`"
            else:
                raise e

        # Get detailed revision information
        try:
            result = run_command(["svn", "log", "-r", target_revision, "--xml"], base_path)
            # For simplicity, we'll parse basic info from the standard log
            result = run_command(["svn", "log", "-r", target_revision], base_path)
            log_output = result.stdout.strip()

            # Extract author, date, and message from SVN log output
            lines = log_output.split('\n')
            if len(lines) >= 2 and ' | ' in lines[1]:
                parts = lines[1].split(' | ')
                author = parts[1].strip() if len(parts) > 1 else "Unknown"
                date = parts[2].strip() if len(parts) > 2 else "Unknown"
                # Message is usually after the separator line
                message_lines = [line for line in lines[3:] if line.strip() and not line.startswith('---')]
                message = message_lines[0].strip() if message_lines else "No message"
            else:
                author = "Unknown"
                date = "Unknown"
                message = "No message"
        except subprocess.CalledProcessError:
            # Fallback if detailed info fails
            author = "Unknown"
            date = "Unknown"
            message = "No message"

        # Build success response
        content_preview = file_content[:200] + "..." if len(file_content) > 200 else file_content
        success_message = f"📜 **Previous File Version Retrieved!**\n\n"
        success_message += f"📝 **File Details:**\n"
        success_message += f"   📄 File: `{file_path}`\n"
        success_message += f"   ⏮️ Revisions Back: {commits_back}\n"
        success_message += f"   📊 Total History: {total_revisions} revisions\n\n"
        success_message += f"🔖 **Revision Information:**\n"
        success_message += f"   🔗 Revision: {target_revision}\n"
        success_message += f"   👤 Author: {author}\n"
        success_message += f"   📅 Date: {date}\n"
        success_message += f"   💬 Message: {message}\n\n"
        success_message += f"📄 **File Content:** ({len(file_content)} characters)\n"
        success_message += f"```\n{file_content}\n```\n\n"
        success_message += f"✅ **Operation Status:** File content successfully retrieved from SVN history"

        return success_message

    except subprocess.CalledProcessError as e:
        error_output = e.stderr or e.stdout or str(e)
        return f"❌ **SVN History Failed!**\n\n🚨 **Error:** SVN operation failed\n🔍 **Details:** {error_output}\n\n🛠️ **Troubleshooting:**\n   • Check if working copy is properly initialized\n   • Verify file has been committed to SVN\n   • Ensure revision history exists for file\n   • Check SVN server connectivity\n   • Try manual SVN commands to diagnose issue\n\n💡 **SVN Commands:**\n   • `svn log {file_path}` - Check file history\n   • `svn info {file_path}` - Verify file is tracked"


# CLI entry point
def cli_main():
    """CLI entry point for Version Control FastMCP server."""
    print("🚀 Starting AgentKnowledgeMCP Version Control FastMCP server...")
    print("⚙️ Tools: setup_version_control, commit_file, get_previous_file_version")
    print("✅ Status: Tool #3 Complete - Version Control Server 100% Migrated!")

    app.run()

if __name__ == "__main__":
    cli_main()
