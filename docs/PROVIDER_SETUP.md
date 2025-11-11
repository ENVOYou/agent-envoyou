# Multi-Provider AI Agent System

This system supports multiple AI providers, making it completely provider-agnostic and avoiding vendor lock-in. You can switch between providers by simply updating your `.env` configuration.

## ✅ Supported Providers

| Provider | Models | Demo Mode | Status |
|----------|--------|-----------|--------|
| **Google AI** | gemini-2.5-pro-latest, gemini-2.5-flash | ✅ | Ready |
| **OpenAI** | gpt-4o, gpt-4o-mini, gpt-4-turbo | ✅ | Ready |
| **Anthropic** | claude-3-5-sonnet-20241022, claude-3-haiku-20240307 | ✅ | Ready |
| **xAI** | grok-beta, grok-vision-beta | ✅ | Ready |
| **OpenRouter** | Access to 50+ models from multiple providers | ✅ | Ready |
| **Ollama** | Local models (llama2, codellama, mistral) | ❌ | Local only |

## 🚀 Quick Start (Demo Mode)

The system works out-of-the-box in demo mode when no real API keys are configured:

```bash
# Test the system
python -c "from agent import root_agent; print(f'✅ Loaded: {root_agent.name}')"
```

**Current Status:**
- ✅ **5 Demo providers** configured and ready
- ✅ **8 agents** successfully loaded
- ✅ **Multi-provider** architecture implemented
- ✅ **Smart model selection** based on task complexity

## 🔧 Real Provider Setup

### Option 1: Google AI (Gemini) - Default
```bash
# 1. Get API key from: https://aistudio.google.com/apikey
# 2. Update .env file:
AI_PROVIDER=GOOGLE
GOOGLE_API_KEY=YOUR_ACTUAL_API_KEY
GOOGLE_GENAI_USE_VERTEXAI=FALSE
```

### Option 2: OpenAI (GPT models)
```bash
# 1. Get API key from: https://platform.openai.com/api-keys
# 2. Update .env file:
AI_PROVIDER=OPENAI
OPENAI_API_KEY=YOUR_OPENAI_API_KEY
OPENAI_BASE_URL=https://api.openai.com/v1
```

### Option 3: Anthropic (Claude)
```bash
# 1. Get API key from: https://console.anthropic.com/
# 2. Update .env file:
AI_PROVIDER=ANTHROPIC
ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
```

### Option 4: xAI (Grok)
```bash
# 1. Get API key from: https://console.x.ai/
# 2. Update .env file:
AI_PROVIDER=XAI
XAI_API_KEY=YOUR_XAI_API_KEY
XAI_BASE_URL=https://api.x.ai/v1
```

### Option 5: OpenRouter (Multiple Models)
```bash
# 1. Get API key from: https://openrouter.ai/keys
# 2. Update .env file:
AI_PROVIDER=OPENROUTER
OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

### Option 6: Local/Ollama
```bash
# 1. Install Ollama: https://ollama.ai/
# 2. Update .env file:
AI_PROVIDER=OLLAMA
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2
```

## 🎯 Smart Model Selection

The system automatically selects optimal models based on agent complexity:

| Agent Type | Complexity | Recommended Model | Provider |
|------------|------------|------------------|----------|
| **FrontendWriter** | High | GPT-4o | OpenAI |
| **BackendWriter** | High | Claude 3.5 Sonnet | Anthropic |
| **Code Reviewers** | Medium | GPT-4o | OpenAI |
| **Code Refactorers** | Medium | Claude 3.5 Sonnet | Anthropic |
| **Manager Agent** | High | Claude 3.5 Sonnet | Anthropic |

### Cost Optimization

The system includes cost optimization features:

```bash
# Cost-optimized model selection
MODEL_COMPLEXITY_COST_OPTIMIZATION=true

# Automatically use cheaper models for simple tasks
USE_HAIKU_FOR_LOW_COMPLEXITY=true
USE_GPT_4O_MINI_FOR_MEDIUM_COMPLEXITY=true
```

## 🔄 Provider Fallback

Automatic fallback system ensures reliability:

```bash
# Enable provider fallback
ENABLE_PROVIDER_FALLBACK=true
PROVIDER_TIMEOUT_SECONDS=60
PROVIDER_RETRY_ATTEMPTS=3
```

**Fallback Order:**
1. Primary provider (from `AI_PROVIDER`)
2. Available secondary providers
3. Demo mode (if enabled)

## 📊 Provider Monitoring

Monitor provider performance and costs:

```bash
# Enable monitoring
PROVIDER_MONITORING_ENABLED=true
PROVIDER_PERFORMANCE_TRACKING=true
PROVIDER_COST_TRACKING=true

