# Troubleshooting Guide

**Purpose**: Common issues and solutions for Personal AI Employee Bronze tier

## Table of Contents

1. [Vault Creation Issues](#vault-creation-issues)
2. [Gmail Watcher Issues](#gmail-watcher-issues)
3. [File System Watcher Issues](#file-system-watcher-issues)
4. [Claude Code Integration Issues](#claude-code-integration-issues)
5. [Agent Skill Issues](#agent-skill-issues)
6. [General System Issues](#general-system-issues)

---

## Vault Creation Issues

### Issue: "Parent directory is not writable"

**Symptoms**: Vault creation script fails with permission error

**Cause**: Insufficient permissions on parent directory

**Solution**:
```bash
# Check parent directory permissions
ls -la ~/

# Create vault in a directory you own
python -m vault_setup.create_vault --path ~/Documents/AI_Employee_Vault

# Or fix permissions (if you have sudo access)
sudo chown -R $USER ~/AI_Employee_Vault
```

### Issue: "Vault directory already exists"

**Symptoms**: Warning message about existing directory

**Cause**: Vault was previously created at this location

**Solution**:
```bash
# Option 1: Use existing vault (script will add missing folders)
python -m vault_setup.create_vault --path ~/AI_Employee_Vault

# Option 2: Create vault in new location
python -m vault_setup.create_vault --path ~/AI_Employee_Vault_New

# Option 3: Delete old vault and recreate
rm -rf ~/AI_Employee_Vault
python -m vault_setup.create_vault --path ~/AI_Employee_Vault
```

### Issue: "Template file not found"

**Symptoms**: Vault created but Dashboard.md or Handbook.md missing

**Cause**: Template files not found in vault_setup/templates/

**Solution**:
```bash
# Verify templates exist
ls vault_setup/templates/

# If missing, re-clone repository
git pull origin 001-bronze-tier

# Recreate vault
python -m vault_setup.create_vault --path ~/AI_Employee_Vault
```

---

## Gmail Watcher Issues

### Issue: "Credentials file not found"

**Symptoms**: `ValueError: Credentials file not found: /path/to/credentials.json`

**Cause**: Gmail credentials not downloaded or path incorrect

**Solution**:
```bash
# Check if credentials exist
ls ~/.credentials/gmail-credentials.json

# If missing, download from Google Cloud Console
# See docs/gmail_api_setup.md for instructions

# Verify path in .env is absolute (not relative)
cat .env | grep GMAIL_CREDENTIALS_PATH

# Update .env with correct path
nano .env
```

### Issue: "Invalid grant" or "Token expired"

**Symptoms**: Authentication fails with "invalid_grant" error

**Cause**: OAuth token expired or revoked

**Solution**:
```bash
# Delete old token
rm ~/.credentials/gmail-token.json

# Re-authenticate
python main.py --test

# Complete OAuth flow in browser
```

### Issue: "Rate limit exceeded"

**Symptoms**: `HttpError 429: Rate Limit Exceeded`

**Cause**: Too many Gmail API requests

**Solution**:
```bash
# Watcher implements exponential backoff automatically
# Wait 1-2 minutes and it will retry

# If persistent, increase check interval in main.py:
# check_interval=300  # 5 minutes instead of 2
```

### Issue: "No emails detected"

**Symptoms**: Watcher runs but doesn't create task files

**Cause**: Gmail query doesn't match any emails

**Solution**:
```bash
# Test with simpler query
# Edit .env:
GMAIL_QUERY=is:unread

# Verify emails exist in Gmail matching query
# Check logs for details
cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Issue: "Duplicate task files created"

**Symptoms**: Same email creates multiple task files

**Cause**: Watcher restarted and lost processed_items tracking

**Solution**:
```bash
# This is expected behavior after restart
# Manually delete duplicates from /Needs_Action

# To prevent: Keep watcher running continuously
# Or implement persistent processed_items storage (Silver tier feature)
```

---

## File System Watcher Issues

### Issue: "Watch directory does not exist"

**Symptoms**: `ValueError: Watch directory does not exist: /path/to/dir`

**Cause**: Watch directory not created or path incorrect

**Solution**:
```bash
# Create watch directory
mkdir -p ~/AI_Employee_Dropbox

# Verify path in .env is absolute
cat .env | grep WATCH_DIRECTORY

# Update .env with correct path
nano .env
```

### Issue: "Files not detected"

**Symptoms**: Files dropped but no task files created

**Cause**: File extension filter or permissions issue

**Solution**:
```bash
# Check file extension filter in .env
cat .env | grep FILE_EXTENSIONS

# Try wildcard to accept all files
FILE_EXTENSIONS=*

# Check watch directory permissions
ls -la ~/AI_Employee_Dropbox

# Test with simple file
echo "test" > ~/AI_Employee_Dropbox/test.txt

# Check watcher logs
cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json
```

### Issue: "Permission denied" when accessing files

**Symptoms**: Watcher crashes with permission error

**Cause**: Insufficient permissions on watch directory or files

**Solution**:
```bash
# Fix watch directory permissions
chmod 755 ~/AI_Employee_Dropbox

# Fix file permissions
chmod 644 ~/AI_Employee_Dropbox/*

# Ensure watcher user owns the directory
chown -R $USER ~/AI_Employee_Dropbox
```

### Issue: "Files processed multiple times"

**Symptoms**: Same file creates multiple task files

**Cause**: File being modified after creation (triggers multiple events)

**Solution**:
```bash
# Watcher has 1-second debouncing to prevent this
# If still occurring, increase debounce time in filesystem_watcher.py:
# debounce_time=3.0  # 3 seconds instead of 1
```

---

## Claude Code Integration Issues

### Issue: "Claude can't find vault"

**Symptoms**: Claude reports it can't access vault files

**Cause**: Not running Claude from vault directory

**Solution**:
```bash
# Always cd to vault directory first
cd ~/AI_Employee_Vault
pwd  # Verify you're in the vault

# Then run Claude
claude "Process tasks in /Needs_Action"

# Or use absolute path
cd ~/AI_Employee_Vault && claude "Process tasks"
```

### Issue: "Task files malformed"

**Symptoms**: Claude reports YAML parsing errors

**Cause**: Invalid YAML frontmatter in task files

**Solution**:
```bash
# Validate task file manually
python -c "
from pathlib import Path
from vault_setup.validators import validate_task_file

file_path = Path('~/AI_Employee_Vault/Needs_Action/TASK_FILE.md').expanduser()
is_valid, error = validate_task_file(file_path)
print(f'Valid: {is_valid}')
if not is_valid:
    print(f'Error: {error}')
"

# Fix YAML syntax (no tabs, proper indentation)
# Ensure required fields present: type, source, timestamp, priority, status
```

### Issue: "Plans not created"

**Symptoms**: Claude processes tasks but no plans appear

**Cause**: Plans folder doesn't exist or permissions issue

**Solution**:
```bash
# Check Plans folder exists
ls -la ~/AI_Employee_Vault/Plans

# Create if missing
mkdir -p ~/AI_Employee_Vault/Plans

# Check permissions
chmod 755 ~/AI_Employee_Vault/Plans

# Try explicit instruction
claude "Create a plan in /Plans for the task in /Needs_Action"
```

### Issue: "Tasks not moved to /Done"

**Symptoms**: Tasks processed but remain in /Needs_Action

**Cause**: Claude didn't complete the move step

**Solution**:
```bash
# Manually move completed tasks
mv ~/AI_Employee_Vault/Needs_Action/TASK_FILE.md ~/AI_Employee_Vault/Done/

# Or ask Claude explicitly
claude "Move all processed tasks from /Needs_Action to /Done"
```

---

## Agent Skill Issues

### Issue: "Skill not found"

**Symptoms**: Claude doesn't apply email-triage skill

**Cause**: Skill not in correct location or invalid structure

**Solution**:
```bash
# Verify skill location
ls .claude/skills/email-triage/SKILL.md

# Validate skill structure
python -c "
from pathlib import Path
from vault_setup.validators import validate_skill

skill_path = Path('.claude/skills/email-triage')
is_valid, error = validate_skill(skill_path)
print(f'Valid: {is_valid}')
if not is_valid:
    print(f'Error: {error}')
"

# Restart Claude Code to reload skills
```

### Issue: "Skill validation fails"

**Symptoms**: validate_skill() returns False

**Cause**: Invalid YAML frontmatter or missing sections

**Solution**:
```bash
# Check YAML frontmatter format
head -n 5 .claude/skills/email-triage/SKILL.md

# Should start with:
# ---
# name: email-triage
# description: ...
# ---

# Check for required sections
grep "## Instructions" .claude/skills/email-triage/SKILL.md
grep "## Examples" .claude/skills/email-triage/SKILL.md

# Fix any issues and re-validate
```

### Issue: "Skill not applied automatically"

**Symptoms**: Skill exists but Claude doesn't use it

**Cause**: Trigger conditions not met or skill description unclear

**Solution**:
```bash
# Explicitly invoke skill
claude "Use the email-triage skill to process all email tasks in /Needs_Action"

# Improve skill description to be more specific about when to use it
# Edit .claude/skills/email-triage/SKILL.md
```

---

## General System Issues

### Issue: "Dependencies not installed"

**Symptoms**: `ModuleNotFoundError: No module named 'watchdog'`

**Cause**: Python dependencies not installed

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Verify installation
python -c "import watchdog; import yaml; import google.auth; print('OK')"
```

### Issue: "Python version too old"

**Symptoms**: `SyntaxError` or version mismatch errors

**Cause**: Python version < 3.13

**Solution**:
```bash
# Check Python version
python --version

# Should be 3.13 or higher
# If not, install Python 3.13+
# Then recreate virtual environment:
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

### Issue: "Watcher crashes unexpectedly"

**Symptoms**: Watcher stops running without error message

**Cause**: Unhandled exception or system resource issue

**Solution**:
```bash
# Check logs for errors
cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json

# Run with verbose logging
python main.py 2>&1 | tee watcher.log

# Check system resources
top  # Look for memory/CPU issues

# Restart watcher
python main.py
```

### Issue: "Logs not created"

**Symptoms**: /Logs folder empty

**Cause**: Logs folder doesn't exist or permissions issue

**Solution**:
```bash
# Create Logs folder
mkdir -p ~/AI_Employee_Vault/Logs

# Check permissions
chmod 755 ~/AI_Employee_Vault/Logs

# Verify watcher is writing logs
python main.py --test
ls ~/AI_Employee_Vault/Logs/
```

### Issue: "Environment variables not loaded"

**Symptoms**: `ValueError: Required environment variable X is not set`

**Cause**: .env file not found or not loaded

**Solution**:
```bash
# Check .env exists
ls -la .env

# Verify .env has correct format (no spaces around =)
cat .env

# Example correct format:
# VAULT_PATH=/path/to/vault
# WATCHER_TYPE=gmail

# Reload environment
source .venv/bin/activate
python main.py
```

---

## Getting Help

If you've tried the solutions above and still have issues:

1. **Check Logs**: `cat ~/AI_Employee_Vault/Logs/$(date +%Y-%m-%d).json`
2. **Run in Test Mode**: `python main.py --test` for detailed output
3. **Validate Configuration**: Check all paths in `.env` are absolute and correct
4. **Review Documentation**: See `/docs` folder for detailed guides
5. **Report Issue**: Create GitHub issue with:
   - Error message (full traceback)
   - Steps to reproduce
   - System info (OS, Python version)
   - Relevant log files

## Quick Diagnostic Script

Run this to check your setup:

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

Save as `diagnostic.sh`, make executable (`chmod +x diagnostic.sh`), and run (`./diagnostic.sh`).
