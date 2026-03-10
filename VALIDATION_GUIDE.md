# Silver Tier Validation Guide

This guide walks through the 3 remaining manual validation tasks (T091-T093) to complete Silver tier implementation.

## Prerequisites

1. **Environment Setup**
   ```bash
   # Copy and configure environment variables
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   uv pip install -e .

   # Node.js dependencies (for email MCP server)
   cd mcp_servers/email_sender
   npm install
   cd ../..
   ```

3. **Create Vault Structure**
   ```bash
   python -m vault_setup.setup
   ```

---

## T091: Quickstart Validation

**Objective**: Verify all 9 quickstart steps work correctly

### Step 1: Install Dependencies ✓
Already completed in prerequisites above.

### Step 2: Configure Environment Variables

Edit `.env` with your credentials:
```bash
# Required
VAULT_PATH=AI_Employee_Vault
WATCH_DIRECTORY=Watch

# Gmail (for email watcher and MCP server)
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle

# LinkedIn (optional)
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password

# State Database
STATE_DB_PATH=state.db

# Orchestrator
ORCHESTRATOR_WATCHERS=gmail,filesystem
ORCHESTRATOR_HEALTH_CHECK_INTERVAL=60
```

**Validation**: Run `cat .env` and verify all required variables are set.

### Step 3: Start Orchestrator

```bash
# Terminal 1: Start orchestrator
python -m watchers.orchestrator
```

**Expected Output**:
```
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Orchestrator initialized with 2 watchers
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Starting orchestrator...
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Starting watcher: gmail
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Watcher gmail started with PID XXXXX
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Starting watcher: filesystem
[2026-03-10 XX:XX:XX] [Orchestrator] [INFO] Watcher filesystem started with PID XXXXX
```

**Validation Checklist**:
- [ ] Orchestrator starts without errors
- [ ] Both watchers start successfully
- [ ] Heartbeat files created in `AI_Employee_Vault/Logs/`
- [ ] No error messages in logs

### Step 4: Test Gmail Watcher

**Action**: Send yourself a test email

**Expected Behavior**:
1. Within 2 minutes, a task file appears in `AI_Employee_Vault/Needs_Action/`
2. Filename format: `EMAIL_YYYYMMDDTHHMMSSZ_subject-slug.md`
3. File contains email metadata (sender, subject, body)

**Validation Checklist**:
- [ ] Task file created within 2 minutes
- [ ] File has correct YAML frontmatter
- [ ] Email content is readable
- [ ] No duplicate tasks after restart

**Test Duplicate Prevention**:
```bash
# Stop orchestrator (Ctrl+C)
# Restart orchestrator
python -m watchers.orchestrator
# Wait 2 minutes - no duplicate task should be created
```

### Step 5: Test Filesystem Watcher

**Action**: Drop a file into the watch directory

```bash
# Create test file
echo "Test content" > Watch/test_document.txt
```

**Expected Behavior**:
1. Within 5 seconds, a task file appears in `AI_Employee_Vault/Needs_Action/`
2. Filename format: `FILE_DROP_YYYYMMDDTHHMMSSZ_filename-slug.md`
3. File contains file metadata (path, size, type)

**Validation Checklist**:
- [ ] Task file created within 5 seconds
- [ ] File has correct YAML frontmatter
- [ ] File metadata is accurate
- [ ] No duplicate tasks after restart

### Step 6: Test LinkedIn Watcher (Optional)

**Prerequisites**: LinkedIn credentials configured in `.env`

**Action**: Send yourself a LinkedIn message

**Expected Behavior**:
1. Within 10 minutes, a task file appears in `AI_Employee_Vault/Needs_Action/`
2. Filename format: `LINKEDIN_MSG_YYYYMMDDTHHMMSSZ_sender-name.md`
3. File contains message metadata

**Validation Checklist**:
- [ ] Task file created within 10 minutes
- [ ] File has correct YAML frontmatter
- [ ] Message content is readable
- [ ] Rate limiting works (no API errors)

### Step 7: Test Email Sending (MCP Server)

**Prerequisites**:
- Gmail API credentials configured
- MCP server built: `cd mcp_servers/email_sender && npm run build`

**Action**: Test email sending via MCP server

```bash
# Terminal 2: Test MCP server
cd mcp_servers/email_sender
node dist/index.js
# Send test JSON input (see mcp_server_setup.md for examples)
```

