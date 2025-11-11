## 🐛 Bug Report Template

### 🔍 **Bug Description**
A clear and concise description of what the bug is.

**Example:** "The BackendWriterAgent fails to generate API endpoints when using PostgreSQL configuration."

### 🚨 **Is your bug report related to a problem?**

- [ ] ✨ I'm reporting a bug in the multi-agent system
- [ ] 🔧 I'm reporting a bug in agent configuration
- [ ] 📝 I'm reporting a bug in documentation
- [ ] 🧪 I'm reporting a bug in tests
- [ ] 🔄 I'm reporting a bug in the workflow

### 🖥️ **Environment Information**
Complete the following information about your environment:

**Operating System:**
- [ ] Linux (Ubuntu/Debian)
- [ ] Linux (CentOS/RHEL)
- [ ] macOS
- [ ] Windows
- [ ] Other: ___________

**Python Version:**
- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12
- [ ] Other: ___________

**Project Version:**
- [ ] Latest main branch
- [ ] Specific tag/version: ___________
- [ ] Development branch: ___________

**Google ADK Version:**
- [ ] Latest stable
- [ ] Specific version: ___________

### 🐛 **Which agent(s) are affected?**
Mark all that apply:

- [ ] 🔥 Root Agent (FullstackManagerAgent)
- [ ] 🎨 Frontend Team
  - [ ] FrontendWriterAgent
  - [ ] FrontendReviewerAgent  
  - [ ] FrontendRefactorAgent
- [ ] ⚙️ Backend Team
  - [ ] BackendWriterAgent
  - [ ] BackendReviewerAgent
  - [ ] BackendRefactorAgent
- [ ] 🔄 Agent Orchestration
- [ ] 📋 Configuration Loading
- [ ] 🔌 Model Integration

### 🕒 **Current Behavior**
A clear description of what happens.

**Example:** "When running the agent system, the backend agents fail to load their YAML configurations and throw a FileNotFoundError."

### ⏳ **Expected Behavior**  
A clear description of what you expected to happen.

**Example:** "The agent system should successfully load all YAML configurations and initialize all agents without errors."

### 📸 **Screenshots/Logs**
If applicable, add screenshots or log outputs that demonstrate the problem:

```
# Paste relevant error logs, agent outputs, or configuration errors here
```

### 🔧 **Configuration Files**
Please provide relevant configuration snippets:

**Root Agent Config:**
```yaml
# Paste relevant part of root_agent.yaml here
```

**Affected Agent Config:**
```yaml
# Paste relevant part of the affected agent's YAML config here
```

**Agent.py Relevant Code:**
```python
# Paste relevant code from agent.py if applicable
```

### 🧪 **Steps to Reproduce**
Steps to reproduce the behavior:

1. Run `python agent.py`
2. Observe the error
3. Check agent initialization
4. See error/failure

**Minimal reproduction steps:**
1. Step 1: ___________
2. Step 2: ___________
3. Step 3: ___________
4. Error occurs

### 💻 **Additional Context**
Add any other context about the problem here.

**Environment Variables:**
```bash
# Relevant .env variables
```

**Dependencies:**
```bash
# Output of `pip list | grep -E "(google|yaml|pyyaml)"` if relevant
```

### 🎯 **What were you trying to do?**
Describe the task or feature you were trying to use when the bug occurred.

**Example:** "I was trying to generate a complete web application with user authentication using the multi-agent system."

### 🚑 **How severe is this bug?**
- [ ] 🔴 Critical - System completely unusable
- [ ] 🟠 High - Major functionality broken
- [ ] 🟡 Medium - Functionality impaired
- [ ] 🟢 Low - Minor issue or cosmetic

### 🔄 **Reproduction Rate**
- [ ] Always reproducible
- [ ] Often reproducible
- [ ] Sometimes reproducible
- [ ] Rarely reproducible

### 🔍 **Possible Root Cause**
Do you have any ideas about what might be causing this issue?

**Examples:**
- YAML configuration syntax error
- Missing required environment variables
- Agent model compatibility issue
- File path/permission issues
- Agent instruction conflicts

### 🔧 **Suggested Fix**
If you have ideas for how to fix this, please share them:

### 🎆 **Workarounds**
Are there any workarounds you've found to temporarily resolve this issue?

### 📊 **Agent Performance Impact**
- [ ] No impact on agent performance
- [ ] Minor performance degradation
- [ ] Significant performance impact
- [ ] System becomes unresponsive

### 🔐 **Security Implications**
- [ ] No security implications
- [ ] Potential security concerns identified
- [ ] Sensitive data exposure risk
- [ ] Authentication/authorization bypass

---

### 📋 **For Maintainers Only**

**Triage Priority:**
- [ ] P0 - Critical/Blocking
- [ ] P1 - High priority
- [ ] P2 - Medium priority
- [ ] P3 - Low priority

**Affected Components:**
- [ ] Core agent orchestration
- [ ] Configuration system
- [ ] Agent creation/loading
- [ ] Model integration
- [ ] Workflow management
- [ ] Error handling
- [ ] Documentation
- [ ] Tests

**Reproducibility:**
- [ ] Can reproduce in clean environment
- [ ] Requires specific setup
- [ ] Intermittent issue
- [ ] Platform-specific

**Related Issues/PRs:**
- [ ] Links to related issues or PRs
- [ ] Duplicate of issue: #(issue_number)
- [ ] Related to PR: #(pr_number)

**Fix Strategy:**
- [ ] Configuration fix needed
- [ ] Code change required
- [ ] Documentation update
- [ ] Test addition needed
- [ ] Breaking change required