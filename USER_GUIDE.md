# User Guide: Personal AI Employee (Bronze Tier)

**Your 24/7 AI Assistant for Personal and Business Task Management**

**Estimated Setup Time**: 1-2 hours  
**Difficulty**: Beginner-friendly (no AI/ML experience required)

---

## Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [Conceptual Overview](#conceptual-overview)
3. [Complete Setup Guide](#complete-setup-guide)
4. [Gmail OAuth2 Deep Dive](#gmail-oauth2-deep-dive)
5. [Daily Workflow](#daily-workflow)
6. [Task File Anatomy](#task-file-anatomy)
7. [Commands Reference](#commands-reference)
8. [Agent Skills](#agent-skills)
9. [Customization Guide](#customization-guide)
10. [Troubleshooting Quick Reference](#troubleshooting-quick-reference)
11. [Real-World Examples](#real-world-examples)

---

## Quick Start (5 Minutes)

### What is Personal AI Employee?

Personal AI Employee is an autonomous AI agent that monitors your email and files 24/7, automatically creating tasks and executing them with Claude AI. Think of it as hiring a digital assistant who never sleeps.

**How it works**:
1. **Watchers** monitor your Gmail inbox or file folders
2. When something important arrives, a **task file** is created
3. **Claude Code** reads the task, creates a plan, and executes it
4. Completed tasks are archived automatically

### Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Obsidian** installed ([download](https://obsidian.md/download))
- [ ] **Python 3.13+** installed ([download](https://www.python.org/downloads/))
- [ ] **Claude Code** installed ([setup](https://code.claude.com))
- [ ] **uv** package manager: run `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] 1GB free disk space
- [ ] A Gmail account (for Gmail Watcher)

**Note**: This guide uses macOS/Linux path examples (`/Users/yourname/`). Windows users should use `C:\Users\yourname\` instead.

### 3-Command Setup

```bash
# 1. Install dependencies
git clone https://github.com/YOUR-USERNAME/personal-ai-employee.git  # Replace YOUR-USERNAME
cd personal-ai-employee
uv venv && source .venv/bin/activate && uv pip install -e .

# 2. Create your Obsidian vault
python -m vault_setup.create_vault --path ~/AI_Employee_Vault

# 3. Test the system
python main.py --test
```

**That's it!** You now have the foundation. Continue reading for detailed setup and usage.

**Important**: Bronze tier requires manual Claude triggering. The Watcher creates tasks automatically, but you must run Claude commands to process them. Automation comes in Silver tier.

---

## Conceptual Overview

### System Architecture: Perception → Reasoning → Action

```
┌─────────────────┐
│   WATCHERS      │  ← Perception (Senses)
│  (Gmail/Files)  │     Monitor external sources
└────────┬────────┘
         │ Creates task files
         ▼
┌─────────────────┐
│  NEEDS_ACTION   │  ← Memory (Obsidian Vault)
│    FOLDER       │     Stores pending tasks
└────────┬────────┘
         │ Claude reads tasks
         ▼
┌─────────────────┐
│  CLAUDE CODE    │  ← Reasoning (Brain)
│   (AI Agent)    │     Analyzes and plans
└────────┬────────┘
         │ Creates plans, moves tasks
         ▼
┌─────────────────┐
│  PLANS / DONE   │  ← Action (Execution)
│    FOLDERS      │     Tracks completed work
└─────────────────┘
```

### What Are Watchers?

**Watchers** are lightweight Python scripts that run continuously in the background, monitoring external sources for new items:

- **Gmail Watcher**: Checks your inbox every 2 minutes for important/unread emails
- **File System Watcher**: Watches a folder for new files (drops, downloads, etc.)

When a Watcher detects something new, it creates a **task file** in your Obsidian vault's `/Needs_Action` folder.

**Note**: In Bronze tier, `processed_items` tracking is in-memory only. If you restart the Watcher, it may create duplicate task files for items it already processed. This is resolved in Silver tier with persistent state.

### What Is the Vault?

The **vault** is an Obsidian folder structure that serves as your AI Employee's memory and dashboard. It contains 8 folders:

| Folder | Purpose |
|--------|---------|
| `/Inbox` | General notes and reference |
| `/Needs_Action` | **Tasks waiting to be processed** (most important) |
| `/Plans` | Execution plans created by Claude |
| `/Done` | Completed tasks (archive) |
| `/Logs` | System logs (JSON format) |
| `/Pending_Approval` | Tasks requiring your approval |
| `/Approved` | Approved tasks ready for execution |
| `/Rejected` | Declined tasks |

### Task Lifecycle

Every task follows this journey:

1. **Detection**: Watcher detects new email/file → creates task file
2. **Triage**: Task appears in `/Needs_Action` with metadata
3. **Processing**: Claude reads task, applies skills, creates plan in `/Plans`
4. **Execution**: Actions are performed (manually in Bronze tier)
5. **Completion**: Task file moved to `/Done`

---

## Complete Setup Guide

### Step 1: Install Dependencies

#### 1.1 Clone the Repository

```bash
# Replace YOUR-USERNAME with your actual GitHub username
git clone https://github.com/YOUR-USERNAME/personal-ai-employee.git
cd personal-ai-employee
```

#### 1.2 Install Python Packages

```bash
# Create virtual environment
uv venv

# Activate virtual environment (Windows: .venv\Scripts\activate)
source .venv/bin/activate

# Install all dependencies
uv pip install -e .
```

#### 1.3 Verify Installation

```bash
python -c "import watchdog; import yaml; import google.auth; print('✓ All dependencies installed')"
```

**Expected output**: `✓ All dependencies installed`

---

### Step 2: Create Your Obsidian Vault

#### 2.1 Run Automated Setup

```bash
python -m vault_setup.create_vault --path ~/AI_Employee_Vault
```

**This creates**:
- Vault directory at `~/AI_Employee_Vault`
- 8 folders (Inbox, Needs_Action, Done, Logs, Plans, etc.)
- `Dashboard.md` - Your real-time status view
- `Company_Handbook.md` - Rules and policies

#### 2.2 Open Vault in Obsidian

1. Launch Obsidian
2. Click "Open folder as vault"
3. Navigate to `~/AI_Employee_Vault`
4. Click "Open"

You should see all 8 folders in the file explorer.

---

### Step 3: Configure Your Watcher

You need to choose **ONE** watcher for Bronze tier:

- **Option A: Gmail Watcher** - Monitors email (recommended for most users)
- **Option B: File System Watcher** - Monitors a folder for file drops

#### Option A: Gmail Watcher Setup

**3A.1: Enable Gmail API**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Personal AI Employee"
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API" and click "Enable"

**3A.2: Create OAuth Credentials**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: **Desktop app**
4. Name: "AI Employee Watcher"
5. Download the JSON file
6. Save to `~/.credentials/gmail-credentials.json`

```bash
# Create credentials directory
mkdir -p ~/.credentials

# Move your downloaded credentials file
mv ~/Downloads/client_secret_*.json ~/.credentials/gmail-credentials.json
```

**3A.3: Configure Environment**

Create a `.env` file in the project root:

```bash
# Copy example
cp .env.example .env

# Edit with your paths (use absolute paths!)
nano .env
```

**Required settings**:
```bash
VAULT_PATH=/Users/yourname/AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=/Users/yourname/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/Users/yourname/.credentials/gmail-token.json
GMAIL_QUERY=is:unread is:important
WATCHER_TYPE=gmail
```

**Important**: Replace `/Users/yourname/` with your actual home directory path.

**3A.4: First Authentication**

```bash
python main.py --test
```

**What happens**:
1. Browser opens automatically
2. Sign in to Google
3. Grant permissions (safe - you created this app)
4. Token saved to `~/.credentials/gmail-token.json`

**Expected output**:
```
[INFO] Authentication successful
[INFO] Checking for new emails...
✅ Test complete: Found 0 new emails
```

---

#### Option B: File System Watcher Setup

**3B.1: Create Watch Directory**

```bash
mkdir -p ~/AI_Employee_Dropbox
```

**3B.2: Configure Environment**

Create `.env` file:

```bash
VAULT_PATH=/Users/yourname/AI_Employee_Vault
WATCH_DIRECTORY=/Users/yourname/AI_Employee_Dropbox
FILE_EXTENSIONS=*
WATCHER_TYPE=filesystem
```

**3B.3: Test File System Watcher**

```bash
python main.py --test
```

**Expected output**:
```
[INFO] Starting FilesystemWatcher
[INFO] Monitoring directory: /Users/yourname/AI_Employee_Dropbox
✅ Test complete: Processed 0 files
```

---

### Step 4: Verify Installation

#### 4.1 Send Test Email (Gmail Watcher)

1. Send yourself an email with subject "Test AI Employee"
2. Mark it as important in Gmail (click star)
3. Wait 2 minutes

#### 4.2 Check for Task File

```bash
ls ~/AI_Employee_Vault/Needs_Action/
```

You should see: `EMAIL_20260307T153000Z_test-ai-employee.md`

#### 4.3 Process with Claude Code

```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action using the email-triage skill. Create plans in /Plans and move tasks to /Done."
```

#### 4.4 Verify Results

Check in Obsidian:
- `/Plans/` contains new plan file
- `/Done/` contains processed task
- `/Needs_Action/` is empty

**Congratulations!** Your Personal AI Employee is working.

---

## Gmail OAuth2 Deep Dive

### How OAuth2 Works

OAuth2 is like giving a valet key to your car instead of your house key:

- **Credentials file** = Valet key application (proves who you are)
- **Token file** = Actual valet key (grants temporary access)
- **Refresh** = Getting a new key when the old one expires

### Where Credentials Are Stored

```
~/.credentials/
├── gmail-credentials.json    # Your OAuth2 client credentials (permanent)
└── gmail-token.json          # Access token (auto-refreshed)
```

**Security**:
```bash
# Set restrictive permissions
chmod 600 ~/.credentials/gmail-credentials.json
chmod 600 ~/.credentials/gmail-token.json
```

### Token Lifecycle

1. **First run**: Browser opens, you grant permissions → token created
2. **Subsequent runs**: Token automatically used (no browser)
3. **Token expires** (rare): Automatically refreshed using refresh_token
4. **Token revoked**: Delete `gmail-token.json` and re-authenticate

### Troubleshooting Authentication

**Error: "Invalid grant"**
```bash
# Delete old token and re-authenticate
rm ~/.credentials/gmail-token.json
python main.py --test
```

**Error: "Credentials file not found"**
```bash
# Verify file exists
ls ~/.credentials/gmail-credentials.json

# Check .env has absolute path (not ~ or relative)
cat .env | grep GMAIL_CREDENTIALS_PATH
```

**Error: "Access blocked"**
1. Go to Google Cloud Console > OAuth Consent Screen
2. Add your email as a "Test User"
3. Ensure Gmail API scope is added

### Security Best Practices

1. **Never commit credentials** to Git (`.gitignore` includes `.credentials/`)
2. **Rotate credentials** every 90 days:
   ```bash
   # Delete old credentials in Google Cloud Console
   # Download new credentials
   mv ~/Downloads/client_secret_*.json ~/.credentials/gmail-credentials.json
   rm ~/.credentials/gmail-token.json  # Force re-auth
   python main.py --test
   ```
3. **Revoke access** when done:
   - Go to [Google Account Security](https://myaccount.google.com/security)
   - Find "Personal AI Employee" under "Third-party apps"
   - Click "Remove Access"

---

## Daily Workflow

### Morning Routine (9:00 AM)

**1. Start Watcher**
```bash
cd ~/personal-ai-employee
source .venv/bin/activate
python main.py
```

Leave this terminal running - it monitors continuously.

**2. Open Obsidian**
```bash
# macOS
open -a Obsidian ~/AI_Employee_Vault

# Windows
start obsidian://open?vault=AI_Employee_Vault

# Linux
obsidian ~/AI_Employee_Vault
```

**3. Check Dashboard.md**
- Review "Recent Activity" section
- Note pending tasks in `/Needs_Action`

**4. Process Tasks**
```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action. Prioritize high-urgency items first."
```

---

### Midday Check (12:00 PM)

**1. Review New Tasks**
- Check `/Needs_Action` for items detected since morning
- Run Claude again if new tasks appeared

**2. Review Plans**
- Open files in `/Plans/` folder
- Verify action steps make sense
- Approve if needed (move to `/Approved`)

**3. Execute Actions**
- Bronze tier: Manual execution (you perform actions)
- Follow plan checkboxes in `/Plans/`

---

### Evening Routine (5:00 PM)

**1. Stop Watcher**
- Press `Ctrl+C` in the terminal running `main.py`

**2. Review Logs**
```bash
cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

**3. Archive Completed Tasks** (optional)
```bash
# Create monthly archive folder
mkdir -p ~/AI_Employee_Vault/Archive/$(date +%Y-%m)

# Move old Done items
mv ~/AI_Employee_Vault/Done/*.md ~/AI_Employee_Vault/Archive/$(date +%Y-%m)/
```

**4. Update Dashboard**
```bash
cd ~/AI_Employee_Vault
claude "Update Dashboard.md with today's activity summary and current task counts."
```

---

## Task File Anatomy

### File Naming Convention

```
{TYPE}_{TIMESTAMP}_{SLUG}.md

Examples:
EMAIL_20260307T103000Z_invoice-request.md
FILE_DROP_20260307T141500Z_quarterly-report.pdf
```

**Components**:
- **TYPE**: `EMAIL`, `FILE_DROP`, or `TRANSACTION`
- **TIMESTAMP**: `YYYYMMDDTHHMMSSZ` format (UTC)
- **SLUG**: Lowercase, hyphenated description (max 50 chars)

### YAML Frontmatter Structure

Every task file starts with YAML frontmatter between `---` markers:

```yaml
---
type: email
source: client@example.com
timestamp: 2026-03-07T10:30:00Z
priority: high
status: pending
subject: Invoice Request for January
---
```

**Required Fields**:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `type` | string | `email`, `file_drop`, `transaction` | Task category |
| `source` | string | Email address or file path | Where task originated |
| `timestamp` | ISO 8601 | `2026-03-07T10:30:00Z` | When created |
| `priority` | enum | `high`, `medium`, `low` | Urgency level |
| `status` | enum | `pending`, `in_progress`, `completed` | Current state |

### Example: Email Task File

```markdown
---
type: email
source: john@client.com
timestamp: 2026-03-07T10:30:00Z
priority: high
status: pending
subject: Invoice Request for January
---

## Email Content

**From**: John Client <john@client.com>
**Subject**: Invoice Request for January
**Received**: Wed, 7 Mar 2026 10:30:00 +0000

Hi,

Can you send me the invoice for January services? I need it by end of day for our accounting close.

Thanks,
John Client

## Metadata

- **Gmail Message ID**: 18d4f2a3b5c6e7f8
- **Created**: 2026-03-07T10:30:00Z
- **Priority**: high

## Suggested Actions

- [ ] Review email content
- [ ] Determine required response
- [ ] Create execution plan
- [ ] Complete actions
- [ ] Move to /Done when finished
```

### Example: File Drop Task File

```markdown
---
type: file_drop
source: /Users/john/AI_Employee_Dropbox/contract.pdf
timestamp: 2026-03-07T14:15:00Z
priority: medium
status: pending
subject: contract.pdf
---

## File Details

**Filename**: contract.pdf
**Location**: /Users/john/AI_Employee_Dropbox/contract.pdf
**Size**: 245.8 KB
**Type**: .pdf
**Detected**: 2026-03-07T14:15:00Z

## Description

New file detected in monitored directory. Review and process as needed.

## Suggested Actions

- [ ] Review file contents
- [ ] Determine required processing
- [ ] Extract relevant information
- [ ] Move to /Done when finished
```

### Validation Rules

Task files must:
- Start with valid YAML frontmatter (`---`)
- Include all 5 required fields
- Use valid enum values (no typos)
- Have ISO 8601 timestamp format
- Non-empty `source` string

**Validate manually**:
```bash
python -c "
from pathlib import Path
from vault_setup.validators import validate_task_file

file_path = Path('~/AI_Employee_Vault/Needs_Action/YOUR_FILE.md').expanduser()
is_valid, error = validate_task_file(file_path)
print(f'✓ Valid' if is_valid else f'✗ Error: {error}')
"
```

---

## Commands Reference

### Watcher Commands

**Start Gmail Watcher (continuous mode)**:
```bash
cd ~/personal-ai-employee
source .venv/bin/activate
python main.py
```

**Start File System Watcher (continuous mode)**:
```bash
cd ~/personal-ai-employee
source .venv/bin/activate
python main.py
```

**Test Mode (single check, then exit)**:
```bash
python main.py --test
```

**Stop Watcher**:
- Press `Ctrl+C` in terminal

---

### Claude Commands

**Process all tasks**:
```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action. Create plans in /Plans and move tasks to /Done."
```

**Process with email triage**:
```bash
claude "Use the email-triage skill to analyze all email tasks in /Needs_Action. Categorize by priority and create plans."
```

**Prioritize tasks**:
```bash
claude "Review all tasks in /Needs_Action and prioritize them by urgency. Create plans for high-priority tasks first."
```

**Process specific task**:
```bash
claude "Process the task EMAIL_20260307T103000Z_invoice-request.md in /Needs_Action. Create a detailed plan with action steps."
```

**Update Dashboard**:
```bash
claude "Update Dashboard.md with: 1) Count of tasks in each folder, 2) Summary of recent activity, 3) System status"
```

**Review pending approvals**:
```bash
claude "Review all items in /Pending_Approval and provide recommendations for approval or rejection."
```

**Create end-of-day summary**:
```bash
claude "Create a summary of all tasks processed today. List completed items and any pending approvals."
```

---

### Configuration Options (.env)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VAULT_PATH` | Yes | Absolute path to Obsidian vault | `/Users/john/AI_Employee_Vault` |
| `WATCHER_TYPE` | Yes | Watcher type: `gmail` or `filesystem` | `gmail` |
| `GMAIL_CREDENTIALS_PATH` | For Gmail | Path to OAuth credentials | `/Users/john/.credentials/gmail-credentials.json` |
| `GMAIL_TOKEN_PATH` | For Gmail | Path to store token | `/Users/john/.credentials/gmail-token.json` |
| `GMAIL_QUERY` | For Gmail | Gmail search query | `is:unread is:important` |
| `WATCH_DIRECTORY` | For File System | Folder to monitor | `/Users/john/AI_Employee_Dropbox` |
| `FILE_EXTENSIONS` | For File System | Extensions to watch (`*` for all) | `*` or `.pdf,.docx` |

**Custom Gmail Queries**:
```bash
# All unread emails
GMAIL_QUERY=is:unread

# From specific sender
GMAIL_QUERY=is:unread from:client@example.com

# With specific subject
GMAIL_QUERY=is:unread subject:invoice

# With label
GMAIL_QUERY=is:unread label:important
```

---

## Agent Skills

### What Are Agent Skills?

**Agent Skills** are reusable AI capabilities defined in `SKILL.md` files. They teach Claude how to handle specific task types consistently.

Think of them as employee training manuals:
- **Instructions**: Step-by-step guidance
- **Examples**: Concrete demonstrations
- **Triggers**: When to automatically apply

### Email Triage Skill (Included)

The Bronze tier includes `email-triage` skill, automatically invoked for email tasks.

**What it does**:
1. Reads email task file from `/Needs_Action`
2. Extracts sender, subject, content, timestamp
3. Analyzes for urgency (keywords, sender importance, deadlines)
4. Categorizes priority (high/medium/low)
5. Suggests actions (reply/forward/archive/flag)
6. Creates plan with draft response if needed

**Location**: `.claude/skills/email-triage/SKILL.md`

### Skill Structure

```markdown
---
name: skill-name
description: What it does and when to use it (max 1024 chars)
---

# Skill Name

## Instructions

1. Step-by-step guidance
2. Each step is actionable
3. Include decision logic

## Examples

### Example 1: High Priority Case

**Input**:
```markdown
[Sample task file]
```

**Output**:
```markdown
[Sample plan file]
```
```

### Creating Custom Skills

**Step 1: Create Skill Directory**
```bash
mkdir -p .claude/skills/your-skill-name
```

**Step 2: Create SKILL.md**
```bash
nano .claude/skills/your-skill-name/SKILL.md
```

**Step 3: Follow Naming Rules**
- Lowercase with hyphens only: `expense-tracker`, `meeting-scheduler`
- Max 64 characters
- No reserved words (`claude`, `anthropic`)
- Must have `## Instructions` and `## Examples` sections

**Step 4: Validate**
```bash
python -c "
from pathlib import Path
from vault_setup.validators import validate_skill

skill_path = Path('.claude/skills/your-skill-name')
is_valid, error = validate_skill(skill_path)
print(f'✓ Valid' if is_valid else f'✗ Error: {error}')
"
```

### How Claude Discovers Skills

1. **Auto-discovery**: On startup, Claude scans `.claude/skills/` directories
2. **Trigger matching**: When processing a task, Claude checks skill descriptions
3. **Automatic application**: If task matches skill, instructions are followed

**Example triggers**:
- Email task (`type: email`) → `email-triage` skill
- File drop with `.pdf` → `document-processor` skill (if created)
- Transaction task → `expense-tracker` skill (if created)

---

## Customization Guide

### Modify Gmail Query

**Goal**: Change which emails trigger tasks

Edit `.env`:
```bash
# Only from VIP clients
GMAIL_QUERY=is:unread from:ceo@company.com OR from:important@client.com

# With attachments
GMAIL_QUERY=is:unread has:attachment

# Specific labels
GMAIL_QUERY=is:unread label:work

# Exclude newsletters
GMAIL_QUERY=is:unread -from:newsletter@
```

### Change Check Intervals

**Goal**: Adjust how often Watcher checks for new items

Edit `watchers/gmail_watcher.py` or `watchers/filesystem_watcher.py`:

```python
# Gmail Watcher (default: 120 seconds)
watcher = GmailWatcher(
    # ...
    check_interval=300,  # Change to 300 for 5 minutes
)

# File System Watcher (default: 5 seconds)
watcher = FilesystemWatcher(
    # ...
    check_interval=10,  # Change to 10 seconds
)
```

### Add New Watcher Types

**Goal**: Monitor additional sources (WhatsApp, SMS, etc.)

**Step 1: Create New Watcher Class**
```python
# watchers/whatsapp_watcher.py
from watchers.base_watcher import BaseWatcher

class WhatsAppWatcher(BaseWatcher):
    def check_for_updates(self) -> int:
        # Your WhatsApp monitoring logic
        pass

    def create_action_file(self, item_data) -> Path:
        # Create task file for WhatsApp messages
        pass
```

**Step 2: Add to main.py**
```python
# In main.py
from watchers.whatsapp_watcher import WhatsAppWatcher

# Add to watcher type selection
if config.watcher_type == "whatsapp":
    return run_whatsapp_watcher(config, test_mode=args.test)
```

### Customize Task Templates

**Goal**: Change task file format

Edit `watchers/gmail_watcher.py` or `watchers/filesystem_watcher.py`:

```python
# In create_action_file() method
content = f"""---
type: email
source: {sender}
timestamp: {timestamp}
priority: {priority}
status: pending
subject: {subject}
custom_field: {your_custom_data}  # Add new fields
---

## Email Content
{body}

## Custom Section  # Add new sections
Your custom content here
"""
```

### Modify Priority Rules

**Goal**: Change how priority is determined

Edit `watchers/gmail_watcher.py`:

```python
def _determine_priority(self, subject: str, sender: str) -> str:
    # Add your custom logic
    if "invoice" in subject.lower():
        return "high"  # All invoices are high priority

    if sender.endswith("@vip-client.com"):
        return "high"  # VIP clients always high priority

    # Default logic
    urgent_keywords = ["urgent", "asap", "deadline"]
    if any(kw in subject.lower() for kw in urgent_keywords):
        return "high"

    return "medium"
```

---

## Troubleshooting Quick Reference

### Common Errors & Quick Fixes

| Error | Quick Fix |
|-------|-----------|
| `Credentials file not found` | `ls ~/.credentials/gmail-credentials.json` - verify path in .env |
| `Invalid grant` | `rm ~/.credentials/gmail-token.json && python main.py --test` |
| `Vault path does not exist` | Run `python -m vault_setup.create_vault --path ~/AI_Employee_Vault` |
| `ModuleNotFoundError` | `source .venv/bin/activate && uv pip install -e .` |
| `No emails detected` | Check Gmail query: `GMAIL_QUERY=is:unread` |
| `Tasks not processed` | Ensure Claude is run from vault: `cd ~/AI_Employee_Vault` |
| `Plans not created` | Check `/Plans` folder exists: `mkdir -p ~/AI_Employee_Vault/Plans` |
| `Skill not applied` | Validate: `python -c "from pathlib import Path; from vault_setup.validators import validate_skill; skill_path = Path('.claude/skills/email-triage'); is_valid, error = validate_skill(skill_path); print(f'✓ Valid' if is_valid else f'✗ Error: {error}')"` |

### Log File Locations

**Watcher Logs** (JSON format):
```bash
# Today's logs
cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Specific date
cat ~/AI_Employee_Vault/Logs/2026-03-07.json

# Pretty-print JSON
python -m json.tool ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

**Console Logs** (run with tee):
```bash
python main.py 2>&1 | tee watcher.log
```

### Reset Authentication

**When**: Token expired, credentials revoked, or "invalid grant" errors

```bash
# 1. Delete old token
rm ~/.credentials/gmail-token.json

# 2. Re-authenticate
python main.py --test

# 3. Complete OAuth flow in browser
# 4. Verify new token created
ls -la ~/.credentials/gmail-token.json
```

### Diagnostic Script

Save as `diagnostic.sh` and run `./diagnostic.sh`:

```bash
#!/bin/bash
echo "=== Personal AI Employee Diagnostic ==="
echo ""
echo "Python version:"
python --version
echo ""
echo "Dependencies:"
python -c "import watchdog; import yaml; import google.auth; print('✓ All installed')" 2>&1
echo ""
echo "Vault exists:"
ls ~/AI_Employee_Vault 2>&1 | head -n 5
echo ""
echo "Environment configured:"
cat .env | grep -E "VAULT_PATH|WATCHER_TYPE" 2>&1
echo ""
echo "Skills exist:"
ls .claude/skills/email-triage/SKILL.md 2>&1
echo ""
echo "=== End Diagnostic ==="
```

Make executable: `chmod +x diagnostic.sh`

---

## Real-World Examples

### Example 1: Client Invoice Request

**Scenario**: Client emails asking for invoice, needs same-day delivery

**1. Email Arrives**
- From: `john@client.com`
- Subject: "Invoice Request for January"
- Body: "Can you send me the invoice for January services? I need it by end of day."

**2. Watcher Creates Task File**
```markdown
---
type: email
source: john@client.com
timestamp: 2026-03-07T10:30:00Z
priority: high
status: pending
subject: Invoice Request for January
---

## Email Content

**From**: John Client <john@client.com>
**Subject**: Invoice Request for January
**Received**: Wed, 7 Mar 2026 10:30:00 +0000

Hi,

Can you send me the invoice for January services? I need it by end of day for our accounting close.

Thanks,
John Client
```

**3. Claude Processes Task**
```bash
cd ~/AI_Employee_Vault
claude "Process EMAIL_20260307T103000Z_invoice-request.md using email-triage skill"
```

**4. Plan Created in `/Plans/`**
```markdown
---
objective: Respond to client invoice request
created: 2026-03-07T10:35:00Z
related_task: EMAIL_20260307T103000Z_invoice-request.md
approval_required: false
---

## Priority Assessment

**HIGH** - Client request with same-day deadline

**Justification**:
- Known client (john@client.com)
- Explicit deadline: "by end of day"
- Financial matter (invoice)
- Blocks client's accounting close

## Action Steps

- [x] Analyze email (completed)
- [ ] Generate January invoice from accounting system
- [ ] Review invoice for accuracy
- [ ] Send invoice via email to john@client.com
- [ ] Log invoice sent in accounting system
- [ ] Move task to /Done

**Timeline**: Complete within 4 hours (by 2:30 PM)

## Draft Response

Subject: Re: Invoice Request for January

Hi John,

I'll generate and send the January invoice within the next hour. You'll receive it at this email address.

The invoice will include:
- Services rendered in January 2026
- Itemized breakdown
- Payment terms and instructions

Please let me know if you need any adjustments or have questions.

Best regards
```

**5. You Execute Actions**
- Generate invoice in your accounting system
- Review for accuracy
- Send email (copy/paste draft)
- Move task to `/Done`

---

### Example 2: Newsletter (Low Priority)

**Scenario**: Weekly tech newsletter arrives

**Task File Created**:
```markdown
---
type: email
source: newsletter@techblog.com
timestamp: 2026-03-07T14:00:00Z
priority: low
status: pending
subject: Weekly Tech Digest - March 7, 2026
---

## Email Content

**From**: Tech Blog <newsletter@techblog.com>
**Subject**: Weekly Tech Digest - March 7, 2026

This week's top stories:
- New AI developments
- Cloud computing trends
- Security updates
```

**Claude Plan**:
```markdown
---
objective: Process newsletter email
created: 2026-03-07T14:05:00Z
related_task: EMAIL_20260307T140000Z_newsletter.md
approval_required: false
---

## Priority Assessment

**LOW** - Informational newsletter, no action required

**Justification**:
- Automated newsletter (newsletter@techblog.com)
- No specific action requested
- No deadline or urgency
- Informational content only

## Action Steps

- [x] Analyze email (completed)
- [ ] Archive email for reference
- [ ] Move task to /Done

**Timeline**: Process when convenient (no deadline)

## Recommendation

No response needed. Archive for reference.
```

---

### Example 3: File Drop - Contract Review

**Scenario**: Contract PDF dropped into monitored folder

**1. File Dropped**
```bash
echo "Contract content" > ~/AI_Employee_Dropbox/vendor-contract.pdf
```

**2. Watcher Creates Task**
```markdown
---
type: file_drop
source: /Users/john/AI_Employee_Dropbox/vendor-contract.pdf
timestamp: 2026-03-07T15:45:00Z
priority: medium
status: pending
subject: vendor-contract.pdf
---

## File Details

**Filename**: vendor-contract.pdf
**Location**: /Users/john/AI_Employee_Dropbox/vendor-contract.pdf
**Size**: 245.8 KB
**Type**: .pdf
**Detected**: 2026-03-07T15:45:00Z

## Description

New file detected in monitored directory. Review and process as needed.
```

**3. Claude Creates Plan**
```markdown
---
objective: Review vendor contract document
created: 2026-03-07T15:50:00Z
related_task: FILE_DROP_20260307T154500Z_vendor-contract.pdf
approval_required: false
---

## Priority Assessment

**MEDIUM** - Business document requiring review

**Justification**:
- PDF document (likely formal)
- Filename suggests vendor contract
- Contract review typically important but not urgent
- May require legal or financial attention

## Action Steps

- [x] Analyze file metadata (completed)
- [ ] Open and review contract PDF
- [ ] Extract key terms (dates, amounts, obligations)
- [ ] Identify approval requirements
- [ ] Create summary for decision-making
- [ ] Move task to /Done after review

**Timeline**: Review within 24 hours

## Suggested Tools

- PDF reader (Preview, Adobe Acrobat)
- Note-taking for key terms
- Calendar for deadline tracking
```

---

## Next Steps After Bronze Tier

Once your Bronze tier system is running smoothly:

### Silver Tier (20-30 hours)
- Add second Watcher (run Gmail + File System simultaneously)
- Implement MCP server for sending emails automatically
- Human-in-the-loop approval workflow
- Automated scheduling via cron/Task Scheduler

### Gold Tier (40+ hours)
- Integrate Odoo accounting system
- Social media integration (LinkedIn, Facebook, Twitter)
- Ralph Wiggum loop for autonomous multi-step execution
- CEO Briefing generation

### Platinum Tier (60+ hours)
- Deploy to cloud (24/7 operation)
- Cloud/Local work-zone specialization
- Advanced monitoring and health checks
- Multi-user support

---

## Support & Resources

**Documentation**:
- `/docs` folder - Detailed technical guides
- `/specs/001-bronze-tier/` - Complete specifications
- `README.md` - Project overview

**Community**:
- GitHub Issues - Report bugs and feature requests
- Wednesday Research Meetings - Learn from other builders (see PROJECT_REFERENCE.md)

**External Resources**:
- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [OAuth2 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Claude Code Documentation](https://code.claude.com)
- [Obsidian Help](https://help.obsidian.md)

---

## Success Checklist

Use this to verify your Bronze tier setup:

- [ ] Obsidian vault created with all 8 folders
- [ ] Dashboard.md and Company_Handbook.md exist
- [ ] Python dependencies installed
- [ ] One Watcher configured and tested
- [ ] Agent Skill validated (email-triage)
- [ ] Test task successfully created by Watcher
- [ ] Claude Code processed task and created plan
- [ ] Task moved to /Done folder
- [ ] System runs for 24 hours without crashes

**Congratulations!** You've mastered Personal AI Employee Bronze Tier. You now have a 24/7 AI assistant managing your tasks.

---

**Version**: 1.0  
**Last Updated**: 2026-03-09  
**Compatible With**: Bronze Tier (v0.1.0)
