# Personal AI Employee - Silver Tier

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

**Status**: Enhanced Automation Implementation
**Version**: 0.2.0
**Python**: 3.13+

## Overview

Personal AI Employee is an autonomous agent that manages personal and business affairs 24/7. The Silver tier builds on Bronze with enhanced automation:

- **Dual Watchers**: Concurrent Gmail and File System monitoring with orchestrator
- **Email Sending**: MCP server for sending email responses via Gmail API
- **LinkedIn Integration**: Monitor messages and post updates automatically
- **State Persistence**: SQLite database prevents duplicate processing across restarts
- **Approval Workflow**: Human-in-the-loop for sensitive actions (HITL)
- **Planning Loop**: Structured Plan.md files for multi-step task reasoning
- **Scheduled Tasks**: Automated execution of recurring tasks (cron/Task Scheduler)

## Silver Tier Scope

Silver tier provides enhanced automation and reliability:
- ✅ Dual watchers (Gmail AND File System) with orchestrator
- ✅ Email sending via MCP server (Gmail API)
- ✅ LinkedIn integration (messages and posts)
- ✅ State persistence (SQLite database)
- ✅ Human-in-the-loop approval workflow
- ✅ Structured planning loop (Plan.md files)
- ✅ Scheduled task execution (cron/Task Scheduler)

**Time Estimate**: 20-30 hours implementation (on top of Bronze tier)

## Prerequisites

- Python 3.13+
- Node.js v24+ (for MCP email server)
- Obsidian v1.10.6+
- Claude Code CLI
- uv package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Google Cloud project with Gmail API enabled (for Gmail watcher and email sending)
- LinkedIn account credentials (for LinkedIn integration)
- Cron (Linux/Mac) or Task Scheduler (Windows) for scheduled tasks

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment and install Python dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install Node.js dependencies for MCP email server
cd mcp_servers/email_sender
npm install
npm run build
cd ../..
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your paths and credentials
nano .env
```

**Required Configuration:**
- `VAULT_PATH`: Path to Obsidian vault
- `GMAIL_CREDENTIALS_PATH`: Path to Gmail OAuth credentials
- `LINKEDIN_USERNAME`: LinkedIn account username
- `LINKEDIN_PASSWORD`: LinkedIn account password
- `ORCHESTRATOR_WATCHERS`: Comma-separated list of watchers (gmail,filesystem,linkedin)

### 3. Create Obsidian Vault

```bash
# Automated setup
python vault_setup/create_vault.py --path ~/AI_Employee_Vault
```

### 4. Setup MCP Email Server

```bash
# Configure Claude Code to use email MCP server
# Add to ~/.claude/config.json:
{
  "mcpServers": {
    "email-sender": {
      "command": "node",
      "args": ["/path/to/mcp_servers/email_sender/dist/index.js"]
    }
  }
}
```

See `docs/mcp_server_setup.md` for detailed instructions.

### 5. Run Orchestrator

```bash
# Start all watchers with orchestrator
python watchers/orchestrator.py
```

The orchestrator will:
- Start Gmail, File System, and LinkedIn watchers concurrently
- Monitor watcher health with heartbeat checks
- Automatically restart crashed watchers
- Check state database health periodically

### 6. Setup Scheduled Tasks (Optional)

```bash
# Linux/Mac (cron)
python -m scheduler.cron_setup setup

