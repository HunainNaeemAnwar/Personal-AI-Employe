# Quickstart: Silver Tier - Enhanced Automation

**Feature**: 002-silver-tier
**Date**: 2026-03-09
**Prerequisites**: Bronze tier implementation complete and functional

## Overview

This quickstart guide walks you through setting up Silver tier enhancements on top of your working Bronze tier foundation. Estimated setup time: 3-4 hours.

---

## Prerequisites Checklist

Before starting Silver tier setup, verify Bronze tier is working:

- [ ] Obsidian vault exists with all 8 folders
- [ ] One watcher (Gmail OR File System) running successfully
- [ ] Claude Code can read/write vault files
- [ ] At least one Agent Skill (email-triage) present
- [ ] Python 3.13+ virtual environment active
- [ ] `.env` file configured with Bronze tier credentials

---

## Step 1: Update Dependencies (15 minutes)

### 1.1 Update pyproject.toml

Add new Silver tier dependencies:

```bash
cd /home/hunain/personal-ai-employee
```

Edit `pyproject.toml` to add:

```toml
[project]
dependencies = [
    # Bronze tier (existing)
    "google-api-python-client>=2.100.0",
    "google-auth-oauthlib>=1.1.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0",
    "watchdog>=3.0.0",

    # Silver tier (new)
    "fastmcp>=0.1.0",           # MCP server framework
    "linkedin-api>=2.0.0",      # LinkedIn API client
    "selenium>=4.15.0",         # LinkedIn scraping fallback
    "beautifulsoup4>=4.12.0",   # HTML parsing
    "pytest>=7.4.0",            # Testing framework
    "pytest-asyncio>=0.21.0",   # Async test support
]
```

### 1.2 Install Dependencies

```bash
uv pip install -e .
```

---

## Step 2: Configure LinkedIn API (30 minutes)

### 2.1 Get LinkedIn API Credentials

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Create new app: "Personal AI Employee"
3. Request API access for:
   - `r_basicprofile` (read profile)
   - `r_emailaddress` (read email)
   - `w_member_social` (post updates)
4. Note your Client ID and Client Secret

### 2.2 Update .env File

Add LinkedIn credentials to `.env`:

```bash
# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_ACCESS_TOKEN=  # Will be generated on first run
LINKEDIN_POLLING_INTERVAL=300  # 5 minutes
```

### 2.3 Test LinkedIn Connection

```bash
python -c "from linkedin_api import Linkedin; print('LinkedIn API ready')"
```

---

## Step 3: Initialize State Database (10 minutes)

### 3.1 Create State Manager

The state database will be created automatically on first watcher run. To initialize manually:

```bash
python -c "
from watchers.state_manager import StateManager
sm = StateManager('state.db')
print('State database initialized')
"
```

### 3.2 Verify Database

```bash
sqlite3 state.db "SELECT * FROM schema_version;"
# Expected output: 1|2026-03-09T...
```

---

## Step 4: Set Up MCP Email Server (45 minutes)

### 4.1 Create MCP Server Directory

```bash
mkdir -p mcp_servers/email_sender
touch mcp_servers/__init__.py
touch mcp_servers/email_sender/__init__.py
```

### 4.2 Configure Gmail API for Sending

Your existing Gmail credentials need send permissions. Update OAuth2 scopes:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to your existing project
3. APIs & Services → Credentials
4. Edit OAuth 2.0 Client ID
5. Add scopes:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.compose`
6. Delete existing `token.json` (will regenerate with new scopes)

### 4.3 Test MCP Server

```bash
# Start MCP server in test mode
python mcp_servers/email_sender/server.py --test

# In another terminal, test with Claude Code
claude "Test email MCP server by sending test email to myself"
```

---

## Step 5: Create New Agent Skills (30 minutes)

### 5.1 LinkedIn Posting Skill

```bash
mkdir -p .claude/skills/linkedin-posting
```

Create `.claude/skills/linkedin-posting/SKILL.md`:

```markdown
---
name: linkedin-posting
description: Generate professional LinkedIn posts for business updates and lead generation
version: 1.0.0
---

# LinkedIn Posting Skill

## Instructions

When creating LinkedIn posts:

