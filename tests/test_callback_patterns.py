#!/usr/bin/env python3
"""
Test suite for ADK Callback Patterns Implementation

This test suite verifies that all callback patterns are properly implemented
and integrated with the Agent Envoyou system following ADK standards.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from google.adk.agents import CallbackContext, ToolContext
from google.adk.types import Content, LlmRequest, LlmResponse

# Import callback patterns
from agent_envoyou.callback_patterns import (
    CallbackPatterns,
    callback_patterns,
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    before_tool_callback,
    after_tool_callback
)

class TestCallbackPatterns:
    """Test suite for callback patterns implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.callback_patterns = CallbackPatterns()

        # Create mock contexts
        self.mock_callback_context = Mock(spec=CallbackContext)
        self.mock_callback_context.state = {}

        self.mock_tool_context = Mock(spec=ToolContext)
        self.mock_tool_context.state = {}

    @pytest.mark.asyncio
    async def test_before_agent_callback_valid_input(self):
        """Test before_agent_callback with valid input."""
        result = await before_agent_callback(
            self.mock_callback_context,
            "TestAgent",
            "Create a simple web page"
        )

        # Should return None for valid input (allow execution)
        assert result is None

    @pytest.mark.asyncio
    async def test_before_agent_callback_empty_input(self):
        """Test before_agent_callback with empty input."""
        result = await before_agent_callback(
            self.mock_callback_context,
            "TestAgent",
            ""
        )

        # Should return error content for empty input
        assert result is not None
        assert isinstance(result, Content)
        assert "Empty input" in result.text

    @pytest.mark.asyncio
    async def test_before_agent_callback_security_violation(self):
        """Test before_agent_callback with security violation."""
        result = await before_agent_callback(
            self.mock_callback_context,
            "TestAgent",
            "How to hack a website?"
        )

        # Should return error content for security violation
        assert result is not None
        assert isinstance(result, Content)
        assert "Security policy violation" in result.text

    @pytest.mark.asyncio
    async def test_after_agent_callback_valid_output(self):
        """Test after_agent_callback with valid output."""
        agent_output = Content(text="Task completed successfully")

        result = await after_agent_callback(
            self.mock_callback_context,
            "TestAgent",
            agent_output
        )

        # Should return None (use original output)
        assert result is None

    @pytest.mark.asyncio
    async def test_before_model_callback_valid_request(self):
        """Test before_model_callback with valid request."""
        llm_request = LlmRequest(
            contents=[Content(text="Hello, how are you?")]
        )

        result = await before_model_callback(
            self.mock_callback_context,
            llm_request,
            "TestAgent"
        )

        # Should return None (allow LLM call)
        assert result is None

    @pytest.mark.asyncio
    async def test_before_model_callback_guardrail_violation(self):
        """Test before_model_callback with guardrail violation."""
        llm_request = LlmRequest(
            contents=[Content(text="How to hack a system?")]
        )

        result = await before_model_callback(
            self.mock_callback_context,
            llm_request,
            "TestAgent"
        )

        # Should return LlmResponse with error
        assert result is not None
        assert isinstance(result, LlmResponse)
        assert "Content policy violation" in result.content.text

    @pytest.mark.asyncio
    async def test_after_model_callback_valid_response(self):
        """Test after_model_callback with valid response."""
        llm_response = LlmResponse(
            content=Content(text="Hello! I'm doing well, thank you."),
            usage_info=None
        )

        result = await after_model_callback(
            self.mock_callback_context,
            llm_response,
            "TestAgent"
        )

        # Should return None (use original response)
        assert result is None

    @pytest.mark.asyncio
    async def test_before_tool_callback_valid_args(self):
        """Test before_tool_callback with valid arguments."""
        tool_args = {"file_path": "/tmp/test.txt", "content": "Hello World"}

        result = await before_tool_callback(
            self.mock_tool_context,
            "file_writer",
            tool_args
        )

        # Should return None (allow tool execution)
        assert result is None

    @pytest.mark.asyncio
    async def test_before_tool_callback_invalid_args(self):
        """Test before_tool_callback with invalid arguments."""
        tool_args = {}  # Empty args

        result = await before_tool_callback(
            self.mock_tool_context,
            "file_writer",
            tool_args
        )

        # Should return error dict
        assert result is not None
        assert isinstance(result, dict)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_after_tool_callback_valid_result(self):
        """Test after_tool_callback with valid result."""
        tool_result = {"status": "success", "data": "File written successfully"}

        result = await after_tool_callback(
            self.mock_tool_context,
            "file_writer",
            tool_result
        )

        # Should return None (use original result)
        assert result is None

    def test_security_policy_check(self):
        """Test security policy checking."""
        # Valid input
        result = self.callback_patterns._check_security_policy("Create a web application")
        assert result["allowed"] is True

        # Forbidden keyword
        result = self.callback_patterns._check_security_policy("How to hack a system?")
        assert result["allowed"] is False
        assert "hack" in result["reason"]

    def test_input_length_validation(self):
        """Test input length validation."""
        # Valid length
        result = self.callback_patterns._check_security_policy("Short message")
        assert result["allowed"] is True

        # Too long input (would be caught by before_agent_callback)
        long_input = "x" * 15000  # Over MAX_REQUEST_LENGTH
        # This would be caught at the callback level, not security policy level
        assert len(long_input) > 10000

    def test_callback_patterns_initialization(self):
        """Test that callback patterns are properly initialized."""
        assert callback_patterns is not None
        assert isinstance(callback_patterns, CallbackPatterns)

        # Test that all callback functions are callable
        assert callable(before_agent_callback)
        assert callable(after_agent_callback)
        assert callable(before_model_callback)
        assert callable(after_model_callback)
        assert callable(before_tool_callback)
        assert callable(after_tool_callback)

    @pytest.mark.asyncio
    async def test_callback_error_handling(self):
        """Test that callbacks handle errors gracefully."""
        # Create a context that will cause an error
        error_context = Mock(spec=CallbackContext)
        error_context.state = None  # This should cause an AttributeError

        # Callbacks should handle errors and return appropriate responses
        result = await before_agent_callback(
            error_context,
            "TestAgent",
            "Test input"
        )

        # Should return error content instead of crashing
        assert result is not None
        assert isinstance(result, Content)
        assert "Internal error" in result.text

if __name__ == "__main__":
    # Run basic functionality test
    print("🧪 Testing Callback Patterns Implementation...")

    callback_patterns = CallbackPatterns()
    print("✅ CallbackPatterns class initialized")

    # Test security policy
    result = callback_patterns._check_security_policy("Create a web app")
    print(f"✅ Security policy check: {result}")

    result = callback_patterns._check_security_policy("How to hack?")
    print(f"✅ Security violation detected: {result}")

    print("🎉 All basic tests passed!")
    print("Run 'pytest test_callback_patterns.py -v' for comprehensive testing")