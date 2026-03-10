# Scheduling Setup Guide

This guide explains how to configure automated scheduled task execution for the AI Employee using cron (Linux/Mac) or Windows Task Scheduler.

## Overview

The AI Employee supports automated execution of recurring tasks at configured intervals. Tasks are defined in `scheduled_tasks.yaml` and executed by the scheduler module.

**Supported Platforms:**
- Linux: Uses cron
- macOS: Uses cron
- Windows: Uses Task Scheduler

## Prerequisites

- AI Employee installed and configured
- Python 3.13+ with all dependencies
- Vault path configured in `.env`
- Appropriate permissions to create scheduled tasks

## Configuration

### 1. Review Scheduled Tasks

Edit `scheduled_tasks.yaml` to configure your scheduled tasks:

```yaml
scheduled_tasks:
  - id: "morning_briefing"
    description: "Generate daily morning briefing"
    schedule: "0 8 * * *"  # Every day at 8:00 AM
    command: "python -m scheduler.task_executor --task morning_briefing"
    enabled: true
    retry_on_failure: true
    max_retries: 3
```

**Schedule Format (Cron Expression):**
- Minute (0-59)
- Hour (0-23)
- Day of month (1-31)
- Month (1-12)
- Day of week (0-7, where 0 and 7 are Sunday)

**Examples:**
- `"0 8 * * *"` - Every day at 8:00 AM
- `"0 */2 * * *"` - Every 2 hours
- `"0 9 * * 1"` - Every Monday at 9:00 AM
- `"0 0 1 * *"` - First day of every month at midnight
- `"*/15 * * * *"` - Every 15 minutes

### 2. Configure Execution Settings

Adjust execution settings in `scheduled_tasks.yaml`:

```yaml
execution_settings:
  prevent_overlap: true  # Prevent concurrent execution of same task
  lock_dir: "/tmp/ai_employee_locks"  # Lock file directory
  max_execution_time: 3600  # Maximum execution time (seconds)
  log_dir: "AI_Employee_Vault/Logs"  # Log directory
  retry_delay: 300  # Delay between retries (seconds)
  verbose_logging: true  # Enable detailed logging
```

## Setup Instructions

### Linux/Mac (Cron)

#### 1. Install Scheduled Tasks

Run the cron setup script to install all scheduled tasks:

```bash
python -m scheduler.cron_setup setup
```

This will:
- Read `scheduled_tasks.yaml`
- Validate cron expressions
- Add cron jobs to your crontab
- Preserve existing cron jobs

#### 2. Verify Installation

List current crontab to verify tasks were added:

```bash
crontab -l
```

You should see entries like:

```
# AI Employee Task: morning_briefing - Generate daily morning briefing
0 8 * * * python -m scheduler.task_executor --task morning_briefing
```

#### 3. Test Execution

Manually execute a task to verify it works:

```bash
python -m scheduler.task_executor --task morning_briefing
```

Check logs for execution results:

```bash
tail -f AI_Employee_Vault/Logs/scheduled_tasks.log
```

#### 4. Remove Scheduled Tasks (Optional)

To remove all AI Employee scheduled tasks:

```bash
python -m scheduler.cron_setup remove
```

### Windows (Task Scheduler)

#### 1. Install Scheduled Tasks

Run the Task Scheduler setup script (requires Administrator privileges):

```powershell
python -m scheduler.task_scheduler_setup setup
```

This will:
- Read `scheduled_tasks.yaml`
- Convert cron expressions to Task Scheduler triggers
- Create scheduled tasks with prefix `AIEmployee_`
- Configure tasks to run with your user account

#### 2. Verify Installation

List AI Employee scheduled tasks:

```powershell
python -m scheduler.task_scheduler_setup list
```

Or use Task Scheduler GUI:
1. Open Task Scheduler (taskschd.msc)
2. Navigate to Task Scheduler Library
3. Look for tasks starting with `AIEmployee_`

#### 3. Test Execution

Manually execute a task to verify it works:

```powershell
python -m scheduler.task_executor --task morning_briefing
```

Check logs for execution results:

```powershell
Get-Content AI_Employee_Vault\Logs\scheduled_tasks.log -Tail 20
```