# Windows (Task Scheduler)
python -m scheduler.task_scheduler_setup setup
```

See `docs/scheduling_setup.md` for detailed instructions.

### 7. Process Tasks with Claude

```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action"
```

## Project Structure

```
personal-ai-employee/
├── .claude/
│   └── skills/
│       ├── email-triage/
│       │   └── SKILL.md
│       ├── linkedin-posting/
│       │   └── SKILL.md
│       ├── approval-workflow/
│       │   └── SKILL.md
│       └── task-planning/
│           └── SKILL.md
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py
│   ├── gmail_watcher.py
│   ├── filesystem_watcher.py
│   ├── linkedin_watcher.py
│   ├── orchestrator.py
│   ├── state_manager.py
│   └── config.py
├── scheduler/
│   ├── __init__.py
│   ├── cron_setup.py
│   ├── task_scheduler_setup.py
│   └── task_executor.py
├── mcp_servers/
│   └── email_sender/
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       │   ├── index.ts
│       │   └── gmail-client.ts
│       └── dist/
├── vault_setup/
│   ├── __init__.py
│   ├── create_vault.py
│   ├── folder_structure.py
│   └── templates/
│       ├── dashboard_template.md
│       ├── handbook_template.md
│       ├── task_template.md
│       └── plan_template.md
├── tests/
│   ├── unit/
│   │   └── test_state_manager.py
│   └── integration/
│       ├── test_dual_watchers.py
│       ├── test_approval_workflow.py
│       └── test_scheduled_tasks.py
├── docs/
│   ├── setup_guide.md
│   ├── gmail_api_setup.md
│   ├── linkedin_api_setup.md
│   ├── mcp_server_setup.md
│   ├── scheduling_setup.md
│   └── troubleshooting.md
├── pyproject.toml
├── .env.example
├── scheduled_tasks.yaml
└── README.md
```

## Documentation

- **Setup Guide**: `docs/setup_guide.md` - Detailed setup instructions for Silver tier
- **Gmail API Setup**: `docs/gmail_api_setup.md` - OAuth2 credential setup
- **LinkedIn API Setup**: `docs/linkedin_api_setup.md` - LinkedIn integration setup
- **MCP Server Setup**: `docs/mcp_server_setup.md` - Email MCP server configuration
- **Scheduling Setup**: `docs/scheduling_setup.md` - Automated task scheduling
- **Troubleshooting**: `docs/troubleshooting.md` - Common issues and solutions
- **Quickstart**: `specs/002-silver-tier/quickstart.md` - Step-by-step validation

## Silver Tier Completion Checklist

Use this checklist to verify your Silver tier implementation is complete and functional:

### Dual Watchers & Orchestrator
- [ ] Orchestrator starts all three watchers (Gmail, File System, LinkedIn)
- [ ] All watchers write heartbeat files every 60 seconds
- [ ] Orchestrator detects crashed watchers and restarts them
- [ ] Orchestrator checks state database health every 5 minutes
- [ ] Logs written to /Logs/orchestrator.log, /Logs/gmail_watcher.log, /Logs/filesystem_watcher.log, /Logs/linkedin_watcher.log
- [ ] Orchestrator handles SIGTERM/SIGINT gracefully

### State Persistence
- [ ] state.db created with processed_items table
- [ ] Watchers check state database before creating tasks
- [ ] No duplicate tasks created after watcher restart
- [ ] State database health check passes
- [ ] Database backup works (creates state_backup_*.db)
- [ ] Corruption detection and recovery works

### Email Sending (MCP Server)
- [ ] MCP email server builds successfully (npm run build)
- [ ] MCP server configured in Claude Code config.json
- [ ] send_email tool available in Claude Code
- [ ] Email sending works with retry logic (3 attempts)
- [ ] Email threading works (In-Reply-To and References headers)
- [ ] Sent emails logged to /Logs/email_sent.log

### LinkedIn Integration
- [ ] LinkedIn watcher authenticates successfully
- [ ] LinkedIn messages detected and task files created
- [ ] LinkedIn posts can be created via watcher
- [ ] Rate limiting enforced (100 requests/hour)
- [ ] LinkedIn activity logged to /Logs/linkedin_watcher.log

### Approval Workflow
- [ ] Company_Handbook.md contains approval thresholds
- [ ] Tasks exceeding thresholds moved to /Pending_Approval
- [ ] Approval metadata added to task YAML frontmatter
- [ ] Approval commands work: `claude "approve task TASK_ID"`
- [ ] Rejection commands work: `claude "reject task TASK_ID --reason 'reason'"`
- [ ] Approved tasks moved to /Approved and executed
- [ ] Rejected tasks moved to /Rejected
- [ ] Approval decisions logged to /Logs/approvals.log

### Planning Loop
- [ ] .claude/skills/task-planning/SKILL.md present
- [ ] Plan.md files created for multi-step tasks in /Plans/
- [ ] Plan.md includes task analysis, proposed actions, execution steps
- [ ] Step status tracking works (pending/in_progress/completed/failed)
- [ ] Reasoning notes and alternative approaches documented
- [ ] Execution log updated as steps complete

### Scheduled Tasks
- [ ] scheduled_tasks.yaml configured with example tasks
- [ ] Cron jobs installed (Linux/Mac) or Task Scheduler tasks created (Windows)
- [ ] Morning briefing executes at 8:00 AM
- [ ] Weekly LinkedIn post task created on Mondays
- [ ] Database backup runs at 2:00 AM
- [ ] System health check runs every 6 hours
- [ ] Scheduled task execution logged to /Logs/scheduled_tasks.log
- [ ] Overlap prevention works (lock files created)
- [ ] Retry logic works for failed tasks

### Agent Skills
- [ ] email-triage skill present and functional
- [ ] linkedin-posting skill present with templates
- [ ] approval-workflow skill present with threshold logic
- [ ] task-planning skill present with Plan.md creation
- [ ] Claude automatically applies skills when processing tasks

### End-to-End Workflow
- [ ] Complete workflow tested: detection → task file → state check → Claude processing → plan creation → approval (if needed) → execution → completion
- [ ] Orchestrator runs continuously for at least 24 hours without crashes
- [ ] Multiple tasks processed successfully across all watchers
- [ ] Error handling works (watchers continue after transient failures)
- [ ] State database remains healthy over 24-hour period
- [ ] Performance benchmarks met: email detection <2min, LinkedIn polling 5min, email sending <5s

### Documentation
- [ ] Setup guide reviewed and accurate for Silver tier
- [ ] Troubleshooting guide covers Silver tier issues
- [ ] MCP server setup guide followed successfully
- [ ] LinkedIn API setup guide followed successfully
- [ ] Scheduling setup guide followed successfully

**Silver Tier Complete**: All checkboxes above should be checked before moving to Gold tier.

## Next Steps: Gold Tier Preview

After Silver tier is working, Gold tier adds:
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