1. **Analyze Context**: Review completed tasks, milestones, or business achievements
2. **Craft Message**: Write engaging post (max 3000 chars) highlighting value and insights
3. **Add Hashtags**: Include 3-5 relevant hashtags for discoverability
4. **Request Approval**: Move post to /Pending_Approval for user review

## Post Structure

- **Hook**: Attention-grabbing first line
- **Value**: Key insight or achievement
- **Context**: Brief background or story
- **Call-to-Action**: Encourage engagement (comments, shares)

## Examples

### Example 1: Milestone Achievement
```
Excited to share that our AI automation system just processed its 1000th task!

Key achievements:
- 99% uptime over 30 days
- 50% reduction in email triage time
- Zero duplicate tasks after 10 system restarts

Building autonomous systems that actually work is incredibly rewarding.

#AIAutomation #ProductivityHacks #TechInnovation
```

### Example 2: Technical Insight
```
Most AI agents fail because they're too eager to help.

The secret? Make them lazy by default.

Our watcher pattern only wakes the agent when there's real work to do. Result: 85% reduction in unnecessary API calls and 10x better reliability.

Sometimes the best code is the code that doesn't run.

#AIEngineering #SystemDesign #LessIsMore
```
```

### 5.2 Task Planning Skill

```bash
mkdir -p .claude/skills/task-planning
```

Create `.claude/skills/task-planning/SKILL.md`:

```markdown
---
name: task-planning
description: Create structured Plan.md files for multi-step task execution
version: 1.0.0
---

# Task Planning Skill

## Instructions

When processing complex tasks requiring multiple steps:

1. **Analyze Task**: Identify objective, context, and constraints
2. **Propose Actions**: List high-level actions in logical order
3. **Detail Steps**: Break down each action into executable steps
4. **Create Plan File**: Write Plan.md to /Plans folder
5. **Execute & Update**: Mark steps as completed with timestamps

## Plan Template

```markdown
---
task_id: "[TASK_FILE_NAME]"
objective: "[High-level goal]"
context: "[Background and constraints]"
completion_status: in_progress
created_at: "[ISO 8601 timestamp]"
---

# Plan: [Task Title]

## Proposed Actions

1. [Action 1]
2. [Action 2]
3. [Action 3]

## Execution Steps

### Step 1: [Action 1 Detail]
- **Status**: pending
- **Description**: [What this step does]

### Step 2: [Action 2 Detail]
- **Status**: pending
- **Description**: [What this step does]

## Reasoning Notes

[Document decision rationale and alternatives considered]
```
```

### 5.3 Approval Workflow Skill

```bash
mkdir -p .claude/skills/approval-workflow
```

Create `.claude/skills/approval-workflow/SKILL.md`:

```markdown
---
name: approval-workflow
description: Evaluate tasks against approval thresholds and manage HITL workflow
version: 1.0.0
---

# Approval Workflow Skill

## Instructions

When processing tasks, check Company_Handbook.md for approval thresholds:

1. **Evaluate Threshold**: Check if task exceeds any approval threshold
2. **Move to Pending**: If approval required, move task to /Pending_Approval
3. **Add Approval Request**: Include approval options in task file
4. **Wait for Decision**: Task remains in /Pending_Approval until user approves/rejects
5. **Execute or Reject**: Move to /Approved or /Rejected based on decision

## Approval Thresholds (from Company_Handbook.md)

- Client communications (emails, LinkedIn messages)
- Payments or financial transactions >$500
- Contract or legal document signing
- Social media posts representing the business
- Data deletion or destructive operations

## Approval Request Format

```markdown
---
type: approval_request
task_id: "[TASK_FILE_NAME]"
approval_threshold_exceeded: "[THRESHOLD_NAME]"
requested_timestamp: "[ISO 8601]"
approval_decision: pending
---

# Approval Required: [Task Title]

**Threshold Exceeded**: [Threshold Name]

**Proposed Action**: [What will be done]

**Approval Options**:
- Approve: `claude "approve task [TASK_ID]"`
- Reject: `claude "reject task [TASK_ID] --reason 'Your reason'"`
```
```

---

## Step 6: Configure Watchers (30 minutes)

### 6.1 Update Existing Watchers

Both Gmail and File System watchers need state manager integration:

```bash
# Test Gmail watcher with state persistence
python watchers/gmail_watcher.py --test

