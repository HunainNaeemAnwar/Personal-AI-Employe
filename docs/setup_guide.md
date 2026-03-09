# Setup Guide: Personal AI Employee - Bronze Tier

**Estimated Time**: 1-2 hours
**Difficulty**: Intermediate

## Overview

This guide walks you through setting up the complete Bronze tier Personal AI Employee system from scratch. By the end, you'll have:

- ✅ Obsidian vault with structured folders
- ✅ One Watcher (Gmail OR File System) monitoring for tasks
- ✅ Claude Code integration for task processing
- ✅ Email triage Agent Skill

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] **Obsidian** v1.10.6+ installed ([download](https://obsidian.md/download))
- [ ] **Python** 3.13+ installed ([download](https://www.python.org/downloads/))
- [ ] **Claude Code** CLI installed ([setup guide](https://code.claude.com))
- [ ] **uv** package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] Basic command-line familiarity
- [ ] 1GB free disk space
- [ ] Stable internet connection

**For Gmail Watcher (optional)**:
- [ ] Google account with Gmail
- [ ] Google Cloud project access

**For File System Watcher (optional)**:
- [ ] Designated drop folder location

## Step 1: Clone and Setup Repository

### 1.1 Clone Repository

```bash
git clone https://github.com/your-username/personal-ai-employee.git
cd personal-ai-employee
git checkout 001-bronze-tier
```

### 1.2 Install Python Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

### 1.3 Verify Installation

```bash
python -c "import google.auth; import watchdog; import yaml; print('✓ Dependencies installed')"
```

**Expected output**: `✓ Dependencies installed`

## Step 2: Configure Environment

### 2.1 Create Environment File

```bash
cp .env.example .env
```

### 2.2 Edit Configuration

Open `.env` in your text editor and configure:

```bash
# Required: Vault path (will be created in Step 3)
VAULT_PATH=/absolute/path/to/personal-ai-employee/AI_Employee_Vault

# Choose ONE watcher type
WATCHER_TYPE=gmail  # or: filesystem

# Gmail Watcher Configuration (if WATCHER_TYPE=gmail)
GMAIL_CREDENTIALS_PATH=/absolute/path/to/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/absolute/path/to/.credentials/gmail-token.json
GMAIL_QUERY=is:unread is:important

# File System Watcher Configuration (if WATCHER_TYPE=filesystem)
WATCH_DIRECTORY=/absolute/path/to/personal-ai-employee/AI_Employee_Dropbox
FILE_EXTENSIONS=*  # Or: .pdf,.docx,.xlsx
```

**Important**: Use absolute paths, not relative paths.

## Step 3: Create Obsidian Vault

### 3.1 Run Vault Creation Script

```bash
python -m vault_setup.create_vault --path ~/AI_Employee_Vault
```

**Expected output**:
```
✅ Vault Created Successfully!

📁 Vault Location: /absolute/path/to/personal-ai-employee/AI_Employee_Vault

📂 Created 8 folders:
   • Approved/
   • Done/
   • Inbox/
   • Logs/
   • Needs_Action/
   • Pending_Approval/
   • Plans/
   • Rejected/

📄 Created 2 configuration files:
   • Dashboard.md
   • Handbook.md
```

### 3.2 Open Vault in Obsidian

1. Launch Obsidian
2. Click "Open folder as vault"
3. Navigate to `personal-ai-employee/AI_Employee_Vault`
4. Click "Open"

### 3.3 Verify Vault Structure

In Obsidian, you should see:
- All 8 folders in the file explorer
- `Dashboard.md` in the root
- `Company_Handbook.md` in the root

## Step 4: Setup Watcher (Choose One)

### Option A: Gmail Watcher

**4A.1: Enable Gmail API**

See [Gmail API Setup Guide](gmail_api_setup.md) for detailed instructions.

Quick steps:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project: "Personal AI Employee"
3. Enable Gmail API
4. Create OAuth credentials (Desktop app)
5. Download credentials JSON
6. Save to `~/.credentials/gmail-credentials.json`

**4A.2: Test Gmail Watcher**

```bash
python main.py --test
```

First run will open browser for OAuth consent. Grant permissions.

**Expected output**:
```
🧪 Running Gmail Watcher in test mode...
📧 Query: is:unread is:important
📁 Vault: /absolute/path/to/personal-ai-employee/AI_Employee_Vault

✅ Test complete: Found 0 new emails
```

### Option B: File System Watcher

**4B.1: Create Watch Directory**

```bash
mkdir -p ~/AI_Employee_Dropbox
```

**4B.2: Test File System Watcher**

```bash
python main.py --test
```

**Expected output**:
```
🧪 Running File System Watcher in test mode...
📂 Watching: /absolute/path/to/personal-ai-employee/AI_Employee_Dropbox
📄 Extensions: *
📁 Vault: /absolute/path/to/personal-ai-employee/AI_Employee_Vault

Monitoring for 10 seconds...
✅ Test complete: Processed 0 files
```

## Step 5: Verify Agent Skill

### 5.1 Check Skill Structure

```bash
ls -la .claude/skills/email-triage/
```

**Expected output**:
```
SKILL.md
examples/
references/
```

### 5.2 Validate Skill

```bash
python -c "
from pathlib import Path
from vault_setup.validators import validate_skill

skill_path = Path('.claude/skills/email-triage')
is_valid, error = validate_skill(skill_path)
print(f'✓ Skill is valid' if is_valid else f'✗ Error: {error}')
"
```

**Expected output**: `✓ Skill is valid`

## Step 6: Run End-to-End Test

### 6.1 Start Watcher

In a terminal window:

```bash
python main.py
```

**Expected output**:
```
======================================================================
🤖 Personal AI Employee - Watcher
======================================================================

📍 Vault: /absolute/path/to/personal-ai-employee/AI_Employee_Vault
🔧 Watcher Type: gmail
🔄 Mode: Continuous monitoring

Press Ctrl+C to stop

======================================================================

[2026-03-07 15:30:00] [GmailWatcher] [INFO] Starting GmailWatcher
[2026-03-07 15:30:00] [GmailWatcher] [INFO] Monitoring with check interval: 120 seconds
```

### 6.2 Trigger Test Event

**For Gmail Watcher**:
1. Send yourself an email
2. Mark it as important in Gmail
3. Wait up to 2 minutes

**For File System Watcher**:
```bash
echo "Test document" > ~/AI_Employee_Dropbox/test.txt
```

### 6.3 Verify Task File Created

Check Obsidian vault:

```bash
ls ~/AI_Employee_Vault/Needs_Action/
```

You should see a new `.md` file (e.g., `EMAIL_20260307T153000Z_test.md`)

### 6.4 Process Task with Claude Code

Open a new terminal:

```bash
cd ~/AI_Employee_Vault
claude "Process all tasks in /Needs_Action using the email-triage skill. Create plans in /Plans and move tasks to /Done."
```

### 6.5 Verify Results

Check in Obsidian:
- `/Plans/` should contain new plan file
- `/Done/` should contain processed task file
- `/Needs_Action/` should be empty

## Step 7: Daily Usage Setup

### 7.1 Create Startup Script (Optional)

Create `~/start-ai-employee.sh`:

```bash
#!/bin/bash
cd ~/personal-ai-employee
source .venv/bin/activate
python main.py
```

Make executable:
```bash
chmod +x ~/start-ai-employee.sh
```

### 7.2 Morning Routine

```bash
# Start watcher
~/start-ai-employee.sh

# Open Obsidian
open -a Obsidian ~/AI_Employee_Vault
```

### 7.3 Process Tasks

When Watcher detects new items:

```bash
cd ~/AI_Employee_Vault
claude "Process tasks in /Needs_Action"
```

## Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for common issues and solutions.

## Success Checklist

- [ ] Obsidian vault created with all folders
- [ ] Dashboard.md and Company_Handbook.md exist
- [ ] Python dependencies installed
- [ ] One Watcher configured and tested
- [ ] Agent Skill validated
- [ ] Test task successfully created by Watcher
- [ ] Claude Code processed task and created plan
- [ ] Task moved to /Done folder
- [ ] System runs for 24 hours without crashes

## Next Steps

After Bronze tier is working:

1. **Test for 24 hours**: Let the system run continuously
2. **Refine Company_Handbook.md**: Add your specific rules and policies
3. **Create more Agent Skills**: Add skills for your specific workflows
4. **Plan Silver Tier**: Add second Watcher, MCP servers, HITL approval

## Support

- **Documentation**: See `/docs` folder
- **Issues**: Report bugs on GitHub
- **Specifications**: See `/specs/001-bronze-tier/`

**Congratulations!** Your Personal AI Employee Bronze tier is ready.
