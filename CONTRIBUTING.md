# 🤝 Contributing to Agent Envoyou

Thank you for your interest in contributing to Agent Envoyou! We welcome contributions from developers of all skill levels and backgrounds.

## 🎯 **Quick Start for Contributors**

### **Prerequisites**
- Python 3.9 or higher
- Git for version control
- Basic understanding of AI/machine learning concepts
- Familiarity with YAML configuration

### **Development Setup (2 minutes)**
```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/agent-envoyou.git
cd agent-envoyou

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install google-adk pyyaml requests

# 4. Test the setup
python -c "from agent import root_agent; print('✅ Development environment ready!')"
```

## 🚀 **Types of Contributions**

### **🐛 Bug Reports**
Help us identify and fix issues:

#### **Before Reporting**
- [ ] Check existing issues to avoid duplicates
- [ ] Test with demo mode (no API keys required)
- [ ] Verify the issue is not configuration-related

#### **Report Template**
```markdown
**Bug Description**
A clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- Python version: 
- OS: 
- Provider: Demo/Real
- Agent: (if specific)

**Additional Context**
Logs, screenshots, or other helpful information
```

### **✨ Feature Requests**
Suggest new features and improvements:

#### **Feature Request Template**
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature useful? Who would benefit?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Screenshots, examples, or mockups
```

### **📝 Code Contributions**
Help improve the codebase:

#### **Areas Where Help is Needed**
- 🎨 **UI/UX Improvements**: Better user interfaces, documentation
- 🧠 **AI Provider Integration**: New providers, model optimizations
- 🏗️ **Architecture**: Performance improvements, scalability
- 🧪 **Testing**: Unit tests, integration tests, end-to-end tests
- 📚 **Documentation**: Guides, examples, tutorials

## 🏗️ **Development Workflow**

### **Branch Strategy**
```bash
# Main branches
main              # Production-ready code
develop          # Integration branch for features

# Feature branches
feature/agent-optimization
feature/new-provider-integration
fix/provider-fallback-issue
docs/improve-setup-guide
```

### **Development Process**

#### **1. Start a Feature Branch**
```bash
# For new features
git checkout -b feature/your-feature-name

# For bug fixes
git checkout -b fix/issue-description

# For documentation
git checkout -b docs/your-docs-update
```

#### **2. Development Guidelines**
```bash
# Code quality
- Follow PEP 8 style guidelines
- Use type hints in all functions
- Write docstrings for all public methods
- Keep functions focused and single-purpose

# Testing
- Test your changes in both demo and real provider modes
- Run provider connectivity tests
- Verify agent loading and execution
- Check error handling and edge cases

# Commit messages
git commit -m "feat: add smart model selection for frontend agents"
git commit -m "fix: resolve provider fallback timeout issue"
git commit -m "docs: update provider setup guide with xAI examples"
```

#### **3. Testing Your Changes**

```bash
# Test the complete system
python -c "
from agent import root_agent
from provider_manager import get_provider_status
print('✅ System loads correctly')
print('Provider status:', get_provider_status())
"

# Test specific agent workflows
python -c "
from agent import load_frontend_agents, load_backend_agents
frontend = load_frontend_agents()
backend = load_backend_agents()
print(f'Frontend agents: {len(frontend)}')
print(f'Backend agents: {len(backend)}')
"

# Test provider integration
python -c "
from provider_manager import provider_manager
for provider in provider_manager.get_available_providers():
    status = '✅' if provider_manager.test_provider(provider) else '❌'
    print(f'{status} {provider.name}')
"
```

#### **4. Submit Pull Request**

```bash
# Push your changes
git push origin feature/your-feature-name

# Create PR with description
# Include:
# - What you changed
# - Why you changed it
# - How to test it
# - Screenshots/examples if applicable
```

## 🎨 **Coding Standards**

### **Python Code Style**
```python
# Good: Clear function names with type hints
def get_optimal_model_for_agent(
    agent_name: str, 
    complexity: str = "medium"
) -> str:
    """Get optimal model for a specific agent based on complexity."""
    pass

