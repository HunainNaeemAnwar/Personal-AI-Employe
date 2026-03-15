# Personal AI Employee - Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
# Python dependencies
uv pip install -e .

# Node.js dependencies (for email MCP server)
cd mcp_servers/email_sender
npm install && npm run build
cd ../..
```

### Step 2: Configure Environment (1 minute)

```bash
# Copy example configuration
cp .env.example .env

# Edit with your settings
nano .env
```

**Minimum Required Configuration**:
```bash
VAULT_PATH=AI_Employee_Vault
WATCH_DIRECTORY=Watch
ORCHESTRATOR_WATCHERS=filesystem  # Start with just filesystem
STATE_DB_PATH=state.db
```

### Step 3: Create Vault Structure (30 seconds)

```bash
python -m vault_setup.setup
```

### Step 4: Start the System (30 seconds)

```bash
# Start orchestrator (runs all configured watchers)
python -m watchers.orchestrator
```

### Step 5: Test It Works (1 minute)

```bash
# In another terminal, drop a test file
echo "Test content" > Watch/test.txt

# Check that a task was created
ls -la AI_Employee_Vault/Needs_Action/
# You should see: FILE_DROP_YYYYMMDDTHHMMSSZ_test.md
```

**Success!** Your AI Employee is now monitoring the Watch directory.

---

## Common Usage Patterns

### Pattern 1: File Processing

**Use Case**: Automatically process documents dropped into a folder

```bash
# 1. Drop files into Watch directory
cp ~/Downloads/invoice.pdf Watch/

# 2. Task appears in vault
ls AI_Employee_Vault/Needs_Action/
# FILE_DROP_20260310T120000Z_invoice.md

# 3. Process with Claude
claude "Process the invoice task in Needs_Action"

# 4. Move to Done when complete
mv AI_Employee_Vault/Needs_Action/FILE_DROP_*.md AI_Employee_Vault/Done/
```

### Pattern 2: Email Monitoring

**Use Case**: Monitor Gmail inbox and create tasks for new emails

```bash
# 1. Configure Gmail credentials in .env
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle
ORCHESTRATOR_WATCHERS=gmail,filesystem

# 2. Restart orchestrator
# New emails will appear as tasks within 2 minutes

# 3. Process email tasks
claude "Draft a reply to the email task in Needs_Action"

# 4. Send reply via MCP server
# (Claude will use the email-sender MCP tool)
```

### Pattern 3: LinkedIn Business Development

**Use Case**: Monitor LinkedIn messages and post updates

```bash
# 1. Configure LinkedIn credentials in .env
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password
ORCHESTRATOR_WATCHERS=gmail,filesystem,linkedin

# 2. Restart orchestrator
# LinkedIn messages will appear as tasks within 10 minutes

# 3. Create a post task
cat > AI_Employee_Vault/Needs_Action/LINKEDIN_POST_manual.md << 'EOF'
---
type: linkedin_post
status: pending
---

# LinkedIn Post: Weekly Update

Post our weekly business update to LinkedIn.

## Content
[Your post content here]
EOF

# 4. Process with Claude
claude "Create a LinkedIn post from the task in Needs_Action"
```

### Pattern 4: Approval Workflow

**Use Case**: Require approval for sensitive actions

```bash
# 1. Create a high-value task
cat > AI_Employee_Vault/Needs_Action/PAYMENT_invoice.md << 'EOF'
---
type: payment
amount: 750
status: pending
---

# Payment: Client Invoice

Process payment of $750 for client invoice #12345.
EOF

# 2. Approval workflow evaluates threshold
# Task automatically moves to Pending_Approval

# 3. Review and approve
claude "approve task PAYMENT_invoice"

# 4. Task moves to Approved and can be executed
```

### Pattern 5: Scheduled Tasks

**Use Case**: Automatically execute recurring tasks

```bash
# 1. Configure scheduled tasks
nano scheduled_tasks.yaml

# 2. Add a task
scheduled_tasks:
  - id: morning_briefing
    description: Generate daily morning briefing
    schedule: "0 8 * * *"  # 8 AM daily
    command: python -m scheduler.task_executor --task morning_briefing
    enabled: true

# 3. Install cron job (Linux/Mac)
python -m scheduler.cron_setup