# Test File System watcher with state persistence
python watchers/filesystem_watcher.py --test
```

### 6.2 Set Up LinkedIn Watcher

```bash
# First run will prompt for LinkedIn authentication
python watchers/linkedin_watcher.py --setup

# Test LinkedIn watcher
python watchers/linkedin_watcher.py --test
```

### 6.3 Configure Orchestrator

The orchestrator manages all three watchers:

```bash
# Test orchestrator (runs all watchers for 5 minutes)
python watchers/orchestrator.py --test --duration 300
```

---

## Step 7: Set Up Automated Scheduling (30 minutes)

### 7.1 Linux/Mac: Configure Cron

```bash
# Edit crontab
crontab -e

# Add scheduled tasks (example: daily morning briefing at 8 AM)
0 8 * * * cd /home/hunain/personal-ai-employee && /home/hunain/personal-ai-employee/.venv/bin/python -c "from scheduler.cron_setup import run_scheduled_task; run_scheduled_task('daily_morning_briefing')" >> /home/hunain/personal-ai-employee/AI_Employee_Vault/Logs/cron.log 2>&1

# Add weekly LinkedIn post (every Monday at 9 AM)
0 9 * * 1 cd /home/hunain/personal-ai-employee && /home/hunain/personal-ai-employee/.venv/bin/python -c "from scheduler.cron_setup import run_scheduled_task; run_scheduled_task('weekly_linkedin_post')" >> /home/hunain/personal-ai-employee/AI_Employee_Vault/Logs/cron.log 2>&1
```

### 7.2 Windows: Configure Task Scheduler

```powershell
# Run setup script
python scheduler/task_scheduler_setup.py

# This will create:
# - Daily morning briefing (8:00 AM)
# - Weekly LinkedIn post (Monday 9:00 AM)
```

---

## Step 8: Validation & Testing (30 minutes)

### 8.1 End-to-End Test: Dual Watchers

```bash
# Terminal 1: Start orchestrator
python watchers/orchestrator.py

# Terminal 2: Send test email to yourself
# Terminal 3: Drop test file in watch directory
# Terminal 4: Send LinkedIn message to yourself

# Wait 5 minutes, then check vault
ls AI_Employee_Vault/Needs_Action/
# Expected: 3 task files (email, file, LinkedIn message)

# Check state database
sqlite3 state.db "SELECT source, status FROM processed_items;"
# Expected: 3 rows with status 'processed'
```

### 8.2 Test Email Sending

```bash
# Process an email task that requires response
cd AI_Employee_Vault
claude "Process EMAIL task and draft response"

# Approve the draft
claude "approve task EMAIL_20260309T143000Z_test-email"

# Verify email was sent (check Gmail Sent folder)
```

### 8.3 Test LinkedIn Posting

```bash
# Create a LinkedIn post task
cd AI_Employee_Vault
claude "Create LinkedIn post about completing Silver tier setup"

# Review post in /Pending_Approval
# Approve post
claude "approve task LINKEDIN_POST_20260309T170000Z_silver-tier-complete"

# Verify post on LinkedIn profile
```

### 8.4 Test State Persistence

```bash
# Stop orchestrator (Ctrl+C)
# Restart orchestrator
python watchers/orchestrator.py

# Send same test email again
# Expected: No duplicate task file created

# Check logs
tail -f AI_Employee_Vault/Logs/gmail_watcher.log
# Expected: "Item already processed: [email_id]"
```

---

## Step 9: Update Documentation (15 minutes)

### 9.1 Update README.md

Add Silver tier status to README:

```markdown
**Status**: Silver Tier Implementation
**Version**: 0.2.0
```

### 9.2 Update Company_Handbook.md

Add approval thresholds:

```markdown
## Approval Thresholds

The following actions require human approval before execution:

