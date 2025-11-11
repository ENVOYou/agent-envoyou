"""
Multi-Provider Fullstack Agent System using Google ADK

This package provides a comprehensive multi-agent system for fullstack development
including frontend and backend specialization with modern SaaS standards.

Modules:
- agent: Main agent configuration and creation logic
- FullstackManagerAgent: Root coordinator agent
- Frontend Team: Writer, Reviewer, and Refactorer agents
- Backend Team: Writer, Reviewer, and Refactorer agents
"""

from .agent import root_agent

__version__ = "2.0.0"
__author__ = "Envoyou"  
__email__ = "hello@envoyou.com" 
__license__ = "Apache 2.0"
__copyright__ = f"Copyright 2025 {__author__}"

__all__ = [
    "root_agent"
]