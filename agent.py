#!/usr/bin/env python3
"""
Agent Envoyou - Root Level Agent Entry Point

This is a simple wrapper that imports the main agent from the agent_envoyou package.
When running 'adk web .', ADK looks for agent files at the root level.
"""

# Import the root agent from our organized package structure
from agent_envoyou.agent import root_agent

# Export for ADK
__all__ = ['root_agent']