1. **Client Communications**: All emails to clients or partners
2. **Financial Transactions**: Payments or transfers >$500
3. **Social Media Posts**: LinkedIn posts representing the business
4. **Data Operations**: Deletions or destructive operations
5. **Legal Documents**: Contract signing or legal commitments
```

---

## Troubleshooting

### Issue: LinkedIn API Rate Limit

**Symptom**: `linkedin_watcher.log` shows "Rate limit exceeded"

**Solution**:
```bash
# Increase polling interval in .env
LINKEDIN_POLLING_INTERVAL=600  # 10 minutes instead of 5
```

### Issue: State Database Locked

**Symptom**: `sqlite3.OperationalError: database is locked`

**Solution**:
```bash
# Stop all watchers
pkill -f "python watchers/"

# Restart orchestrator
python watchers/orchestrator.py
```

### Issue: MCP Server Not Found

**Symptom**: Claude Code says "Email MCP server not available"

**Solution**:
```bash
# Verify MCP server is running
ps aux | grep email_sender

# Restart MCP server
python mcp_servers/email_sender/server.py
```

### Issue: Duplicate Tasks After Restart

**Symptom**: Same email creates multiple task files

**Solution**:
```bash
# Check state database
sqlite3 state.db "SELECT * FROM processed_items WHERE source='gmail';"

# If empty, watchers aren't using state manager
# Verify watchers import StateManager correctly
```

---

## Silver Tier Completion Checklist

Use this checklist to verify Silver tier is fully functional:

### Dual Watchers
- [ ] Gmail watcher running continuously
- [ ] File System watcher running continuously
- [ ] LinkedIn watcher running continuously
- [ ] Orchestrator manages all three watchers
- [ ] Health checks show all watchers active

### Email Sending
- [ ] MCP email server running
- [ ] Test email sent successfully
- [ ] Email threading works (replies preserve conversation)
- [ ] Attachments can be sent
- [ ] Sent emails logged to /Logs

### LinkedIn Integration
- [ ] LinkedIn messages detected and converted to tasks
- [ ] LinkedIn posts can be created and approved
- [ ] Posts published successfully to LinkedIn
- [ ] Post performance metrics tracked

### State Persistence
- [ ] State database created (state.db)
- [ ] No duplicate tasks after restart (tested 3x)
- [ ] Processed items table populated
- [ ] State queries working correctly

### Human-in-the-Loop
- [ ] Tasks move to /Pending_Approval when threshold exceeded
- [ ] Approval commands work (approve/reject)
- [ ] Approved tasks execute successfully
- [ ] Rejected tasks move to /Rejected with reason

### Claude Reasoning Loop
- [ ] Plan.md files created for multi-step tasks
- [ ] Plans include reasoning notes
- [ ] Execution steps tracked with timestamps
- [ ] Plans updated as tasks progress

### Automated Scheduling
- [ ] Cron jobs configured (Linux/Mac) OR Task Scheduler (Windows)
- [ ] Daily briefing runs at scheduled time
- [ ] Weekly LinkedIn post runs at scheduled time
- [ ] Scheduled task logs written to /Logs

### Agent Skills
- [ ] email-triage skill working (Bronze tier)
- [ ] linkedin-posting skill working
- [ ] task-planning skill working
- [ ] approval-workflow skill working

### End-to-End Workflow
- [ ] Complete workflow tested: detection → task → plan → approval → execution → logging
- [ ] All three watchers run simultaneously for 1 hour without crashes
- [ ] Multiple tasks processed successfully across all sources
- [ ] Error handling works (watchers continue after transient failures)

**Silver Tier Complete**: All checkboxes above should be checked before moving to Gold tier.

---

## Next Steps: Gold Tier Preview

After Silver tier is working, Gold tier adds:

- **Odoo ERP Integration**: Accounting system with MCP server
- **Social Media Expansion**: Facebook, Instagram, Twitter (X) integration
- **Ralph Wiggum Loop**: Autonomous multi-step task completion
- **CEO Briefing**: Weekly business and accounting audit
- **Advanced Error Recovery**: Graceful degradation and self-healing

Estimated Gold tier implementation time: 40+ hours

---

## Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: See `/docs` folder for detailed guides
- **Specifications**: See `/specs/002-silver-tier/` for complete design documents
- **Research Meetings**: Join Wednesday 10 PM Zoom sessions for community support
