#!/usr/bin/env python3
"""
Advanced State Management for Fullstack Multi-Agent System

Implements ADK's advanced state management capabilities including:
- Session State (current conversation context)
- User State (user preferences and history)
- App State (global settings and templates)
- Temp State (temporary execution context)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from google.adk.agents import readonly_context


class FullstackStateManager:
    """Advanced state management for fullstack agents."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # State templates for different contexts
        self.state_templates = {
            "project_development": {
                "user:preferred_framework": None,
                "user:preferred_language": None,
                "user:preferred_database": None,
                "user:project_history": [],
                "app:default_project_structure": {},
                "app:supported_frameworks": ["React", "Vue", "Angular", "Next.js"],
                "app:supported_languages": ["JavaScript", "TypeScript", "Python", "Node.js"],
                "app:supported_databases": ["PostgreSQL", "MongoDB", "MySQL", "Redis"],
                "temp:current_phase": None,
                "temp:completed_steps": [],
                "temp:current_file": None,
                "temp:build_status": None,
                "current_task": None,
                "current_step": None,
                "task_progress": 0
            },
            "code_review": {
                "user:code_standards": [],
                "user:review_preferences": {},
                "app:review_criteria": [
                    "security", "performance", "maintainability", "testability"
                ],
                "temp:review_session": None,
                "temp:reviewed_files": [],
                "temp:issues_found": [],
                "current_file_being_reviewed": None,
                "review_status": "in_progress"
            },
            "deployment": {
                "user:deployment_preferences": {},
                "app:deployment_targets": ["local", "staging", "production"],
                "app:deployment_strategies": ["docker", "manual", "ci_cd"],
                "temp:deployment_config": {},
                "temp:deployment_status": None,
                "temp:deployment_logs": [],
                "current_deployment_target": None,
                "deployment_progress": 0
            }
        }
    
    def initialize_project_state(self, context, project_type: str) -> Dict[str, Any]:
        """Initialize state for a new project development session."""
        try:
            # Start with the project development template
            initial_state = self.state_templates["project_development"].copy()
            
            # Set current context
            initial_state["current_task"] = f"new_{project_type}_project"
            initial_state["current_step"] = "project_setup"
            initial_state["task_progress"] = 0
            
            # Get user preferences if available
            user_prefs = self.get_user_preferences(context)
            if user_prefs:
                initial_state.update(user_prefs)
            
            # Update context state
            context.state.update(initial_state)
            
            self.logger.info(f"Initialized project state for: {project_type}")
            
            return initial_state
            
        except Exception as e:
            self.logger.error(f"Error initializing project state: {e}")
            return {}
    
    def get_user_preferences(self, context) -> Dict[str, Any]:
        """Extract user preferences from state."""
        try:
            preferences = {}
            
            # Check for user preferences in state
            user_keys = [k for k in context.state.keys() if k.startswith("user:")]
            for key in user_keys:
                preferences[key.replace("user:", "")] = context.state[key]
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return {}
    
    def update_project_progress(self, context, step: str, status: str = "completed") -> Dict[str, Any]:
        """Update project development progress."""
        try:
            # Update current step
            context.state["current_step"] = step
            
            # Add to completed steps if completed
            if status == "completed":
                completed_steps = context.state.get("temp:completed_steps", [])
                if step not in completed_steps:
                    completed_steps.append(step)
                context.state["temp:completed_steps"] = completed_steps
            
            # Calculate progress percentage
            total_steps = len(context.state.get("temp:completed_steps", []))
            context.state["task_progress"] = min(100, (total_steps / 10) * 100)  # Assuming 10 total steps
            
            progress_update = {
                "current_step": step,
                "status": status,
                "completed_steps": len(completed_steps),
                "progress_percentage": context.state["task_progress"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Updated progress: {step} ({status})")
            
            return progress_update
            
        except Exception as e:
            self.logger.error(f"Error updating project progress: {e}")
            return {}
    
    def set_current_file(self, context, file_path: str, operation: str = "editing") -> None:
        """Set the current file being worked on."""
        try:
            context.state["temp:current_file"] = file_path
            context.state["temp:current_operation"] = operation
            context.state["temp:file_timestamp"] = datetime.now().isoformat()
            
            self.logger.debug(f"Set current file: {file_path} ({operation})")
            
        except Exception as e:
            self.logger.error(f"Error setting current file: {e}")
    
    def set_user_preference(self, context, preference_type: str, value: Any) -> None:
        """Set a user preference in state."""
        try:
            context.state[f"user:{preference_type}"] = value
            context.state["temp:last_preference_update"] = datetime.now().isoformat()
            
            self.logger.info(f"Set user preference: {preference_type} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting user preference: {e}")
    
    def get_context_for_agent(self, context, agent_type: str) -> Dict[str, Any]:
        """Get relevant context for a specific agent type."""
        try:
            base_context = {
                "user_preferences": self.get_user_preferences(context),
                "current_task": context.state.get("current_task"),
                "current_step": context.state.get("current_step"),
                "progress": context.state.get("task_progress", 0)
            }
            
            # Add agent-specific context
            if agent_type == "frontend":
                base_context.update({
                    "current_file": context.state.get("temp:current_file"),
                    "framework": context.state.get("user:preferred_framework"),
                    "supported_frameworks": context.state.get("app:supported_frameworks", [])
                })
                
            elif agent_type == "backend":
                base_context.update({
                    "database": context.state.get("user:preferred_database"),
                    "language": context.state.get("user:preferred_language"),
                    "supported_languages": context.state.get("app:supported_languages", [])
                })
                
            elif agent_type == "reviewer":
                base_context.update({
                    "code_standards": context.state.get("user:code_standards", []),
                    "review_criteria": context.state.get("app:review_criteria", []),
                    "reviewed_files": context.state.get("temp:reviewed_files", [])
                })
            
            return base_context
            
        except Exception as e:
            self.logger.error(f"Error getting context for agent {agent_type}: {e}")
            return {}
    
    def store_task_result(self, context, task_name: str, result: Dict[str, Any]) -> None:
        """Store the result of a completed task."""
        try:
            # Store in temp state for current session
            context.state[f"temp:task_result_{task_name}"] = result
            
            # If successful, store in user history
            if result.get("success", False):
                user_history = context.state.get("user:project_history", [])
                history_entry = {
                    "task": task_name,
                    "result": result,
                    "timestamp": result.get("timestamp", datetime.now().isoformat())
                }
                user_history.append(history_entry)
                
                # Keep only last 10 entries
                if len(user_history) > 10:
                    user_history = user_history[-10:]
                
                context.state["user:project_history"] = user_history
            
            self.logger.info(f"Stored task result: {task_name}")
            
        except Exception as e:
            self.logger.error(f"Error storing task result: {e}")
    
    def get_task_history(self, context, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent task history for context."""
        try:
            user_history = context.state.get("user:project_history", [])
            return user_history[-limit:] if user_history else []
            
        except Exception as e:
            self.logger.error(f"Error getting task history: {e}")
            return []
    
    def set_app_setting(self, context, setting_name: str, value: Any) -> None:
        """Set a global application setting."""
        try:
            context.state[f"app:{setting_name}"] = value
            self.logger.info(f"Set app setting: {setting_name} = {value}")
            
        except Exception as e:
            self.logger.error(f"Error setting app setting: {e}")
    
    def get_app_setting(self, context, setting_name: str, default: Any = None) -> Any:
        """Get a global application setting."""
        try:
            return context.state.get(f"app:{setting_name}", default)
            
        except Exception as e:
            self.logger.error(f"Error getting app setting: {e}")
            return default
    
    def clear_temp_state(self, context) -> None:
        """Clear all temporary state."""
        try:
            temp_keys = [k for k in context.state.keys() if k.startswith("temp:")]
            for key in temp_keys:
                del context.state[key]
            
            self.logger.info("Cleared temporary state")
            
        except Exception as e:
            self.logger.error(f"Error clearing temp state: {e}")


# Global state manager instance
state_manager = FullstackStateManager()


def inject_state_templates(agent_instructions: str, context = None) -> str:
    """Inject state values into agent instructions using {state_key} syntax."""
    try:
        if not context:
            return agent_instructions
        
        # Replace {state_key} patterns with actual values
        result = agent_instructions
        
        # Find all {key} patterns in the instructions
        import re
        state_pattern = r'\{([^}]+)\}'
        
        def replace_state_match(match):
            key = match.group(1)
            # Handle optional keys with ?
            optional = key.endswith('?')
            if optional:
                key = key[:-1]
            
            value = context.state.get(key, "")
            
            # If optional and value is empty, remove the whole pattern
            if optional and not value:
                return ""
            
            return str(value)
        
        result = re.sub(state_pattern, replace_state_match, result)
        
        return result
        
    except Exception as e:
        logging.error(f"Error injecting state templates: {e}")
        return agent_instructions


class StateAwareAgentMixin:
    """Mixin class to add state management capabilities to agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_manager = state_manager
    
    def get_state_context(self, agent_type: str = "general") -> Dict[str, Any]:
        """Get relevant context from state for this agent."""
        try:
            # This would be called with the actual context during execution
            # For now, return template structure
            return {
                "agent_type": agent_type,
                "has_state_context": True
            }
            
        except Exception as e:
            logging.error(f"Error getting state context: {e}")
            return {}
    
    def update_progress(self, step: str, status: str = "completed") -> Dict[str, Any]:
        """Update task progress (would be called with actual context)."""
        # Template method - actual implementation would use real context
        return {
            "step": step,
            "status": status,
            "message": f"Progress updated: {step} ({status})"
        }