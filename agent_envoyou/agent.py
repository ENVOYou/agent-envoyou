#!/usr/bin/env python3
"""
Multi-Provider Fullstack Multi-Agent System using Google ADK

This agent orchestrates a team of specialized agents for frontend and backend development:
- Root Agent: FullstackManagerAgent (coordinates overall project)
- Frontend Team: FrontendWriterAgent, FrontendReviewerAgent, FrontendRefactorerAgent
- Backend Team: BackendWriterAgent, BackendReviewerAgent, BackendRefactorerAgent

Technologies:
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: FastAPI/Node.js + PostgreSQL + Redis + Modern APIs
- Framework: Google ADK for multi-agent coordination
- AI Providers: Google, OpenAI, Anthropic, xAI, OpenRouter, Ollama
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent

# Import our multi-provider manager
from provider_manager import (
    provider_manager,
    get_optimal_model,
    get_best_available_provider,
    get_model_config,
    is_provider_fallback_enabled,
    get_demo_or_real_model,
    is_demo_mode
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_providers():
    """Initialize and test AI providers."""
    logger.info("🚀 Initializing Multi-Provider AI System...")
    
    # Test available providers
    available_providers = provider_manager.get_available_providers()
    logger.info(f"📋 Found {len(available_providers)} configured providers:")
    
    for provider in available_providers:
        if provider_manager.test_provider(provider):
            logger.info(f"   ✅ {provider.name} - Available")
        else:
            logger.warning(f"   ❌ {provider.name} - Unavailable")
    
    # Get best provider
    best_provider = get_best_available_provider()
    if best_provider:
        logger.info(f"🎯 Primary Provider: {best_provider.name}")
    else:
        logger.error("❌ No available providers found!")
        return False
    
    return True

def get_optimal_model_for_agent(agent_name: str, complexity: str = "medium") -> str:
    """Get optimal model for a specific agent."""
    
    # Agent-specific complexity mappings
    complexity_mapping = {
        "FrontendWriterAgent": "high",      # Complex UI development
        "FrontendReviewerAgent": "medium",  # Code review
        "FrontendRefactorAgent": "medium",  # Code refactoring
        "BackendWriterAgent": "high",       # Complex backend architecture
        "BackendReviewerAgent": "medium",   # Code review
        "BackendRefactorAgent": "medium",   # Code refactoring
        "FullstackManagerAgent": "high"     # High-level coordination
    }
    
    # Use specific complexity if provided, otherwise use default
    if complexity == "medium":
        agent_complexity = complexity_mapping.get(agent_name, "medium")
    else:
        agent_complexity = complexity
    
    # Use demo or real model based on available providers
    return get_demo_or_real_model(agent_name, agent_complexity)

def load_agent_config(config_path: str) -> Dict[str, Any]:
    """Load agent configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_agent_from_config(config_path: str) -> BaseAgent:
    """Create an agent from YAML configuration file."""
    config = load_agent_config(config_path)
    
    # Extract configuration values
    name = config.get('name', 'UnnamedAgent')
    agent_class = config.get('agent_class', 'LlmAgent')
    description = config.get('description', '')
    
    # Handle instruction which might be a multiline string
    instruction = config.get('instruction', '')
    if isinstance(instruction, list):
        instruction = '\n'.join(instruction)
    
    # Get optimal model for this agent
    model = get_optimal_model_for_agent(name)
    
    # Create the agent based on class type
    if agent_class == 'LlmAgent':
        agent = LlmAgent(
            name=name,
            model=model,
            description=description,
            instruction=instruction
        )
        
        # Add sub-agents if they exist
        sub_agents_config = config.get('sub_agents', [])
        if sub_agents_config:
            sub_agents = []
            for sub_agent_config in sub_agents_config:
                config_path = sub_agent_config.get('config_path')
                if config_path:
                    sub_agent = create_agent_from_config(config_path)
                    sub_agents.append(sub_agent)
            agent.sub_agents = sub_agents
            
        return agent
    elif agent_class == 'SequentialAgent':
        agent = SequentialAgent(
            name=name,
            description=description
        )
        
        # Add sub-agents for SequentialAgent
        sub_agents_config = config.get('sub_agents', [])
        if sub_agents_config:
            sub_agents = []
            for sub_agent_config in sub_agents_config:
                config_path = sub_agent_config.get('config_path')
                if config_path:
                    sub_agent = create_agent_from_config(config_path)
                    sub_agents.append(sub_agent)
            agent.sub_agents = sub_agents
            
        return agent
    else:
        raise ValueError(f"Unsupported agent class: {agent_class}")