# 4. Task executes automatically at 8 AM
# Output appears in AI_Employee_Vault/Briefings/
```

---

## Daily Workflow

### Morning Routine (5 minutes)

```bash
# 1. Check overnight activity
ls AI_Employee_Vault/Needs_Action/

# 2. Review pending approvals
ls AI_Employee_Vault/Pending_Approval/

# 3. Process high-priority tasks
claude "Review all tasks in Needs_Action and prioritize"

# 4. Check system health
./scripts/validate.sh
```

### During the Day (as needed)

```bash
# Drop files for processing
cp ~/Downloads/*.pdf Watch/

# Check for new tasks
watch -n 60 'ls -lt AI_Employee_Vault/Needs_Action/ | head -10'

# Process tasks with Claude
claude "Process the next task in Needs_Action"
```

### Evening Routine (2 minutes)

```bash
# Review completed tasks
ls AI_Employee_Vault/Done/

# Check for pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Review logs for errors
tail -50 AI_Employee_Vault/Logs/orchestrator.log
```

---

## Monitoring & Maintenance

### Check System Status

```bash
# Quick status check
./scripts/validate.sh

# Check if orchestrator is running
ps aux | grep orchestrator

# Check watcher processes
ps aux | grep watcher

# View recent logs
tail -f AI_Employee_Vault/Logs/orchestrator.log
```

### Monitor Performance

```bash
# Check task creation rate
find AI_Employee_Vault/Needs_Action -name "*.md" -mtime -1 | wc -l

# Check state database size
du -h state.db

# Check for duplicate tasks
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Items:', len(sm.get_items_by_status('pending', limit=1000)))"
```

### Troubleshooting

```bash
# Restart orchestrator
pkill -f orchestrator
python -m watchers.orchestrator

# Check state database health
python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Health:', sm.health_check())"

# Rebuild state database if corrupted
python -c "from watchers.state_manager import StateManager; sm = StateManager(); sm.rebuild_from_vault('AI_Employee_Vault')"

# View detailed logs
tail -100 AI_Employee_Vault/Logs/gmail_watcher_error.log
tail -100 AI_Employee_Vault/Logs/filesystem_watcher_error.log
```

---

## Advanced Usage

### Custom Scheduled Tasks

```yaml
# scheduled_tasks.yaml
scheduled_tasks:
  - id: weekly_report
    description: Generate weekly activity report
    schedule: "0 9 * * 1"  # Monday 9 AM
    command: python -m scheduler.task_executor --task weekly_report
    enabled: true
    retry_on_failure: true
    max_retries: 3

  - id: database_backup
    description: Backup state database
    schedule: "0 2 * * *"  # 2 AM daily
    command: python -m scheduler.task_executor --task database_backup
    enabled: true
```

### Custom Approval Thresholds

Edit `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Approval Thresholds

### Financial Decisions
- Under $100: Auto-approve
- $100-$500: Flag for review
- Over $500: Require explicit approval

### Communication Actions
- Reply to known contacts: Auto-approve
- Reply to new contacts: Require approval
- Client communications: Require approval
- Social media posts: Require approval

### Data Operations
- Read operations: Auto-approve
- Create/Update single records: Auto-approve
- Bulk operations (>10 items): Require approval
- Delete operations: Always require approval
```

### Multi-Step Task Planning

```bash
# 1. Create a complex task
cat > AI_Employee_Vault/Needs_Action/COMPLEX_campaign.md << 'EOF'
---
type: email_campaign
status: pending
---

# Email Campaign: Product Launch

Send product launch emails to 50 customers.

## Requirements
- Personalized emails
- Track opens and clicks
- Follow up with non-responders
EOF

# 2. Use planning skill
claude "Create a plan for the email campaign task"

# 3. Plan.md created in /Plans
cat AI_Employee_Vault/Plans/PLAN_COMPLEX_campaign.md

# 4. Execute plan step by step
claude "Execute step 1 of the email campaign plan"
```

---

## Configuration Reference

### Environment Variables

```bash
# Vault Configuration
VAULT_PATH=AI_Employee_Vault          # Path to Obsidian vault
WATCH_DIRECTORY=Watch                  # Directory to monitor for files

# Orchestrator Configuration
ORCHESTRATOR_WATCHERS=gmail,filesystem,linkedin  # Comma-separated list
ORCHESTRATOR_HEALTH_CHECK_INTERVAL=60  # Seconds between health checks
ORCHESTRATOR_RESTART_DELAY=5           # Seconds before restarting crashed watcher
WATCHER_HEARTBEAT_INTERVAL=60          # Seconds between heartbeat writes

# State Management
STATE_DB_PATH=state.db                 # SQLite database path

# Gmail Configuration
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle
GMAIL_CHECK_INTERVAL=60                # Seconds between checks

# Filesystem Configuration
FILESYSTEM_POLLING_INTERVAL=5          # Seconds between checks
FILE_EXTENSIONS=*                      # Comma-separated or * for all

# LinkedIn Configuration
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password
LINKEDIN_CHECK_INTERVAL=300            # Seconds between checks (5 minutes)
```

### Watcher Options

**Gmail Watcher**:
- Monitors Gmail inbox for new emails
- Creates EMAIL_* tasks in Needs_Action
- Checks every 60 seconds (configurable)
- Requires Gmail API credentials

**Filesystem Watcher**:
- Monitors directory for new files
- Creates FILE_DROP_* tasks in Needs_Action
- Checks every 5 seconds (configurable)
- Supports file extension filtering

**LinkedIn Watcher**:
- Monitors LinkedIn messages
- Creates LINKEDIN_MSG_* tasks in Needs_Action
- Checks every 5 minutes (configurable)
- Requires LinkedIn credentials
- Rate limited to 100 requests/hour

---

## Tips & Best Practices

### Performance Optimization

1. **Adjust Check Intervals**: Increase intervals if you don't need real-time monitoring
   ```bash
   GMAIL_CHECK_INTERVAL=300  # Check every 5 minutes instead of 1
   ```

2. **Filter File Types**: Only monitor specific file types
   ```bash
   FILE_EXTENSIONS=pdf,docx,xlsx  # Only process these types
   ```

3. **Disable Unused Watchers**: Only run watchers you need
   ```bash
   ORCHESTRATOR_WATCHERS=filesystem  # Only filesystem watcher
   ```

### Security Best Practices

1. **Protect Credentials**: Never commit .env to version control
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use OAuth2**: Prefer OAuth2 over password authentication
   - Gmail: Use OAuth2 credentials
   - LinkedIn: Consider API tokens when available

3. **Review Approval Thresholds**: Regularly review and update thresholds
   ```bash
   nano AI_Employee_Vault/Company_Handbook.md
   ```

### Reliability Best Practices

1. **Monitor Logs**: Regularly check logs for errors
   ```bash
   tail -f AI_Employee_Vault/Logs/orchestrator.log
   ```

2. **Backup State Database**: Regular backups prevent data loss
   ```bash
   cp state.db state.db.backup.$(date +%Y%m%d)
   ```

3. **Test Restart Recovery**: Verify no duplicates after restart
   ```bash
   # Stop orchestrator
   # Restart orchestrator
   # Verify no duplicate tasks created
   ```

---

## Getting Help

### Documentation
- **Setup Guide**: docs/setup_guide.md
- **Troubleshooting**: docs/troubleshooting.md
- **MCP Server**: docs/mcp_server_setup.md
- **LinkedIn API**: docs/linkedin_api_setup.md
- **Scheduling**: docs/scheduling_setup.md

### Validation
- **Validation Guide**: VALIDATION_GUIDE.md
- **Implementation Summary**: SILVER_TIER_IMPLEMENTATION_SUMMARY.md
- **Validation Helper**: scripts/validate.sh

### Common Issues
See docs/troubleshooting.md for solutions to:
- Orchestrator won't start
- Watchers crash immediately
- No tasks created
- Duplicate tasks
- Performance issues

---

## Next Steps

1. **Complete Validation**: Follow VALIDATION_GUIDE.md
2. **Customize Configuration**: Adjust settings for your needs
3. **Set Up Scheduled Tasks**: Configure recurring tasks
4. **Integrate with Claude**: Use Claude Code to process tasks
5. **Monitor Performance**: Track metrics and optimize

---

*Quick Start Guide - Version 0.2.0*
*Last Updated: 2026-03-10*
