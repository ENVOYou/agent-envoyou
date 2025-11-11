# 🔧 Development Guide

This guide covers everything you need to know about developing, testing, and deploying Agent Envoyou.

## 🎯 **Development Environment Setup**

### **Complete Setup (Recommended)**
```bash
# 1. Clone and setup
git clone https://github.com/ENVOYou/agent-envoyou.git
cd agent-envoyou

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install google-adk pyyaml requests typing-extensions

# 4. Test everything works
python -c "
from agent import root_agent
from provider_manager import get_provider_status
print('✅ Development environment ready!')
print('Agent:', root_agent.name)
print('Providers:', list(get_provider_status().keys()))
"
```

### **IDE Configuration**

#### **VS Code Setup**
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

#### **PyCharm Setup**
```python
# Interpreter: .venv/bin/python
# Code style: Black formatter
# Linting: flake8 + mypy
# Testing: pytest
```

## 🏗️ **Architecture Overview**

### **System Components**
```
Agent Envoyou System
├── 📊 Provider Manager (provider_manager.py)
│   ├── Multi-provider support
│   ├── Smart model selection
│   ├── Cost optimization
│   └── Fallback mechanisms
├── 🎯 Agent Orchestrator (agent.py)
│   ├── YAML configuration loading
│   ├── Agent creation and management
│   ├── Workflow coordination
│   └── Error handling
├── 📁 Agent Configurations
│   ├── agent_envoyou/frontend_agent/
│   │   └── sub_agent/ (Writer/Reviewer/Refactor)
│   └── agent_envoyou/backend_agent/
│       └── sub_agent/ (Writer/Reviewer/Refactor)
└── 🔧 Core Services
    ├── Model selection algorithms
    ├── Provider connectivity testing
    ├── Performance monitoring
    └── Cost tracking
```

### **Data Flow**
```
User Request
    ↓
Root Agent (FullstackManagerAgent)
    ↓
Task Analysis & Delegation
    ↓
Frontend Team OR Backend Team
    ↓
Sequential Processing
    ↓
Writer → Reviewer → Refactorer
    ↓
Quality Assurance & Integration
    ↓
Final Output
```

## 🧪 **Testing Strategy**

### **Unit Tests**
```python
# tests/test_provider_manager.py
import pytest
from provider_manager import ProviderManager, get_optimal_model

def test_provider_loading():
    manager = ProviderManager()
    assert len(manager.get_available_providers()) >= 5  # Demo providers

def test_model_selection():
    model = get_optimal_model("FrontendWriterAgent", "high")
    assert model in ["gpt-4o", "claude-3-5-sonnet"]
```

### **Integration Tests**
```python
# tests/test_agent_loading.py
from agent import load_frontend_agents, load_backend_agents, root_agent

def test_agent_loading():
    frontend = load_frontend_agents()
    backend = load_backend_agents()
    
    assert len(frontend) == 3
    assert len(backend) == 3
    assert root_agent is not None

def test_agent_configuration():
    # Test that all agents have proper configurations
    agents = load_frontend_agents() + load_backend_agents()
    for agent in agents:
        assert agent.name.endswith('Agent')
        assert agent.model is not None
```

### **Performance Tests**
```python
# tests/test_performance.py
import time
from provider_manager import provider_manager

def test_provider_response_time():
    start_time = time.time()
    for provider in provider_manager.get_available_providers():
        provider_manager.test_provider(provider)
    end_time = time.time()
    
    # Should complete within reasonable time
    assert (end_time - start_time) < 30.0
```

### **Running Tests**
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_provider_manager.py

# Run with verbose output
python -m pytest -v

# Run only demo mode tests
python -m pytest -m demo
```

## 🔧 **Development Workflow**

### **Daily Development**
```bash
# 1. Pull latest changes
git pull origin develop

# 2. Create feature branch
git checkout -b feature/your-feature

# 3. Make changes
# ... your development work ...

# 4. Test locally
python -c "from agent import root_agent; print('✅ Working!')"

# 5. Commit and push
git commit -m "feat: your changes"
git push origin feature/your-feature

# 6. Create PR on GitHub
```

### **Testing Checklist**
Before pushing any changes, verify:

```bash
# System health check
python -c "
from agent import root_agent
from provider_manager import get_provider_status, provider_manager

# Test 1: System loads
print('✅ System loads successfully')

# Test 2: All agents available
frontend = len(load_frontend_agents())
backend = len(load_backend_agents())
print(f'✅ Agents: {frontend} frontend, {backend} backend')

# Test 3: Providers working
status = get_provider_status()
available = sum(1 for s in status.values() if 'Available' in s or 'Demo' in s)
print(f'✅ {available}/{len(status)} providers available')

# Test 4: No exceptions
try:
    from provider_manager import get_optimal_model
    model = get_optimal_model('FrontendWriterAgent')
    print(f'✅ Model selection works: {model}')
