#!/usr/bin/env python3
"""
Test script for Tool Confirmation System
"""

import asyncio
import sys
import os
from pathlib import Path

# Add agent_envoyou/tools to path
tools_path = Path(__file__).parent / "agent_envoyou" / "tools"
sys.path.insert(0, str(tools_path))

# Import directly from the confirmation module
from tool_confirmation import (
    request_destructive_confirmation,
    should_require_confirmation,
    tool_confirmation
)

async def test_confirmation_system():
    """Test the tool confirmation system."""
    print("🧪 Testing Tool Confirmation System")
    print("=" * 50)
    
    # Test 1: Safe operation (should auto-approve)
    print("\n1. Testing safe file read operation...")
    requires_confirmation = should_require_confirmation("read", {"path": "/tmp/test.txt"})
    print(f"   File read requires confirmation: {requires_confirmation}")
    assert not requires_confirmation, "Safe read should not require confirmation"
    print("   ✅ PASS: Safe operations auto-approved")
    
    # Test 2: Dangerous operation
    print("\n2. Testing dangerous file deletion...")
    requires_confirmation = should_require_confirmation("delete_files", {"paths": ["/important/file.txt"]})
    print(f"   File deletion requires confirmation: {requires_confirmation}")
    assert requires_confirmation, "Dangerous operations should require confirmation"
    print("   ✅ PASS: Dangerous operations require confirmation")
    
    # Test 3: Complex code execution
    print("\n3. Testing complex code execution...")
    complex_code = """
import os
import subprocess
import sys
import json
import requests
from pathlib import Path
import asyncio

# This is a dangerous code example that exceeds 200 characters
result = subprocess.run(['ls', '-la', '/etc/passwd'], capture_output=True)
data = json.loads(result.stdout)
for item in data:
    print(f"Processing: {item['name']}")
    
# Additional complex operations
api_response = requests.get('https://api.example.com/data')
if api_response.status_code == 200:
    with open('/tmp/secret.txt', 'w') as f:
        f.write(api_response.text)
"""
    requires_confirmation = should_require_confirmation("execute", {
        "code": complex_code,
        "language": "python"
    })
    print(f"   Complex code requires confirmation: {requires_confirmation}")
    print(f"   Code length: {len(complex_code)} characters")
    assert requires_confirmation, "Complex code should require confirmation"
    print("   ✅ PASS: Complex code requires confirmation")
    
    # Test 4: Simple code execution (should be safe)
    print("\n4. Testing simple code execution...")
    simple_code = "print('Hello World')"
    requires_confirmation = should_require_confirmation("execute", {
        "code": simple_code,
        "language": "python"
    })
    print(f"   Simple code requires confirmation: {requires_confirmation}")
    print(f"   Code length: {len(simple_code)} characters")
    assert not requires_confirmation, "Simple code should not require confirmation"
    print("   ✅ PASS: Simple code auto-approved")
    
    # Test 5: Pending confirmations
    print("\n5. Testing pending confirmations management...")
    pending = tool_confirmation.get_pending_confirmations()
    print(f"   Current pending confirmations: {len(pending)}")
    assert len(pending) == 0, "Should have no pending confirmations initially"
    print("   ✅ PASS: Clean pending confirmations")
    
    print("\n" + "=" * 50)
    print("🎉 All Tool Confirmation System Tests Passed!")
    print("\n📋 Summary:")
    print("   ✅ Safe operations auto-approved")
    print("   ✅ Dangerous operations require confirmation")
    print("   ✅ Code complexity detection works")
    print("   ✅ Pending confirmations management")
    print("\n🔒 Production Safety Features Active:")
    print("   - File deletion confirmation")
    print("   - File overwrite confirmation") 
    print("   - Complex code execution confirmation")
    print("   - Threshold-based safety checks")

if __name__ == "__main__":
    asyncio.run(test_confirmation_system())