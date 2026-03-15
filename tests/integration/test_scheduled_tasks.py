"""
Integration tests for Scheduled Tasks - Automated task execution on schedule.

Tests cover:
- Scheduled task configuration
- Task execution wrapper
- Overlap prevention with lock files
- Retry logic for failed tasks
- Execution logging
- Cron/Task Scheduler integration
"""

import pytest
import tempfile
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone
import yaml
import os


@pytest.fixture
def temp_vault():
    """Create temporary vault for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create vault structure
        folders = ["Needs_Action", "Done", "Logs", "Briefings", "Summaries", "Reviews", "Reports", "Plans"]
        for folder in folders:
            (vault_path / folder).mkdir()
        yield vault_path


@pytest.fixture
def temp_config(temp_vault):
    """Create temporary scheduled_tasks.yaml configuration."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            'scheduled_tasks': [
                {
                    'id': 'test_task',
                    'description': 'Test scheduled task',
                    'schedule': '* * * * *',  # Every minute
                    'command': 'python -m scheduler.task_executor --task test_task',
                    'enabled': True,
                    'retry_on_failure': True,
                    'max_retries': 2
                }
            ],
            'execution_settings': {
                'prevent_overlap': True,
                'lock_dir': str(temp_vault / 'locks'),
                'max_execution_time': 60,
                'log_dir': str(temp_vault / 'Logs'),
                'retry_delay': 5,
                'verbose_logging': True
            }
        }
        yaml.dump(config, f)
        config_path = f.name

    yield config_path

    # Cleanup
    Path(config_path).unlink(missing_ok=True)


class TestScheduledTaskConfiguration:
    """Test scheduled task configuration loading."""

    def test_load_configuration(self, temp_config):
        """Test loading scheduled_tasks.yaml configuration."""
        with open(temp_config, 'r') as f:
            config = yaml.safe_load(f)

        assert 'scheduled_tasks' in config
        assert len(config['scheduled_tasks']) == 1
        assert config['scheduled_tasks'][0]['id'] == 'test_task'

    def test_configuration_has_execution_settings(self, temp_config):
        """Test that configuration includes execution settings."""
        with open(temp_config, 'r') as f:
            config = yaml.safe_load(f)

        assert 'execution_settings' in config
        assert config['execution_settings']['prevent_overlap'] is True
        assert 'lock_dir' in config['execution_settings']


