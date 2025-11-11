# Fullstack Multi-Agent System

A sophisticated multi-agent orchestration system built with Google ADK for coordinating specialized agents in frontend and backend development.

## 🚀 Overview

This project implements a hierarchical multi-agent system that coordinates specialized AI agents for fullstack development tasks. The system features a root agent that delegates work to frontend and backend teams, ensuring efficient and high-quality software development.

## ✨ Features

### 🤖 Agent Architecture
- **Root Agent**: `FullstackManagerAgent` - Coordinates overall project execution
- **Frontend Team**: Specialized agents for UI development, reviewing, and refactoring
- **Backend Team**: Specialized agents for API development, reviewing, and refactoring
- **Hierarchical Coordination**: Multi-level agent delegation and workflow management

### 🛠️ Technology Stack
- **Framework**: Google ADK (Agent Development Kit)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI/Node.js + PostgreSQL + Redis + Modern APIs
- **Agent Models**: Gemini-2.5-Pro-Latest, Gemini-2.5-Flash
- **Configuration**: YAML-based agent configuration
- **Language**: Python 3.x

## 🏗️ Project Structure

```
agent-envoyou/
├── agent.py                          # Main orchestrator script
├── root_agent.yaml                   # Root agent configuration
├── backend_agent/
│   ├── root.yaml                     # Backend team configuration
│   └── sub_agent/
│       ├── BackendWriterAgent.yaml   # Backend code generation
│       ├── BackendReviewerAgent.yaml # Backend code review
│       └── BackendRefactorAgent.yaml # Backend code refactoring
├── frontend_agent/
│   ├── root.yaml                     # Frontend team configuration
│   └── sub_agent/
│       ├── FrontendWriterAgent.yaml  # Frontend code generation
│       ├── FrontendReviewerAgent.yaml # Frontend code review
│       └── FrontendRefactorAgent.yaml # Frontend code refactoring
├── __init__.py                       # Package initialization
└── .gitignore                        # Git ignore rules
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Google ADK framework
- Required Python packages (install via requirements.txt)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agent-envoyou
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the system**
   ```bash
   python agent.py
   ```

## 💻 Usage

### Running Individual Agents

```python
from agent import create_agent_from_config

# Load a specific agent configuration
agent = create_agent_from_config('frontend_agent/sub_agent/FrontendWriterAgent.yaml')

# Run agent tasks
result = agent.run("Create a modern React component for user authentication")
```

### Running the Fullstack Manager

```python
from agent import root_agent

# The main orchestrator agent is automatically initialized
print(f"Agent: {root_agent.name}")
print(f"Model: {root_agent.model}")

# Delegate tasks through the root agent
result = root_agent.run("Build a complete e-commerce application with user authentication")
```

## 🔧 Configuration

### Agent Configuration (YAML)

Agents are configured using YAML files with the following structure:

```yaml
agent_class: LlmAgent        # Agent type: LlmAgent, SequentialAgent
model: gemini-2.5-flash     # AI model to use
name: AgentName              # Agent identifier
description: "Agent purpose" # Human-readable description
instruction: |               # Agent instructions
  Detailed agent instructions...
sub_agents:                  # Sub-agents for SequentialAgent
  - config_path: path/to/subagent.yaml
```

### Available Agent Classes

- **LlmAgent**: Language model-based agent for single-purpose tasks
- **SequentialAgent**: Orchestrates multiple sub-agents in sequence

### Supported Models

- `gemini-2.5-pro-latest`: For complex reasoning and planning
- `gemini-2.5-flash`: For fast, efficient tasks
- Other models supported by Google ADK

## 🏭 Workflow

### Development Workflow

1. **Project Analysis**: Root agent analyzes requirements and scope
2. **Task Delegation**: Tasks are assigned to appropriate frontend/backend teams
3. **Sequential Processing**: Each team executes write → review → refactor cycle
4. **Integration**: Components are integrated and tested
5. **Quality Assurance**: Final review and validation
6. **Delivery**: Complete solution with documentation

### Agent Coordination

```
Root Agent (FullstackManagerAgent)
├── Frontend Team (SequentialAgent)
│   ├── FrontendWriterAgent
│   ├── FrontendReviewerAgent
│   └── FrontendRefactorAgent
└── Backend Team (SequentialAgent)
    ├── BackendWriterAgent
    ├── BackendReviewerAgent
    └── BackendRefactorAgent
```

## 🧪 Testing

Run the test suite to ensure system integrity:

```bash
# Run all tests
python -m pytest tests/

# Run specific agent tests
python -m pytest tests/test_agents.py

# Run integration tests
python -m pytest tests/test_integration.py
```

## 📋 API Reference

### Core Functions

#### `create_agent_from_config(config_path: str) -> BaseAgent`
Creates an agent instance from YAML configuration.

**Parameters:**
- `config_path`: Path to the YAML configuration file

**Returns:**
- `BaseAgent`: Configured agent instance

#### `load_frontend_agents() -> List[BaseAgent]`
Loads all frontend sub-agents from configuration files.

**Returns:**
- `List[BaseAgent]`: List of configured frontend agents

#### `load_backend_agents() -> List[BaseAgent]`
Loads all backend sub-agents from configuration files.

**Returns:**
- `List[BaseAgent]`: List of configured backend agents

#### `create_fullstack_agent() -> BaseAgent`
Creates the main fullstack agent with all sub-agents.

**Returns:**
- `BaseAgent`: Root agent with configured sub-agents

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `python -m pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 for Python code
- Use type hints in all function signatures
- Write comprehensive docstrings
- Add tests for new functionality
- Update documentation as needed

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code documentation
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions in GitHub Discussions

## 🎯 Roadmap

- [ ] Enhanced error handling and recovery mechanisms
- [ ] Support for additional AI models and providers
- [ ] Web-based dashboard for agent monitoring
- [ ] Plugin system for custom agent extensions
- [ ] Integration with CI/CD pipelines
- [ ] Performance monitoring and analytics

## 📊 Project Status

This project is currently in active development. The core agent orchestration system is functional, and we're working on expanding agent capabilities and improving system reliability.

---

**Built with ❤️ using Google ADK and modern AI technologies**