# Good: Comprehensive docstrings
def create_agent_from_config(config_path: str) -> BaseAgent:
    """
    Create an agent from YAML configuration file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        BaseAgent: Configured agent instance
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        ValueError: If configuration is invalid
        
    Example:
        >>> agent = create_agent_from_config('frontend_agent/root.yaml')
        >>> print(agent.name)
        'FrontendTeamAgent'
    """
    pass
```

### **YAML Configuration**
```yaml
# Good: Clear, well-documented configuration
agent_class: LlmAgent
name: CustomAgent
description: "Custom agent for specific tasks"
instruction: |
  You are a specialized agent with focused capabilities.
  
  Guidelines:
  - Use modern best practices
  - Prioritize security and performance
  - Provide comprehensive error handling

# Model selection (let system choose optimal model)
model: auto  # System will select best available model
```

### **Error Handling**
```python
# Good: Comprehensive error handling
try:
    provider = provider_manager.get_provider()
    if not provider:
        logger.warning("No providers available, using demo mode")
        return get_demo_model(agent_name)
        
    if provider_manager.test_provider(provider):
        return provider_manager.get_model_for_task(agent_name, complexity)
    else:
        logger.warning(f"Provider {provider.name} unavailable")
        return get_fallback_model()
        
except Exception as e:
    logger.error(f"Error getting optimal model: {e}")
    return "demo-model"  # Safe fallback
```

## 🧪 **Testing Guidelines**

### **Unit Testing**
```python
# Example test structure
import pytest
from provider_manager import get_optimal_model, ProviderManager

class TestProviderManager:
    def test_optimal_model_selection(self):
        model = get_optimal_model("FrontendWriterAgent", "high")
        assert model in ["gpt-4o", "claude-3-5-sonnet"]
        
    def test_demo_mode_fallback(self):
        manager = ProviderManager()
        manager.demo_mode = True
        models = manager.get_demo_models()
        assert "FrontendWriterAgent" in models
        assert "demo" in models["FrontendWriterAgent"].lower()
```

### **Integration Testing**
```python
# Test agent loading
def test_agent_loading():
    from agent import load_frontend_agents, load_backend_agents
    
    frontend_agents = load_frontend_agents()
    backend_agents = load_backend_agents()
    
    assert len(frontend_agents) == 3
    assert len(backend_agents) == 3
    assert all(agent.name.endswith('Agent') for agent in frontend_agents)
```

### **Manual Testing Checklist**
```bash
# Before submitting PR, test:
- [ ] System loads without errors in demo mode
- [ ] All agents are properly configured
- [ ] Provider connectivity works
- [ ] Error messages are clear and helpful
- [ ] Documentation is accurate
- [ ] Code follows style guidelines
```

## 📚 **Documentation Contributions**

### **Types of Documentation**
- **Setup Guides**: Installation, configuration, troubleshooting
- **API Documentation**: Function references, examples
- **Tutorials**: Step-by-step guides for common use cases
- **Best Practices**: Design patterns, optimization tips
- **Provider Guides**: Specific setup for each AI provider

### **Documentation Style**
```markdown
# Use clear, actionable headings

## Getting Started
Quick setup for new users

### For Demo Mode
No API keys required - instant start

### For Production
Real provider setup with best practices

## Common Issues
Solutions to frequently encountered problems

### Provider Connection Issues
Troubleshooting guide for each provider

### Agent Configuration
How to customize agent behavior
```

## 🔧 **Special Contribution Areas**

### **AI Provider Integration**
Adding new AI providers:

```python
# 1. Add provider to enum
class AIProvider(Enum):
    NEW_PROVIDER = "NEW_PROVIDER"

# 2. Add configuration
def _load_new_provider(self):
    new_key = os.getenv('NEW_PROVIDER_API_KEY')
    if new_key:
        self.providers[AIProvider.NEW_PROVIDER] = ProviderConfig(
            name="New Provider",
            api_key=new_key,
            base_url="https://api.newprovider.com/v1",
            headers={"Authorization": f"Bearer {new_key}"}
        )