#### 4. Remove Scheduled Tasks (Optional)

To remove all AI Employee scheduled tasks:

```powershell
python -m scheduler.task_scheduler_setup remove
```

## Available Scheduled Tasks

### Daily Tasks

**Morning Briefing** (`morning_briefing`)
- **Schedule**: Every day at 8:00 AM
- **Purpose**: Generate summary of overnight activity
- **Output**: `AI_Employee_Vault/Briefings/briefing_YYYYMMDD.md`

**Email Summary** (`daily_email_summary`)
- **Schedule**: Every day at 6:00 PM
- **Purpose**: Summarize important emails from the day
- **Output**: `AI_Employee_Vault/Summaries/email_summary_YYYYMMDD.md`

**Database Backup** (`database_backup`)
- **Schedule**: Every day at 2:00 AM
- **Purpose**: Backup state database to prevent data loss
- **Output**: `state_backup_YYYYMMDD_HHMMSS.db`

### Weekly Tasks

**LinkedIn Post** (`weekly_linkedin_post`)
- **Schedule**: Every Monday at 9:00 AM
- **Purpose**: Post weekly business update to LinkedIn
- **Output**: Task file in `AI_Employee_Vault/Needs_Action/`

**Task Review** (`weekly_task_review`)
- **Schedule**: Every Friday at 5:00 PM
- **Purpose**: Generate weekly task completion report
- **Output**: `AI_Employee_Vault/Reviews/task_review_YYYYMMDD.md`

### Periodic Tasks

**System Health Check** (`system_health_check`)
- **Schedule**: Every 6 hours
- **Purpose**: Check health of watchers, database, and MCP servers
- **Output**: `AI_Employee_Vault/Logs/health_check_YYYYMMDDTHHMMSSZ.md`

### Monthly Tasks

**Monthly Report** (`monthly_report`)
- **Schedule**: First day of every month at 9:00 AM
- **Purpose**: Generate comprehensive monthly activity report
- **Output**: `AI_Employee_Vault/Reports/monthly_report_YYYYMM.md`

## Task Execution Features

### Overlap Prevention

The scheduler prevents concurrent execution of the same task using lock files:

- Lock files are created in `/tmp/ai_employee_locks/` (Linux/Mac) or configured `lock_dir`
- If a task is already running, subsequent executions are skipped
- Lock is automatically released when task completes

### Retry Logic

Failed tasks can be automatically retried:

- Configure `retry_on_failure: true` in task definition
- Set `max_retries` to control number of retry attempts
- Retry delay is configurable in `execution_settings.retry_delay`
- Each retry is logged with retry count

### Execution Logging

All task executions are logged to `AI_Employee_Vault/Logs/scheduled_tasks.log`:

```json
{
  "timestamp": "2026-03-09T14:30:00Z",
  "task_id": "morning_briefing",
  "status": "success",
  "start_time": "2026-03-09T14:30:00Z",
  "end_time": "2026-03-09T14:30:15Z",
  "duration_seconds": 15.2,
  "retry_count": 0,
  "error": null
}
```

## Adding Custom Scheduled Tasks

### 1. Define Task in Configuration

Add task definition to `scheduled_tasks.yaml`:

```yaml
scheduled_tasks:
  - id: "custom_task"
    description: "My custom scheduled task"
    schedule: "0 12 * * *"  # Every day at noon
    command: "python -m scheduler.task_executor --task custom_task"
    enabled: true
    retry_on_failure: true
    max_retries: 2
```

### 2. Implement Task Logic

Add task execution logic to `scheduler/task_executor.py`:

```python
def _execute_task_logic(self, task_id: str) -> bool:
    # ... existing tasks ...
    elif task_id == "custom_task":
        return self._execute_custom_task()
    # ...

def _execute_custom_task(self) -> bool:
    """Execute custom task logic."""
    try:
        # Your task implementation here
        self.logger.info("Executing custom task")

        # Example: Create a file in vault
        output_file = self.vault_path / "Custom" / f"output_{datetime.utcnow().strftime('%Y%m%d')}.md"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("Custom task output")

        return True
    except Exception as e:
        self.logger.error(f"Failed to execute custom task: {e}")
        return False
```

