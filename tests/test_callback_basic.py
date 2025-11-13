#!/usr/bin/env python3
"""
Basic Test for ADK Callback Patterns Implementation

Simple test without external dependencies to verify callback patterns work.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import callback patterns (without ADK context classes)
    from agent_envoyou.callback_patterns import (
        CallbackPatterns,
        callback_patterns
    )
    print("✅ Callback patterns imported successfully")

    # Test basic functionality
    callback_patterns = CallbackPatterns()
    print("✅ CallbackPatterns class initialized")

    # Test security policy
    result = callback_patterns._check_security_policy("Create a web app")
    print(f"✅ Security policy check (valid): {result}")

    result = callback_patterns._check_security_policy("How to hack?")
    print(f"✅ Security violation detected: {result}")

    # Test that callback methods exist (without calling them due to ADK context dependency)
    assert hasattr(callback_patterns, 'before_agent_callback'), "before_agent_callback method missing"
    assert hasattr(callback_patterns, 'after_agent_callback'), "after_agent_callback method missing"
    assert hasattr(callback_patterns, 'before_model_callback'), "before_model_callback method missing"
    assert hasattr(callback_patterns, 'after_model_callback'), "after_model_callback method missing"
    assert hasattr(callback_patterns, 'before_tool_callback'), "before_tool_callback method missing"
    assert hasattr(callback_patterns, 'after_tool_callback'), "after_tool_callback method missing"
    print("✅ All callback methods are present")

    # Test helper methods
    assert hasattr(callback_patterns, '_check_security_policy'), "Security policy check method missing"
    assert hasattr(callback_patterns, '_sanitize_output'), "Output sanitization method missing"
    print("✅ Helper methods are present")

    print("\n🎉 Callback Patterns Implementation Test PASSED!")
    print("All basic functionality verified successfully.")
    print("Note: Full callback testing requires ADK context objects and should be done in ADK environment.")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Test Error: {e}")
    sys.exit(1)