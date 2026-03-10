"""
Task Executor for Scheduled Tasks - Handles execution, logging, and error handling.

This module provides the execution wrapper for scheduled tasks. It handles:
- Task execution with proper error handling
- Overlapping task prevention using lock files
- Retry logic for failed tasks
- Execution logging to vault
"""

import argparse
import logging
import os
import sys
import time
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import fcntl


class TaskExecutor:
    """
    Executes scheduled tasks with overlap prevention and retry logic.

    Responsibilities:
    - Execute scheduled tasks by task ID
    - Prevent overlapping execution using lock files
    - Retry failed tasks with exponential backoff
    - Log execution results to vault
    - Handle task-specific execution logic
    """

    def __init__(
        self,
        config_path: str = "scheduled_tasks.yaml",
        vault_path: str = "AI_Employee_Vault"
    ):
        """
        Initialize TaskExecutor.

        Args:
            config_path: Path to scheduled_tasks.yaml configuration
            vault_path: Path to Obsidian vault
        """
        self.config_path = Path(config_path)
        self.vault_path = Path(vault_path)
        self.logger = self._setup_logging()
        self.config = self._load_config()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for task executor."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "scheduled_tasks.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            self.logger.error(f"Configuration file not found: {self.config_path}")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            return {}

    def _get_lock_file_path(self, task_id: str) -> Path:
        """
        Get lock file path for task.

        Args:
            task_id: Task identifier

        Returns:
            Path to lock file
        """
        lock_dir = Path(self.config.get('execution_settings', {}).get('lock_dir', '/tmp/ai_employee_locks'))
        lock_dir.mkdir(parents=True, exist_ok=True)
        return lock_dir / f"{task_id}.lock"

    def _acquire_lock(self, task_id: str) -> Optional[int]:
        """
        Acquire lock for task to prevent overlapping execution.

        Args:
            task_id: Task identifier

        Returns:
            File descriptor if lock acquired, None if task already running
        """
        lock_file = self._get_lock_file_path(task_id)

        try:
            # Open lock file
            fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR)

            # Try to acquire exclusive lock (non-blocking)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)

            # Write PID to lock file
            os.write(fd, str(os.getpid()).encode())

            self.logger.info(f"Acquired lock for task: {task_id}")
            return fd

        except BlockingIOError:
            # Lock already held by another process
            self.logger.warning(f"Task {task_id} is already running, skipping execution")
            return None
        except Exception as e:
            self.logger.error(f"Failed to acquire lock for {task_id}: {e}")
            return None

    def _release_lock(self, fd: int, task_id: str):
        """
        Release lock for task.

        Args:
            fd: File descriptor of lock file
            task_id: Task identifier
        """
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            self.logger.info(f"Released lock for task: {task_id}")
        except Exception as e:
            self.logger.error(f"Failed to release lock for {task_id}: {e}")

    def _log_execution(
        self,
        task_id: str,
        status: str,
        start_time: datetime,
        end_time: datetime,
        error: Optional[str] = None,
        retry_count: int = 0
    ):
        """
        Log task execution to vault.

        Args:
            task_id: Task identifier
            status: Execution status (success, failed, skipped)
            start_time: Execution start time
            end_time: Execution end time
            error: Error message if failed
            retry_count: Number of retry attempts
        """
        log_file = self.vault_path / "Logs" / "scheduled_tasks.log"

        duration = (end_time - start_time).total_seconds()

        log_entry = {
            'timestamp': end_time.isoformat() + 'Z',
            'task_id': task_id,
            'status': status,
            'start_time': start_time.isoformat() + 'Z',
            'end_time': end_time.isoformat() + 'Z',
            'duration_seconds': duration,
            'retry_count': retry_count,
            'error': error
        }

        try:
            import json
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            self.logger.info(f"Logged execution for task {task_id}: {status}")
        except Exception as e:
            self.logger.error(f"Failed to log execution: {e}")

    def _execute_task_logic(self, task_id: str) -> bool:
        """
        Execute task-specific logic.

        Args:
            task_id: Task identifier

        Returns:
            True on success, False on failure
        """
        self.logger.info(f"Executing task: {task_id}")

        # Task-specific execution logic
        if task_id == "morning_briefing":
            return self._execute_morning_briefing()
        elif task_id == "weekly_linkedin_post":
            return self._execute_weekly_linkedin_post()
        elif task_id == "daily_email_summary":
            return self._execute_daily_email_summary()
        elif task_id == "weekly_task_review":
            return self._execute_weekly_task_review()
        elif task_id == "database_backup":
            return self._execute_database_backup()
        elif task_id == "system_health_check":
            return self._execute_system_health_check()
        elif task_id == "monthly_report":
            return self._execute_monthly_report()
        else:
            self.logger.error(f"Unknown task: {task_id}")
            return False

    def _execute_morning_briefing(self) -> bool:
        """Generate daily morning briefing."""
        try:
            # Create briefing file in vault
            briefing_file = self.vault_path / "Briefings" / f"briefing_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
            briefing_file.parent.mkdir(parents=True, exist_ok=True)

            # Generate briefing content
            content = f"""---
type: briefing
date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
generated_at: {datetime.now(timezone.utc).isoformat()}Z
---

# Daily Morning Briefing - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

## Overnight Activity Summary

[AI Employee will analyze overnight emails, LinkedIn messages, and file drops]

## Priority Tasks for Today

[AI Employee will identify high-priority tasks from /Needs_Action]

## Pending Approvals

[AI Employee will list tasks in /Pending_Approval requiring attention]

## System Status

[AI Employee will report watcher health, database status, and any issues]
"""

            briefing_file.write_text(content)
            self.logger.info(f"Generated morning briefing: {briefing_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to generate morning briefing: {e}")
            return False

    def _execute_weekly_linkedin_post(self) -> bool:
        """Post weekly business update to LinkedIn."""
        try:
            # Create LinkedIn post task in /Needs_Action
            task_file = self.vault_path / "Needs_Action" / f"LINKEDIN_POST_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_weekly-update.md"

            content = f"""---
type: linkedin_post
created_at: {datetime.now(timezone.utc).isoformat()}Z
status: pending
scheduled_task: weekly_linkedin_post
---

# LinkedIn Post: Weekly Business Update

## Task

Post weekly business update to LinkedIn profile.

## Instructions

1. Review this week's accomplishments and insights
2. Draft engaging LinkedIn post using /linkedin-posting skill
3. Seek approval before posting (social media threshold)
4. Post to LinkedIn using LinkedIn watcher
5. Log post to /Logs/linkedin_posts.log

## Post Guidelines

- Focus on value and insights
- Keep it professional and engaging
- Include 3-5 relevant hashtags
- Optimal length: 1,300-2,000 characters
"""

            task_file.write_text(content)
            self.logger.info(f"Created LinkedIn post task: {task_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create LinkedIn post task: {e}")
            return False

    def _execute_daily_email_summary(self) -> bool:
        """Generate end-of-day email summary."""
        try:
            # Create summary file in vault
            summary_file = self.vault_path / "Summaries" / f"email_summary_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
            summary_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: email_summary