except Exception as e:
    print(f'❌ Error: {e}')
"
```

## 🎯 **Adding New Features**

### **New AI Provider Integration**

#### **Step 1: Add Provider Support**
```python
# provider_manager.py

# 1. Add to enum
class AIProvider(Enum):
    NEW_PROVIDER = "NEW_PROVIDER"

# 2. Add to _load_providers method
def _load_providers(self):
    # ... existing code ...
    
    new_key = os.getenv('NEW_PROVIDER_API_KEY')
    if new_key and new_key != "YOUR_NEW_PROVIDER_API_KEY_HERE":
        self.providers[AIProvider.NEW_PROVIDER] = ProviderConfig(
            name="New Provider",
            api_key=new_key,
            base_url="https://api.newprovider.com/v1",
            headers={"Authorization": f"Bearer {new_key}"}
        )

# 3. Add model mappings
def get_provider_models(self, provider: ProviderConfig):
    if provider.name == "New Provider":
        return ["new-model-1", "new-model-2", "new-model-3"]
```

#### **Step 2: Add Model Selection Logic**
```python
def get_model_for_task(self, task_type: str, complexity: str = "medium"):
    # ... existing logic ...
    
    # Add new provider models
    task_models = {
        # ... existing models ...
        "new_provider_tasks": {
            "high": "new-model-1",
            "medium": "new-model-2", 
            "low": "new-model-3"
        }
    }
```

#### **Step 3: Test the Integration**
```python
def test_new_provider_integration():
    from provider_manager import provider_manager
    
    # Check provider loads
    new_provider = provider_manager.providers.get(AIProvider.NEW_PROVIDER)
    assert new_provider is not None
    
    # Check model availability
    models = provider_manager.get_provider_models(new_provider)
    assert len(models) >= 3
    
    # Check model selection
    model = provider_manager.get_model_for_task("new_provider_tasks", "high")
    assert model == "new-model-1"
```

### **New Agent Creation**

#### **Step 1: Create Agent YAML**
```yaml
# agent_envoyou/backend_agent/sub_agent/DatabaseAgent.yaml
agent_class: LlmAgent
name: DatabaseAgent
description: "Specialized agent for database design and optimization"
instruction: |
  You are a database specialist with expertise in:
  - Modern database design patterns
  - Query optimization techniques
  - Performance tuning strategies
  - Security best practices
  
  Always:
  - Design for scalability
  - Include proper indexing
  - Add transaction management
  - Follow security guidelines

# Model will be auto-selected by provider manager
```

#### **Step 2: Add to Team**
```yaml
# Update agent_envoyou/backend_agent/root.yaml
sub_agents:
  - config_path: agent_envoyou/backend_agent/sub_agent/DatabaseAgent.yaml
  - config_path: agent_envoyou/backend_agent/sub_agent/BackendWriterAgent.yaml
  - config_path: agent_envoyou/backend_agent/sub_agent/BackendReviewerAgent.yaml
  - config_path: agent_envoyou/backend_agent/sub_agent/BackendRefactorAgent.yaml
```

#### **Step 3: Update Agent Task Mapping**
```python
# provider_manager.py
def get_optimal_model(agent_type: str, complexity: str = "medium"):
    agent_task_mapping = {
        # ... existing mappings ...
        "DatabaseAgent": "database_design",  # Add this
    }
    
    task_type = agent_task_mapping.get(agent_type, "backend_simple")
    # ... rest of function
```

### **Performance Optimization**

#### **Caching Implementation**
```python
from functools import lru_cache
import time

# Cache frequently accessed data
@lru_cache(maxsize=128)
def get_cached_model_selection(agent_type: str, complexity: str, provider: str) -> str:
    """Cache model selections to avoid repeated calculations."""
    return _calculate_optimal_model(agent_type, complexity, provider)

# Cache provider configurations
class ProviderCache:
    def __init__(self, ttl_seconds=300):  # 5 minute TTL
        self.cache = {}
        self.ttl = ttl_seconds
    
    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value):
        self.cache[key] = (value, time.time())
```

#### **Connection Pooling**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class ProviderConnectionPool:
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def test_provider(self, provider: ProviderConfig) -> bool:
        try:
            response = self.session.get(
                f"{provider.base_url}/models",
                headers=provider.headers,
                timeout=10
            )
            return response.status_code < 400
        except Exception:
            return False
```

## 📊 **Monitoring & Debugging**

### **Logging Configuration**
```python
# development_logging.py
import logging
import sys

def setup_development_logging():
    """Setup detailed logging for development."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = logging.FileHandler('logs/development.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Setup provider manager logger
    provider_logger = logging.getLogger('provider_manager')
    provider_logger.setLevel(logging.DEBUG)
    
    # Setup agent logger
    agent_logger = logging.getLogger('agent')
    agent_logger.setLevel(logging.DEBUG)

# Usage in agent.py
if os.getenv('ADK_DEBUG', 'false').lower() == 'true':
    setup_development_logging()
```

