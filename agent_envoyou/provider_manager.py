#!/usr/bin/env python3
"""
Multi-Provider AI Manager for ADK Agents

This module handles multiple AI providers (Google, OpenAI, Anthropic, xAI, etc.)
with automatic fallback, cost optimization, and provider-specific configurations.

Supports DEMO MODE when no API keys are available for testing and development.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import requests
import json

class AIProvider(Enum):
    """Supported AI providers."""
    GOOGLE = "GOOGLE"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    XAI = "XAI"
    OPENROUTER = "OPENROUTER"
    OLLAMA = "OLLAMA"

@dataclass
class ProviderConfig:
    """Configuration for an AI provider."""
    name: str
    api_key: str
    base_url: str
    headers: Dict[str, str]
    timeout: int = 60
    retry_attempts: int = 3
    demo_mode: bool = False

class ProviderManager:
    """Manages multiple AI providers with fallback and optimization."""
    
    def __init__(self):
        self.providers = {}
        self.current_provider = None
        self.fallback_providers = []
        self.logger = logging.getLogger(__name__)
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        self._load_providers()
    
    def _load_providers(self):
        """Load provider configurations from environment variables."""
        
        # Google AI (Gemini)
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key and google_key != "YOUR_GOOGLE_API_KEY_HERE":
            self.providers[AIProvider.GOOGLE] = ProviderConfig(
                name="Google AI",
                api_key=google_key,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": google_key
                }
            )
        elif self.demo_mode:
            self.providers[AIProvider.GOOGLE] = ProviderConfig(
                name="Google AI (Demo)",
                api_key="demo",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                headers={"Content-Type": "application/json"},
                demo_mode=True
            )
        
        # OpenAI
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key != "YOUR_OPENAI_API_KEY_HERE":
            base_url = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')
            self.providers[AIProvider.OPENAI] = ProviderConfig(
                name="OpenAI",
                api_key=openai_key,
                base_url=base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openai_key}"
                }
            )
        elif self.demo_mode:
            self.providers[AIProvider.OPENAI] = ProviderConfig(
                name="OpenAI (Demo)",
                api_key="demo",
                base_url="https://api.openai.com/v1",
                headers={"Content-Type": "application/json"},
                demo_mode=True
            )
        
        # Anthropic
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key and anthropic_key != "YOUR_ANTHROPIC_API_KEY_HERE":
            base_url = os.getenv('ANTHROPIC_BASE_URL', 'https://api.anthropic.com/v1')
            self.providers[AIProvider.ANTHROPIC] = ProviderConfig(
                name="Anthropic",
                api_key=anthropic_key,
                base_url=base_url,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": anthropic_key,
                    "anthropic-version": "2023-06-01"
                }
            )
        elif self.demo_mode:
            self.providers[AIProvider.ANTHROPIC] = ProviderConfig(
                name="Anthropic (Demo)",
                api_key="demo",
                base_url="https://api.anthropic.com/v1",
                headers={
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                demo_mode=True
            )
        
        # xAI (Grok)
        xai_key = os.getenv('XAI_API_KEY')
        if xai_key and xai_key != "YOUR_XAI_API_KEY_HERE":
            base_url = os.getenv('XAI_BASE_URL', 'https://api.x.ai/v1')
            self.providers[AIProvider.XAI] = ProviderConfig(
                name="xAI",
                api_key=xai_key,
                base_url=base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {xai_key}"
                }
            )
        elif self.demo_mode:
            self.providers[AIProvider.XAI] = ProviderConfig(
                name="xAI (Demo)",
                api_key="demo",
                base_url="https://api.x.ai/v1",
                headers={"Content-Type": "application/json"},
                demo_mode=True
            )
        
        # OpenRouter
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key and openrouter_key != "YOUR_OPENROUTER_API_KEY_HERE":
            base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
            site_url = os.getenv('OPENROUTER_SITE_URL', 'http://localhost:3000')
            self.providers[AIProvider.OPENROUTER] = ProviderConfig(
                name="OpenRouter",
                api_key=openrouter_key,
                base_url=base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_key}",
                    "HTTP-Referer": site_url,
                    "X-Title": "Multi-Provider Agent System"
                }
            )
        elif self.demo_mode:
            self.providers[AIProvider.OPENROUTER] = ProviderConfig(
                name="OpenRouter (Demo)",
                api_key="demo",
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "Multi-Provider Agent System"
                },
                demo_mode=True
            )
        
        # Local/Ollama
        ollama_host = os.getenv('OLLAMA_HOST')
        if ollama_host:
            self.providers[AIProvider.OLLAMA] = ProviderConfig(
                name="Ollama",
                api_key="",  # No API key needed for local
                base_url=f"{ollama_host}/api",
                headers={"Content-Type": "application/json"},
                timeout=30
            )
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[ProviderConfig]:
        """Get provider configuration by name or auto-select."""
        
        if provider_name:
            try:
                provider_enum = AIProvider(provider_name.upper())
                return self.providers.get(provider_enum)
            except ValueError:
                self.logger.warning(f"Unknown provider: {provider_name}")
                return None
        
        # Auto-select provider
        env_provider = os.getenv('AI_PROVIDER', 'GOOGLE')
        try:
            provider_enum = AIProvider(env_provider)
            if provider_enum in self.providers:
                return self.providers[provider_enum]
        except ValueError:
            self.logger.warning(f"Invalid AI_PROVIDER: {env_provider}")
        
        # Fallback to any available provider
        if self.providers:
            return list(self.providers.values())[0]
        
        return None
    
    def get_available_providers(self) -> List[ProviderConfig]:
        """Get list of available providers."""
        return list(self.providers.values())
    
    def get_provider_models(self, provider: ProviderConfig) -> List[str]:
        """Get available models for a provider."""
        
        model_mappings = {
            "Google AI": [
                "gemini-2.5-pro-latest", "gemini-2.5-flash", "gemini-1.5-pro-latest",
                "gemini-1.5-flash", "gemini-1.0-pro"
            ],
            "OpenAI": [
                "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"
            ],
            "Anthropic": [
                "claude-3-5-sonnet-20241022", "claude-3-opus-20240229",
                "claude-3-sonnet-20240307", "claude-3-haiku-20240307"
            ],
            "xAI": [
                "grok-beta", "grok-vision-beta"
            ],
            "OpenRouter": [
                "openai/gpt-4o", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet",
                "meta-llama/llama-3.1-405b-instruct", "google/gemini-2.5-pro"
            ],
            "Ollama": [
                "llama2", "codellama", "mistral", "vicuna", "alpaca"
            ]
        }
        
        return model_mappings.get(provider.name, [])
    
    def get_model_for_task(self, task_type: str, complexity: str = "medium") -> str:
        """Get appropriate model for a specific task."""
        
        # Task-specific model mappings
        task_models = {
            "frontend_complex": {
                "high": "gpt-4o",  # GPT-4o for complex UI/UX
                "medium": "claude-3-5-sonnet-20241022",
                "low": "gemini-2.5-flash"
            },
            "frontend_simple": {
                "high": "gpt-4o-mini",
                "medium": "gemini-2.5-flash", 
                "low": "claude-3-haiku-20240307"
            },
            "backend_complex": {
                "high": "claude-3-5-sonnet-20241022",  # Claude for architecture
                "medium": "gpt-4o",
                "low": "gemini-2.5-pro-latest"
            },
            "backend_simple": {
                "high": "gpt-4o-mini",
                "medium": "claude-3-haiku-20240307",
                "low": "grok-beta"
            },
            "code_review": {
                "high": "claude-3-5-sonnet-20241022",
                "medium": "gpt-4o",
                "low": "gemini-2.5-pro-latest"
            },
            "code_refactor": {
                "high": "gpt-4o",
                "medium": "claude-3-5-sonnet-20241022",
                "low": "grok-beta"
            }
        }
        
        return task_models.get(task_type, {}).get(complexity, "gemini-2.5-pro-latest")
    
    def test_provider(self, provider: ProviderConfig) -> bool:
        """Test if a provider is working."""
        
        # If in demo mode, consider all demo providers as available
        if provider.demo_mode:
            self.logger.info(f"✅ Demo mode: {provider.name} considered available")
            return True
        
        try:
            # Simple test endpoint for each provider
            test_endpoints = {
                "Google AI": "/models",
                "OpenAI": "/models",
                "Anthropic": "/messages",
                "xAI": "/chat/completions",
                "OpenRouter": "/models",
                "Ollama": "/tags"
            }
            
            endpoint = test_endpoints.get(provider.name, "/models")
            url = f"{provider.base_url}{endpoint}"
            
            response = requests.get(url, headers=provider.headers, timeout=10)
            return response.status_code < 400
            
        except Exception as e:
            self.logger.error(f"Provider test failed for {provider.name}: {e}")
            return False
    
    def get_cost_optimized_model(self, task_complexity: str) -> str:
        """Get cost-optimized model for task complexity."""
        
        cost_matrix = {
            "low": "claude-3-haiku-20240307",  # Cheapest
            "medium": "gpt-4o-mini",
            "high": "gpt-4o",
            "premium": "claude-3-5-sonnet-20241022"
        }
        
        return cost_matrix.get(task_complexity, "gpt-4o-mini")
    
    def get_demo_models(self) -> Dict[str, str]:
        """Get demo models for when no API keys are available."""
        return {
            "FrontendWriterAgent": "gpt-4o (Demo)",
            "FrontendReviewerAgent": "claude-3-5-sonnet (Demo)",
            "FrontendRefactorAgent": "gpt-4o-mini (Demo)",
            "BackendWriterAgent": "claude-3-5-sonnet (Demo)",
            "BackendReviewerAgent": "gpt-4o (Demo)",
            "BackendRefactorAgent": "gemini-2.5-pro (Demo)",
            "FullstackManagerAgent": "claude-3-5-sonnet (Demo)"
        }

# Global provider manager instance
provider_manager = ProviderManager()

def get_optimal_model(agent_type: str, complexity: str = "medium") -> str:
    """Get optimal model for agent type and complexity."""
    
    # Agent type to task type mapping
    agent_task_mapping = {
        "FrontendWriterAgent": "frontend_complex",
        "FrontendReviewerAgent": "code_review", 
        "FrontendRefactorAgent": "code_refactor",
        "BackendWriterAgent": "backend_complex",
        "BackendReviewerAgent": "code_review",
        "BackendRefactorAgent": "code_refactor"
    }
    
    task_type = agent_task_mapping.get(agent_type, "backend_simple")
    
    # First try to get provider-specific model
    provider = provider_manager.get_provider()
    if provider:
        model = provider_manager.get_model_for_task(task_type, complexity)
        
        # Check if model is available for this provider
        available_models = provider_manager.get_provider_models(provider)
        if model in available_models:
            return model
    
    # Fallback to generic cost-optimized model
    return provider_manager.get_cost_optimized_model(complexity)

def get_best_available_provider() -> Optional[ProviderConfig]:
    """Get the best available provider."""
    
    provider = provider_manager.get_provider()
    if not provider:
        return None
    
    # Test provider availability
    if provider_manager.test_provider(provider):
        return provider
    
    # Try fallback providers
    for fallback_provider in provider_manager.get_available_providers():
        if fallback_provider != provider and provider_manager.test_provider(fallback_provider):
            return fallback_provider
    
    return None

def get_demo_or_real_model(agent_name: str, complexity: str = "medium") -> str:
    """Get demo model if no real providers available, otherwise real model."""
    
    # Check if we have any real providers
    real_providers = [p for p in provider_manager.get_available_providers() if not p.demo_mode]
    
    if real_providers:
        return get_optimal_model(agent_name, complexity)
    else:
        # Use demo models
        demo_models = provider_manager.get_demo_models()
        return demo_models.get(agent_name, "demo-model")

# Environment-based configuration helpers
def get_model_config() -> Dict[str, Any]:
    """Get model configuration from environment."""
    return {
        "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "4096")),
        "top_p": float(os.getenv("MODEL_TOP_P", "0.9")),
        "frequency_penalty": float(os.getenv("MODEL_FREQUENCY_PENALTY", "0.0")),
        "presence_penalty": float(os.getenv("MODEL_PRESENCE_PENALTY", "0.0")),
    }

def is_provider_fallback_enabled() -> bool:
    """Check if provider fallback is enabled."""
    return os.getenv("ENABLE_PROVIDER_FALLBACK", "true").lower() == "true"

def get_provider_timeout() -> int:
    """Get provider timeout setting."""
    return int(os.getenv("PROVIDER_TIMEOUT_SECONDS", "60"))

def get_retry_attempts() -> int:
    """Get provider retry attempts."""
    return int(os.getenv("PROVIDER_RETRY_ATTEMPTS", "3"))

def is_demo_mode() -> bool:
    """Check if running in demo mode."""
    return provider_manager.demo_mode

def get_provider_status() -> Dict[str, str]:
    """Get status of all providers."""
    status = {}
    for provider in provider_manager.get_available_providers():
        if provider.demo_mode:
            status[provider.name] = "Demo Mode"
        elif provider_manager.test_provider(provider):
            status[provider.name] = "Available"
        else:
            status[provider.name] = "Unavailable"
    return status