**Validation Checklist**:
- [ ] MCP server starts without errors
- [ ] send_email tool is registered
- [ ] Test email sends successfully
- [ ] Email appears in sent folder
- [ ] Retry logic works on failure

### Step 8: Test Approval Workflow

**Action**: Create a task requiring approval

```bash
# Create high-value payment task
cat > AI_Employee_Vault/Needs_Action/PAYMENT_test.md << 'EOF'
---
type: payment
amount: 750
status: pending
---

# Payment: Test Invoice

Process payment of $750 for test invoice.
EOF
```

**Expected Behavior**:
1. Approval workflow skill evaluates threshold
2. Task moves to `AI_Employee_Vault/Pending_Approval/`
3. Approval metadata added to file

**Validation Checklist**:
- [ ] Task moves to /Pending_Approval
- [ ] Approval metadata is correct
- [ ] Approval commands work
- [ ] Approved tasks move to /Approved
- [ ] Rejected tasks move to /Rejected

### Step 9: Test Scheduled Tasks

**Action**: Configure and test a scheduled task

```bash
# Edit scheduled_tasks.yaml
# Add a test task with 1-minute interval
# Run task executor manually
python -m scheduler.task_executor --task morning_briefing --vault AI_Employee_Vault
```

**Validation Checklist**:
- [ ] Task executes successfully
- [ ] Output file created in vault
- [ ] Execution logged to /Logs/scheduled_tasks.log
- [ ] Lock file prevents overlapping execution

---

## T092: 24-Hour Continuous Operation Test

**Objective**: Verify system stability over 24 hours

### Setup

1. **Start Orchestrator**
   ```bash
   # Use nohup to run in background
   nohup python -m watchers.orchestrator > orchestrator.out 2>&1 &
   echo $! > orchestrator.pid
   ```

2. **Monitor Script**
   ```bash
   # Create monitoring script
   cat > monitor.sh << 'EOF'
   #!/bin/bash
   while true; do
       echo "=== $(date) ==="
       echo "Orchestrator PID: $(cat orchestrator.pid)"
       ps -p $(cat orchestrator.pid) > /dev/null && echo "Status: Running" || echo "Status: STOPPED"
       echo "Watchers:"
       pgrep -f "gmail_watcher" && echo "  Gmail: Running" || echo "  Gmail: STOPPED"
       pgrep -f "filesystem_watcher" && echo "  Filesystem: Running" || echo "  Filesystem: STOPPED"
       echo "Tasks created: $(ls AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)"
       echo "State DB size: $(du -h state.db 2>/dev/null | cut -f1)"
       echo "Memory usage:"
       ps aux | grep -E "(orchestrator|watcher)" | grep -v grep
       echo ""
       sleep 300  # Check every 5 minutes
   done
   EOF
   chmod +x monitor.sh
   ```

3. **Start Monitoring**
   ```bash
   ./monitor.sh > monitor.log 2>&1 &
   echo $! > monitor.pid
   ```

### Metrics to Track

Create a spreadsheet or log file to track:

| Time | Uptime | Crashes | Tasks Created | Duplicates | Memory (MB) | CPU (%) |
|------|--------|---------|---------------|------------|-------------|---------|
| 0h   |        |         |               |            |             |         |
| 1h   |        |         |               |            |             |         |
| 6h   |        |         |               |            |             |         |
| 12h  |        |         |               |            |             |         |
| 18h  |        |         |               |            |             |         |
| 24h  |        |         |               |            |             |         |

### Validation Checklist

After 24 hours:
- [ ] Orchestrator still running (uptime >99%)
- [ ] All watchers still running
- [ ] Zero unrecovered crashes
- [ ] Zero duplicate tasks created
- [ ] Memory usage stable (no leaks)
- [ ] CPU usage reasonable (<10% average)
- [ ] All heartbeat files updated recently
- [ ] State database not corrupted

### Cleanup

```bash
# Stop monitoring
kill $(cat monitor.pid)

# Stop orchestrator
kill $(cat orchestrator.pid)

# Review logs
tail -100 orchestrator.out
tail -100 monitor.log
```

---

## T093: Performance Benchmarks Validation

**Objective**: Measure and validate performance metrics

### Benchmark 1: Email Detection Latency

**Target**: <2 minutes from receipt to task creation

**Test Procedure**:
1. Note current time: `date +%s`
2. Send yourself an email
3. Watch for task file creation: `watch -n 1 'ls -lt AI_Employee_Vault/Needs_Action/ | head -5'`
4. Note task creation time from filename
5. Calculate latency: creation_time - send_time