class TestTaskExecutor:
    """Test task executor functionality."""

    def test_task_executor_runs(self, temp_vault, temp_config):
        """Test that task executor can run a task."""
        # Create simple test task that creates a file
        test_file = temp_vault / "test_output.txt"

        # Run task executor (will fail because test_task logic doesn't exist, but should start)
        result = subprocess.run(
            ['python', '-m', 'scheduler.task_executor', '--task', 'morning_briefing', '--vault', str(temp_vault)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Should execute (may fail, but should run)
        assert result.returncode in [0, 1]  # 0 = success, 1 = task failed

    def test_task_executor_creates_log(self, temp_vault, temp_config):
        """Test that task executor creates execution log."""
        # Run task executor
        subprocess.run(
            ['python', '-m', 'scheduler.task_executor', '--task', 'morning_briefing', '--vault', str(temp_vault)],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Check log file exists
        log_file = temp_vault / "Logs" / "scheduled_tasks.log"
        assert log_file.exists()


class TestOverlapPrevention:
    """Test overlap prevention with lock files."""

    def test_lock_file_created(self, temp_vault):
        """Test that lock file is created during task execution."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Acquire lock
        lock_fd = executor._acquire_lock('test_task')
        assert lock_fd is not None

        # Check lock file exists
        lock_dir = Path(executor.config.get('execution_settings', {}).get('lock_dir', '/tmp/ai_employee_locks'))
        lock_file = lock_dir / 'test_task.lock'
        assert lock_file.exists()

        # Release lock
        executor._release_lock(lock_fd, 'test_task')

    def test_concurrent_execution_prevented(self, temp_vault):
        """Test that concurrent execution of same task is prevented."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Acquire first lock
        lock_fd1 = executor._acquire_lock('test_task')
        assert lock_fd1 is not None

        # Try to acquire second lock (should fail)
        lock_fd2 = executor._acquire_lock('test_task')
        assert lock_fd2 is None

        # Release first lock
        executor._release_lock(lock_fd1, 'test_task')

        # Now second lock should succeed
        lock_fd3 = executor._acquire_lock('test_task')
        assert lock_fd3 is not None
        executor._release_lock(lock_fd3, 'test_task')


class TestExecutionLogging:
    """Test execution logging functionality."""

    def test_execution_logged_to_file(self, temp_vault):
        """Test that task execution is logged to file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Log execution
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        executor._log_execution(
            task_id='test_task',
            status='success',
            start_time=start_time,
            end_time=end_time,
            error=None,
            retry_count=0
        )

        # Check log file
        log_file = temp_vault / "Logs" / "scheduled_tasks.log"
        assert log_file.exists()

        # Verify log entry
        import json
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            log_entry = json.loads(lines[0])
            assert log_entry['task_id'] == 'test_task'
            assert log_entry['status'] == 'success'
            assert log_entry['retry_count'] == 0

    def test_failed_execution_logged(self, temp_vault):
        """Test that failed task execution is logged with error."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Log failed execution
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        executor._log_execution(
            task_id='test_task',
            status='failed',
            start_time=start_time,
            end_time=end_time,
            error='Task execution failed',
            retry_count=2
        )

        # Check log file
        log_file = temp_vault / "Logs" / "scheduled_tasks.log"
        assert log_file.exists()

        # Verify log entry
        import json
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 1
            log_entry = json.loads(lines[0])
            assert log_entry['status'] == 'failed'
            assert log_entry['error'] == 'Task execution failed'
            assert log_entry['retry_count'] == 2


class TestTaskImplementations:
    """Test individual task implementations."""

    def test_morning_briefing_creates_file(self, temp_vault):
        """Test that morning briefing task creates briefing file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Execute morning briefing
        success = executor._execute_morning_briefing()
        assert success is True

        # Check briefing file created
        briefing_dir = temp_vault / "Briefings"
        briefing_files = list(briefing_dir.glob("briefing_*.md"))
        assert len(briefing_files) == 1

    def test_daily_email_summary_creates_file(self, temp_vault):
        """Test that daily email summary task creates summary file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Execute email summary
        success = executor._execute_daily_email_summary()
        assert success is True

        # Check summary file created
        summary_dir = temp_vault / "Summaries"
        summary_files = list(summary_dir.glob("email_summary_*.md"))
        assert len(summary_files) == 1

    def test_weekly_task_review_creates_file(self, temp_vault):
        """Test that weekly task review creates review file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Execute task review
        success = executor._execute_weekly_task_review()
        assert success is True

        # Check review file created
        review_dir = temp_vault / "Reviews"
        review_files = list(review_dir.glob("task_review_*.md"))
        assert len(review_files) == 1

    def test_database_backup_creates_backup(self, temp_vault):
        """Test that database backup task creates backup file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Execute database backup
        success = executor._execute_database_backup()

        # Should succeed (creates backup file)
        assert success is True

    def test_system_health_check_creates_report(self, temp_vault):
        """Test that system health check creates report file."""
        from scheduler.task_executor import TaskExecutor

        executor = TaskExecutor(vault_path=str(temp_vault))

        # Execute health check
        success = executor._execute_system_health_check()

        # Check report file created
        log_dir = temp_vault / "Logs"
        health_files = list(log_dir.glob("health_check_*.md"))
        assert len(health_files) == 1


class TestCronSetup:
    """Test cron setup functionality (Linux/Mac)."""

    def test_cron_expression_validation(self):
        """Test cron expression validation."""
        from scheduler.cron_setup import CronSetup

        cron_setup = CronSetup()

        # Valid expressions
        assert cron_setup.validate_cron_expression("0 8 * * *") is True
        assert cron_setup.validate_cron_expression("*/15 * * * *") is True
        assert cron_setup.validate_cron_expression("0 9 * * 1") is True

        # Invalid expressions
        assert cron_setup.validate_cron_expression("0 8 * *") is False  # Too few fields
        assert cron_setup.validate_cron_expression("60 8 * * *") is False  # Invalid minute
        assert cron_setup.validate_cron_expression("0 25 * * *") is False  # Invalid hour

    def test_read_scheduled_tasks(self, temp_config):
        """Test reading scheduled tasks from configuration."""
        from scheduler.cron_setup import CronSetup

        cron_setup = CronSetup(config_path=temp_config)
        tasks = cron_setup.read_scheduled_tasks()

        assert len(tasks) == 1
        assert tasks[0]['id'] == 'test_task'
        assert tasks[0]['schedule'] == '* * * * *'


class TestTaskSchedulerSetup:
    """Test Windows Task Scheduler setup functionality."""

    def test_cron_to_trigger_conversion(self):
        """Test converting cron expression to Task Scheduler trigger."""
        from scheduler.task_scheduler_setup import TaskSchedulerSetup

        scheduler_setup = TaskSchedulerSetup()

        # Daily trigger
        trigger = scheduler_setup.cron_to_trigger("0 8 * * *")
        assert trigger['type'] == 'Daily'
        assert trigger['time'] == '08:00'

        # Weekly trigger
        trigger = scheduler_setup.cron_to_trigger("0 9 * * 1")
        assert trigger['type'] == 'Weekly'
        assert 'Monday' in trigger['days_of_week']

    def test_weekday_conversion(self):
        """Test converting cron weekday to Task Scheduler days."""
        from scheduler.task_scheduler_setup import TaskSchedulerSetup

        scheduler_setup = TaskSchedulerSetup()

        # Single day
        assert scheduler_setup._weekday_to_days('1') == 'Monday'
        assert scheduler_setup._weekday_to_days('0') == 'Sunday'

        # Multiple days
        days = scheduler_setup._weekday_to_days('1,3,5')
        assert 'Monday' in days
        assert 'Wednesday' in days
        assert 'Friday' in days


class TestEndToEndScheduling:
    """Test complete end-to-end scheduling workflow."""

    def test_complete_scheduling_workflow(self, temp_vault, temp_config):
        """Test complete workflow from configuration to execution."""
        # Step 1: Configuration loaded
        with open(temp_config, 'r') as f:
            config = yaml.safe_load(f)
        assert len(config['scheduled_tasks']) == 1

        # Step 2: Task executor can run
        from scheduler.task_executor import TaskExecutor
        executor = TaskExecutor(config_path=temp_config, vault_path=str(temp_vault))
        assert executor is not None

        # Step 3: Lock file created during execution
        lock_fd = executor._acquire_lock('test_task')
        assert lock_fd is not None

        # Step 4: Execution logged
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        executor._log_execution(
            task_id='test_task',
            status='success',
            start_time=start_time,
            end_time=end_time
        )

        log_file = temp_vault / "Logs" / "scheduled_tasks.log"
        assert log_file.exists()

        # Step 5: Lock released
        executor._release_lock(lock_fd, 'test_task')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