def load_frontend_agents() -> List[BaseAgent]:
    """Load frontend sub-agents from their configuration files."""
    frontend_agents = []
    
    # Load frontend sub-agents
    frontend_configs = [
        'agent_envoyou/frontend_agent/sub_agent/FrontendWriterAgent.yaml',
        'agent_envoyou/frontend_agent/sub_agent/FrontendReviewerAgent.yaml',
        'agent_envoyou/frontend_agent/sub_agent/FrontendRefactorAgent.yaml'
    ]
    
    for config_path in frontend_configs:
        if os.path.exists(config_path):
            agent = create_agent_from_config(config_path)
            frontend_agents.append(agent)
        else:
            logger.warning(f"Configuration file not found: {config_path}")
    
    return frontend_agents

def load_backend_agents() -> List[BaseAgent]:
    """Load backend sub-agents from their configuration files."""
    backend_agents = []
    
    # Load backend sub-agents
    backend_configs = [
        'agent_envoyou/backend_agent/sub_agent/BackendWriterAgent.yaml',
        'agent_envoyou/backend_agent/sub_agent/BackendReviewerAgent.yaml',
        'agent_envoyou/backend_agent/sub_agent/BackendRefactorAgent.yaml'
    ]
    
    for config_path in backend_configs:
        if os.path.exists(config_path):
            agent = create_agent_from_config(config_path)
            backend_agents.append(agent)
        else:
            logger.warning(f"Configuration file not found: {config_path}")
    
    return backend_agents

def create_fullstack_agent() -> BaseAgent:
    """Create the main fullstack agent with all sub-agents."""
    try:
        # Initialize providers first
        if not initialize_providers():
            logger.error("❌ Failed to initialize providers")
            raise Exception("Provider initialization failed")
        
        # Load the root agent configuration
        root_config = load_agent_config('root_agent.yaml')
        
        # Extract root agent details
        name = root_config.get('name', 'FullstackManagerAgent')
        description = root_config.get('description', 'Project manager for fullstack development')
        
        # Handle instruction which might be a multiline string
        instruction = root_config.get('instruction', '')
        if isinstance(instruction, list):
            instruction = '\n'.join(instruction)
        
        # Get optimal model for root agent (high complexity)
        root_model = get_optimal_model_for_agent(name, "high")
        
        # Create the root agent
        root_agent = LlmAgent(
            name=name,
            model=root_model,
            description=description,
            instruction=instruction
        )
        
        # Load frontend and backend agents
        frontend_agents = load_frontend_agents()
        backend_agents = load_backend_agents()
        
        # Combine all sub-agents
        all_sub_agents = frontend_agents + backend_agents
        
        # If root config has sub_agents, append our agents
        root_sub_agents = root_config.get('sub_agents', [])
        for sub_agent_config in root_sub_agents:
            config_path = sub_agent_config.get('config_path')
            if config_path and os.path.exists(config_path):
                sub_agent = create_agent_from_config(config_path)
                all_sub_agents.append(sub_agent)
        
        # Assign sub-agents to root agent
        root_agent.sub_agents = all_sub_agents
        
        logger.info(f"✅ Successfully created Fullstack Manager Agent with {len(all_sub_agents)} sub-agents:")
        logger.info(f"   🎨 Frontend Team: {len(frontend_agents)} agents")
        logger.info(f"   ⚙️  Backend Team: {len(backend_agents)} agents")
        
        return root_agent
        
    except FileNotFoundError as e:
        logger.error(f"❌ Error: Configuration file not found - {e}")
        logger.error("Please ensure all YAML configuration files exist:")
        logger.error("- root_agent.yaml")
        logger.error("- agent_envoyou/frontend_agent/sub_agent/*.yaml")
        logger.error("- agent_envoyou/backend_agent/sub_agent/*.yaml")
        raise
    except Exception as e:
        logger.error(f"❌ Error creating agent: {e}")
        raise

# Create the main agent instance
try:
    root_agent = create_fullstack_agent()
    logger.info(f"🚀 Fullstack Multi-Agent System ready!")
    logger.info(f"   Agent Name: {root_agent.name}")
    logger.info(f"   Model: {root_agent.model}")
    logger.info(f"   Description: {root_agent.description}")
    
except Exception as e:
    logger.error(f"❌ Failed to initialize agents: {e}")
    exit(1)

# Export the main agent for ADK
__all__ = ['root_agent']