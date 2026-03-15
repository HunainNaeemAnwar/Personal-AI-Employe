"""
Cron Setup for Linux/Mac - Automated scheduled task execution.

This module provides functions to configure cron jobs for scheduled task execution
on Linux and macOS systems. It reads task definitions from scheduled_tasks.yaml
and creates corresponding cron entries.
"""

import logging
import subprocess
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional


class CronSetup:
    """
    Manages cron job configuration for scheduled tasks.

    Responsibilities:
    - Read scheduled task definitions from YAML
    - Generate cron expressions from task schedules
    - Add/remove cron jobs via crontab
    - Validate cron syntax
    - Handle cron job conflicts
    """

    def __init__(self, config_path: str = "scheduled_tasks.yaml"):
        """
        Initialize CronSetup.

        Args:
            config_path: Path to scheduled_tasks.yaml configuration file
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger(__name__)

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

    def validate_cron_expression(self, cron_expr: str) -> bool:
        """
        Validate cron expression syntax.

        Args:
            cron_expr: Cron expression (e.g., "0 8 * * *")

        Returns:
            True if valid, False otherwise
        """
        # Basic validation: 5 fields (minute hour day month weekday)
        parts = cron_expr.split()
        if len(parts) != 5:
            self.logger.error(f"Invalid cron expression (expected 5 fields): {cron_expr}")
            return False

        # Validate each field
        minute, hour, day, month, weekday = parts

        # Minute: 0-59 or * or */N
        if not self._validate_cron_field(minute, 0, 59):
            self.logger.error(f"Invalid minute field: {minute}")
            return False

        # Hour: 0-23 or * or */N
        if not self._validate_cron_field(hour, 0, 23):
            self.logger.error(f"Invalid hour field: {hour}")
            return False

        # Day: 1-31 or * or */N
        if not self._validate_cron_field(day, 1, 31):
            self.logger.error(f"Invalid day field: {day}")
            return False

        # Month: 1-12 or * or */N
        if not self._validate_cron_field(month, 1, 12):
            self.logger.error(f"Invalid month field: {month}")
            return False

        # Weekday: 0-7 or * or */N (0 and 7 are Sunday)
        if not self._validate_cron_field(weekday, 0, 7):
            self.logger.error(f"Invalid weekday field: {weekday}")
            return False

        return True

    def _validate_cron_field(self, field: str, min_val: int, max_val: int) -> bool:
        """
        Validate a single cron field.

        Args:
            field: Cron field value
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            True if valid, False otherwise
        """
        # Wildcard
        if field == '*':
            return True

        # Step values (*/N)
        if field.startswith('*/'):
            try:
                step = int(field[2:])
                return step > 0
            except ValueError:
                return False

        # Range (N-M)
        if '-' in field:
            try:
                start, end = field.split('-')
                start_val = int(start)
                end_val = int(end)
                return min_val <= start_val <= max_val and min_val <= end_val <= max_val and start_val <= end_val
            except ValueError:
                return False

        # List (N,M,O)
        if ',' in field:
            try:
                values = [int(v) for v in field.split(',')]
                return all(min_val <= v <= max_val for v in values)
            except ValueError:
                return False

        # Single value
        try:
            value = int(field)
            return min_val <= value <= max_val
        except ValueError:
            return False

    def get_current_crontab(self) -> str:
        """
        Get current crontab contents.

        Returns:
            Current crontab as string, or empty string if no crontab exists
        """
        try:
            result = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return result.stdout
            else:
                # No crontab exists yet
                return ""
        except Exception as e:
            self.logger.error(f"Failed to read crontab: {e}")
            return ""

    def add_cron_job(self, cron_expr: str, command: str, comment: Optional[str] = None) -> bool:
        """
        Add a cron job to crontab.

        Args:
            cron_expr: Cron expression (e.g., "0 8 * * *")
            command: Command to execute
            comment: Optional comment for the cron job

        Returns:
            True on success, False on failure
        """
        # Validate cron expression
        if not self.validate_cron_expression(cron_expr):
            return False

        # Get current crontab
        current_crontab = self.get_current_crontab()

        # Check if job already exists
        job_line = f"{cron_expr} {command}"
        if job_line in current_crontab:
            self.logger.info(f"Cron job already exists: {job_line}")
            return True

        # Add new job
        new_crontab = current_crontab
        if comment:
            new_crontab += f"\n# {comment}\n"
        new_crontab += f"{job_line}\n"

        # Write new crontab
        try:
            process = subprocess.Popen(
                ['crontab', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=new_crontab)

            if process.returncode == 0:
                self.logger.info(f"Added cron job: {job_line}")
                return True
            else:
                self.logger.error(f"Failed to add cron job: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to write crontab: {e}")
            return False

    def remove_cron_job(self, command: str) -> bool:
        """
        Remove a cron job from crontab by command.

        Args:
            command: Command to remove

        Returns:
            True on success, False on failure
        """
        # Get current crontab
        current_crontab = self.get_current_crontab()

        # Filter out lines containing the command
        lines = current_crontab.split('\n')
        new_lines = [line for line in lines if command not in line]

        if len(new_lines) == len(lines):
            self.logger.warning(f"Cron job not found: {command}")
            return False

        # Write new crontab
        new_crontab = '\n'.join(new_lines)

        try:
            process = subprocess.Popen(
                ['crontab', '-'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(input=new_crontab)

            if process.returncode == 0:
                self.logger.info(f"Removed cron job: {command}")
                return True
            else:
                self.logger.error(f"Failed to remove cron job: {stderr}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to write crontab: {e}")
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

            # Add cron job
            comment = f"AI Employee Task: {task_id} - {description}"
            if self.add_cron_job(cron_expr, command, comment):
                success_count += 1

        self.logger.info(f"Configured {success_count}/{len(tasks)} scheduled tasks")
        return success_count

    def remove_all_scheduled_tasks(self) -> int:
        """
        Remove all AI Employee scheduled tasks from crontab.

        Returns:
            Number of removed tasks
        """
        tasks = self.read_scheduled_tasks()
        removed_count = 0

        for task in tasks:
            command = task.get('command', '')
            if command and self.remove_cron_job(command):
                removed_count += 1

        self.logger.info(f"Removed {removed_count} scheduled tasks")
        return removed_count


def main():
    """Main entry point for cron setup."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    cron_setup = CronSetup()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'setup':
            count = cron_setup.setup_scheduled_tasks()
            print(f"Configured {count} scheduled tasks")
        elif command == 'remove':
            count = cron_setup.remove_all_scheduled_tasks()
            print(f"Removed {count} scheduled tasks")
        elif command == 'list':
            print(cron_setup.get_current_crontab())
        else:
            print(f"Unknown command: {command}")
            print("Usage: python -m scheduler.cron_setup [setup|remove|list]")
            sys.exit(1)
    else:
        print("Usage: python -m scheduler.cron_setup [setup|remove|list]")
        sys.exit(1)


if __name__ == '__main__':
    main()