**Validation**:
- [ ] Latency < 2 minutes (average of 5 tests)

### Benchmark 2: LinkedIn Polling Interval

**Target**: 5-minute intervals maintained

**Test Procedure**:
1. Check LinkedIn watcher log: `tail -f AI_Employee_Vault/Logs/linkedin_watcher.log`
2. Note timestamps of check operations
3. Calculate intervals between checks

**Validation**:
- [ ] Average interval = 5 minutes ± 10 seconds
- [ ] No missed checks over 1-hour period

### Benchmark 3: Email Sending Latency

**Target**: <5 seconds from approval to delivery

**Test Procedure**:
1. Create email task requiring approval
2. Approve task: `claude "approve task TASK_ID"`
3. Note approval time
4. Check sent email timestamp
5. Calculate latency

**Validation**:
- [ ] Latency < 5 seconds (average of 5 tests)
- [ ] 99% delivery success rate

### Benchmark 4: File Detection Latency

**Target**: <5 seconds from drop to task creation

**Test Procedure**:
```bash
# Automated test script
for i in {1..10}; do
    start=$(date +%s%N)
    echo "Test $i" > Watch/test_$i.txt
    while [ ! -f AI_Employee_Vault/Needs_Action/FILE_DROP_*test_$i*.md ]; do
        sleep 0.1
    done
    end=$(date +%s%N)
    latency=$(( (end - start) / 1000000 ))
    echo "Test $i: ${latency}ms"
done
```

**Validation**:
- [ ] Average latency < 5 seconds
- [ ] 100% detection rate

### Benchmark 5: State Persistence

**Target**: Zero duplicates after restart

**Test Procedure**:
1. Process 10 items (emails, files, LinkedIn messages)
2. Note task IDs created
3. Restart orchestrator
4. Wait 10 minutes
5. Check for duplicate tasks

**Validation**:
- [ ] Zero duplicate tasks created
- [ ] All original tasks still in vault
- [ ] State database intact

---

## Validation Summary

After completing all tests, fill out this summary:

### T091: Quickstart Validation
- [ ] All 9 steps completed successfully
- [ ] No blocking issues found
- Issues found (if any): _______________

### T092: 24-Hour Test
- [ ] System ran for 24 hours
- [ ] Uptime: ____%
- [ ] Crashes: ____
- [ ] Duplicates: ____
- Issues found (if any): _______________

### T093: Performance Benchmarks
- [ ] Email detection: ____ seconds (target: <120s)
- [ ] LinkedIn polling: ____ seconds (target: 300s ± 10s)
- [ ] Email sending: ____ seconds (target: <5s)
- [ ] File detection: ____ seconds (target: <5s)
- [ ] State persistence: ____ duplicates (target: 0)
- Issues found (if any): _______________

### Overall Assessment
- [ ] All validation tasks passed
- [ ] System is production-ready
- [ ] Ready to deploy

---

## Troubleshooting

### Common Issues

**Issue**: Orchestrator won't start
- Check: Python version (3.13+)
- Check: Dependencies installed (`uv pip list`)
- Check: Environment variables set
- Check: Vault directory exists

**Issue**: Watchers crash immediately
- Check: Watcher logs in `AI_Employee_Vault/Logs/`
- Check: Credentials configured correctly
- Check: State database not locked

**Issue**: No tasks created
- Check: Watchers are running (`ps aux | grep watcher`)
- Check: Heartbeat files updated recently
- Check: Source has new items (email inbox, watch directory)

**Issue**: Duplicate tasks created
- Check: State database exists and is not corrupted
- Check: StateManager initialized correctly
- Run: `python -c "from watchers.state_manager import StateManager; sm = StateManager(); print(sm.health_check())"`

**Issue**: Performance below target
- Check: System resources (CPU, memory, disk)
- Check: Network latency (for Gmail/LinkedIn APIs)
- Check: Database size (vacuum if needed)

For more troubleshooting, see `docs/troubleshooting.md`.

---

## Next Steps After Validation

Once all validation tasks pass:

1. **Update tasks.md**
   - Mark T091, T092, T093 as complete [X]

2. **Create Release**
   - Tag version 0.2.0
   - Create release notes
   - Document known issues

3. **Deploy to Production**
   - Set up production environment
   - Configure monitoring
   - Enable scheduled tasks

4. **Begin Gold Tier Planning**
   - Ralph Loop implementation
   - Advanced reasoning capabilities
   - Multi-step task orchestration
