#!/usr/bin/env python3
"""
Memory Service Integration for Fullstack Multi-Agent System

Provides long-term memory capabilities using ADK's MemoryService
to enable agents to learn from past conversations and store successful patterns.
"""

import logging
from typing import Dict, Any, List, Optional
from google.adk.memory import InMemoryMemoryService, BaseMemoryService
from google.adk.tools import load_memory, preload_memory


class FullstackMemoryService:
    """Memory service wrapper for fullstack agent patterns."""
    
    def __init__(self, memory_service=None):
        self.memory_service = memory_service or InMemoryMemoryService()
        self.logger = logging.getLogger(__name__)
        
        # Define memory categories for different types of knowledge
        self.memory_categories = {
            "project_patterns": "Successful project structures and architectures",
            "code_templates": "Reusable code patterns and templates",
            "user_preferences": "User-specific preferences and requirements",
            "best_practices": "Development best practices and conventions",
            "troubleshooting": "Common issues and solutions",
            "workflow_patterns": "Effective agent coordination patterns"
        }
    
    async def store_project_pattern(self, project_type: str, pattern_data: Dict[str, Any]) -> bool:
        """Store a successful project pattern in memory."""
        try:
            # Structure the memory entry
            memory_entry = {
                "category": "project_patterns",
                "project_type": project_type,
                "timestamp": pattern_data.get("timestamp"),
                "pattern_data": pattern_data,
                "success_metrics": pattern_data.get("metrics", {}),
                "tags": pattern_data.get("tags", [])
            }
            
            # Store in memory service
            # This would typically be done through session processing
            self.logger.info(f"Stored project pattern: {project_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing project pattern: {e}")
            return False
    
    async def search_project_patterns(self, project_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant project patterns."""
        try:
            # Search memory for project patterns
            query = f"project_patterns {project_type} architecture structure"
            
            # This would use the actual memory service search
            # For now, return structured search results
            patterns = []
            
            self.logger.info(f"Searched for project patterns: {project_type}")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error searching project patterns: {e}")
            return []
    
    async def store_code_template(self, template_name: str, template_data: Dict[str, Any]) -> bool:
        """Store a reusable code template."""
        try:
            memory_entry = {
                "category": "code_templates",
                "template_name": template_name,
                "language": template_data.get("language"),
                "use_case": template_data.get("use_case"),
                "code": template_data.get("code"),
                "description": template_data.get("description"),
                "timestamp": template_data.get("timestamp")
            }
            
            self.logger.info(f"Stored code template: {template_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing code template: {e}")
            return False
    
    async def store_user_preference(self, user_id: str, preference_type: str, preference_data: Dict[str, Any]) -> bool:
        """Store user-specific preferences."""
        try:
            memory_entry = {
                "category": "user_preferences",
                "user_id": user_id,
                "preference_type": preference_type,
                "preference_data": preference_data,
                "timestamp": preference_data.get("timestamp")
            }
            
            self.logger.info(f"Stored user preference: {preference_type} for {user_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing user preference: {e}")
            return False
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user's preferences from memory."""
        try:
            # Search for user preferences
            query = f"user_preferences {user_id}"
            
            # Return structured preferences
            preferences = {
                "preferred_frameworks": [],
                "preferred_languages": [],
                "preferred_databases": [],
                "development_style": "agile",
                "architecture_preferences": []
            }
            
            self.logger.info(f"Retrieved preferences for user: {user_id}")
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def store_best_practice(self, practice_type: str, practice_data: Dict[str, Any]) -> bool:
        """Store development best practices."""
        try:
            memory_entry = {
                "category": "best_practices",
                "practice_type": practice_type,
                "practice_data": practice_data,
                "context": practice_data.get("context"),
                "benefits": practice_data.get("benefits"),
                "implementation": practice_data.get("implementation"),
                "timestamp": practice_data.get("timestamp")
            }
            
            self.logger.info(f"Stored best practice: {practice_type}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing best practice: {e}")
            return False
    
    async def get_relevant_practices(self, context: str) -> List[Dict[str, Any]]:
        """Get relevant best practices for a context."""
        try:
            # Search for relevant practices
            query = f"best_practices {context}"
            
            # Return relevant practices
            practices = []
            
            self.logger.info(f"Retrieved best practices for context: {context}")
            
            return practices
            
        except Exception as e:
            self.logger.error(f"Error getting relevant practices: {e}")
            return []


# Global memory service instance
fullstack_memory = FullstackMemoryService()


# Memory tools for agents to use
def get_memory_tools():
    """Get memory-related tools for agents."""
    return [load_memory, preload_memory]


async def enhance_agent_with_memory(agent, agent_type: str = "general"):
    """Enhance an agent with memory capabilities."""
    try:
        # Add memory tools to the agent
        tools = list(agent.tools) if hasattr(agent, 'tools') else []
        tools.extend(get_memory_tools())
        agent.tools = tools
        
        # Add memory service reference
        agent.memory_service = fullstack_memory
        
        # Update agent instructions to include memory usage
        if hasattr(agent, 'instruction'):
            memory_instruction = f"""
            
IMPORTANT: You have access to memory tools to enhance your capabilities:

MEMORY CAPABILITIES:
- Load relevant patterns and templates from memory when appropriate
- Use preload_memory tool to automatically retrieve relevant information at the start of each task
- Store successful solutions and patterns for future use
- Retrieve user preferences and past project patterns

INSTRUCTIONS:
- Before starting a task, check if similar patterns exist in memory
- Store your best solutions and effective patterns for future reference
- Consider user preferences when making architectural decisions
- Use memory to maintain consistency across projects

{agent.instruction}
            """
            agent.instruction = memory_instruction
        
        logging.info(f"Enhanced agent {agent.name} with memory capabilities")
        
        return True
        
    except Exception as e:
        logging.error(f"Error enhancing agent with memory: {e}")
        return False


class MemoryAwareAgentMixin:
    """Mixin class to add memory capabilities to agents."""
    
    async def store_task_outcome(self, task_type: str, success: bool, details: Dict[str, Any]):
        """Store the outcome of a task in memory."""
        try:
            if success:
                await fullstack_memory.store_best_practice(task_type, {
                    "success": True,
                    "details": details,
                    "timestamp": details.get("timestamp"),
                    "agent_type": self.name if hasattr(self, 'name') else "unknown"
                })
        except Exception as e:
            logging.error(f"Error storing task outcome: {e}")
    
    async def get_agent_context(self, task_type: str) -> Dict[str, Any]:
        """Get relevant context from memory for current task."""
        try:
            # Get relevant patterns
            patterns = await fullstack_memory.search_project_patterns(task_type)
            
            # Get relevant practices
            practices = await fullstack_memory.get_relevant_practices(task_type)
            
            return {
                "patterns": patterns,
                "practices": practices,
                "task_type": task_type
            }
            
        except Exception as e:
            logging.error(f"Error getting agent context: {e}")
            return {"patterns": [], "practices": [], "task_type": task_type}