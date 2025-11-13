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

# Import ADK's built-in components
from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.adk.models.lite_llm import LiteLlm

# Import our enhanced tools
from agent_envoyou.tools import (
    FileSystemTool,
    CodeExecutorTool,
    GitManagerTool,
    DockerBuilderTool,
    PackageManagerTool
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model_for_provider(provider_name: str, complexity: str = "medium") -> str:
    """Get appropriate model string based on provider and complexity."""
    
    # Map provider to model strings (ADK native approach)
    provider_models = {
        "GOOGLE": {
            "complex": "gemini-2.5-pro",      # Complex tasks
            "simple": "gemini-2.5-flash",           # Simple/fast tasks
        },
        "OPENAI": {
            "complex": "openai/gpt-5",
            "simple": "openai/gpt-4",
        },
        "ANTHROPIC": {
            "complex": "anthropic/Opus 4.1",
            "simple": "anthropic/Sonnet 4.5",
        },
        "XAI": {
            "complex": "xai/grok-code-fast-1",
            "simple": "xai/grok-code-fast-1",
        },
        "OPENROUTER": {
            "complex": "openrouter/openai/gpt-4o",
            "simple": "openrouter/openai/gpt-4o-mini",
        }
    }
    
    # Get provider from environment
    env_provider = os.getenv("AI_PROVIDER", "GOOGLE").upper()
    
    # Get models for the provider
    models = provider_models.get(env_provider, provider_models["GOOGLE"])
    
    # Return appropriate model based on complexity
    return models.get(complexity, models["simple"])

def create_lite_llm_model(model_string: str):
    """Create LiteLlm wrapper for non-Gemini models."""
    return LiteLlm(model=model_string)

def get_agent_model(agent_name: str) -> str:
    """Get model string for specific agent type."""
    
    # Map agent types to complexity requirements
    agent_complexity = {
        "FullstackManagerAgent": "complex",
        "FrontendWriterAgent": "complex",       # Complex UI development
        "FrontendReviewerAgent": "simple",      # Code review (faster)
        "FrontendRefactorerAgent": "simple",    # Code refactoring (faster)
        "BackendWriterAgent": "complex",        # Complex backend architecture
        "BackendReviewerAgent": "simple",       # Code review (faster)
        "BackendRefactorerAgent": "simple",     # Code refactoring (faster)
    }
    
    complexity = agent_complexity.get(agent_name, "simple")
    return get_model_for_provider("", complexity)

def load_agent_config(config_path: str) -> Dict[str, Any]:
    """Load agent configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_agent_from_config(config_path: str) -> BaseAgent:
    """Create an agent from YAML configuration file following ADK patterns."""
    config = load_agent_config(config_path)
    
    # Extract configuration values
    name = config.get('name', 'UnnamedAgent')
    agent_class = config.get('agent_class', 'LlmAgent')
    description = config.get('description', '')
    
    # Handle instruction which might be a multiline string
    instruction = config.get('instruction', '')
    if isinstance(instruction, list):
        instruction = '\n'.join(instruction)
    
    # Get model for this agent
    model_string = config.get('model', 'auto')
    if model_string == 'auto':
        model_string = get_agent_model(name)
    
    # Create model wrapper if needed (for non-Gemini models)
    model = model_string
    if not model_string.startswith("gemini"):
        model = create_lite_llm_model(model_string)
    
    # Get tools configuration
    tools_config = config.get('tools', [])
    tools = []
    
    # Add appropriate tools based on agent type and config
    if 'file_system' in tools_config or name in ['FrontendWriterAgent', 'BackendWriterAgent', 'FullstackManagerAgent']:
        tools.append(FileSystemTool())
    
    if 'code_executor' in tools_config or name in ['FrontendReviewerAgent', 'BackendReviewerAgent', 'FrontendRefactorerAgent', 'BackendRefactorerAgent']:
        tools.append(CodeExecutorTool())
    
    if 'git_manager' in tools_config or name in ['FrontendWriterAgent', 'BackendWriterAgent', 'FullstackManagerAgent']:
        tools.append(GitManagerTool())
    
    # Add memory tools for all agents
    tools.extend([load_memory, preload_memory])
    
    # Create the agent based on class type
    if agent_class == 'LlmAgent':
        agent = LlmAgent(
            name=name,
            model=model,  # Pass model directly (string for Gemini, LiteLlm wrapper for others)
            description=description,
            instruction=instruction,
            tools=tools
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

def create_fullstack_agent() -> BaseAgent:
    """Create the main fullstack agent following ADK patterns."""
    try:
        # Load the root agent configuration
        root_config = load_agent_config('agent_envoyou/root_agent.yaml')
        
        # Extract root agent details
        name = root_config.get('name', 'FullstackManagerAgent')
        description = root_config.get('description', 'Project manager for fullstack development')
        
        # Handle instruction which might be a multiline string
        instruction = root_config.get('instruction', '')
        if isinstance(instruction, list):
            instruction = '\n'.join(instruction)
        
        # Get model for root agent (complex)
        root_model_string = get_agent_model(name)
        root_model = root_model_string
        if not root_model_string.startswith("gemini"):
            root_model = create_lite_llm_model(root_model_string)
        
        # Create the root agent following ADK patterns
        root_agent = LlmAgent(
            name=name,
            model=root_model,
            description=description,
            instruction=instruction
        )
        
        # Load frontend and backend agents
        frontend_agents = load_frontend_agents()
        backend_agents = load_backend_agents()
        
        # Assign sub-agents to root agent
        all_sub_agents = frontend_agents + backend_agents
        root_agent.sub_agents = all_sub_agents
        
        logger.info(f"✅ Successfully created Fullstack Manager Agent with {len(all_sub_agents)} sub-agents:")
        logger.info(f"   🎨 Frontend Team: {len(frontend_agents)} agents")
        logger.info(f"   ⚙️  Backend Team: {len(backend_agents)} agents")
        
        return root_agent
        
    except FileNotFoundError as e:
        logger.error(f"❌ Error: Configuration file not found - {e}")
        logger.error("Please ensure all YAML configuration files exist:")
        logger.error("- agent_envoyou/root_agent.yaml")
        logger.error("- agent_envoyou/frontend_agent/sub_agent/*.yaml")
        logger.error("- agent_envoyou/backend_agent/sub_agent/*.yaml")
        raise
    except Exception as e:
        logger.error(f"❌ Error creating agent: {e}")
        raise

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

# Create the main agent instance following ADK patterns
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