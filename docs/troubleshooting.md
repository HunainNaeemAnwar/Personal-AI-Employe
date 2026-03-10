# Troubleshooting Guide

**Purpose**: Common issues and solutions for Personal AI Employee (Bronze and Silver tiers)

## Table of Contents

1. [Vault Creation Issues](#vault-creation-issues)
2. [Gmail Watcher Issues](#gmail-watcher-issues)
3. [File System Watcher Issues](#file-system-watcher-issues)
4. [State Database Issues](#state-database-issues) (Silver Tier)
5. [LinkedIn Watcher Issues](#linkedin-watcher-issues) (Silver Tier)
6. [MCP Server Issues](#mcp-server-issues) (Silver Tier)
7. [Claude Code Integration Issues](#claude-code-integration-issues)
8. [Agent Skill Issues](#agent-skill-issues)
9. [General System Issues](#general-system-issues)

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

## State Database Issues (Silver Tier)

### Issue: "State database corruption detected"

**Symptoms**: Orchestrator logs show database corruption, watchers may create duplicate tasks

**Cause**: Unexpected shutdown, disk full, or file system errors

**Solution (Automatic)**:
The orchestrator automatically detects and recovers from corruption:
1. Backs up corrupted database to `state_corrupted_YYYYMMDD_HHMMSS.db`
2. Deletes corrupted database
3. Reinitializes schema
4. Rebuilds state from vault task files

**Solution (Manual)**:
```bash
# Check database integrity
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Healthy' if sm.health_check() else 'Corrupted')"

# Manual recovery
python -c "from watchers.state_manager import StateManager; from pathlib import Path; sm = StateManager(); sm.recover_from_corruption(Path('AI_Employee_Vault'))"

# Verify recovery
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Items:', len(sm.get_items_by_status('processed', limit=1000)))"
```

### Issue: "Duplicate tasks created after restart"

**Symptoms**: Same email/file creates multiple task files after watcher restart

**Cause**: State database not persisting or being cleared

**Solution**:
```bash
# Check if state.db exists
ls -la state.db

# Check state database contents
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Total items:', len(sm.get_items_by_status('processed', limit=1000)))"

# If empty, rebuild from vault
python -c "from watchers.state_manager import StateManager; from pathlib import Path; sm = StateManager(); count = sm.rebuild_from_vault(Path('AI_Employee_Vault')); print(f'Rebuilt {count} items')"

# Restart watchers
python -m watchers.orchestrator
```

### Issue: "Database is locked"

**Symptoms**: Error message "database is locked" in logs

**Cause**: Multiple processes trying to write to database simultaneously, or stale lock

**Solution**:
```bash
# Stop all watchers
pkill -f "python -m watchers"

# Check for stale locks
lsof state.db  # Linux/macOS
# Or check Task Manager on Windows

# Wait 5 seconds for locks to clear
sleep 5

# Restart orchestrator (manages all watchers)
python -m watchers.orchestrator
```

### Issue: "State database health check failed"

**Symptoms**: Orchestrator logs show health check failures every 5 minutes

**Cause**: Schema version mismatch or missing tables

**Solution**:
```bash
# Backup current database
cp state.db state_backup_manual.db

# Check schema version
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Health:', sm.health_check())"

# If schema mismatch, reinitialize
rm state.db
python -c "from watchers.state_manager import StateManager; sm = StateManager()"

# Rebuild from vault
python -c "from watchers.state_manager import StateManager; from pathlib import Path; sm = StateManager(); sm.rebuild_from_vault(Path('AI_Employee_Vault'))"
```

### Issue: "State database growing too large"

**Symptoms**: state.db file size exceeds 100MB, performance degradation

**Cause**: Too many processed items accumulated over time

**Solution**:
```bash
# Check database size
ls -lh state.db

# Archive old items (manual cleanup)
python -c "
from watchers.state_manager import StateManager
## LinkedIn Rate Limits

### Issue: LinkedIn API Rate Limit Exceeded

**Symptoms:**
- LinkedIn watcher logs show "Rate limit exceeded" errors
- LinkedIn messages not being detected
- LinkedIn posts failing to publish

**Cause:** LinkedIn API has rate limits (100 requests/hour by default)

**Solution:**

1. **Check current rate limit usage:**
```python
python -c "
from watchers.linkedin_watcher import LinkedInWatcher
import os
from dotenv import load_dotenv

load_dotenv()
watcher = LinkedInWatcher(
    vault_path=os.getenv('VAULT_PATH'),
    username=os.getenv('LINKEDIN_USERNAME'),
    password=os.getenv('LINKEDIN_PASSWORD')
)
print(f'Requests made: {watcher.rate_limiter.requests_made}')
print(f'Window start: {watcher.rate_limiter.window_start}')
"
```

2. **Increase polling interval in .env:**
```bash
LINKEDIN_POLLING_INTERVAL=600  # 10 minutes instead of 5
```

3. **Reduce rate limit requests:**
```bash
LINKEDIN_RATE_LIMIT_REQUESTS=50  # More conservative limit
```

4. **Wait for rate limit window to reset** (1 hour from first request)

5. **Use Selenium fallback** if API consistently hits limits

### Issue: LinkedIn Authentication Failed

**Symptoms:**
- LinkedIn watcher fails to start
- "Authentication failed" in logs
- LinkedIn API returns 401 Unauthorized

**Cause:** Invalid LinkedIn credentials or expired session

**Solution:**

1. **Verify credentials in .env:**
```bash
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

2. **Test authentication manually:**
```python
python -c "
from linkedin_api import Linkedin
import os
from dotenv import load_dotenv

load_dotenv()
api = Linkedin(
    os.getenv('LINKEDIN_USERNAME'),
    os.getenv('LINKEDIN_PASSWORD')
)
profile = api.get_profile('me')
print(f'✓ Authenticated as: {profile.get(\"firstName\")} {profile.get(\"lastName\")}')
"
```

3. **If using 2FA**, disable it temporarily or use app-specific password

4. **Check for LinkedIn account restrictions** (e.g., temporary suspension)

5. **Try Selenium fallback** if API authentication continues to fail

## MCP Server Not Found

### Issue: Claude Code Cannot Find Email MCP Server

**Symptoms:**
- `send_email` tool not available in Claude Code
- "MCP server not found" error
- Email sending fails

**Cause:** MCP server not configured in Claude Code config.json

**Solution:**

1. **Verify MCP server is built:**
```bash
cd mcp_servers/email_sender
npm run build
ls dist/index.js  # Should exist
```

2. **Check Claude Code config:**
```bash
cat ~/.claude/config.json
```

Should contain:
```json
{
  "mcpServers": {
    "email-sender": {
      "command": "node",
      "args": ["/absolute/path/to/mcp_servers/email_sender/dist/index.js"]
    }
  }
}
```

3. **Update config with absolute path:**
```bash
# Get absolute path
cd mcp_servers/email_sender
pwd  # Copy this path

# Edit config
nano ~/.claude/config.json
```

4. **Restart Claude Code** after config change

5. **Test MCP server manually:**
```bash
cd mcp_servers/email_sender
node dist/index.js
# Should start without errors
```

### Issue: MCP Server Crashes on Startup

**Symptoms:**
- MCP server starts but immediately crashes
- "Module not found" errors in logs
- Gmail API errors

**Cause:** Missing dependencies or invalid Gmail credentials

**Solution:**

1. **Reinstall dependencies:**
```bash
cd mcp_servers/email_sender
rm -rf node_modules package-lock.json
npm install
npm run build
```

2. **Verify Gmail credentials:**
```bash
ls -la ~/.credentials/gmail-credentials.json
# Should exist and be readable
```

3. **Check .env configuration:**
```bash
grep GMAIL .env
# Verify paths are absolute and correct
```

4. **Test Gmail API access:**
```bash
cd mcp_servers/email_sender
node -e "
const { GmailClient } = require('./dist/gmail-client.js');
const client = new GmailClient();
console.log('✓ Gmail client initialized');
"
```

5. **Check Node.js version:**
```bash
node --version  # Should be v24+
```

## State Database Locked

### Issue: Database is Locked Error

**Symptoms:**
- "database is locked" errors in watcher logs
- Tasks not being marked as processed
- Watchers unable to write to state database

**Cause:** Multiple processes trying to write to SQLite database simultaneously

**Solution:**

1. **Check for multiple watcher processes:**
```bash
ps aux | grep -E "gmail_watcher|filesystem_watcher|linkedin_watcher"
```

2. **Kill duplicate processes:**
```bash
pkill -f "python -m watchers.gmail_watcher"
pkill -f "python -m watchers.filesystem_watcher"
pkill -f "python -m watchers.linkedin_watcher"
```

3. **Use orchestrator instead of running watchers individually:**
```bash
python watchers/orchestrator.py
```

4. **Increase SQLite timeout in state_manager.py** (if needed):
```python
conn = sqlite3.connect(str(self.db_path), timeout=30.0)
```

5. **Check file permissions:**
```bash
ls -la state.db
chmod 644 state.db  # If needed
```

## Orchestrator Issues

### Issue: Orchestrator Not Restarting Crashed Watchers

**Symptoms:**
- Watcher crashes but orchestrator doesn't restart it
- "Maximum restart attempts reached" in logs
- Watchers remain stopped

**Cause:** Watcher crashing repeatedly, exceeding max restart attempts

**Solution:**

1. **Check orchestrator logs:**
```bash
tail -f AI_Employee_Vault/Logs/orchestrator.log
```

2. **Check individual watcher error logs:**
```bash
tail -f AI_Employee_Vault/Logs/gmail_watcher_error.log
tail -f AI_Employee_Vault/Logs/filesystem_watcher_error.log
tail -f AI_Employee_Vault/Logs/linkedin_watcher_error.log
```

3. **Fix underlying watcher issue** (credentials, permissions, etc.)

4. **Increase max restart attempts in .env:**
```bash
ORCHESTRATOR_MAX_RESTART_ATTEMPTS=20  # Default is 10
```

5. **Restart orchestrator:**
```bash
pkill -f orchestrator
python watchers/orchestrator.py
```

### Issue: Heartbeat Files Not Being Updated

**Symptoms:**
- Orchestrator reports "heartbeat is stale"
- Watchers appear to be running but heartbeat not updating
- Orchestrator keeps restarting healthy watchers

**Cause:** Watcher process frozen or heartbeat write failing

**Solution:**

1. **Check heartbeat files:**
```bash
ls -la AI_Employee_Vault/Logs/*_heartbeat.txt
cat AI_Employee_Vault/Logs/gmail_watcher_heartbeat.txt
```

2. **Verify file permissions:**
```bash
chmod 644 AI_Employee_Vault/Logs/*_heartbeat.txt
```

3. **Check watcher process status:**
```bash
ps aux | grep -E "gmail_watcher|filesystem_watcher|linkedin_watcher"
```

4. **Restart specific watcher:**
```bash
# Orchestrator will detect crash and restart automatically
pkill -f "python -m watchers.gmail_watcher"
```

5. **Adjust health check interval if needed:**
```bash
ORCHESTRATOR_HEALTH_CHECK_INTERVAL=120  # 2 minutes instead of 1
```

## Scheduled Tasks Not Executing

### Issue: Cron Jobs Not Running (Linux/Mac)

**Symptoms:**
- Scheduled tasks not executing at configured times
- No entries in scheduled_tasks.log
- Cron jobs appear in crontab but don't run

**Cause:** Cron service not running, incorrect paths, or permission issues

**Solution:**

1. **Verify cron service is running:**
```bash
# Linux
sudo systemctl status cron

# macOS
sudo launchctl list | grep cron
```

2. **Check crontab entries:**
```bash
crontab -l | grep "AI Employee"
```

3. **Test task execution manually:**
```bash
python -m scheduler.task_executor --task morning_briefing
```

4. **Check cron logs:**
```bash
# Linux
sudo tail -f /var/log/syslog | grep CRON

# macOS
tail -f /var/log/system.log | grep cron
```

5. **Use absolute paths in cron commands:**
```bash
# Edit crontab
crontab -e

# Change relative paths to absolute
0 8 * * * /usr/bin/python3 /absolute/path/to/scheduler/task_executor.py --task morning_briefing
```

### Issue: Task Scheduler Jobs Not Running (Windows)

**Symptoms:**
- Scheduled tasks not executing at configured times
- Task Scheduler shows tasks as "Ready" but never run
- No entries in scheduled_tasks.log

**Cause:** Task Scheduler configuration issues or permission problems

**Solution:**

1. **Check Task Scheduler:**
```powershell
Get-ScheduledTask -TaskName "AIEmployee_*" | Format-Table TaskName, State, LastRunTime, NextRunTime
```

2. **Verify task is enabled:**
```powershell
Get-ScheduledTask -TaskName "AIEmployee_morning_briefing" | Select-Object State
# Should be "Ready", not "Disabled"
```

3. **Check task history:**
```powershell
Get-ScheduledTask -TaskName "AIEmployee_morning_briefing" | Get-ScheduledTaskInfo
```

4. **Run task manually:**
```powershell
Start-ScheduledTask -TaskName "AIEmployee_morning_briefing"
```

5. **Recreate task with correct settings:**
```powershell
python -m scheduler.task_scheduler_setup remove
python -m scheduler.task_scheduler_setup setup
```

### Issue: Tasks Skipped Due to Overlap

**Symptoms:**
- "Task already running, skipping execution" in logs
- Tasks not executing even though previous execution finished
- Lock files remain after task completion

**Cause:** Lock file not released properly or task still running

**Solution:**

1. **Check for running task processes:**
```bash
ps aux | grep task_executor
```

2. **Check lock files:**
```bash
ls -la /tmp/ai_employee_locks/
```

3. **Remove stale lock files:**
```bash
rm /tmp/ai_employee_locks/*.lock
```

4. **Disable overlap prevention if not needed:**
```yaml
# In scheduled_tasks.yaml
execution_settings:
  prevent_overlap: false
```

5. **Increase task timeout:**
```yaml
execution_settings:
  max_execution_time: 7200  # 2 hours
```

## Approval Workflow Issues

### Issue: Approval Commands Not Working

**Symptoms:**
- `claude "approve task TASK_ID"` does nothing
- Tasks remain in /Pending_Approval
- No approval log entries

**Cause:** Approval workflow skill not loaded or incorrect command syntax

**Solution:**

1. **Verify approval workflow skill exists:**
```bash
ls -la .claude/skills/approval-workflow/SKILL.md
```

2. **Check task ID format:**
```bash
# List pending tasks
ls AI_Employee_Vault/Pending_Approval/
# Use exact filename without .md extension
```

3. **Use correct command syntax:**
```bash
claude "approve task EMAIL_20260309T143000Z_client-inquiry"
# NOT: claude "approve EMAIL_20260309T143000Z_client-inquiry.md"
```

4. **Check approval log:**
```bash
tail -f AI_Employee_Vault/Logs/approvals.log
```

5. **Manually move task if needed:**
```bash
mv AI_Employee_Vault/Pending_Approval/TASK_ID.md AI_Employee_Vault/Approved/
```

### Issue: Tasks Not Moving to Pending Approval

**Symptoms:**
- Tasks that should require approval go directly to execution
- No tasks in /Pending_Approval folder
- Approval thresholds not being enforced

**Cause:** Approval workflow skill not being applied or thresholds not configured

**Solution:**

1. **Verify Company_Handbook.md has approval thresholds:**
```bash
grep -A 10 "Approval Thresholds" AI_Employee_Vault/Company_Handbook.md
```

2. **Check if approval workflow skill is loaded:**
```bash
claude "list skills" | grep approval
```

3. **Manually trigger approval workflow:**
```bash
claude "Evaluate task EMAIL_20260309T143000Z for approval requirements"
```

4. **Check task metadata:**
```bash
head -20 AI_Employee_Vault/Needs_Action/EMAIL_*.md
# Should have approval_required: true if threshold exceeded
```

5. **Update Company_Handbook.md with thresholds** if missing

## Performance Issues

### Issue: Email Detection Slow (>2 minutes)

**Symptoms:**
- Gmail watcher takes >2 minutes to detect new emails
- High latency between email arrival and task creation

**Cause:** High polling interval or Gmail API quota issues

**Solution:**

1. **Reduce polling interval:**
```bash
GMAIL_POLLING_INTERVAL=30  # 30 seconds instead of 60
```

2. **Check Gmail API quota:**
```bash
# Visit Google Cloud Console
# APIs & Services > Gmail API > Quotas
```

3. **Optimize Gmail query:**
```bash
GMAIL_QUERY="is:unread is:important newer_than:1h"
```

4. **Check network latency:**
```bash
ping gmail.googleapis.com
```

### Issue: LinkedIn Polling Slow (>5 minutes)

**Symptoms:**
- LinkedIn watcher takes >5 minutes to detect new messages
- High latency between message arrival and task creation

**Cause:** High polling interval or rate limit throttling

**Solution:**

1. **Reduce polling interval (carefully):**
```bash
LINKEDIN_POLLING_INTERVAL=180  # 3 minutes instead of 5
```

2. **Check rate limit usage:**
```python
python -c "
from watchers.linkedin_watcher import LinkedInWatcher
# Check requests_made vs rate_limit_requests
"
```

3. **Use Selenium fallback** for more frequent checks

### Issue: Email Sending Slow (>5 seconds)

**Symptoms:**
- Email sending takes >5 seconds
- MCP server timeout errors

**Cause:** Network latency or Gmail API throttling

**Solution:**

1. **Check network latency:**
```bash
ping gmail.googleapis.com
```

2. **Verify Gmail API quota:**
```bash
# Check daily send limit in Google Cloud Console
```

3. **Reduce retry attempts if needed:**
```typescript
// In mcp_servers/email_sender/src/gmail-client.ts
const MAX_RETRIES = 2;  // Instead of 3
```

4. **Check MCP server logs:**
```bash
tail -f AI_Employee_Vault/Logs/email_sent.log
```

## Getting Help

If you're still experiencing issues after trying these solutions:

1. **Check GitHub Issues**: Search for similar problems
2. **Enable verbose logging**: Set `verbose_logging: true` in configs
3. **Collect diagnostic information**:
   - Orchestrator logs
   - Watcher logs
   - State database health check
   - MCP server logs
   - Scheduled task logs
4. **Create GitHub Issue** with:
   - Error messages
   - Log excerpts
   - Configuration (sanitized)
   - Steps to reproduce

## Additional Resources

- **Setup Guide**: `docs/setup_guide.md`
- **Gmail API Setup**: `docs/gmail_api_setup.md`
- **LinkedIn API Setup**: `docs/linkedin_api_setup.md`
- **MCP Server Setup**: `docs/mcp_server_setup.md`
- **Scheduling Setup**: `docs/scheduling_setup.md`
- **Quickstart Validation**: `specs/002-silver-tier/quickstart.md`
    print(f'✓ {len(processed)} processed items')
else:
    print('✗ Database still unhealthy')
"

# 6. Restart orchestrator
python -m watchers.orchestrator
```

**Preventive Maintenance:**

```bash
# Daily backup (add to cron)
python -c "from watchers.state_manager import StateManager; sm = StateManager(); sm.backup_database('backups/state_$(date +%Y%m%d).db')"

# Weekly integrity check
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Corrupted' if sm.detect_corruption() else 'Healthy')"

# Monthly cleanup (remove items older than 90 days)
python -c "
from watchers.state_manager import StateManager
from datetime import datetime, timedelta
import sqlite3

sm = StateManager()
cutoff = (datetime.utcnow() - timedelta(days=90)).isoformat()

with sm._get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute('DELETE FROM processed_items WHERE created_at < ?', (cutoff,))
    conn.commit()
    print(f'Cleaned up {cursor.rowcount} old items')
"
```

---

## LinkedIn Watcher Issues (Silver Tier)

### Issue: "LinkedIn API authentication failed"

**Symptoms**: LinkedIn watcher logs show authentication errors

**Cause**: Invalid credentials or LinkedIn API access revoked

**Solution**:
```bash
# Check credentials in .env
grep LINKEDIN .env

# Test LinkedIn API connection
python -c "from linkedin_api import Linkedin; api = Linkedin('your_email@example.com', 'your_password'); print('Connected')"

# If API fails, watcher automatically falls back to Selenium
# Check logs for "Using Selenium fallback" message
```

### Issue: "LinkedIn rate limit exceeded"

**Symptoms**: Watcher logs show "Rate limit reached" warnings

**Cause**: Too many API requests in 1-hour window (limit: 100 requests/hour)

**Solution**:
```bash
# Watcher automatically waits for rate limit reset
# Check logs for wait time

# Increase polling interval to reduce requests
# Edit .env:
LINKEDIN_POLLING_INTERVAL=600  # 10 minutes instead of 5
```

### Issue: "LinkedIn messages not detected"

**Symptoms**: LinkedIn messages don't create task files

**Cause**: Messaging API access not approved by LinkedIn

**Solution**:
1. Apply for LinkedIn Messaging API access (may take days/weeks)
2. Use Selenium fallback (automatic)
3. Manually check LinkedIn messages

---

## MCP Server Issues (Silver Tier)

### Issue: "Email MCP server not found"

**Symptoms**: Claude Code can't find send_email tool

**Cause**: MCP server not built or not configured in Claude Code

**Solution**:
```bash
# Build MCP server
cd mcp_servers/email_sender
npm install
npm run build

# Verify build
ls -la dist/index.js

# Check Claude Code MCP settings
cat ~/.claude/mcp_settings.json

# Test MCP server manually
node dist/index.js
# Should output: "Email Sender MCP server running on stdio"
```

### Issue: "Email sending fails with auth error"

**Symptoms**: send_email tool returns "Insufficient Permission" error

**Cause**: Gmail token doesn't have send permissions

**Solution**:
```bash
# Delete existing token
rm /path/to/.credentials/gmail-token.json

# Update .env with send scopes
# GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.compose

# Re-authenticate (run Gmail watcher to generate new token)
python -m watchers.gmail_watcher
# Follow OAuth flow in browser

# Verify new token has send permissions
python -c "import pickle; token = pickle.load(open('/path/to/.credentials/gmail-token.json', 'rb')); print('Scopes:', token.scopes)"
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