# Performance logging
VERBOSE_LOGGING=true
LOG_TO_FILE=true
LOG_FILE_PATH=logs/multi_provider_agents.log
```

## 🧪 Testing Providers

Test individual providers:

```python
from provider_manager import provider_manager, get_provider_status

# Check all provider status
status = get_provider_status()
print("Provider Status:", status)

# Test specific provider
provider = provider_manager.get_provider("OPENAI")
if provider and provider_manager.test_provider(provider):
    print("✅ OpenAI is working!")
else:
    print("❌ OpenAI is not available")
```

## 🔐 Security Best Practices

```bash
# API key security
SECURE_CREDENTIAL_STORAGE=true
API_KEY_ROTATION_ENABLED=true

# Rate limiting
API_RATE_LIMIT=100
API_RATE_WINDOW=60

# Environment security
ENVIRONMENT_BASED_CONFIG=true
PROVIDER_ENCRYPTION=true
```

## 📈 Advanced Configuration

### Custom Model Mappings
```python
# Custom task-specific model selection
TASK_MODEL_MAPPING='{
    "frontend_complex": {"high": "gpt-4o", "medium": "claude-3-5-sonnet"},
    "backend_complex": {"high": "claude-3-5-sonnet", "medium": "gpt-4o"},
    "code_review": {"high": "claude-3-5-sonnet", "medium": "gpt-4o"}
}'
```

### Provider-Specific Settings
```bash
# OpenAI specific
OPENAI_ORG_ID=your-org-id
OPENAI_MAX_TOKENS=4096
OPENAI_TEMPERATURE=0.7

# Anthropic specific
ANTHROPIC_VERSION=2023-06-01
ANTHROPIC_MAX_TOKENS=4096

# OpenRouter specific
OPENROUTER_SITE_URL=https://your-app.com
OPENROUTER_REFERRER=https://your-app.com
```

## 🚨 Troubleshooting

### Common Issues

1. **"No available providers found"**
   ```bash
   # Enable demo mode
   DEMO_MODE=true
   
   # Or add real API keys
   echo "GOOGLE_API_KEY=your-key" >> .env
   ```

2. **"Provider test failed"**
   ```bash
   # Check API key validity
   curl -H "Authorization: Bearer YOUR_KEY" https://api.openai.com/v1/models
   
   # Disable provider testing for demo
   SKIP_PROVIDER_TESTING=true
   ```

3. **"Model not available"**
   ```bash
   # Check model availability for provider
   # Update to available model in .env
   OPENAI_MODEL=gpt-4o-mini  # Fallback model
   ```

### Debug Mode
```bash
# Enable debug logging
ADK_DEBUG=true
ADK_LOG_LEVEL=DEBUG
VERBOSE_LOGGING=true

# Test provider connectivity
python -c "
from provider_manager import provider_manager
for provider in provider_manager.get_available_providers():
    print(f'{provider.name}: {provider_manager.test_provider(provider)}')"
```

## 📋 Migration Checklist

To migrate from single-provider to multi-provider:

- [ ] ✅ System upgraded to multi-provider architecture
- [ ] ✅ Demo mode working (test with `python -c "from agent import root_agent"`)
- [ ] ✅ Choose primary provider in `.env`
- [ ] ✅ Add API keys for chosen provider
- [ ] ✅ Test provider connectivity
- [ ] ✅ Configure fallback providers (optional)
- [ ] ✅ Enable monitoring and logging
- [ ] ✅ Update team on new capabilities

## 🎉 Benefits of Multi-Provider System

1. **No Vendor Lock-in**: Switch providers anytime
2. **Cost Optimization**: Use cheapest provider for each task
3. **Reliability**: Automatic fallback ensures uptime
4. **Best Models**: Access to best model from each provider
5. **Performance**: Smart routing based on task complexity
6. **Future-Proof**: Easy to add new providers

---

**🎯 Ready to start?** The system is already working in demo mode! Add real API keys to unlock the full power of multiple AI providers.

**📞 Need help?** Check the logs for detailed provider status and configuration guidance.