"""
Task Scheduler Setup for Windows - Automated scheduled task execution.

This module provides functions to configure Windows Task Scheduler jobs for
scheduled task execution. It reads task definitions from scheduled_tasks.yaml
and creates corresponding scheduled tasks using PowerShell.
"""

import logging
import subprocess
import yaml
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional


class TaskSchedulerSetup:
    """
    Manages Windows Task Scheduler configuration for scheduled tasks.

    Responsibilities:
    - Read scheduled task definitions from YAML
    - Convert cron expressions to Task Scheduler triggers
    - Create/remove scheduled tasks via PowerShell
    - Validate task configuration
    - Handle task conflicts
    """

    def __init__(self, config_path: str = "scheduled_tasks.yaml"):
        """
        Initialize TaskSchedulerSetup.

        Args:
            config_path: Path to scheduled_tasks.yaml configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)

        # Verify Windows platform
        if platform.system() != 'Windows':
            self.logger.warning("TaskSchedulerSetup is designed for Windows only")

    def read_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """
        Read scheduled task definitions from YAML configuration.

        Returns:
            List of task definitions with schedule and command information
        """
        if not self.config_path.exists():
            self.logger.error(f"Configuration file not found: {self.config_path}")
            return []

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                tasks = config.get('scheduled_tasks', [])
                self.logger.info(f"Loaded {len(tasks)} scheduled tasks from {self.config_path}")
                return tasks
        except Exception as e:
            self.logger.error(f"Failed to read scheduled tasks: {e}")
            return []

    def cron_to_trigger(self, cron_expr: str) -> Dict[str, Any]:
        """
        Convert cron expression to Task Scheduler trigger parameters.

        Args:
            cron_expr: Cron expression (e.g., "0 8 * * *")

        Returns:
            Dictionary with trigger parameters for Task Scheduler
        """
        parts = cron_expr.split()
        if len(parts) != 5:
            self.logger.error(f"Invalid cron expression: {cron_expr}")
            return {}

        minute, hour, day, month, weekday = parts

        # Build trigger parameters
        trigger = {
            'type': 'Daily',  # Default to daily
            'time': f"{hour.zfill(2) if hour != '*' else '00'}:{minute.zfill(2) if minute != '*' else '00'}",
            'days_interval': 1
        }

        # Adjust trigger type based on cron expression
        if weekday != '*':
            # Weekly trigger
            trigger['type'] = 'Weekly'
            trigger['days_of_week'] = self._weekday_to_days(weekday)
        elif day != '*' and month != '*':
            # Monthly trigger
            trigger['type'] = 'Monthly'
            trigger['day'] = day
            trigger['months'] = self._month_to_months(month)
        elif day != '*':
            # Monthly trigger (all months)
            trigger['type'] = 'Monthly'
            trigger['day'] = day
            trigger['months'] = 'January,February,March,April,May,June,July,August,September,October,November,December'

        return trigger

    def _weekday_to_days(self, weekday: str) -> str:
        """
        Convert cron weekday to Task Scheduler days of week.

        Args:
            weekday: Cron weekday (0-7, where 0 and 7 are Sunday)

        Returns:
            Comma-separated list of day names
        """
        day_map = {
            '0': 'Sunday', '7': 'Sunday',
            '1': 'Monday',
            '2': 'Tuesday',
            '3': 'Wednesday',
            '4': 'Thursday',
            '5': 'Friday',
            '6': 'Saturday'
        }

        if ',' in weekday:
            # Multiple days
            days = [day_map.get(d.strip(), '') for d in weekday.split(',')]
            return ','.join(filter(None, days))
        elif '-' in weekday:
            # Range of days
            start, end = weekday.split('-')
            start_idx = int(start)
            end_idx = int(end)
            days = [day_map.get(str(i), '') for i in range(start_idx, end_idx + 1)]
            return ','.join(filter(None, days))
        else:
            # Single day
            return day_map.get(weekday, 'Monday')

    def _month_to_months(self, month: str) -> str:
        """
        Convert cron month to Task Scheduler months.

        Args:
            month: Cron month (1-12)

        Returns:
            Comma-separated list of month names
        """
        month_map = {
            '1': 'January', '2': 'February', '3': 'March',
            '4': 'April', '5': 'May', '6': 'June',
            '7': 'July', '8': 'August', '9': 'September',
            '10': 'October', '11': 'November', '12': 'December'
        }

        if ',' in month:
            # Multiple months
            months = [month_map.get(m.strip(), '') for m in month.split(',')]
            return ','.join(filter(None, months))
        elif '-' in month:
            # Range of months
            start, end = month.split('-')
            start_idx = int(start)
            end_idx = int(end)
            months = [month_map.get(str(i), '') for i in range(start_idx, end_idx + 1)]
            return ','.join(filter(None, months))
        else:
            # Single month
            return month_map.get(month, 'January')

    def task_exists(self, task_name: str) -> bool:
        """
        Check if a scheduled task exists.

        Args:
            task_name: Name of the task

        Returns:
            True if task exists, False otherwise
        """
        try:
            result = subprocess.run(
                ['powershell', '-Command', f'Get-ScheduledTask -TaskName "{task_name}" -ErrorAction SilentlyContinue'],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip() != ''
        except Exception as e:
            self.logger.error(f"Failed to check task existence: {e}")
            return False

    def create_scheduled_task(
        self,
        task_name: str,
        command: str,
        cron_expr: str,
        description: Optional[str] = None
    ) -> bool:
        """
        Create a scheduled task in Windows Task Scheduler.

        Args:
            task_name: Name for the scheduled task
            command: Command to execute
            cron_expr: Cron expression for schedule
            description: Optional task description

        Returns:
            True on success, False on failure
        """
        # Check if task already exists
        if self.task_exists(task_name):
            self.logger.info(f"Scheduled task already exists: {task_name}")
            return True

        # Convert cron to trigger
        trigger = self.cron_to_trigger(cron_expr)
        if not trigger:
            return False

        # Build PowerShell command
        ps_command = self._build_register_task_command(
            task_name, command, trigger, description
        )

        # Execute PowerShell command
        try:
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info(f"Created scheduled task: {task_name}")
                return True
            else:
                self.logger.error(f"Failed to create scheduled task: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to execute PowerShell command: {e}")
            return False

    def _build_register_task_command(
        self,
        task_name: str,
        command: str,
        trigger: Dict[str, Any],
        description: Optional[str]
    ) -> str:
        """
        Build PowerShell Register-ScheduledTask command.

        Args:
            task_name: Task name
            command: Command to execute
            trigger: Trigger parameters
            description: Task description

        Returns:
            PowerShell command string
        """
        # Escape quotes in command
        command_escaped = command.replace('"', '`"')

        # Build action
        action = f'$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-Command \\"{command_escaped}\\""'

        # Build trigger based on type
        trigger_type = trigger.get('type', 'Daily')
        trigger_time = trigger.get('time', '00:00')

        if trigger_type == 'Daily':
            days_interval = trigger.get('days_interval', 1)
            trigger_cmd = f'$trigger = New-ScheduledTaskTrigger -Daily -DaysInterval {days_interval} -At "{trigger_time}"'
        elif trigger_type == 'Weekly':
            days_of_week = trigger.get('days_of_week', 'Monday')
            trigger_cmd = f'$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek {days_of_week} -At "{trigger_time}"'
        elif trigger_type == 'Monthly':
            day = trigger.get('day', '1')
            months = trigger.get('months', 'January')
            trigger_cmd = f'$trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth {day} -MonthsOfYear {months} -At "{trigger_time}"'
        else:
            trigger_cmd = f'$trigger = New-ScheduledTaskTrigger -Daily -At "{trigger_time}"'

        # Build settings
        settings = '$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable'

        # Build description
        desc = description or f"AI Employee scheduled task: {task_name}"
        desc_escaped = desc.replace('"', '`"')

        # Build register command
        register = f'Register-ScheduledTask -TaskName "{task_name}" -Action $action -Trigger $trigger -Settings $settings -Description "{desc_escaped}" -Force'

        # Combine all commands
        ps_command = f'{action}; {trigger_cmd}; {settings}; {register}'

        return ps_command

    def remove_scheduled_task(self, task_name: str) -> bool:
        """
        Remove a scheduled task from Windows Task Scheduler.

        Args:
            task_name: Name of the task to remove

        Returns:
            True on success, False on failure
        """
        if not self.task_exists(task_name):
            self.logger.warning(f"Scheduled task not found: {task_name}")
            return False

        try:
            result = subprocess.run(
                ['powershell', '-Command', f'Unregister-ScheduledTask -TaskName "{task_name}" -Confirm:$false'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                self.logger.info(f"Removed scheduled task: {task_name}")
                return True
            else:
                self.logger.error(f"Failed to remove scheduled task: {result.stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to execute PowerShell command: {e}")
            return False

    def setup_scheduled_tasks(self) -> int:
        """
        Setup all scheduled tasks from configuration file.

        Returns:
            Number of successfully configured tasks
        """
        tasks = self.read_scheduled_tasks()
        success_count = 0

        for task in tasks:
            task_id = task.get('id', 'unknown')
            cron_expr = task.get('schedule', '')
            command = task.get('command', '')
            description = task.get('description', '')

            if not cron_expr or not command:
                self.logger.warning(f"Skipping task {task_id}: missing schedule or command")
                continue

            # Create scheduled task
            task_name = f"AIEmployee_{task_id}"
            if self.create_scheduled_task(task_name, command, cron_expr, description):
                success_count += 1

        self.logger.info(f"Configured {success_count}/{len(tasks)} scheduled tasks")
        return success_count

    def remove_all_scheduled_tasks(self) -> int:
        """
        Remove all AI Employee scheduled tasks from Task Scheduler.

        Returns:
            Number of removed tasks
        """
        tasks = self.read_scheduled_tasks()
        removed_count = 0

        for task in tasks:
            task_id = task.get('id', 'unknown')
            task_name = f"AIEmployee_{task_id}"
            if self.remove_scheduled_task(task_name):
                removed_count += 1

        self.logger.info(f"Removed {removed_count} scheduled tasks")
        return removed_count


def main():
    """Main entry point for Task Scheduler setup."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    scheduler_setup = TaskSchedulerSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'setup':
            count = scheduler_setup.setup_scheduled_tasks()
            print(f"Configured {count} scheduled tasks")
        elif command == 'remove':
            count = scheduler_setup.remove_all_scheduled_tasks()
            print(f"Removed {count} scheduled tasks")
        elif command == 'list':
            # List all AI Employee tasks
            result = subprocess.run(
                ['powershell', '-Command', 'Get-ScheduledTask | Where-Object {$_.TaskName -like "AIEmployee_*"} | Format-Table TaskName, State, LastRunTime, NextRunTime'],
                capture_output=True,
                text=True
            )
            print(result.stdout)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m scheduler.task_scheduler_setup [setup|remove|list]")
            sys.exit(1)
    else:
        print("Usage: python -m scheduler.task_scheduler_setup [setup|remove|list]")
        sys.exit(1)


if __name__ == '__main__':
    main()
