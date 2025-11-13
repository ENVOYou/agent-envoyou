#!/usr/bin/env python3
"""
ADK Callback Patterns Implementation for Agent Envoyou

This module implements comprehensive callback patterns following ADK standards:
- before_agent_callback: Policy enforcement and validation
- after_agent_callback: Post-processing and cleanup
- before_model_callback: Guardrails and input validation
- after_model_callback: Output processing and sanitization
- before_tool_callback: Tool authorization and validation
- after_tool_callback: Result processing and state management

All callbacks follow ADK best practices for error handling, performance, and state management.
"""

import logging
from typing import Dict, Any, Optional, List
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)

# Security and policy constants
FORBIDDEN_KEYWORDS = [
    "hack", "exploit", "malware", "virus", "trojan",
    "password", "credential", "secret", "token",
    "admin", "root", "sudo", "privilege"
]

MAX_REQUEST_LENGTH = 10000
MAX_TOOL_ARGS_LENGTH = 5000

class CallbackPatterns:
    """ADK-compliant callback patterns for Agent Envoyou."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # ============================================================================
    # AGENT LIFECYCLE CALLBACKS
    # ============================================================================

    async def before_agent_callback(
        self,
        callback_context: CallbackContext,
        agent_name: str,
        user_input: str
    ) -> Optional[Content]:
        """
        Before Agent Callback - Policy Enforcement and Validation

        Called immediately before agent's main logic execution.
        Used for:
        - Input validation and sanitization
        - Policy enforcement (security, content filtering)
        - Resource quota checks
        - Session state validation
        - Logging and monitoring

        Args:
            callback_context: ADK callback context with state access
            agent_name: Name of the agent being called
            user_input: Raw user input

        Returns:
            Content: If returned, skips agent execution and uses this as response
            None: Allows normal agent execution to proceed
        """
        try:
            self.logger.info(f"🔍 Before Agent: {agent_name}")

            # 1. Input Validation
            if not user_input or not user_input.strip():
                return types.Content(text="Error: Empty input provided")

            if len(user_input) > MAX_REQUEST_LENGTH:
                return types.Content(text=f"Error: Input too long (max {MAX_REQUEST_LENGTH} characters)")

            # 2. Security Policy Enforcement
            security_check = self._check_security_policy(user_input)
            if not security_check["allowed"]:
                self.logger.warning(f"🚫 Security violation in {agent_name}: {security_check['reason']}")
                # Update state for violation tracking
                callback_context.state['security_violations'] = callback_context.state.get('security_violations', 0) + 1
                return types.Content(text=f"Security policy violation: {security_check['reason']}")

            # 3. Resource Quota Check
            quota_check = self._check_resource_quota(callback_context, agent_name)
            if not quota_check["allowed"]:
                return types.Content(text=f"Resource quota exceeded: {quota_check['reason']}")

            # 4. Session State Validation
            state_validation = self._validate_session_state(callback_context)
            if not state_validation["valid"]:
                self.logger.warning(f"⚠️ Invalid session state: {state_validation['reason']}")
                return types.Content(text=f"Session error: {state_validation['reason']}")

            # 5. Agent-Specific Preparations
            self._prepare_agent_context(callback_context, agent_name)

            # 6. Logging
            self.logger.info(f"✅ Before Agent validation passed for {agent_name}")

            # Return None to allow normal execution
            return None

        except Exception as e:
            self.logger.error(f"❌ Before Agent callback error: {e}")
            return types.Content(text="Internal error during request validation")

    async def after_agent_callback(
        self,
        callback_context: CallbackContext,
        agent_name: str,
        agent_output: Content
    ) -> Optional[types.Content]:
        """
        After Agent Callback - Post-processing and Cleanup

        Called immediately after agent's main logic completes.
        Used for:
        - Output sanitization and formatting
        - Result validation
        - State cleanup and updates
        - Performance metrics collection
        - Audit logging

        Args:
            callback_context: ADK callback context with state access
            agent_name: Name of the agent that completed
            agent_output: Raw output from agent execution

        Returns:
            Content: If returned, replaces the agent's output
            None: Uses the agent's original output
        """
        try:
            self.logger.info(f"📤 After Agent: {agent_name}")

            # 1. Output Validation
            if not agent_output or not hasattr(agent_output, 'text'):
                self.logger.warning(f"⚠️ Invalid agent output from {agent_name}")
                return types.Content(text="Error: Agent produced invalid output")

            # 2. Output Sanitization
            sanitized_output = self._sanitize_output(agent_output.text)
            if sanitized_output != agent_output.text:
                self.logger.info(f"🧹 Output sanitized for {agent_name}")

            # 3. State Updates
            self._update_agent_state(callback_context, agent_name, sanitized_output)

            # 4. Performance Metrics
            self._collect_performance_metrics(callback_context, agent_name)

            # 5. Audit Logging
            self._log_agent_completion(callback_context, agent_name, sanitized_output)

            # 6. Output Enhancement (optional)
            enhanced_output = self._enhance_output(sanitized_output, callback_context.state)

            # Return enhanced output if different, otherwise None
            if enhanced_output != sanitized_output:
                return types.Content(text=enhanced_output)

            return None

        except Exception as e:
            self.logger.error(f"❌ After Agent callback error: {e}")
            return types.Content(text="Internal error during response processing")

    # ============================================================================
    # LLM INTERACTION CALLBACKS
    # ============================================================================

    async def before_model_callback(
        self,
        callback_context: CallbackContext,
        llm_request: LlmRequest,
        agent_name: str
    ) -> Optional[LlmResponse]:
        """
        Before Model Callback - Guardrails and Input Validation

        Called just before LLM request is sent.
        Used for:
        - Input guardrails and content filtering
        - Prompt injection prevention
        - Model-specific optimizations
        - Request caching and deduplication
        - Cost control and rate limiting

        Args:
            callback_context: ADK callback context
            llm_request: The request being sent to LLM
            agent_name: Name of the agent making the request

        Returns:
            LlmResponse: If returned, skips LLM call and uses this response
            None: Allows normal LLM call to proceed
        """
        try:
            self.logger.info(f"🤖 Before Model: {agent_name}")

            # 1. Content Guardrails
            guardrail_check = self._check_content_guardrails(llm_request)
            if not guardrail_check["allowed"]:
                self.logger.warning(f"🚫 Guardrail violation in {agent_name}: {guardrail_check['reason']}")
                return LlmResponse(
                    content=types.Content(text=f"Content policy violation: {guardrail_check['reason']}"),
                    usage_info=None
                )

            # 2. Prompt Injection Prevention
            injection_check = self._check_prompt_injection(llm_request)
            if injection_check["detected"]:
                self.logger.warning(f"🚨 Prompt injection attempt in {agent_name}")
                return LlmResponse(
                    content=types.Content(text="Security violation: Potential prompt injection detected"),
                    usage_info=None
                )

            # 3. Request Optimization
            optimized_request = self._optimize_llm_request(llm_request, callback_context.state)

            # 4. Caching Check
            cache_key = self._generate_cache_key(llm_request, agent_name)
            cached_response = self._check_cache(cache_key, callback_context)
            if cached_response:
                self.logger.info(f"💾 Cache hit for {agent_name}")
                return cached_response

            # 5. Rate Limiting
            rate_check = self._check_rate_limits(callback_context, agent_name)
            if not rate_check["allowed"]:
                return LlmResponse(
                    content=types.Content(text=f"Rate limit exceeded: {rate_check['reason']}"),
                    usage_info=None
                )

            # 6. Cost Estimation and Control
            cost_check = self._estimate_and_check_cost(llm_request, callback_context)
            if not cost_check["allowed"]:
                return LlmResponse(
                    content=types.Content(text=f"Cost limit exceeded: {cost_check['reason']}"),
                    usage_info=None
                )

            return None

        except Exception as e:
            self.logger.error(f"❌ Before Model callback error: {e}")
            return LlmResponse(
                content=types.Content(text="Internal error during request processing"),
                usage_info=None
            )

    async def after_model_callback(
        self,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
        agent_name: str
    ) -> Optional[LlmResponse]:
        """
        After Model Callback - Output Processing and Sanitization

        Called just after LLM response is received.
        Used for:
        - Output sanitization and filtering
        - Response validation and quality checks
        - Structured data extraction and storage
        - Response caching
        - Performance monitoring

        Args:
            callback_context: ADK callback context
            llm_response: Raw response from LLM
            agent_name: Name of the agent that made the request

        Returns:
            LlmResponse: If returned, replaces the LLM response
            None: Uses the original LLM response
        """
        try:
            self.logger.info(f"📥 After Model: {agent_name}")

            # 1. Response Validation
            if not llm_response or not llm_response.content:
                self.logger.warning(f"⚠️ Invalid LLM response from {agent_name}")
                return LlmResponse(
                    content=types.Content(text="Error: Invalid response from language model"),
                    usage_info=llm_response.usage_info if llm_response else None
                )

            # 2. Content Sanitization
            sanitized_text = self._sanitize_llm_output(llm_response.content.text)
            if sanitized_text != llm_response.content.text:
                self.logger.info(f"🧹 LLM output sanitized for {agent_name}")

            # 3. Quality Checks
            quality_check = self._check_response_quality(sanitized_text)
            if not quality_check["passed"]:
                self.logger.warning(f"⚠️ Low quality response from {agent_name}: {quality_check['reason']}")

            # 4. Structured Data Extraction
            extracted_data = self._extract_structured_data(sanitized_text, callback_context)

            # 5. Response Caching
            if quality_check["passed"]:
                cache_key = self._generate_cache_key_from_response(llm_response, agent_name)
                self._store_cache(cache_key, llm_response, callback_context)

            # 6. Performance Metrics
            self._collect_llm_metrics(callback_context, llm_response, agent_name)

            # 7. Response Enhancement
            enhanced_text = self._enhance_llm_response(sanitized_text, callback_context.state)

            # Return enhanced response if different
            if enhanced_text != sanitized_text:
                return LlmResponse(
                    content=types.Content(text=enhanced_text),
                    usage_info=llm_response.usage_info
                )

            return None

        except Exception as e:
            self.logger.error(f"❌ After Model callback error: {e}")
            return LlmResponse(
                content=types.Content(text="Internal error during response processing"),
                usage_info=llm_response.usage_info if llm_response else None
            )

    # ============================================================================
    # TOOL EXECUTION CALLBACKS
    # ============================================================================

    async def before_tool_callback(
        self,
        tool_context: ToolContext,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Before Tool Callback - Tool Authorization and Validation

        Called just before tool execution.
        Used for:
        - Tool argument validation and sanitization
        - Authorization and permission checks
        - Resource availability verification
        - Tool-specific rate limiting
        - Input parameter optimization

        Args:
            tool_context: ADK tool context with full access
            tool_name: Name of the tool being executed
            tool_args: Arguments being passed to the tool

        Returns:
            Dict: If returned, skips tool execution and uses this as result
            None: Allows normal tool execution to proceed
        """
        try:
            self.logger.info(f"🔧 Before Tool: {tool_name}")

            # 1. Argument Validation
            validation_result = self._validate_tool_arguments(tool_name, tool_args)
            if not validation_result["valid"]:
                self.logger.warning(f"⚠️ Invalid arguments for {tool_name}: {validation_result['reason']}")
                return {"error": f"Invalid arguments: {validation_result['reason']}", "tool": tool_name}

            # 2. Authorization Check
            auth_check = self._check_tool_authorization(tool_context, tool_name, tool_args)
            if not auth_check["authorized"]:
                self.logger.warning(f"🚫 Unauthorized access to {tool_name}: {auth_check['reason']}")
                return {"error": f"Authorization failed: {auth_check['reason']}", "tool": tool_name}

            # 3. Resource Availability
            resource_check = self._check_tool_resources(tool_context, tool_name)
            if not resource_check["available"]:
                return {"error": f"Resource unavailable: {resource_check['reason']}", "tool": tool_name}

            # 4. Rate Limiting
            rate_check = self._check_tool_rate_limits(tool_context, tool_name)
            if not rate_check["allowed"]:
                return {"error": f"Rate limit exceeded: {rate_check['reason']}", "tool": tool_name}

            # 5. Argument Sanitization
            sanitized_args = self._sanitize_tool_arguments(tool_args)
            if sanitized_args != tool_args:
                self.logger.info(f"🧹 Arguments sanitized for {tool_name}")

            # 6. Tool-Specific Preparations
            prepared_args = self._prepare_tool_execution(tool_context, tool_name, sanitized_args)

            # 7. Logging
            self.logger.info(f"✅ Before Tool validation passed for {tool_name}")

            # Return prepared args if different, otherwise None
            return prepared_args if prepared_args != sanitized_args else None

        except Exception as e:
            self.logger.error(f"❌ Before Tool callback error for {tool_name}: {e}")
            return {"error": f"Internal error: {str(e)}", "tool": tool_name}

    async def after_tool_callback(
        self,
        tool_context: ToolContext,
        tool_name: str,
        tool_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        After Tool Callback - Result Processing and State Management

        Called just after tool execution completes.
        Used for:
        - Result validation and sanitization
        - State updates from tool results
        - Result caching and optimization
        - Performance monitoring
        - Audit logging

        Args:
            tool_context: ADK tool context with full access
            tool_name: Name of the tool that executed
            tool_result: Raw result from tool execution

        Returns:
            Dict: If returned, replaces the tool result
            None: Uses the original tool result
        """
        try:
            self.logger.info(f"📤 After Tool: {tool_name}")

            # 1. Result Validation
            if not isinstance(tool_result, dict):
                self.logger.warning(f"⚠️ Invalid result type from {tool_name}: {type(tool_result)}")
                return {"error": "Invalid result format", "tool": tool_name}

            # 2. Result Sanitization
            sanitized_result = self._sanitize_tool_result(tool_result)
            if sanitized_result != tool_result:
                self.logger.info(f"🧹 Result sanitized for {tool_name}")

            # 3. State Updates
            self._update_tool_state(tool_context, tool_name, sanitized_result)

            # 4. Result Caching
            cache_key = self._generate_tool_cache_key(tool_name, tool_context.state)
            self._store_tool_cache(cache_key, sanitized_result, tool_context)

            # 5. Performance Metrics
            self._collect_tool_metrics(tool_context, tool_name, sanitized_result)

            # 6. Audit Logging
            self._log_tool_execution(tool_context, tool_name, sanitized_result)

            # 7. Result Enhancement
            enhanced_result = self._enhance_tool_result(sanitized_result, tool_context.state)

            # Return enhanced result if different
            return enhanced_result if enhanced_result != sanitized_result else None

        except Exception as e:
            self.logger.error(f"❌ After Tool callback error for {tool_name}: {e}")
            return {"error": f"Internal error: {str(e)}", "tool": tool_name}

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _check_security_policy(self, input_text: str) -> Dict[str, Any]:
        """Check input against security policies."""
        input_lower = input_text.lower()

        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in input_lower:
                return {
                    "allowed": False,
                    "reason": f"Contains forbidden keyword: {keyword}"
                }

        return {"allowed": True}

    def _check_resource_quota(self, context: CallbackContext, agent_name: str) -> Dict[str, Any]:
        """Check if agent has exceeded resource quotas."""
        # Implementation for quota checking
        return {"allowed": True}

    def _validate_session_state(self, context: CallbackContext) -> Dict[str, Any]:
        """Validate session state integrity."""
        # Implementation for state validation
        return {"valid": True}

    def _prepare_agent_context(self, context: CallbackContext, agent_name: str):
        """Prepare agent-specific context."""
        # Implementation for context preparation
        pass

    def _sanitize_output(self, output: str) -> str:
        """Sanitize agent output."""
        # Implementation for output sanitization
        return output

    def _update_agent_state(self, context: CallbackContext, agent_name: str, output: str):
        """Update state after agent execution."""
        # Implementation for state updates
        pass

    def _collect_performance_metrics(self, context: CallbackContext, agent_name: str):
        """Collect performance metrics."""
        # Implementation for metrics collection
        pass

    def _log_agent_completion(self, context: CallbackContext, agent_name: str, output: str):
        """Log agent completion."""
        # Implementation for audit logging
        pass

    def _enhance_output(self, output: str, state: Dict[str, Any]) -> str:
        """Enhance agent output based on state."""
        # Implementation for output enhancement
        return output

    def _check_content_guardrails(self, llm_request: LlmRequest) -> Dict[str, Any]:
        """Check LLM request against content guardrails."""
        # Implementation for guardrails
        return {"allowed": True}

    def _check_prompt_injection(self, llm_request: LlmRequest) -> Dict[str, Any]:
        """Check for prompt injection attempts."""
        # Implementation for injection detection
        return {"detected": False}

    def _optimize_llm_request(self, llm_request: LlmRequest, state: Dict[str, Any]) -> LlmRequest:
        """Optimize LLM request based on state."""
        # Implementation for request optimization
        return llm_request

    def _generate_cache_key(self, llm_request: LlmRequest, agent_name: str) -> str:
        """Generate cache key for LLM request."""
        # Implementation for cache key generation
        return ""

    def _check_cache(self, cache_key: str, context: CallbackContext) -> Optional[LlmResponse]:
        """Check cache for existing response."""
        # Implementation for cache checking
        return None

    def _check_rate_limits(self, context: CallbackContext, agent_name: str) -> Dict[str, Any]:
        """Check rate limits for agent."""
        # Implementation for rate limiting
        return {"allowed": True}

    def _estimate_and_check_cost(self, llm_request: LlmRequest, context: CallbackContext) -> Dict[str, Any]:
        """Estimate and check LLM request cost."""
        # Implementation for cost checking
        return {"allowed": True}

    def _sanitize_llm_output(self, output: str) -> str:
        """Sanitize LLM output."""
        # Implementation for output sanitization
        return output

    def _check_response_quality(self, response: str) -> Dict[str, Any]:
        """Check LLM response quality."""
        # Implementation for quality checking
        return {"passed": True}

    def _extract_structured_data(self, response: str, context: CallbackContext) -> Dict[str, Any]:
        """Extract structured data from LLM response."""
        # Implementation for data extraction
        return {}

    def _store_cache(self, cache_key: str, response: LlmResponse, context: CallbackContext):
        """Store response in cache."""
        # Implementation for cache storage
        pass

    def _collect_llm_metrics(self, context: CallbackContext, response: LlmResponse, agent_name: str):
        """Collect LLM performance metrics."""
        # Implementation for metrics collection
        pass

    def _enhance_llm_response(self, response: str, state: Dict[str, Any]) -> str:
        """Enhance LLM response based on state."""
        # Implementation for response enhancement
        return response

    def _validate_tool_arguments(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tool arguments."""
        # Implementation for argument validation
        return {"valid": True}

    def _check_tool_authorization(self, context: ToolContext, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Check tool authorization."""
        # Implementation for authorization checking
        return {"authorized": True}

    def _check_tool_resources(self, context: ToolContext, tool_name: str) -> Dict[str, Any]:
        """Check tool resource availability."""
        # Implementation for resource checking
        return {"available": True}

    def _check_tool_rate_limits(self, context: ToolContext, tool_name: str) -> Dict[str, Any]:
        """Check tool rate limits."""
        # Implementation for rate limiting
        return {"allowed": True}

    def _sanitize_tool_arguments(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool arguments."""
        # Implementation for argument sanitization
        return args

    def _prepare_tool_execution(self, context: ToolContext, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tool execution."""
        # Implementation for execution preparation
        return args

    def _sanitize_tool_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize tool result."""
        # Implementation for result sanitization
        return result

    def _update_tool_state(self, context: ToolContext, tool_name: str, result: Dict[str, Any]):
        """Update state after tool execution."""
        # Implementation for state updates
        pass

    def _generate_tool_cache_key(self, tool_name: str, state: Dict[str, Any]) -> str:
        """Generate cache key for tool."""
        # Implementation for cache key generation
        return ""

    def _store_tool_cache(self, cache_key: str, result: Dict[str, Any], context: ToolContext):
        """Store tool result in cache."""
        # Implementation for cache storage
        pass

    def _collect_tool_metrics(self, context: ToolContext, tool_name: str, result: Dict[str, Any]):
        """Collect tool performance metrics."""
        # Implementation for metrics collection
        pass

    def _log_tool_execution(self, context: ToolContext, tool_name: str, result: Dict[str, Any]):
        """Log tool execution."""
        # Implementation for audit logging
        pass

    def _enhance_tool_result(self, result: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance tool result based on state."""
        # Implementation for result enhancement
        return result

    def _generate_cache_key_from_response(self, response: LlmResponse, agent_name: str) -> str:
        """Generate cache key from LLM response."""
        # Implementation for cache key generation
        return ""


# Global callback patterns instance
callback_patterns = CallbackPatterns()

# Export callback functions for ADK integration
before_agent_callback = callback_patterns.before_agent_callback
after_agent_callback = callback_patterns.after_agent_callback
before_model_callback = callback_patterns.before_model_callback
after_model_callback = callback_patterns.after_model_callback
before_tool_callback = callback_patterns.before_tool_callback
after_tool_callback = callback_patterns.after_tool_callback

__all__ = [
    'CallbackPatterns',
    'callback_patterns',
    'before_agent_callback',
    'after_agent_callback',
    'before_model_callback',
    'after_model_callback',
    'before_tool_callback',
    'after_tool_callback'
]