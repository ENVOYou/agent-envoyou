# Tool Confirmation System for ADK
"""
Production safety tool confirmation system following Google ADK patterns.
Implements human-in-the-loop confirmation for destructive operations.
"""

import asyncio
from typing import Any, Dict, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConfirmationType(Enum):
    """Types of confirmation supported."""
    BOOLEAN = "boolean"  # Simple yes/no
    STRUCTURED = "structured"  # Complex data input
    CONDITIONAL = "conditional"  # Conditional based on parameters

@dataclass
class ConfirmationRequest:
    """Data structure for confirmation requests."""
    operation_id: str
    tool_name: str
    operation_type: str
    description: str
    parameters: Dict[str, Any]
    confirmation_type: ConfirmationType
    requires_confirmation: bool
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None

@dataclass
class ConfirmationResponse:
    """Data structure for confirmation responses."""
    operation_id: str
    confirmed: bool
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    user_input: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class ToolConfirmationSystem:
    """
    Centralized tool confirmation system following ADK patterns.
    Handles both boolean and advanced confirmation flows.
    """
    
    def __init__(self):
        self.pending_requests: Dict[str, ConfirmationRequest] = {}
        self.response_handlers: Dict[str, Callable] = {}
        self.confirmation_callbacks: Dict[str, Callable] = {}
        
    async def request_confirmation(
        self,
        operation_id: str,
        tool_name: str,
        operation_type: str,
        description: str,
        parameters: Dict[str, Any],
        confirmation_type: ConfirmationType = ConfirmationType.BOOLEAN,
        requires_confirmation: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> Union[bool, Dict[str, Any], None]:
        """
        Request user confirmation for a tool operation.
        
        Args:
            operation_id: Unique identifier for this operation
            tool_name: Name of the tool requesting confirmation
            operation_type: Type of operation (e.g., "delete", "execute", "deploy")
            description: Human-readable description of what will happen
            parameters: Operation parameters for context
            confirmation_type: Type of confirmation required
            requires_confirmation: Whether confirmation is mandatory
            context: Additional context for the confirmation
            
        Returns:
            Confirmation result: bool for boolean, dict for structured, None if waiting
        """
        
        # Create confirmation request
        request = ConfirmationRequest(
            operation_id=operation_id,
            tool_name=tool_name,
            operation_type=operation_type,
            description=description,
            parameters=parameters,
            confirmation_type=confirmation_type,
            requires_confirmation=requires_confirmation,
            timestamp=datetime.now(),
            context=context
        )
        
        # Store pending request
        self.pending_requests[operation_id] = request
        
        if not requires_confirmation:
            # Auto-approve if confirmation not required
            await self._auto_approve(request)
            return self._get_default_response(confirmation_type)
        
        # Log the confirmation request
        logger.info(f"Confirmation requested: {operation_id} - {description}")
        
        # For ADK integration, this would use confirm_with_user
        # For now, we'll implement a basic confirmation mechanism
        
        try:
            if confirmation_type == ConfirmationType.BOOLEAN:
                return await self._handle_boolean_confirmation(request)
            elif confirmation_type == ConfirmationType.STRUCTURED:
                return await self._handle_structured_confirmation(request)
            elif confirmation_type == ConfirmationType.CONDITIONAL:
                return await self._handle_conditional_confirmation(request)
        except Exception as e:
            logger.error(f"Error handling confirmation {operation_id}: {e}")
            # Default to deny on error for safety
            return False
        
        return None
    
    async def respond_to_confirmation(
        self,
        operation_id: str,
        confirmed: bool,
        payload: Optional[Dict[str, Any]] = None,
        user_input: Optional[str] = None
    ) -> bool:
        """
        Respond to a pending confirmation request.
        
        Args:
            operation_id: ID of the operation to respond to
            confirmed: Whether the operation is approved
            payload: Additional structured data (for advanced confirmations)
            user_input: Raw user input text
            
        Returns:
            True if response was processed successfully
        """
        
        if operation_id not in self.pending_requests:
            logger.warning(f"Confirmation response for unknown operation: {operation_id}")
            return False
        
        request = self.pending_requests[operation_id]
        
        # Create response
        response = ConfirmationResponse(
            operation_id=operation_id,
            confirmed=confirmed,
            payload=payload,
            user_input=user_input
        )
        
        # Process response through handlers
        if operation_id in self.response_handlers:
            try:
                await self.response_handlers[operation_id](response)
                logger.info(f"Confirmation processed: {operation_id} - {confirmed}")
            except Exception as e:
                logger.error(f"Error processing confirmation response {operation_id}: {e}")
                return False
        
        # Clean up pending request
        del self.pending_requests[operation_id]
        
        return True
    
    async def _handle_boolean_confirmation(self, request: ConfirmationRequest) -> bool:
        """Handle simple yes/no confirmation."""
        # In real ADK implementation, this would use confirm_with_user
        # For now, implement basic confirmation logic
        
        description = f"""
🔴 DESTRUCTIVE OPERATION CONFIRMATION

Tool: {request.tool_name}
Operation: {request.operation_type}
Description: {request.description}

⚠️  This operation cannot be undone!
        
Do you want to proceed? (yes/no): """
        
        # For demo purposes, return True if parameters suggest it's safe
        # In production, this would show the dialog to the user
        if self._is_safe_operation(request):
            logger.info(f"Auto-approved safe operation: {request.operation_id}")
            return True
        
        # In production, this would wait for user input
        logger.info(f"Boolean confirmation requested: {request.operation_id}")
        return False  # Default to deny for safety
    
    async def _handle_structured_confirmation(self, request: ConfirmationRequest) -> Dict[str, Any]:
        """Handle complex confirmation with structured data."""
        # For advanced confirmations, request additional data
        description = f"""
🔴 ADVANCED CONFIRMATION REQUIRED

Tool: {request.tool_name}
Operation: {request.operation_type}
Description: {request.description}

Please provide the following information:
"""
        
        # In production, this would show a form to the user
        # For now, return default structured response
        return {"approved": False, "reason": "Confirmation required"}
    
    async def _handle_conditional_confirmation(self, request: ConfirmationRequest) -> bool:
        """Handle conditional confirmation based on operation parameters."""
        # Check if this operation requires confirmation based on its parameters
        threshold_func = self.confirmation_callbacks.get(request.operation_id)
        if threshold_func:
            try:
                needs_confirmation = await threshold_func(request.parameters)
                if not needs_confirmation:
                    logger.info(f"Auto-approved by conditional check: {request.operation_id}")
                    return True
            except Exception as e:
                logger.error(f"Error in conditional confirmation: {e}")
        
        # Default to requesting confirmation
        return await self._handle_boolean_confirmation(request)
    
    async def _auto_approve(self, request: ConfirmationRequest):
        """Auto-approve operations that don't require confirmation."""
        logger.info(f"Auto-approved operation: {request.operation_id}")
    
    def _get_default_response(self, confirmation_type: ConfirmationType) -> Union[bool, Dict[str, Any]]:
        """Get default response for non-confirmation scenarios."""
        if confirmation_type == ConfirmationType.BOOLEAN:
            return True
        elif confirmation_type == ConfirmationType.STRUCTURED:
            return {"auto_approved": True}
        return None
    
    def _is_safe_operation(self, request: ConfirmationRequest) -> bool:
        """Determine if an operation is safe to auto-approve."""
        # Define safety rules based on operation type and parameters
        
        # Read operations are always safe
        if request.operation_type in ["read", "list", "get", "view"]:
            return True
        
        # Check file operations
        if request.tool_name == "FileSystemTool":
            if request.operation_type == "read":
                return True
            elif request.operation_type == "delete":
                # Only auto-approve if path is in safe directories
                path = request.parameters.get("path", "")
                return self._is_safe_path(path)
            elif request.operation_type == "copy":
                # Auto-approve if both source and dest are safe
                source = request.parameters.get("source_path", "")
                dest = request.parameters.get("dest_path", "")
                return self._is_safe_path(source) and self._is_safe_path(dest)
        
        # Check code execution
        elif request.tool_name == "CodeExecutorTool":
            code = request.parameters.get("code", "")
            return self._is_safe_code(code)
        
        # Check git operations
        elif request.tool_name == "GitManagerTool":
            operation = request.parameters.get("operation", "")
            if operation in ["status", "log", "show"]:
                return True
        
        # Check docker operations
        elif request.tool_name == "DockerBuilderTool":
            operation = request.parameters.get("operation", "")
            if operation in ["build", "test"]:
                return True
        
        # Default: require confirmation for unknown or potentially dangerous operations
        return False
    
    def _is_safe_path(self, path: str) -> bool:
        """Check if a file path is safe for auto-approval."""
        safe_patterns = [
            "/tmp/",
            "/var/tmp/",
            "./execution_sandbox/",
            "./assets/",
            "./docs/",
        ]
        
        for pattern in safe_patterns:
            if path.startswith(pattern):
                return True
        
        return False
    
    def _is_safe_code(self, code: str) -> bool:
        """Check if code is safe for execution."""
        dangerous_keywords = [
            "import os",
            "import subprocess", 
            "import sys",
            "import shutil",
            "import socket",
            "import requests",
            "urllib",
            "eval(",
            "exec(",
            "__import__",
            "open(",
            "file(",
            "input(",
            "raw_input(",
        ]
        
        for keyword in dangerous_keywords:
            if keyword.lower() in code.lower():
                return False
        
        # Only very simple, safe code patterns are auto-approved
        safe_patterns = [
            "print(",
            "print(",
            "return",
            "def ",
            "class ",
        ]
        
        has_safe_pattern = any(pattern in code for pattern in safe_patterns)
        has_complex_structure = any(op in code for op in ["for", "while", "if", "try"])
        
        return has_safe_pattern and not has_complex_structure
    
    def set_confirmation_callback(self, operation_id: str, callback: Callable):
        """Set a custom confirmation callback for an operation."""
        self.confirmation_callbacks[operation_id] = callback
    
    def set_response_handler(self, operation_id: str, handler: Callable):
        """Set a response handler for an operation."""
        self.response_handlers[operation_id] = handler
    
    def get_pending_confirmations(self) -> Dict[str, ConfirmationRequest]:
        """Get all pending confirmation requests."""
        return self.pending_requests.copy()
    
    def clear_pending_confirmations(self):
        """Clear all pending confirmation requests."""
        self.pending_requests.clear()

# Global instance
tool_confirmation = ToolConfirmationSystem()

# Convenience functions
async def request_destructive_confirmation(
    tool_name: str,
    operation_type: str,
    description: str,
    parameters: Dict[str, Any],
    operation_id: Optional[str] = None
) -> bool:
    """Request confirmation for a destructive operation."""
    if operation_id is None:
        operation_id = f"{tool_name}_{operation_type}_{int(datetime.now().timestamp())}"
    
    return await tool_confirmation.request_confirmation(
        operation_id=operation_id,
        tool_name=tool_name,
        operation_type=operation_type,
        description=description,
        parameters=parameters,
        confirmation_type=ConfirmationType.BOOLEAN,
        requires_confirmation=True
    )

async def request_structured_confirmation(
    tool_name: str,
    operation_type: str,
    description: str,
    parameters: Dict[str, Any],
    operation_id: Optional[str] = None
) -> Dict[str, Any]:
    """Request structured confirmation with additional data."""
    if operation_id is None:
        operation_id = f"{tool_name}_{operation_type}_{int(datetime.now().timestamp())}"
    
    result = await tool_confirmation.request_confirmation(
        operation_id=operation_id,
        tool_name=tool_name,
        operation_type=operation_type,
        description=description,
        parameters=parameters,
        confirmation_type=ConfirmationType.STRUCTURED,
        requires_confirmation=True
    )
    
    return result or {"confirmed": False}

def should_require_confirmation(operation_type: str, parameters: Dict[str, Any]) -> bool:
    """Determine if an operation should require confirmation based on its parameters."""
    # Specific thresholds first
    if operation_type == "delete_files":
        return True  # Always require confirmation for file deletions
    
    if operation_type in ["execute_code", "execute"]:
        code = parameters.get("code", "")
        return len(code) > 200  # Complex code needs confirmation
    
    if operation_type == "deploy":
        return parameters.get("environment") == "production"
    
    if operation_type == "delete_branch":
        return parameters.get("branch") == "main"
    
    # Destructive operations that always require confirmation
    destructive_operations = [
        "delete", "remove", "rm",
        "copy_overwrite", "overwrite", "replace",
        "run"
    ]
    
    if operation_type.lower() in destructive_operations:
        return True
    
    # Safe operations that don't require confirmation
    safe_operations = ["read", "list", "get", "view", "show", "status", "info"]
    
    if operation_type.lower() in safe_operations:
        return False
    
    # For unknown operations, be cautious and require confirmation
    return True