### 3. Install Updated Schedule

Reinstall scheduled tasks to include the new task:

**Linux/Mac:**
```bash
python -m scheduler.cron_setup setup
```

**Windows:**
```powershell
python -m scheduler.task_scheduler_setup setup
```

## Troubleshooting

### Task Not Executing

**Check if task is enabled:**
```yaml
enabled: true  # Must be true
```

**Verify cron expression:**
```bash
# Test cron expression at https://crontab.guru/
```

**Check logs:**
```bash
tail -f AI_Employee_Vault/Logs/scheduled_tasks.log
```

**Verify task is installed:**

Linux/Mac:
```bash
crontab -l | grep "morning_briefing"
```

Windows:
```powershell
Get-ScheduledTask -TaskName "AIEmployee_morning_briefing"
```

### Task Failing

**Check error logs:**
```bash
cat AI_Employee_Vault/Logs/scheduled_tasks.log | grep "failed"
```

**Run task manually:**
```bash
python -m scheduler.task_executor --task morning_briefing
```

**Check Python environment:**
```bash
which python  # Verify correct Python version
python --version  # Should be 3.13+
```

**Verify dependencies:**
```bash
pip list | grep -E "pyyaml|python-dotenv"
```

### Task Skipped (Overlap)

If you see "Task already running, skipping execution":

1. Check if previous execution is still running:
   ```bash
   ps aux | grep task_executor
   ```

2. Check lock file:
   ```bash
   ls -la /tmp/ai_employee_locks/
   ```

3. If task is stuck, remove lock file:
   ```bash
   rm /tmp/ai_employee_locks/morning_briefing.lock
   ```

### Permissions Issues (Windows)

If Task Scheduler tasks fail to run:

1. Verify task is configured to run with your user account
2. Check "Run whether user is logged on or not" is NOT selected (unless needed)
3. Ensure Python is in system PATH
4. Run Task Scheduler as Administrator when creating tasks

### Cron Not Working (Linux/Mac)

**Verify cron service is running:**
```bash
# Linux
sudo systemctl status cron

# macOS
sudo launchctl list | grep cron
```

**Check cron logs:**
```bash
# Linux
sudo tail -f /var/log/syslog | grep CRON

# macOS
tail -f /var/log/system.log | grep cron
```

**Test cron with simple command:**
```bash
# Add test cron job
echo "* * * * * echo 'Cron works' >> /tmp/cron_test.log" | crontab -

# Wait 1 minute, then check
cat /tmp/cron_test.log
```

## Best Practices

1. **Test tasks manually** before scheduling them
2. **Monitor logs** regularly for failures
3. **Set appropriate retry limits** to avoid infinite loops
4. **Use overlap prevention** for long-running tasks
5. **Schedule backups** during low-activity periods (e.g., 2 AM)
6. **Review scheduled tasks** monthly to remove unused tasks
7. **Keep execution times reasonable** (< 1 hour per task)
8. **Log all task outputs** to vault for audit trail

## Performance Considerations

- **Task frequency**: Don't schedule tasks too frequently (minimum 5 minutes apart)
- **Concurrent tasks**: Limit number of tasks running simultaneously
- **Resource usage**: Monitor CPU and memory during task execution
- **Database locks**: Avoid multiple tasks accessing database simultaneously
- **API rate limits**: Respect LinkedIn and Gmail API rate limits

## Security Considerations

- **Credentials**: Store API credentials in `.env`, never in `scheduled_tasks.yaml`
- **Permissions**: Run tasks with minimum required permissions
- **Lock files**: Ensure lock directory has appropriate permissions
- **Logs**: Protect log files from unauthorized access
- **Task commands**: Validate all commands before adding to schedule

## Next Steps

After setting up scheduled tasks:

1. Monitor first few executions to verify they work correctly
2. Review logs daily for the first week
3. Adjust schedules based on your workflow
4. Add custom tasks as needed
5. Set up alerts for task failures (optional)

For more information, see:
- [Troubleshooting Guide](troubleshooting.md)
- [Configuration Reference](.env.example)
- [Task Executor Source](../scheduler/task_executor.py)
