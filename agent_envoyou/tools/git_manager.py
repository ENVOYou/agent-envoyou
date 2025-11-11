#!/usr/bin/env python3
"""
Git Manager Tool for Fullstack Agent

Provides Git version control operations for generated projects,
including repository initialization, commits, and branch management.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.tool_context import ToolContext


class GitManagerTool(BaseTool):
    """Tool for Git version control operations."""
    
    def __init__(self):
        super().__init__(
            name="git_manager_tool",
            description="Git version control operations for project management"
        )
        self.logger = logging.getLogger(__name__)
    
    def _run_git_command(self, command: List[str], cwd: Path = None) -> Dict[str, Any]:
        """Run a git command and return the result."""
        try:
            result = subprocess.run(
                command,
                cwd=str(cwd) if cwd else None,
                capture_output=True,
                text=True,
                check=False,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip()
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": " ".join(command)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(command)
            }
    
    async def initialize_repository(self, context: ToolContext, project_path: str, commit: bool = False) -> Dict[str, Any]:
        """Initialize a Git repository in the project directory."""
        try:
            project_path = Path(project_path).resolve()
            
            if not project_path.exists():
                raise FileNotFoundError(f"Project directory not found: {project_path}")
            
            # Initialize repository
            result = self._run_git_command(["git", "init"], cwd=project_path)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to initialize Git repository: {result.get('error', result.get('stderr', 'Unknown error'))}",
                    "project_path": str(project_path)
                }
            
            # Configure git user (required for commits)
            user_name_result = self._run_git_command(
                ["git", "config", "user.name", "Fullstack Agent"], 
                cwd=project_path
            )
            
            user_email_result = self._run_git_command(
                ["git", "config", "user.email", "agent@fullstack.dev"], 
                cwd=project_path
            )
            
            init_info = {
                "success": True,
                "project_path": str(project_path),
                "repository_initialized": True,
                "timestamp": datetime.now().isoformat(),
                "config_updated": user_name_result["success"] and user_email_result["success"]
            }
            
            # Create initial commit if requested
            if commit:
                commit_result = await self.create_initial_commit(context, str(project_path))
                init_info["initial_commit"] = commit_result
            
            # Update context state
            context.state['temp:last_git_operation'] = "initialize_repository"
            context.state['temp:git_repo_path'] = str(project_path)
            
            self.logger.info(f"Git repository initialized at: {project_path}")
            
            return init_info
            
        except Exception as e:
            self.logger.error(f"Error initializing Git repository: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_path": project_path
            }
    
    async def create_initial_commit(self, context: ToolContext, project_path: str) -> Dict[str, Any]:
        """Create an initial commit with all current files."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Add all files
            add_result = self._run_git_command(["git", "add", "."], cwd=project_path)
            
            if not add_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to add files: {add_result.get('error', add_result.get('stderr', 'Unknown error'))}"
                }
            
            # Create commit
            commit_message = "Initial commit by Fullstack Agent"
            commit_result = self._run_git_command(
                ["git", "commit", "-m", commit_message], 
                cwd=project_path
            )
            
            if not commit_result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create commit: {commit_result.get('error', commit_result.get('stderr', 'Unknown error'))}"
                }
            
            # Get commit hash
            hash_result = self._run_git_command(["git", "rev-parse", "HEAD"], cwd=project_path)
            
            return {
                "success": True,
                "commit_hash": hash_result["stdout"] if hash_result["success"] else "unknown",
                "commit_message": commit_message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating initial commit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def add_files(self, context: ToolContext, project_path: str, files: List[str] = None) -> Dict[str, Any]:
        """Add files to Git staging area."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            if files:
                # Add specific files
                result = self._run_git_command(
                    ["git", "add"] + files, 
                    cwd=project_path
                )
            else:
                # Add all files
                result = self._run_git_command(["git", "add", "."], cwd=project_path)
            
            return {
                "success": result["success"],
                "files_added": files if files else ["."],
                "stderr": result.get("stderr", ""),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error adding files to Git: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_commit(self, context: ToolContext, project_path: str, message: str) -> Dict[str, Any]:
        """Create a commit with the current staging changes."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Create commit
            result = self._run_git_command(
                ["git", "commit", "-m", message], 
                cwd=project_path
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create commit: {result.get('error', result.get('stderr', 'Unknown error'))}"
                }
            
            # Get commit hash
            hash_result = self._run_git_command(["git", "rev-parse", "HEAD"], cwd=project_path)
            
            # Update context state
            context.state['temp:last_commit_hash'] = hash_result["stdout"] if hash_result["success"] else "unknown"
            context.state['temp:last_commit_message'] = message
            
            return {
                "success": True,
                "commit_hash": hash_result["stdout"] if hash_result["success"] else "unknown",
                "commit_message": message,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating commit: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_status(self, context: ToolContext, project_path: str) -> Dict[str, Any]:
        """Get Git repository status."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                return {
                    "success": False,
                    "error": f"Git repository not found at: {project_path}",
                    "is_git_repo": False
                }
            
            # Get status
            status_result = self._run_git_command(["git", "status", "--porcelain"], cwd=project_path)
            
            # Parse status output
            modified_files = []
            new_files = []
            deleted_files = []
            
            if status_result["success"] and status_result["stdout"]:
                for line in status_result["stdout"].split("\n"):
                    if line.strip():
                        status_code = line[:2]
                        file_path = line[3:]
                        
                        if status_code[0] == "M" or status_code[1] == "M":
                            modified_files.append(file_path)
                        elif status_code[0] == "A":
                            new_files.append(file_path)
                        elif status_code[0] == "D":
                            deleted_files.append(file_path)
            
            # Get current branch
            branch_result = self._run_git_command(["git", "branch", "--show-current"], cwd=project_path)
            current_branch = branch_result["stdout"] if branch_result["success"] else "unknown"
            
            # Get last commit
            last_commit_result = self._run_git_command(
                ["git", "log", "-1", "--pretty=format:%H|%s|%an|%ad"], 
                cwd=project_path
            )
            
            last_commit = None
            if last_commit_result["success"] and last_commit_result["stdout"]:
                parts = last_commit_result["stdout"].split("|")
                if len(parts) >= 4:
                    last_commit = {
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "date": parts[3]
                    }
            
            status_info = {
                "success": True,
                "is_git_repo": True,
                "project_path": str(project_path),
                "current_branch": current_branch.strip(),
                "last_commit": last_commit,
                "modified_files": modified_files,
                "new_files": new_files,
                "deleted_files": deleted_files,
                "has_changes": len(modified_files) + len(new_files) + len(deleted_files) > 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Update context state
            context.state['temp:git_status'] = status_info
            
            return status_info
            
        except Exception as e:
            self.logger.error(f"Error getting Git status: {e}")
            return {
                "success": False,
                "error": str(e),
                "is_git_repo": False
            }
    
    async def create_branch(self, context: ToolContext, project_path: str, branch_name: str) -> Dict[str, Any]:
        """Create and switch to a new branch."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Create and switch to new branch
            result = self._run_git_command(
                ["git", "checkout", "-b", branch_name], 
                cwd=project_path
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to create branch '{branch_name}': {result.get('error', result.get('stderr', 'Unknown error'))}"
                }
            
            # Update context state
            context.state['temp:current_branch'] = branch_name
            context.state['temp:last_git_operation'] = "create_branch"
            
            return {
                "success": True,
                "branch_name": branch_name,
                "current_branch": branch_name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def push_to_remote(self, context: ToolContext, project_path: str, remote: str = "origin", branch: str = None) -> Dict[str, Any]:
        """Push changes to remote repository."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Get current branch if not specified
            if not branch:
                branch_result = self._run_git_command(["git", "branch", "--show-current"], cwd=project_path)
                branch = branch_result["stdout"].strip() if branch_result["success"] else "main"
            
            # Push to remote
            result = self._run_git_command(
                ["git", "push", remote, branch], 
                cwd=project_path
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Failed to push to remote '{remote}': {result.get('error', result.get('stderr', 'Unknown error'))}",
                    "note": "This might be because no remote is configured or authentication is required"
                }
            
            # Update context state
            context.state['temp:last_push_remote'] = remote
            context.state['temp:last_push_branch'] = branch
            
            return {
                "success": True,
                "remote": remote,
                "branch": branch,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error pushing to remote: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_commits(self, context: ToolContext, project_path: str, limit: int = 10) -> Dict[str, Any]:
        """Get recent commit history."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Get commit log
            result = self._run_git_command(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%s|%an|%ad|%cd"], 
                cwd=project_path
            )
            
            commits = []
            if result["success"] and result["stdout"]:
                for line in result["stdout"].split("\n"):
                    if line.strip():
                        parts = line.split("|", 4)
                        if len(parts) >= 5:
                            commits.append({
                                "hash": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                                "author_date": parts[3],
                                "commit_date": parts[4]
                            })
            
            return {
                "success": True,
                "project_path": str(project_path),
                "commits": commits,
                "total_count": len(commits),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting commit history: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def configure_remote(self, context: ToolContext, project_path: str, remote_name: str, remote_url: str) -> Dict[str, Any]:
        """Configure a remote repository URL."""
        try:
            project_path = Path(project_path).resolve()
            
            if not (project_path / ".git").exists():
                raise ValueError(f"Git repository not found at: {project_path}")
            
            # Add or update remote
            result = self._run_git_command(
                ["git", "remote", "set-url", remote_name, remote_url], 
                cwd=project_path
            )
            
            # If setting URL failed, try adding the remote
            if not result["success"]:
                add_result = self._run_git_command(
                    ["git", "remote", "add", remote_name, remote_url], 
                    cwd=project_path
                )
                
                if not add_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to configure remote '{remote_name}': {add_result.get('error', add_result.get('stderr', 'Unknown error'))}"
                    }
            
            # Update context state
            context.state['temp:git_remote_configured'] = remote_name
            context.state['temp:git_remote_url'] = remote_url
            
            return {
                "success": True,
                "remote_name": remote_name,
                "remote_url": remote_url,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error configuring remote: {e}")
            return {
                "success": False,
                "error": str(e)
            }