date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
generated_at: {datetime.now(timezone.utc).isoformat()}Z
---

# Daily Email Summary - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

## Emails Processed Today

[AI Employee will count emails processed from /Done folder]

## Important Emails

[AI Employee will highlight high-priority emails from today]

## Pending Responses

[AI Employee will list emails in /Needs_Action requiring response]

## Email Statistics

- Total emails processed: [count]
- Emails sent: [count]
- Emails pending: [count]
"""

            summary_file.write_text(content)
            self.logger.info(f"Generated email summary: {summary_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to generate email summary: {e}")
            return False

    def _execute_weekly_task_review(self) -> bool:
        """Generate weekly task completion report."""
        try:
            # Create review file in vault
            review_file = self.vault_path / "Reviews" / f"task_review_{datetime.now(timezone.utc).strftime('%Y%m%d')}.md"
            review_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: task_review
week_ending: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
generated_at: {datetime.now(timezone.utc).isoformat()}Z
---

# Weekly Task Review - Week Ending {datetime.now(timezone.utc).strftime('%Y-%m-%d')}

## Tasks Completed This Week

[AI Employee will count tasks in /Done from this week]

## Tasks Still Pending

[AI Employee will count tasks in /Needs_Action]

## Tasks Rejected

[AI Employee will count tasks in /Rejected from this week]

## Performance Metrics

- Completion rate: [percentage]
- Average response time: [time]
- Approval rate: [percentage]
"""

            review_file.write_text(content)
            self.logger.info(f"Generated task review: {review_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to generate task review: {e}")
            return False

    def _execute_database_backup(self) -> bool:
        """Backup state database."""
        try:
            from watchers.state_manager import StateManager

            state_manager = StateManager()
            backup_path = f"state_backup_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"

            if state_manager.backup_database(backup_path):
                self.logger.info(f"Database backed up to: {backup_path}")
                return True
            else:
                self.logger.error("Database backup failed")
                return False

        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False

    def _execute_system_health_check(self) -> bool:
        """Check health of watchers, database, and MCP servers."""
        try:
            from watchers.state_manager import StateManager

            # Check state database health
            state_manager = StateManager()
            db_healthy = state_manager.health_check()

            # Create health check report
            report_file = self.vault_path / "Logs" / f"health_check_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.md"

            content = f"""---
type: health_check
timestamp: {datetime.now(timezone.utc).isoformat()}Z
---

# System Health Check - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC

## State Database

- Status: {'✓ Healthy' if db_healthy else '✗ Unhealthy'}

## Watchers

[Check watcher heartbeat files]

## MCP Servers

[Check MCP server availability]

## Overall Status

{'✓ All systems operational' if db_healthy else '✗ Issues detected - review logs'}
"""

            report_file.write_text(content)
            self.logger.info(f"Generated health check report: {report_file}")
            return db_healthy

        except Exception as e:
            self.logger.error(f"Failed to perform health check: {e}")
            return False

    def _execute_monthly_report(self) -> bool:
        """Generate monthly activity and performance report."""
        try:
            # Create report file in vault
            report_file = self.vault_path / "Reports" / f"monthly_report_{datetime.now(timezone.utc).strftime('%Y%m')}.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""---
