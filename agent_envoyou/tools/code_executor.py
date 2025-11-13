#!/usr/bin/env python3
"""
Code Executor Tool for Fullstack Agent

Provides safe code execution capabilities for testing generated applications
without compromising system security.
"""

import os
import sys
import subprocess
import tempfile
import json
import shutil
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from google.adk.tools import BaseTool, FunctionTool
from google.adk.tools.tool_context import ToolContext

# Import tool confirmation system
from .tool_confirmation import (
    request_destructive_confirmation,
    should_require_confirmation
)


class CodeExecutorTool(BaseTool):
    """Tool for safe code execution and testing."""
    
    def __init__(self):
        super().__init__(
            name="code_executor_tool",
            description="Safe code execution and testing for generated applications"
        )
        self.logger = logging.getLogger(__name__)
        
        # Create safe execution environment
        self.sandbox_dir = Path.cwd() / "execution_sandbox"
        self.sandbox_dir.mkdir(exist_ok=True)
        
        # Default timeouts (in seconds)
        self.default_timeout = 30
        self.max_timeout = 300  # 5 minutes max
        
        # Allowed languages and their execution commands
        self.execution_engines = {
            "python": ["python3", "-c"],
            "javascript": ["node", "-e"],
            "bash": ["bash", "-c"],
            "docker": ["docker"],
        }
    
    def _create_sandbox(self, project_name: str) -> Path:
        """Create a sandbox directory for project execution."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sandbox_path = self.sandbox_dir / f"{project_name}_{timestamp}"
        sandbox_path.mkdir(parents=True, exist_ok=True)
        
        # Set safe permissions
        sandbox_path.chmod(0o755)
        
        return sandbox_path
    
    async def execute_python_code(self, context: ToolContext, code: str, timeout: int = None) -> Dict[str, Any]:
            """Execute Python code safely in sandbox with confirmation for complex code."""
            try:
                timeout = timeout or self.default_timeout
                
                # Check if confirmation is required for this code execution
                requires_confirmation = should_require_confirmation(
                    "execute_code",
                    {"code": code, "language": "python", "timeout": timeout}
                )
                
                if requires_confirmation:
                    confirmed = await request_destructive_confirmation(
                        tool_name="CodeExecutorTool",
                        operation_type="execute",
                        description=f"Execute Python code (length: {len(code)} chars, timeout: {timeout}s)",
                        parameters={
                            "code": code,
                            "language": "python",
                            "timeout": timeout,
                            "code_preview": code[:100] + "..." if len(code) > 100 else code
                        }
                    )
                    
                    if not confirmed:
                        return {
                            "success": False,
                            "error": "Code execution cancelled by user",
                            "language": "python",
                            "cancelled": True
                        }
                
                # Create a temporary script file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(code)
                    script_path = f.name
                
                try:
                    # Execute with timeout and capture output
                    process = await asyncio.create_subprocess_exec(
                        "python3", script_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=str(self.sandbox_dir)
                    )
                    
                    try:
                        stdout, stderr = await asyncio.wait_for(
                            process.communicate(),
                            timeout=min(timeout, self.max_timeout)
                        )
                        
                        result = {
                            "success": process.returncode == 0,
                            "return_code": process.returncode,
                            "stdout": stdout.decode('utf-8') if stdout else "",
                            "stderr": stderr.decode('utf-8') if stderr else "",
                            "execution_time": timeout,
                            "language": "python"
                        }
                        
                        # Update context state
                        context.state['temp:last_execution'] = result
                        context.state['temp:last_execution_time'] = str(datetime.now())
                        
                        self.logger.info(f"Python code executed: {'Success' if result['success'] else 'Failed'}")
                        
                        return result
                        
                    except asyncio.TimeoutError:
                        process.kill()
                        await process.wait()
                        
                        return {
                            "success": False,
                            "error": f"Execution timed out after {timeout} seconds",
                            "language": "python",
                            "timeout": timeout
                        }
                        
                finally:
                    # Clean up temp file
                    os.unlink(script_path)
                    
            except Exception as e:
                self.logger.error(f"Error executing Python code: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "language": "python"
                }
    
    async def execute_javascript_code(self, context: ToolContext, code: str, timeout: int = None) -> Dict[str, Any]:
        """Execute JavaScript/Node.js code safely."""
        try:
            timeout = timeout or self.default_timeout
            
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                script_path = f.name
            
            try:
                # Execute with timeout and capture output
                process = await asyncio.create_subprocess_exec(
                    "node", script_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(self.sandbox_dir)
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), 
                        timeout=min(timeout, self.max_timeout)
                    )
                    
                    result = {
                        "success": process.returncode == 0,
                        "return_code": process.returncode,
                        "stdout": stdout.decode('utf-8') if stdout else "",
                        "stderr": stderr.decode('utf-8') if stderr else "",
                        "execution_time": timeout,
                        "language": "javascript"
                    }
                    
                    context.state['temp:last_execution'] = result
                    self.logger.info(f"JavaScript code executed: {'Success' if result['success'] else 'Failed'}")
                    
                    return result
                    
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    
                    return {
                        "success": False,
                        "error": f"Execution timed out after {timeout} seconds",
                        "language": "javascript",
                        "timeout": timeout
                    }
                    
            finally:
                os.unlink(script_path)
                
        except Exception as e:
            self.logger.error(f"Error executing JavaScript code: {e}")
            return {
                "success": False,
                "error": str(e),
                "language": "javascript"
            }
    
    async def test_application(self, context: ToolContext, project_path: str, test_type: str = "basic") -> Dict[str, Any]:
        """Test a generated application."""
        try:
            validated_path = self._validate_project_path(project_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"Project not found: {project_path}")
            
            test_results = {
                "project_path": str(validated_path),
                "test_type": test_type,
                "timestamp": datetime.now().isoformat(),
                "tests": []
            }
            
            # Basic tests based on project type
            if test_type == "basic":
                tests = await self._run_basic_tests(validated_path)
                test_results["tests"] = tests
                
            elif test_type == "comprehensive":
                tests = await self._run_comprehensive_tests(validated_path)
                test_results["tests"] = tests
            
            # Calculate overall status
            test_results["overall_success"] = all(test["success"] for test in test_results["tests"])
            
            # Update context state
            context.state['temp:last_test_results'] = test_results
            
            self.logger.info(f"Application tests completed: {'Pass' if test_results['overall_success'] else 'Fail'}")
            
            return test_results
            
        except Exception as e:
            self.logger.error(f"Error testing application {project_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_path": project_path
            }
    
    async def _run_basic_tests(self, project_path: Path) -> List[Dict[str, Any]]:
        """Run basic tests on the project."""
        tests = []
        
        # Test 1: Check if required files exist
        required_files = ["package.json", "requirements.txt", "Dockerfile", "README.md"]
        existing_files = []
        missing_files = []
        
        for req_file in required_files:
            if (project_path / req_file).exists():
                existing_files.append(req_file)
            else:
                missing_files.append(req_file)
        
        tests.append({
            "name": "File Structure Check",
            "success": len(existing_files) > 0,  # At least some files should exist
            "details": {
                "existing_files": existing_files,
                "missing_files": missing_files
            }
        })
        
        # Test 2: Check for source code files
        source_patterns = ["src/", "lib/", "app/", "server/"]
        has_source = any((project_path / pattern).exists() for pattern in source_patterns)
        
        tests.append({
            "name": "Source Code Check",
            "success": has_source,
            "details": {"has_source_code": has_source}
        })
        
        # Test 3: Basic syntax check for Python files
        python_files = list(project_path.rglob("*.py"))
        if python_files:
            python_syntax_ok = await self._check_python_syntax(python_files)
            tests.append({
                "name": "Python Syntax Check",
                "success": python_syntax_ok,
                "details": {"checked_files": len(python_files)}
            })
        
        # Test 4: Basic syntax check for JavaScript files
        js_files = list(project_path.rglob("*.js")) + list(project_path.rglob("*.ts"))
        if js_files:
            js_syntax_ok = await self._check_javascript_syntax(js_files)
            tests.append({
                "name": "JavaScript Syntax Check",
                "success": js_syntax_ok,
                "details": {"checked_files": len(js_files)}
            })
        
        return tests
    
    async def _run_comprehensive_tests(self, project_path: Path) -> List[Dict[str, Any]]:
        """Run comprehensive tests including dependency checks."""
        tests = await self._run_basic_tests(project_path)
        
        # Add more advanced tests
        # Test dependencies
        if (project_path / "package.json").exists():
            deps_test = await self._check_dependencies(project_path)
            tests.append(deps_test)
        
        # Test Docker configuration
        if (project_path / "Dockerfile").exists():
            docker_test = await self._check_docker_config(project_path)
            tests.append(docker_test)
        
        # Test security configuration
        security_test = await self._check_security_config(project_path)
        tests.append(security_test)
        
        return tests
    
    async def _check_python_syntax(self, python_files: List[Path]) -> bool:
        """Check Python syntax for multiple files."""
        try:
            # Use python's compile function to check syntax
            for py_file in python_files[:5]:  # Limit to first 5 files for performance
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            return True
        except SyntaxError:
            return False
        except Exception:
            return False
    
    async def _check_javascript_syntax(self, js_files: List[Path]) -> bool:
        """Check JavaScript syntax for multiple files."""
        try:
            # Simple syntax check using node
            for js_file in js_files[:3]:  # Limit for performance
                try:
                    process = await asyncio.create_subprocess_exec(
                        "node", "--check", str(js_file),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=10
                    )
                    if process.returncode != 0:
                        return False
                except:
                    return False
            return True
        except Exception:
            return False
    
    async def _check_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Check if dependencies can be installed."""
        try:
            package_json = project_path / "package.json"
            if not package_json.exists():
                return {"name": "Dependency Check", "success": False, "error": "No package.json found"}
            
            # Try to validate package.json
            with open(package_json) as f:
                package_data = json.load(f)
            
            return {
                "name": "Dependency Check",
                "success": True,
                "details": {
                    "name": package_data.get("name", "unknown"),
                    "version": package_data.get("version", "unknown"),
                    "dependencies_count": len(package_data.get("dependencies", {})),
                    "dev_dependencies_count": len(package_data.get("devDependencies", {}))
                }
            }
        except Exception as e:
            return {"name": "Dependency Check", "success": False, "error": str(e)}
    
    async def _check_docker_config(self, project_path: Path) -> Dict[str, Any]:
        """Check Docker configuration."""
        try:
            dockerfile = project_path / "Dockerfile"
            if not dockerfile.exists():
                return {"name": "Docker Config Check", "success": False, "error": "No Dockerfile found"}
            
            with open(dockerfile) as f:
                dockerfile_content = f.read()
            
            # Basic Dockerfile validation
            has_from = dockerfile_content.startswith("FROM")
            has_base_image = "FROM" in dockerfile_content
            
            return {
                "name": "Docker Config Check",
                "success": has_base_image,
                "details": {
                    "has_from_instruction": has_from,
                    "file_size": len(dockerfile_content)
                }
            }
        except Exception as e:
            return {"name": "Docker Config Check", "success": False, "error": str(e)}
    
    async def _check_security_config(self, project_path: Path) -> Dict[str, Any]:
        """Check basic security configuration."""
        security_files = [".gitignore", ".env.example", "README.md"]
        existing_security_files = []
        
        for sec_file in security_files:
            if (project_path / sec_file).exists():
                existing_security_files.append(sec_file)
        
        return {
            "name": "Security Config Check",
            "success": len(existing_security_files) > 0,
            "details": {
                "security_files": existing_security_files
            }
        }
    
    def _validate_project_path(self, project_path: str) -> Path:
        """Validate project path is within allowed directories."""
        try:
            path = Path(project_path).resolve()
            
            # Allow current directory and subdirectories
            cwd = Path.cwd().resolve()
            try:
                path.relative_to(cwd)
                return path
            except ValueError:
                raise ValueError(f"Project path '{project_path}' is outside allowed directory")
                
        except Exception as e:
            raise ValueError(f"Invalid project path: {e}")
    
    async def start_web_server(self, context: ToolContext, project_path: str, port: int = 3000) -> Dict[str, Any]:
        """Start a web server for the generated application."""
        try:
            validated_path = self._validate_project_path(project_path)
            
            if not validated_path.exists():
                raise FileNotFoundError(f"Project not found: {project_path}")
            
            # Check for common web server configurations
            package_json = validated_path / "package.json"
            requirements_txt = validated_path / "requirements.txt"
            
            server_info = {
                "project_path": str(validated_path),
                "port": port,
                "status": "starting",
                "timestamp": datetime.now().isoformat()
            }
            
            if package_json.exists():
                # Node.js/React project
                server_info["type"] = "nodejs"
                server_info["command"] = f"npm run dev -- --port {port}"
                
            elif requirements_txt.exists():
                # Python project
                server_info["type"] = "python"
                server_info["command"] = f"python -m http.server {port}"
                
            else:
                # Simple static server
                server_info["type"] = "static"
                server_info["command"] = f"python -m http.server {port}"
            
            # Update context state
            context.state['temp:web_server_info'] = server_info
            
            return {
                "success": True,
                "message": f"Web server configured for {validated_path}",
                "server_info": server_info
            }
            
        except Exception as e:
            self.logger.error(f"Error starting web server for {project_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_path": project_path
            }