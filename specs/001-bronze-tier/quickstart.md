# Quickstart Guide: Bronze Tier - Personal AI Employee Foundation

**Estimated Setup Time**: 1-2 hours
**Difficulty**: Intermediate (requires command-line familiarity)

## Prerequisites

Before starting, ensure you have:

- [ ] **Obsidian** v1.10.6+ installed ([download](https://obsidian.md/download))
- [ ] **Python** 3.13+ installed ([download](https://www.python.org/downloads/))
- [ ] **Claude Code** CLI installed and configured ([setup guide](https://code.claude.com))
- [ ] **uv** package manager installed: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Basic command-line familiarity (terminal/bash)
- [ ] 1GB free disk space
- [ ] Stable internet connection

## Step 1: Clone Repository

```bash
git clone https://github.com/your-username/personal-ai-employee.git
cd personal-ai-employee
git checkout 001-bronze-tier
```

## Step 2: Install Python Dependencies

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

**Verify installation**:
```bash
python -c "import watchdog; print('Dependencies installed successfully')"
```

## Step 3: Create Obsidian Vault

### Option A: Automated Setup (Recommended)

```bash
python vault_setup/create_vault.py --path ~/AI_Employee_Vault
```

This creates:
- Vault at `~/AI_Employee_Vault`
- All required folders (Inbox, Needs_Action, Done, Logs, Plans, etc.)
- Dashboard.md and Company_Handbook.md templates

### Option B: Manual Setup

1. Open Obsidian
2. Click "Create new vault"
3. Name it "AI_Employee_Vault"
4. Choose location (e.g., `~/AI_Employee_Vault`)
5. Create folders manually:
   - Inbox
   - Needs_Action
   - Done
   - Logs
   - Plans
   - Pending_Approval
   - Approved
   - Rejected

6. Create `Dashboard.md`:
```markdown
# AI Employee Dashboard

## Recent Activity
*Last updated: [Auto-updated by Claude]*

## Pending Tasks
- Check /Needs_Action folder

## System Status
- Watcher: Not running
- Last check: Never
```

7. Create `Company_Handbook.md`:
```markdown
# Company Handbook

## Rules of Engagement
- Always be professional in communications
- Prioritize urgent tasks (keywords: urgent, asap, deadline)
- Flag financial matters for manual review

## Approval Thresholds
- Payments >$100: Require approval
- New contacts: Require approval
- Bulk operations: Require approval

## Communication Guidelines
- Email responses: Professional, concise
- Task prioritization: Urgent > Important > Normal
```

**Verify vault**:
- Open Obsidian and confirm vault opens
- Check all folders exist
- Confirm Dashboard.md and Company_Handbook.md are readable

## Step 4: Choose Your Watcher

You must choose **ONE** watcher for Bronze tier:
- **Option A**: Gmail Watcher (for email-based workflows)
- **Option B**: File System Watcher (for document-based workflows)

### Option A: Gmail Watcher Setup

**4A.1: Enable Gmail API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Personal AI Employee"
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"

**4A.2: Create OAuth Credentials**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "AI Employee Watcher"
5. Download credentials JSON file
6. Save as `~/.credentials/gmail-credentials.json`

**4A.3: Configure Environment**

Create `.env` file in project root:
```bash
# Gmail Watcher Configuration
VAULT_PATH=/Users/yourname/AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=/Users/yourname/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/Users/yourname/.credentials/gmail-token.json
GMAIL_QUERY=is:unread is:important
WATCHER_TYPE=gmail
```

**4A.4: Test Gmail Watcher**

```bash
python watchers/gmail_watcher.py --test
```

First run will open browser for OAuth consent. Grant permissions.

**Expected output**:
```
[INFO] Starting GmailWatcher
[INFO] Authenticating with Gmail API...
[INFO] Authentication successful
[INFO] Checking for new emails...
[INFO] Found 0 unread important emails
[INFO] Test complete
```

### Option B: File System Watcher Setup

**4B.1: Create Watch Directory**

```bash
mkdir -p ~/AI_Employee_Dropbox
```

**4B.2: Configure Environment**

Create `.env` file in project root:
```bash
# File System Watcher Configuration
VAULT_PATH=/Users/yourname/AI_Employee_Vault
WATCH_DIRECTORY=/Users/yourname/AI_Employee_Dropbox
FILE_EXTENSIONS=*  # Or: .pdf,.docx,.xlsx
WATCHER_TYPE=filesystem
```

**4B.3: Test File System Watcher**

```bash
python watchers/filesystem_watcher.py --test
```

**Expected output**:
```
[INFO] Starting FilesystemWatcher
[INFO] Monitoring directory: /Users/yourname/AI_Employee_Dropbox
[INFO] Watching for file extensions: *
[INFO] Test complete
```

## Step 5: Create Agent Skill

**5.1: Create Skill Directory**

```bash
mkdir -p .claude/skills/email-triage/{examples,references}
```

**5.2: Create SKILL.md**

Create `.claude/skills/email-triage/SKILL.md`:

```markdown
---
name: email-triage
description: Analyze incoming emails and categorize by urgency and action required. Use when processing email tasks from /Needs_Action.
---

# Email Triage

## Instructions

1. Read the email task file from /Needs_Action
2. Extract key information:
   - Sender and subject
   - Email content and context
   - Received timestamp
3. Analyze for urgency indicators:
   - Keywords: urgent, asap, deadline, important, critical
   - Sender importance (client, boss, team member)
   - Time sensitivity (deadlines mentioned)
4. Categorize priority:
   - **High**: Urgent keywords, important sender, deadline <24 hours
   - **Medium**: Important but not urgent, deadline 1-7 days
   - **Low**: Informational, no deadline, can wait
5. Suggest actions:
   - Reply: Draft response needed
   - Forward: Needs another person's attention
   - Archive: Informational only, no action needed
   - Flag: Requires follow-up or tracking
6. Create Plan.md in /Plans with:
   - Priority assessment
   - Suggested actions with checkboxes
   - Draft response if applicable
7. Move original task file to /Done

## Examples

### Example 1: High Priority Client Email

**Input** (`/Needs_Action/EMAIL_20260307T103000Z_invoice-request.md`):
```markdown
---
type: email
source: client@example.com
timestamp: 2026-03-07T10:30:00Z
priority: high
status: pending
---

## Email Content
Subject: Invoice Request for January

Hi, can you send me the invoice for January services? I need it by end of day for our accounting close.

Thanks,
John Client
```

**Output** (`/Plans/PLAN_EMAIL_20260307T103000Z_invoice-request.md`):
```markdown
---
objective: Respond to client invoice request
created: 2026-03-07T10:35:00Z
related_task: EMAIL_20260307T103000Z_invoice-request.md
approval_required: false
---

## Priority Assessment
**HIGH** - Client request with same-day deadline

## Action Steps
- [x] Analyze email (completed)
- [ ] Generate January invoice
- [ ] Send invoice via email
- [ ] Log in accounting system
- [ ] Move task to /Done

## Draft Response
Subject: Re: Invoice Request for January

Hi John,

I'll generate and send the January invoice within the next hour. You'll receive it at this email address.

Best regards
```

### Example 2: Low Priority Newsletter

**Input** (`/Needs_Action/EMAIL_20260307T140000Z_newsletter.md`):
```markdown
---
type: email
source: newsletter@techblog.com
timestamp: 2026-03-07T14:00:00Z
priority: low
status: pending
---

## Email Content
Subject: Weekly Tech Digest - March 7, 2026

[Newsletter content...]
```

**Output** (`/Plans/PLAN_EMAIL_20260307T140000Z_newsletter.md`):
```markdown
---
objective: Process newsletter email
created: 2026-03-07T14:05:00Z
related_task: EMAIL_20260307T140000Z_newsletter.md
approval_required: false
---

## Priority Assessment
**LOW** - Informational newsletter, no action required

## Action Steps
- [x] Analyze email (completed)
- [ ] Archive email
- [ ] Move task to /Done

## Recommendation
No response needed. Archive for reference.
```
```

**5.3: Verify Skill**

```bash
# Check skill is valid
python -c "
from pathlib import Path
import yaml

skill_path = Path('.claude/skills/email-triage/SKILL.md')
content = skill_path.read_text()
parts = content.split('---', 2)
frontmatter = yaml.safe_load(parts[1])
print(f'Skill name: {frontmatter[\"name\"]}')
print(f'Skill description: {frontmatter[\"description\"][:50]}...')
print('✓ Skill is valid')
"
```

## Step 6: Run Your First Test

**6.1: Start Watcher**

```bash
# Gmail Watcher
python watchers/gmail_watcher.py

# OR File System Watcher
python watchers/filesystem_watcher.py
```

**6.2: Trigger Task Creation**

**For Gmail Watcher**:
- Send yourself an important email with subject "Test Task"
- Mark it as important in Gmail
- Wait up to 2 minutes

**For File System Watcher**:
- Drop a test file into watch directory:
  ```bash
  echo "Test document" > ~/AI_Employee_Dropbox/test.txt
  ```
- Wait up to 30 seconds

**6.3: Verify Task File Created**

Check Obsidian vault:
```bash
ls ~/AI_Employee_Vault/Needs_Action/
```

You should see a new `.md` file (e.g., `EMAIL_20260307T103000Z_test-task.md`)

**6.4: Process Task with Claude Code**

```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action. For each task, create a plan in /Plans and move the task to /Done."
```

**6.5: Verify Results**

Check Obsidian:
- `/Plans/` should contain new plan file
- `/Done/` should contain processed task file
- `/Needs_Action/` should be empty

## Step 7: Daily Usage

### Morning Routine

1. **Start Watcher** (in terminal):
   ```bash
   cd personal-ai-employee
   source .venv/bin/activate
   python watchers/gmail_watcher.py  # or filesystem_watcher.py
   ```

2. **Open Obsidian** and view Dashboard.md

3. **Process Tasks** (when Watcher detects new items):
   ```bash
   cd ~/AI_Employee_Vault
   claude "Process tasks in /Needs_Action"
   ```

4. **Review Plans** in `/Plans/` folder

5. **Execute Actions** manually (Bronze tier has no automation)

### Evening Routine

1. **Stop Watcher** (Ctrl+C in terminal)

2. **Review Logs**:
   ```bash
   cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
   ```

3. **Archive Completed Tasks** (optional):
   ```bash
   mv ~/AI_Employee_Vault/Done/* ~/AI_Employee_Vault/Archive/$(date +%Y-%m)/
   ```

## Troubleshooting

### Watcher Not Detecting Tasks

**Gmail Watcher**:
- Check OAuth token is valid: `ls ~/.credentials/gmail-token.json`
- Verify Gmail API is enabled in Google Cloud Console
- Check query matches your emails: `GMAIL_QUERY=is:unread`
- Review logs: `cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json`

**File System Watcher**:
- Verify watch directory exists: `ls ~/AI_Employee_Dropbox`
- Check file permissions: `ls -la ~/AI_Employee_Dropbox`
- Test with simple file: `touch ~/AI_Employee_Dropbox/test.txt`

### Claude Code Not Finding Vault

- Verify you're in vault directory: `pwd` should show vault path
- Check vault structure: `ls -la` should show folders
- Try absolute path: `cd ~/AI_Employee_Vault && claude "..."`

### Task Files Malformed

- Check YAML frontmatter syntax (no tabs, proper indentation)
- Validate with: `python -c "import yaml; yaml.safe_load(open('file.md').read().split('---')[1])"`
- Review task-file-schema.json for required fields

### Agent Skill Not Working

- Verify skill location: `.claude/skills/email-triage/SKILL.md`
- Check YAML frontmatter is valid
- Restart Claude Code to reload skills
- Review skill name matches trigger conditions

## Next Steps

After Bronze tier is working:

1. **Silver Tier** (20-30 hours):
   - Add second Watcher (Gmail + File System)
   - Implement MCP server for email sending
   - Add Human-in-the-Loop approval workflow
   - Set up cron/Task Scheduler for automation

2. **Gold Tier** (40+ hours):
   - Integrate Odoo accounting system
   - Add social media integration (LinkedIn, Facebook, Twitter)
   - Implement Ralph Wiggum loop for autonomous execution
   - Build CEO Briefing generation

3. **Platinum Tier** (60+ hours):
   - Deploy to cloud (24/7 operation)
   - Implement Cloud/Local work-zone specialization
   - Add advanced monitoring and health checks

## Support

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Community**: Join Wednesday Research Meetings (details in PROJECT_REFERENCE.md)

## Success Checklist

- [ ] Obsidian vault created with all folders
- [ ] Dashboard.md and Company_Handbook.md exist
- [ ] Python dependencies installed
- [ ] One Watcher configured and tested
- [ ] Agent Skill created and validated
- [ ] Test task successfully created by Watcher
- [ ] Claude Code processed task and created plan
- [ ] Task moved to /Done folder
- [ ] System runs for 24 hours without crashes

**Congratulations!** You've completed Bronze tier setup. Your Personal AI Employee foundation is ready.
