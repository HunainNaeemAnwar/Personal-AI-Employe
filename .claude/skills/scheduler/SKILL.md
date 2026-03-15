---
name: scheduler
description: Manage scheduled tasks via cron (Linux/Mac) or Task Scheduler (Windows) - setup, execute, and monitor recurring automated tasks
version: 1.0.0
---

# SKILL: Scheduler

## 🎯 PRIMARY MISSION

> "Configure and execute scheduled tasks using cron (Linux/Mac) or Task Scheduler (Windows) for automated recurring operations like morning briefings, weekly LinkedIn posts, and database backups."

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `scheduler` skill when:**
- User says: "setup scheduled tasks"
- User says: "configure cron jobs"
- User says: "setup Task Scheduler"
- Need to execute recurring tasks (daily briefing, weekly posts)
- Need to check scheduled task execution logs
- Need to troubleshoot failed scheduled tasks

**DO NOT use:**
- `inbox-processor` (that's for one-off tasks in `/Needs_Action/`)
- `task-planner` (that's for planning individual tasks, not scheduling)
- `social-poster` (that's for creating posts - scheduler TRIGGERS it)

---

## 📋 SCHEDULED TASKS CONFIGURATION

### scheduled_tasks.yaml

```yaml
# Scheduled Tasks Configuration
# Located in project root: /home/hunain/personal-ai-employee/scheduled_tasks.yaml

scheduled_tasks:
  # Daily morning briefing - Generate summary of overnight activity
  - id: "morning_briefing"
    description: "Generate daily morning briefing with overnight activity summary"
    schedule: "0 8 * * *"  # Every day at 8:00 AM
    command: "cd /home/hunain/personal-ai-employee && claude 'Generate morning briefing'"
    enabled: true
    retry_on_failure: true
    max_retries: 3

  # Weekly LinkedIn post - Share business update or insight
  - id: "weekly_linkedin_post"
    description: "Post weekly business update to LinkedIn"
    schedule: "0 9 * * 1"  # Every Monday at 9:00 AM
    command: "cd /home/hunain/personal-ai-employee && claude 'Create weekly business update LinkedIn post'"
    enabled: true
    retry_on_failure: true
    max_retries: 3

  # Database backup - Backup state database
  - id: "database_backup"
    description: "Backup state database to prevent data loss"
    schedule: "0 2 * * *"  # Every day at 2:00 AM
    command: "cd /home/hunain/personal-ai-employee && python -m scheduler.task_executor --task database_backup"
    enabled: true
    retry_on_failure: true
    max_retries: 3

  # System health check - Verify all systems are operational
  - id: "system_health_check"
    description: "Check health of watchers, database, and MCP servers"
    schedule: "0 */6 * * *"  # Every 6 hours
    command: "cd /home/hunain/personal-ai-employee && python -m scheduler.task_executor --task system_health_check"
    enabled: true
    retry_on_failure: false
    max_retries: 1

execution_settings:
  prevent_overlap: true
  lock_dir: "/tmp/ai_employee_locks"
  max_execution_time: 3600  # 1 hour
  log_dir: "AI_Employee_Vault/Logs"
  retry_delay: 300  # 5 minutes
  verbose_logging: true
```

---

## 🔄 SCHEDULER WORKFLOW

### Step 1: Setup Cron Jobs (Linux/Mac)

```python
# scheduler/cron_setup.py
import croniter
from pathlib import Path

def setup_cron_jobs():
    """Install cron jobs from scheduled_tasks.yaml"""
    
    # Read configuration
    config = yaml.safe_load(Path("scheduled_tasks.yaml").read_text())
    
    # Build crontab entries
    crontab_entries = []
    for task in config['scheduled_tasks']:
        if task.get('enabled', True):
            # Format: minute hour day month weekday command
            cron_line = f"{task['schedule']} {task['command']} >> {config['execution_settings']['log_dir']}/cron_{task['id']}.log 2>&1"
            crontab_entries.append(cron_line)
    
    # Install crontab
    crontab_content = "\n".join(crontab_entries)
    
    # Use crontab command to install
    import subprocess
    process = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(crontab_content.encode())
    
    if process.returncode == 0:
        print(f"✓ Installed {len(crontab_entries)} cron jobs")
        log_cron_installation(crontab_entries)
    else:
        print(f"✗ Failed to install cron jobs: {stderr.decode()}")
```

### Step 2: Setup Task Scheduler (Windows)

```powershell
# scheduler/task_scheduler_setup.py
import subprocess

def setup_task_scheduler():
    """Install scheduled tasks using Windows Task Scheduler"""
    
    config = yaml.safe_load(Path("scheduled_tasks.yaml").read_text())
    
    for task in config['scheduled_tasks']:
        if task.get('enabled', True):
            # Convert cron expression to Task Scheduler trigger
            trigger = convert_cron_to_task_scheduler_trigger(task['schedule'])
            
            # Create scheduled task
            command = f"""
            schtasks /Create /TN "AI_Employee_{task['id']}" /TR "{task['command']}" /SC {trigger['frequency']} /ST {trigger['time']} /RU SYSTEM /F
            """
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Created task: AI_Employee_{task['id']}")
            else:
                print(f"✗ Failed to create task: {result.stderr}")
```

### Step 3: Execute Scheduled Task

```python
# scheduler/task_executor.py
import fcntl
from pathlib import Path
from datetime import datetime, timezone

def execute_task(task_id: str) -> bool:
    """Execute a scheduled task with overlap prevention"""
    
    config = yaml.safe_load(Path("scheduled_tasks.yaml").read_text())
    task = next((t for t in config['scheduled_tasks'] if t['id'] == task_id), None)
    
    if not task:
        print(f"Task not found: {task_id}")
        return False
    
    # Check overlap prevention (lock file)
    lock_dir = Path(config['execution_settings']['lock_dir'])
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_file = lock_dir / f"{task_id}.lock"
    
    try:
        # Try to acquire lock
        fd = open(lock_file, 'w')
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Lock acquired - execute task
        print(f"Executing task: {task['description']}")
        
        # Run command
        import subprocess
        result = subprocess.run(
            task['command'],
            shell=True,
            capture_output=True,
            text=True,
            timeout=config['execution_settings']['max_execution_time']
        )
        
        # Log result
        log_execution(task_id, result.returncode == 0, result.stdout, result.stderr)
        
        # Release lock
        fcntl.flock(fd, fcntl.LOCK_UN)
        fd.close()
        
        return result.returncode == 0
        
    except BlockingIOError:
        print(f"Task {task_id} already running (lock file exists)")
        return False
    except subprocess.TimeoutExpired:
        print(f"Task {task_id} timed out after {config['execution_settings']['max_execution_time']}s")
        log_execution(task_id, False, error="Timeout expired")
        return False
    except Exception as e:
        print(f"Task {task_id} failed: {e}")
        log_execution(task_id, False, error=str(e))
        
        # Retry logic
        if task.get('retry_on_failure', False):
            return retry_task(task, config)
        
        return False
```

---

## 📝 PRE-CONFIGURED SCHEDULED TASKS

### 1. Morning Briefing (Daily at 8:00 AM)

**Purpose:** Generate summary of overnight activity

**Command:**
```bash
cd /home/hunain/personal-ai-employee && claude 'Generate morning briefing'
```

**Output:**
- Emails received overnight
- Tasks completed
- Pending items requiring attention
- System health status

**Cron Expression:** `0 8 * * *`

---

### 2. Weekly LinkedIn Post (Mondays at 9:00 AM)

**Purpose:** Create and publish business update post

**Command:**
```bash
cd /home/hunain/personal-ai-employee && claude 'Create weekly business update LinkedIn post'
```

**Output:**
- LinkedIn post draft in `/Needs_Action/`
- Moved to `/Pending_Approval/` for review
- After approval: published to LinkedIn

**Cron Expression:** `0 9 * * 1`

---

### 3. Database Backup (Daily at 2:00 AM)

**Purpose:** Backup SQLite state database

**Command:**
```bash
cd /home/hunain/personal-ai-employee && python -m scheduler.task_executor --task database_backup
```

**Output:**
- Backup file: `state_backup_YYYYMMDD_HHMMSS.db`
- Log entry in `/Logs/database_backup.log`

**Cron Expression:** `0 2 * * *`

---

### 4. System Health Check (Every 6 Hours)

**Purpose:** Verify watchers, database, and MCP servers are operational

**Command:**
```bash
cd /home/hunain/personal-ai-employee && python -m scheduler.task_executor --task system_health_check
```

**Output:**
- Watcher heartbeat status
- Database health check result
- MCP server connection status
- Log entry in `/Logs/health_check.log`

**Cron Expression:** `0 */6 * * *`

---

## 🔧 CRON EXPRESSION REFERENCE

| Expression | Meaning | Example Use |
|------------|---------|-------------|
| `0 8 * * *` | Daily at 8:00 AM | Morning briefing |
| `0 9 * * 1` | Every Monday at 9:00 AM | Weekly LinkedIn post |
| `0 2 * * *` | Daily at 2:00 AM | Database backup |
| `0 */6 * * *` | Every 6 hours | Health check |
| `0 0 1 * *` | First day of month at midnight | Monthly report |
| `*/15 * * * *` | Every 15 minutes | Frequent polling |

**Cron Format:**
```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-7, 0 and 7 are Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

---

## 📊 EXECUTION LOGGING

### Log File: /Logs/scheduled_tasks.log

```json
{
  "timestamp": "2026-03-15T08:00:00Z",
  "task_id": "morning_briefing",
  "status": "completed",
  "execution_time_ms": 45230,
  "output": "Morning briefing generated successfully",
  "error": null,
  "retry_count": 0
}
```

### Lock File: /tmp/ai_employee_locks/{task_id}.lock

```
# Created: 2026-03-15T08:00:00Z
# PID: 12345
# Task: morning_briefing
```

---

## 🚨 TROUBLESHOOTING

### Cron Job Not Running

**Check cron daemon:**
```bash
# Check if cron is running
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog
```

**Verify crontab:**
```bash
# List installed cron jobs
crontab -l

# Edit cron jobs
crontab -e
```

### Task Scheduler Not Running (Windows)

**Check Task Scheduler:**
```powershell
# List all AI Employee tasks
schtasks /Query /TN "AI_Employee_*"

# Check task status
schtasks /Query /TN "AI_Employee_morning_briefing" /V /FO LIST
```

### Task Fails Repeatedly

**Check logs:**
```bash
# View task execution log
cat AI_Employee_Vault/Logs/scheduled_tasks.log | grep "task_id": "morning_briefing"

# View cron output log
cat AI_Employee_Vault/Logs/cron_morning_briefing.log
```

**Common issues:**
- Path not absolute (use full paths in commands)
- Python environment not activated (use full path to Python)
- Lock file stuck (delete stale lock files)
- Timeout too short (increase `max_execution_time`)

---

## 📋 QUALITY CHECKLIST

Before considering scheduler setup complete:

- [ ] `scheduled_tasks.yaml` configured with all desired tasks
- [ ] Cron jobs installed (Linux/Mac) OR Task Scheduler tasks created (Windows)
- [ ] Overlap prevention working (lock files created)
- [ ] Execution logging to `/Logs/scheduled_tasks.log`
- [ ] Retry logic working for failed tasks
- [ ] Database backup running successfully
- [ ] Health check executing every 6 hours
- [ ] Morning briefing generating at 8:00 AM
- [ ] Weekly LinkedIn post task created for Mondays

---

## 📈 PERFORMANCE METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Execution reliability | 99% | Successful executions / total scheduled |
| Morning briefing latency | <2 minutes | Scheduled time to completion |
| Overlap prevention | 100% | No concurrent executions of same task |
| Retry success rate | >80% | Failed tasks recovered on retry |

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Processes tasks that may be created by scheduled tasks
- `task-planner` - Creates plans for complex scheduled operations
- `vault-manager` - File operations for logs and task files
- `social-poster` - Triggered by weekly LinkedIn post scheduled task
- `approval-workflow` - Scheduled posts require approval before publishing

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Scheduled Task Execution via Cron/Task Scheduler*