# 3. Add model mapping
def get_new_provider_models(self):
    return ["new-model-1", "new-model-2", "new-model-3"]
```

### **Agent Development**
Creating new specialized agents:

```yaml
# 1. Create YAML configuration
agent_class: LlmAgent
name: DatabaseAgent
description: "Specialized agent for database design and optimization"
instruction: |
  You are a database specialist agent.
  
  Capabilities:
  - Design efficient database schemas
  - Optimize queries for performance
  - Implement proper indexing strategies
  - Ensure data integrity and consistency

# 2. Add to appropriate team
# Update agent_envoyou/backend_agent/root.yaml
sub_agents:
  - config_path: agent_envoyou/backend_agent/sub_agent/DatabaseAgent.yaml
```

### **Performance Optimization**
Improving system performance:

```python
# Caching example
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_model_for_task(task_type: str, complexity: str) -> str:
    """Cache frequently requested model selections."""
    return get_model_for_task(task_type, complexity)

# Provider pooling
class ProviderPool:
    def __init__(self):
        self.providers = {}
        self.active_providers = set()
        
    def get_healthy_provider(self):
        # Return least loaded healthy provider
        pass
```

## 🎯 **Review Process**

### **For Contributors**
- **Self-Review**: Check your code against our standards
- **Testing**: Verify works in demo and real provider modes
- **Documentation**: Update relevant docs
- **Changelog**: Note significant changes

### **For Maintainers**
- **Code Review**: Style, functionality, tests
- **Documentation**: Accuracy and completeness
- **Breaking Changes**: Proper migration guidance
- **Performance**: Impact on system performance

### **Review Checklist**
```markdown
**Code Quality**
- [ ] Follows PEP 8 style guidelines
- [ ] Includes proper type hints
- [ ] Has comprehensive docstrings
- [ ] Includes error handling
- [ ] Has appropriate tests

**Functionality**
- [ ] Works in demo mode
- [ ] Works with real providers
- [ ] Handles edge cases
- [ ] Provides useful error messages

**Documentation**
- [ ] Updated README if needed
- [ ] Added docstrings
- [ ] Updated relevant guides
- [ ] Examples work correctly

**Performance**
- [ ] No obvious performance issues
- [ ] Efficient resource usage
- [ ] Proper caching where applicable
```

## 🌟 **Recognition**

### **Contributor Levels**
- **🥉 Bronze**: First contribution
- **🥈 Silver**: 5+ quality contributions
- **🥇 Gold**: 15+ significant contributions
- **💎 Diamond**: 25+ major contributions

### **Hall of Fame**
Contributors who have made exceptional contributions:
- Bug fixes and improvements
- New provider integrations
- Documentation excellence
- Community support

## 📞 **Getting Help**

### **For Contributors**
- **GitHub Discussions**: General questions and ideas
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Check our comprehensive guides
- **Code Examples**: Browse the codebase for examples

### **Communication Guidelines**
- **Be Respectful**: Treat all contributors with courtesy
- **Be Constructive**: Provide helpful, actionable feedback
- **Be Patient**: Help newcomers learn and grow
- **Be Collaborative**: Work together toward shared goals

## 🎉 **Thank You!**

Every contribution, no matter how small, helps make Agent Envoyou better for everyone. Whether you're:

- 🐛 Fixing a typo in documentation
- 🐛 Reporting a bug you found
- ✨ Suggesting a new feature
- 💻 Writing code for a new provider
- 📚 Improving documentation
- 💬 Helping other users

**You are making a difference!** Thank you for being part of our community.

---

<div align="center">

### Ready to contribute? [Check our issues](https://github.com/ENVOYou/agent-envoyou/issues) for beginner-friendly tasks!

**Questions?** Join our [GitHub Discussions](https://github.com/ENVOYou/agent-envoyou/discussions) or email contributors@envoyou.com

</div>