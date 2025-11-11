#!/usr/bin/env python3
"""
File System Tool for Fullstack Agent

Provides safe file operations for agents to read, write, create, and manage
project files without risking system security or data loss.
"""

import os
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part


class FileSystemTool(BaseTool):
    """Tool for safe file system operations."""
    
    def __init__(self):
        super().__init__(
            name="file_system_tool",
            description="Safe file system operations for project management"
        )
        self.logger = logging.getLogger(__name__)
        
        # Define safe directories (project root and subdirectories only)
        self.allowed_base_paths = [
            Path.cwd(),  # Current working directory
            Path.cwd() / "generated",  # Generated projects directory
            Path.cwd() / "temp",       # Temporary files directory
        ]
    
    def _validate_path(self, file_path: Union[str, Path]) -> Path:
        """Validate that the file path is within allowed directories."""
        try:
            path = Path(file_path).resolve()
            
            # Check if path is within any allowed base path
            for base_path in self.allowed_base_paths:
                base_resolved = base_path.resolve()
                try:
                    path.relative_to(base_resolved)
                    return path
                except ValueError:
                    continue
            
            raise ValueError(f"File path '{file_path}' is outside allowed directories")
        except Exception as e:
            raise ValueError(f"Invalid file path: {e}")
    
    def _ensure_parent_dir(self, file_path: Path) -> None:
        """Ensure parent directory exists."""
        parent_dir = file_path.parent
        parent_dir.mkdir(parents=True, exist_ok=True)
    
    async def read_file(self, context: ToolContext, file_path: str) -> str:
        """Read content from a file."""
        try:
            validated_path = self._validate_path(file_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(validated_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Log the operation
            self.logger.info(f"Read file: {validated_path}")
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    async def write_file(self, context: ToolContext, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            validated_path = self._validate_path(file_path)
            self._ensure_parent_dir(validated_path)
            
            with open(validated_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Update context state
            context.state['temp:last_written_file'] = str(validated_path)
            context.state['temp:last_write_timestamp'] = str(validated_path.stat().st_mtime)
            
            self.logger.info(f"Wrote file: {validated_path}")
            
            return {
                "success": True,
                "file_path": str(validated_path),
                "size": validated_path.stat().st_size,
                "message": f"File written successfully: {file_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            raise
    
    async def create_directory(self, context: ToolContext, dir_path: str) -> Dict[str, Any]:
        """Create a directory."""
        try:
            validated_path = self._validate_path(dir_path)
            validated_path.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Created directory: {validated_path}")
            
            return {
                "success": True,
                "directory_path": str(validated_path),
                "message": f"Directory created successfully: {dir_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating directory {dir_path}: {e}")
            raise
    
    async def list_files(self, context: ToolContext, directory_path: str, recursive: bool = False) -> List[str]:
        """List files in a directory."""
        try:
            validated_path = self._validate_path(directory_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            if not validated_path.is_dir():
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            if recursive:
                files = [str(p.relative_to(validated_path)) for p in validated_path.rglob('*') if p.is_file()]
            else:
                files = [p.name for p in validated_path.iterdir() if p.is_file()]
            
            # Sort files for consistent output
            files.sort()
            
            self.logger.info(f"Listed {len(files)} files in: {validated_path}")
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files in {directory_path}: {e}")
            raise
    
    async def delete_file(self, context: ToolContext, file_path: str) -> Dict[str, Any]:
        """Delete a file."""
        try:
            validated_path = self._validate_path(file_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not validated_path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            validated_path.unlink()
            
            self.logger.info(f"Deleted file: {validated_path}")
            
            return {
                "success": True,
                "file_path": str(validated_path),
                "message": f"File deleted successfully: {file_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            raise
    
    async def copy_file(self, context: ToolContext, source_path: str, dest_path: str) -> Dict[str, Any]:
        """Copy a file from source to destination."""
        try:
            source_validated = self._validate_path(source_path)
            dest_validated = self._validate_path(dest_path)
            
            if not source_validated.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if not source_validated.is_file():
                raise ValueError(f"Source path is not a file: {source_path}")
            
            self._ensure_parent_dir(dest_validated)
            
            # Copy the file
            import shutil
            shutil.copy2(source_validated, dest_validated)
            
            self.logger.info(f"Copied {source_validated} to {dest_validated}")
            
            return {
                "success": True,
                "source": str(source_validated),
                "destination": str(dest_validated),
                "message": f"File copied successfully: {source_path} -> {dest_path}"
            }
            
        except Exception as e:
            self.logger.error(f"Error copying file {source_path} -> {dest_path}: {e}")
            raise
    
    async def get_file_info(self, context: ToolContext, file_path: str) -> Dict[str, Any]:
        """Get information about a file."""
        try:
            validated_path = self._validate_path(file_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = validated_path.stat()
            
            info = {
                "success": True,
                "file_path": str(validated_path),
                "is_file": validated_path.is_file(),
                "is_directory": validated_path.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "permissions": oct(stat.st_mode)[-3:]
            }
            
            self.logger.info(f"Got file info for: {validated_path}")
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {e}")
            raise
    
    async def search_files(self, context: ToolContext, directory: str, pattern: str) -> List[str]:
        """Search for files matching a pattern."""
        try:
            validated_path = self._validate_path(directory)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            import glob
            
            search_pattern = str(validated_path / "**" / pattern)
            matches = glob.glob(search_pattern, recursive=True)
            
            # Convert to relative paths
            relative_matches = [str(Path(m).relative_to(validated_path)) for m in matches]
            relative_matches.sort()
            
            self.logger.info(f"Found {len(relative_matches)} files matching '{pattern}' in {validated_path}")
            
            return relative_matches
            
        except Exception as e:
            self.logger.error(f"Error searching files in {directory} with pattern {pattern}: {e}")
            raise