# Personal AI Employee - Bronze Tier

**Status**: MVP Implementation (User Story 1)
**Version**: 0.1.0
**Python**: 3.13+

## Overview

Personal AI Employee is an autonomous agent that manages personal and business affairs 24/7. The Bronze tier establishes the foundation with:

- **Obsidian Vault**: Structured knowledge base for task management
- **Watcher Scripts**: Automated detection of tasks from Gmail or file system
- **Claude Code Integration**: AI reasoning and task processing
- **Agent Skills**: Reusable AI capabilities (email triage)

## Bronze Tier Scope

Bronze tier provides the minimal viable foundation:
- ✅ Obsidian vault with folder structure
- ✅ ONE Watcher (Gmail OR File System)
- ✅ Claude Code reads/writes vault files
- ✅ At least one Agent Skill
- ⏭️ Manual Claude triggering (no automation)

**Time Estimate**: 8-12 hours implementation

## Prerequisites

- Python 3.13+
- Obsidian v1.10.6+
- Claude Code CLI
- uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- For Gmail Watcher: Google Cloud project with Gmail API enabled
- For File System Watcher: Designated drop folder

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your paths and credentials
nano .env
```

### 3. Create Obsidian Vault

```bash
# Automated setup
python vault_setup/create_vault.py --path ~/AI_Employee_Vault
```

### 4. Run Watcher

```bash
# Gmail Watcher
python watchers/gmail_watcher.py

# OR File System Watcher
python watchers/filesystem_watcher.py
```

### 5. Process Tasks with Claude

```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action"
```

## Project Structure

```
personal-ai-employee/
├── .claude/
│   └── skills/
│       └── email-triage/
│           └── SKILL.md
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   ├── filesystem_watcher.py
│   └── config.py
├── vault_setup/
│   ├── __init__.py
│   ├── create_vault.py
│   ├── folder_structure.py
│   └── templates/
│       ├── dashboard_template.md
│       ├── handbook_template.md
│       └── task_template.md
├── tests/
│   └── integration/
├── docs/
│   ├── setup_guide.md
│   ├── gmail_api_setup.md
│   └── troubleshooting.md
├── pyproject.toml
├── .env.example
└── README.md
```

## Documentation

- **Setup Guide**: `docs/setup_guide.md` - Detailed setup instructions
- **Gmail API Setup**: `docs/gmail_api_setup.md` - OAuth2 credential setup
- **Troubleshooting**: `docs/troubleshooting.md` - Common issues and solutions
- **Quickstart**: `specs/001-bronze-tier/quickstart.md` - Step-by-step validation

## Bronze Tier Completion Checklist

Use this checklist to verify your Bronze tier implementation is complete and functional:

### Vault Setup
- [ ] Vault created at configured path with all 8 folders
- [ ] Dashboard.md and Company_Handbook.md templates present
- [ ] All folders writable by watcher process
- [ ] Vault opens successfully in Obsidian

### Watcher Configuration
- [ ] .env file configured with correct paths
- [ ] Watcher type selected (gmail or filesystem)
- [ ] For Gmail: OAuth credentials downloaded and configured
- [ ] For Gmail: Token generated successfully after first auth
- [ ] For File System: Watch directory created and accessible
- [ ] Watcher starts without errors in test mode

### Task Detection
- [ ] Watcher detects new items (emails or files)
- [ ] Task files created in /Needs_Action with proper YAML frontmatter
- [ ] Task filenames follow naming convention (TYPE_TIMESTAMP_slug.md)
- [ ] No duplicate task files created for same item
- [ ] Logs written to /Logs folder in JSON format

### Claude Code Integration
- [ ] Claude Code CLI installed and authenticated
- [ ] Claude can read task files from /Needs_Action
- [ ] Claude can create plan files in /Plans
- [ ] Claude can move completed tasks to /Done
- [ ] Claude respects Company_Handbook.md rules

### Agent Skills
- [ ] email-triage skill present in .claude/skills/
- [ ] Skill has valid YAML frontmatter
- [ ] Skill includes Instructions and Examples sections
- [ ] Claude automatically applies skill when processing email tasks

### End-to-End Workflow
- [ ] Complete workflow tested: detection → task file → Claude processing → plan creation → task completion
- [ ] Watcher runs continuously for at least 1 hour without crashes
- [ ] Multiple tasks processed successfully
- [ ] Error handling works (watcher continues after transient failures)

### Documentation
- [ ] Setup guide reviewed and accurate
- [ ] Troubleshooting guide covers common issues
- [ ] Gmail API setup guide (if using Gmail Watcher) followed successfully

**Bronze Tier Complete**: All checkboxes above should be checked before moving to Silver tier.

## Next Steps: Silver Tier Preview

After Bronze tier is working, Silver tier adds:

### Silver Tier Enhancements (20-30 hours)

**Dual Watchers**:
- Run both Gmail and File System watchers simultaneously
- Unified task queue in /Needs_Action
- Separate log streams for each watcher

**Email Sending (MCP Server)**:
- Custom MCP server for sending emails via Gmail API
- Claude can draft and send email responses
- Email templates for common responses
- Sent email tracking in vault

**Human-in-the-Loop (HITL) Approval**:
- /Pending_Approval folder for tasks requiring approval
- Approval thresholds from Company_Handbook.md enforced
- Approval workflow: pending → approved/rejected → execution
- Notification system for pending approvals

**Persistent State**:
- SQLite database for processed_items tracking
- Watcher state persists across restarts
- No duplicate processing after restart
- Task history and audit trail

**Enhanced Skills**:
- file-processor skill for document analysis
- meeting-scheduler skill for calendar integration
- expense-tracker skill for financial tasks

**Testing & Validation**:
- Automated integration tests (pytest)
- 24-hour continuous operation validation
- Performance benchmarks (tasks/hour, latency)
- Error recovery testing

### Gold Tier (40+ hours)
- Odoo ERP integration for business operations
- Social media monitoring and posting
- Ralph Wiggum autonomous loop (self-directed task discovery)
- CEO daily briefing generation

### Platinum Tier (60+ hours)
- Cloud deployment (AWS/GCP)
- 24/7 operation with monitoring
- Multi-user support
- Advanced analytics dashboard

## Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: See `/docs` folder for detailed guides
- **Specifications**: See `/specs/001-bronze-tier/` for complete design documents

## License

MIT License - see [LICENSE](LICENSE) file for details.

Open source and free to use, modify, and distribute.