### **Performance Monitoring**
```python
# performance_monitor.py
import time
import psutil
from typing import Dict, Any

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, operation: str):
        self.metrics[operation] = {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss
        }
    
    def end_timer(self, operation: str) -> Dict[str, Any]:
        if operation not in self.metrics:
            return {}
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        return {
            'operation': operation,
            'duration': end_time - self.metrics[operation]['start_time'],
            'memory_delta': end_memory - self.metrics[operation]['start_memory'],
            'memory_peak': end_memory
        }
    
    def log_provider_performance(self, provider_name: str, success: bool, response_time: float):
        """Log provider-specific performance metrics."""
        self.metrics[f'provider_{provider_name}'] = {
            'last_success': success,
            'last_response_time': response_time,
            'timestamp': time.time()
        }

# Usage
monitor = PerformanceMonitor()

def test_provider_with_monitoring(provider: ProviderConfig):
    monitor.start_timer(f'test_provider_{provider.name}')
    
    try:
        result = test_provider_connectivity(provider)
        duration = monitor.end_timer(f'test_provider_{provider.name}')
        
        monitor.log_provider_performance(
            provider.name, 
            result, 
            duration['duration']
        )
        
        return result
    except Exception as e:
        duration = monitor.end_timer(f'test_provider_{provider.name}')
        logger.error(f"Provider test failed: {e} (took {duration['duration']:.2f}s)")
        return False
```

### **Debug Commands**
```bash
# Quick system check
python -c "
from provider_manager import get_provider_status
print('=== System Status ===')
for provider, status in get_provider_status().items():
    print(f'{provider}: {status}')
"

# Detailed provider testing
python -c "
from provider_manager import provider_manager
print('=== Provider Testing ===')
for provider in provider_manager.get_available_providers():
    try:
        start = time.time()
        result = provider_manager.test_provider(provider)
        duration = time.time() - start
        status = '✅' if result else '❌'
        print(f'{status} {provider.name}: {duration:.2f}s')
    except Exception as e:
        print(f'❌ {provider.name}: Error - {e}')
"

# Memory usage check
python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
print(f'CPU usage: {process.cpu_percent():.1f}%')
"
```

## 🚀 **Deployment**

### **Local Development Deployment**
```bash
# Development server
adk web

# Production-like deployment
export ADK_ENVIRONMENT=production
export ADK_LOG_LEVEL=WARNING
python agent.py
```

### **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "agent.py"]
```

### **Environment Variables for Production**
```bash
# Production settings
export ADK_ENVIRONMENT=production
export ADK_LOG_LEVEL=WARNING
export VERBOSE_LOGGING=false
export LOG_TO_FILE=true

# Provider configuration
export AI_PROVIDER=OPENAI
export OPENAI_API_KEY=your_production_key

# Performance settings
export PROVIDER_TIMEOUT_SECONDS=30
export PROVIDER_RETRY_ATTEMPTS=2
export ENABLE_PROVIDER_FALLBACK=true
```

## 📈 **Performance Benchmarking**

### **Baseline Performance**
```python
# benchmarks/performance_test.py
import time
import statistics
from provider_manager import provider_manager

def benchmark_provider_response_times():
    """Benchmark all providers for response times."""
    results = {}
    
    for provider in provider_manager.get_available_providers():
        times = []
        for _ in range(5):  # Test 5 times
            start = time.time()
            provider_manager.test_provider(provider)
            times.append(time.time() - start)
        
        results[provider.name] = {
            'avg': statistics.mean(times),
            'min': min(times),
            'max': max(times),
            'stdev': statistics.stdev(times)
        }
    
    return results

def benchmark_agent_loading():
    """Benchmark agent loading performance."""
    from agent import load_frontend_agents, load_backend_agents
    
    start = time.time()
    frontend_agents = load_frontend_agents()
    backend_agents = load_backend_agents()
    total_time = time.time() - start
    
    return {
        'total_time': total_time,
        'frontend_count': len(frontend_agents),
        'backend_count': len(backend_agents),
        'avg_per_agent': total_time / (len(frontend_agents) + len(backend_agents))
    }

# Run benchmarks
if __name__ == "__main__":
    print("=== Provider Performance ===")
    provider_results = benchmark_provider_response_times()
    for name, metrics in provider_results.items():
        print(f"{name}: {metrics['avg']:.3f}s ± {metrics['stdev']:.3f}s")
    
    print("\n=== Agent Loading Performance ===")
    loading_results = benchmark_agent_loading()
    print(f"Total loading time: {loading_results['total_time']:.3f}s")
    print(f"Average per agent: {loading_results['avg_per_agent']:.3f}s")
```

This comprehensive development guide provides everything developers need to contribute effectively to Agent Envoyou, from basic setup to advanced performance optimization and deployment strategies.