type: monthly_report
month: {datetime.now(timezone.utc).strftime('%Y-%m')}
generated_at: {datetime.now(timezone.utc).isoformat()}Z
---

# Monthly Activity Report - {datetime.now(timezone.utc).strftime('%B %Y')}

## Executive Summary

[AI Employee will provide high-level overview of the month]

## Email Activity

- Total emails processed: [count]
- Emails sent: [count]
- Average response time: [time]

## LinkedIn Activity

- Messages received: [count]
- Posts published: [count]
- Engagement metrics: [data]

## Task Completion

- Tasks completed: [count]
- Tasks pending: [count]
- Completion rate: [percentage]

## Approval Workflow

- Approvals requested: [count]
- Approval rate: [percentage]
- Average approval time: [time]

## System Performance

- Uptime: [percentage]
- Database health: [status]
- Watcher restarts: [count]
"""

            report_file.write_text(content)
            self.logger.info(f"Generated monthly report: {report_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to generate monthly report: {e}")
            return False

    def execute_task(self, task_id: str) -> bool:
        """
        Execute a scheduled task with overlap prevention and retry logic.

        Args:
            task_id: Task identifier

        Returns:
            True on success, False on failure
        """
        # Get task configuration
        tasks = self.config.get('scheduled_tasks', [])
        task_config = next((t for t in tasks if t['id'] == task_id), None)

        if not task_config:
            self.logger.error(f"Task not found in configuration: {task_id}")
            return False

        if not task_config.get('enabled', True):
            self.logger.info(f"Task {task_id} is disabled, skipping execution")
            return True

        # Check overlap prevention
        prevent_overlap = self.config.get('execution_settings', {}).get('prevent_overlap', True)
        lock_fd = None

        if prevent_overlap:
            lock_fd = self._acquire_lock(task_id)
            if lock_fd is None:
                # Task already running
                start_time = datetime.now(timezone.utc)
                self._log_execution(task_id, 'skipped', start_time, datetime.now(timezone.utc), 'Task already running')
                return False

        # Execute task with retry logic
        max_retries = task_config.get('max_retries', 0) if task_config.get('retry_on_failure', False) else 0
        retry_delay = self.config.get('execution_settings', {}).get('retry_delay', 300)

        success = False
        retry_count = 0
        error_message = None

        start_time = datetime.now(timezone.utc)

        try:
            for attempt in range(max_retries + 1):
                try:
                    success = self._execute_task_logic(task_id)

                    if success:
                        break
                    else:
                        error_message = "Task execution returned False"
                        if attempt < max_retries:
                            self.logger.warning(f"Task {task_id} failed, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries + 1})")
                            time.sleep(retry_delay)
                            retry_count += 1
                        else:
                            self.logger.error(f"Task {task_id} failed after {max_retries + 1} attempts")

                except Exception as e:
                    error_message = str(e)
                    self.logger.error(f"Task {task_id} raised exception: {e}")

                    if attempt < max_retries:
                        self.logger.warning(f"Retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries + 1})")
                        time.sleep(retry_delay)
                        retry_count += 1
                    else:
                        self.logger.error(f"Task {task_id} failed after {max_retries + 1} attempts")

        finally:
            end_time = datetime.now(timezone.utc)

            # Log execution
            status = 'success' if success else 'failed'
            self._log_execution(task_id, status, start_time, end_time, error_message, retry_count)

            # Release lock
            if lock_fd is not None:
                self._release_lock(lock_fd, task_id)

        return success


def main():
    """Main entry point for task executor."""
    parser = argparse.ArgumentParser(description='Execute scheduled tasks for AI Employee')
    parser.add_argument('--task', required=True, help='Task ID to execute')
    parser.add_argument('--config', default='scheduled_tasks.yaml', help='Path to configuration file')
    parser.add_argument('--vault', default='AI_Employee_Vault', help='Path to Obsidian vault')

    args = parser.parse_args()

    executor = TaskExecutor(config_path=args.config, vault_path=args.vault)
    success = executor.execute_task(args.task)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
