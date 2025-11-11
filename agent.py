#!/usr/bin/env python3
"""
Fullstack Multi-Agent System using Google ADK

This agent orchestrates a team of specialized agents for frontend and backend development:
- Root Agent: FullstackManagerAgent (coordinates overall project)
- Frontend Team: FrontendWriterAgent, FrontendReviewerAgent, FrontendRefactorerAgent
- Backend Team: BackendWriterAgent, BackendReviewerAgent, BackendRefactorerAgent

Technologies:
- Frontend: React + TypeScript + Vite + Tailwind CSS
- Backend: FastAPI/Node.js + PostgreSQL + Redis + Modern APIs
- Framework: Google ADK for multi-agent coordination
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List
from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent

def load_agent_config(config_path: str) -> Dict[str, Any]:
    """Load agent configuration from YAML file."""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def create_agent_from_config(config_path: str) -> BaseAgent:
    """Create an agent from YAML configuration file."""
    config = load_agent_config(config_path)
    
    # Extract configuration values
    name = config.get('name', 'UnnamedAgent')
    model = config.get('model', 'gemini-2.5-flash')
    agent_class = config.get('agent_class', 'LlmAgent')
    description = config.get('description', '')
    
    # Handle instruction which might be a multiline string
    instruction = config.get('instruction', '')
    if isinstance(instruction, list):
        instruction = '\n'.join(instruction)
    
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
        'frontend_agent/sub_agent/FrontendWriterAgent.yaml',
        'frontend_agent/sub_agent/FrontendReviewerAgent.yaml',
        'frontend_agent/sub_agent/FrontendRefactorAgent.yaml'
    ]
    
    for config_path in frontend_configs:
        if os.path.exists(config_path):
            agent = create_agent_from_config(config_path)
            frontend_agents.append(agent)
        else:
            print(f"Warning: Configuration file not found: {config_path}")
    
    return frontend_agents

def load_backend_agents() -> List[BaseAgent]:
    """Load backend sub-agents from their configuration files."""
    backend_agents = []
    
    # Load backend sub-agents
    backend_configs = [
        'backend_agent/sub_agent/BackendWriterAgent.yaml',
        'backend_agent/sub_agent/BackendReviewerAgent.yaml',
        'backend_agent/sub_agent/BackendRefactorAgent.yaml'
    ]
    
    for config_path in backend_configs:
        if os.path.exists(config_path):
            agent = create_agent_from_config(config_path)
            backend_agents.append(agent)
        else:
            print(f"Warning: Configuration file not found: {config_path}")
    
    return backend_agents

def create_fullstack_agent() -> BaseAgent:
    """Create the main fullstack agent with all sub-agents."""
    try:
        # Load the root agent configuration
        root_config = load_agent_config('root_agent.yaml')
        
        # Extract root agent details
        name = root_config.get('name', 'FullstackManagerAgent')
        model = root_config.get('model', 'gemini-2.5-pro-latest')
        description = root_config.get('description', 'Project manager for fullstack development')
        
        # Handle instruction which might be a multiline string
        instruction = root_config.get('instruction', '')
        if isinstance(instruction, list):
            instruction = '\n'.join(instruction)
        
        # Create the root agent
        root_agent = LlmAgent(
            name=name,
            model=model,
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
        
        print(f"✅ Successfully created Fullstack Manager Agent with {len(all_sub_agents)} sub-agents:")
        print(f"   🎨 Frontend Team: {len(frontend_agents)} agents")
        print(f"   ⚙️  Backend Team: {len(backend_agents)} agents")
        
        return root_agent
        
    except FileNotFoundError as e:
        print(f"❌ Error: Configuration file not found - {e}")
        print("Please ensure all YAML configuration files exist:")
        print("- root_agent.yaml")
        print("- frontend_agent/sub_agent/*.yaml")
        print("- backend_agent/sub_agent/*.yaml")
        raise
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        raise

# Create the main agent instance
try:
    root_agent = create_fullstack_agent()
    print(f"🚀 Fullstack Multi-Agent System ready!")
    print(f"   Agent Name: {root_agent.name}")
    print(f"   Model: {root_agent.model}")
    print(f"   Description: {root_agent.description}")
    
except Exception as e:
    print(f"❌ Failed to initialize agents: {e}")
    exit(1)

# Export the main agent for ADK
__all__ = ['root_agent']