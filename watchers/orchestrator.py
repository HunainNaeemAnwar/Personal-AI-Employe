"""
Orchestrator for managing multiple concurrent watchers.

This module coordinates multiple watcher processes (Gmail, File System, LinkedIn)
running simultaneously. It provides health monitoring, automatic restart on crashes,
and graceful shutdown handling.
"""

import logging
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional


class WatcherProcess:
    """Represents a managed watcher process.

    Attributes:
        name: Watcher name (e.g., "gmail", "filesystem", "linkedin")
        command: Command to start the watcher
        process: Subprocess instance
        last_heartbeat: Timestamp of last heartbeat
        restart_count: Number of times this watcher has been restarted
    """

    def __init__(self, name: str, command: List[str]):
        """Initialize watcher process configuration.

        Args:
            name: Watcher name
            command: Command to start the watcher as list of strings
        """
        self.name = name
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self.last_heartbeat: Optional[datetime] = None
        self.restart_count = 0


class Orchestrator:
    """
    Orchestrates multiple watcher processes with health monitoring and auto-restart.

    Responsibilities:
    - Launch and manage multiple watcher processes concurrently
    - Monitor watcher health via heartbeat files
    - Automatically restart crashed watchers
    - Handle graceful shutdown on SIGTERM/SIGINT
    - Log orchestrator operations
    """

    def __init__(
        self,
        vault_path: Path,
        watchers: List[Dict[str, any]],
        health_check_interval: int = 60,
        restart_delay: int = 5,
        max_restart_attempts: int = 10,
        log_path: Optional[str] = None,
        state_db_path: str = "state.db"
    ):
        """Initialize the orchestrator.

        Args:
            vault_path: Path to Obsidian vault
            watchers: List of watcher configurations with 'name' and 'command' keys
            health_check_interval: Seconds between health checks (default: 60)
            restart_delay: Seconds to wait before restarting crashed watcher (default: 5)
            max_restart_attempts: Maximum restart attempts per watcher (default: 10)
            log_path: Optional path to orchestrator log file
            state_db_path: Path to SQLite state database (default: state.db)
        """
        self.vault_path = vault_path
        self.health_check_interval = health_check_interval
        self.restart_delay = restart_delay
        self.max_restart_attempts = max_restart_attempts
        self.running = False
        self.state_db_path = Path(state_db_path)
        self.last_state_check = time.time()
        self.state_check_interval = 300  # Check state DB every 5 minutes

        # Setup logging
        self.logger = self._setup_logging(log_path)

        # Initialize watcher processes
        self.watchers: Dict[str, WatcherProcess] = {}
        for watcher_config in watchers:
            name = watcher_config["name"]
            command = watcher_config["command"]
            self.watchers[name] = WatcherProcess(name, command)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self.logger.info(f"Orchestrator initialized with {len(self.watchers)} watchers")

    def _setup_logging(self, log_path: Optional[str]) -> logging.Logger:
        """Setup logging for orchestrator.

        Args:
            log_path: Optional path to log file

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger("Orchestrator")
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if log path provided
        if log_path:
            log_file = Path(log_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals (SIGTERM, SIGINT).

        Args:
            signum: Signal number
            frame: Current stack frame
        """
        signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        self.running = False

    def _start_watcher(self, watcher: WatcherProcess) -> bool:
        """Start a watcher process.

        Args:
            watcher: WatcherProcess instance to start

        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info(f"Starting watcher: {watcher.name}")
            self.logger.debug(f"Command: {' '.join(watcher.command)}")

            # Start process with stdout/stderr redirected to logs
            log_dir = self.vault_path / "Logs"
            log_dir.mkdir(exist_ok=True)

            stdout_log = log_dir / f"{watcher.name}_watcher.log"
            stderr_log = log_dir / f"{watcher.name}_watcher_error.log"

            watcher.process = subprocess.Popen(
                watcher.command,
                stdout=open(stdout_log, "a"),
                stderr=open(stderr_log, "a"),
                cwd=str(Path.cwd())
            )

            watcher.last_heartbeat = datetime.now(timezone.utc)
            self.logger.info(f"Watcher {watcher.name} started with PID {watcher.process.pid}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start watcher {watcher.name}: {e}")
            return False

    def _stop_watcher(self, watcher: WatcherProcess, timeout: int = 10) -> bool:
        """Stop a watcher process gracefully.

        Args:
            watcher: WatcherProcess instance to stop
            timeout: Seconds to wait for graceful shutdown (default: 10)

        Returns:
            True if stopped successfully, False otherwise
        """
        if watcher.process is None:
            return True

        try:
            self.logger.info(f"Stopping watcher: {watcher.name} (PID {watcher.process.pid})")

            # Send SIGTERM for graceful shutdown
            watcher.process.terminate()

            # Wait for process to exit
            try:
                watcher.process.wait(timeout=timeout)
                self.logger.info(f"Watcher {watcher.name} stopped gracefully")
                return True
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                self.logger.warning(f"Watcher {watcher.name} did not stop gracefully, forcing kill")
                watcher.process.kill()
                watcher.process.wait()
                return True

        except Exception as e:
            self.logger.error(f"Error stopping watcher {watcher.name}: {e}")
            return False
        finally:
            watcher.process = None

    def _check_watcher_health(self, watcher: WatcherProcess) -> bool:
        """Check if a watcher is healthy via heartbeat file.

        Args:
            watcher: WatcherProcess instance to check

        Returns:
            True if healthy, False if crashed or stale heartbeat
        """
        # Check if process is still running
        if watcher.process is None:
            return False

        poll_result = watcher.process.poll()
        if poll_result is not None:
            self.logger.warning(f"Watcher {watcher.name} process exited with code {poll_result}")
            return False

        # Check heartbeat file
        heartbeat_file = self.vault_path / "Logs" / f"{watcher.name}_watcher_heartbeat.txt"

        if not heartbeat_file.exists():
            # No heartbeat file yet - give it time to start
            if watcher.last_heartbeat and (datetime.now(timezone.utc) - watcher.last_heartbeat).seconds < 120:
                return True
            self.logger.warning(f"Watcher {watcher.name} has no heartbeat file")
            return False

        try:
            # Read heartbeat timestamp
            heartbeat_timestamp = heartbeat_file.read_text().strip()
            heartbeat_time = datetime.fromisoformat(heartbeat_timestamp.replace("Z", "+00:00"))

            # Check if heartbeat is recent (within 2x health check interval)
            max_age = timedelta(seconds=self.health_check_interval * 2)
            age = datetime.now(timezone.utc) - heartbeat_time

            if age > max_age:
                self.logger.warning(
                    f"Watcher {watcher.name} heartbeat is stale "
                    f"(age: {age.seconds}s, max: {max_age.seconds}s)"
                )
                return False

            # Update last known heartbeat
            watcher.last_heartbeat = heartbeat_time.replace(tzinfo=None)
            return True

        except Exception as e:
            self.logger.error(f"Error reading heartbeat for {watcher.name}: {e}")
            return False

    def _restart_watcher(self, watcher: WatcherProcess) -> bool:
        """Restart a crashed watcher.

        Args:
            watcher: WatcherProcess instance to restart

        Returns:
            True if restarted successfully, False otherwise
        """
        # Check restart limit
        if watcher.restart_count >= self.max_restart_attempts:
            self.logger.error(
                f"Watcher {watcher.name} has reached maximum restart attempts "
                f"({self.max_restart_attempts}), giving up"
            )
            return False

        # Stop existing process if still running
        if watcher.process is not None:
            self._stop_watcher(watcher)

        # Wait before restarting
        self.logger.info(f"Waiting {self.restart_delay}s before restarting {watcher.name}...")
        time.sleep(self.restart_delay)

        # Attempt restart
        watcher.restart_count += 1
        success = self._start_watcher(watcher)

        if success:
            self.logger.info(
                f"Watcher {watcher.name} restarted successfully "
                f"(restart count: {watcher.restart_count})"
            )
        else:
            self.logger.error(f"Failed to restart watcher {watcher.name}")

        return success

    def run(self):
        """Run the orchestrator main loop.

        Starts all watchers and monitors their health, restarting as needed.
        Runs until interrupted by signal or fatal error.
        """
        self.logger.info("Starting orchestrator...")
        self.running = True

        # Start all watchers
        for watcher in self.watchers.values():
            if not self._start_watcher(watcher):
                self.logger.error(f"Failed to start watcher {watcher.name}, continuing with others")

        # Main monitoring loop
        try:
            # Wait for initial heartbeat files to be written (watchers need time to start)
            self.logger.info(f"Waiting {self.health_check_interval}s for watchers to initialize...")
            time.sleep(self.health_check_interval)

            while self.running:
                # Check health of all watchers
                for watcher in self.watchers.values():
                    if not self._check_watcher_health(watcher):
                        self.logger.warning(f"Watcher {watcher.name} is unhealthy, restarting...")
                        self._restart_watcher(watcher)

                # Check state database health periodically
                current_time = time.time()
                if current_time - self.last_state_check >= self.state_check_interval:
                    self._check_state_database_health()
                    self.last_state_check = current_time

                # Wait before next health check
                time.sleep(self.health_check_interval)

        except KeyboardInterrupt:
            self.logger.info("Orchestrator interrupted by user")
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
        finally:
            self._shutdown()

    def _check_state_database_health(self):
        """Check state database health and attempt recovery if corrupted."""
        from watchers.state_manager import StateManager

        try:
            state_manager = StateManager(db_path=str(self.state_db_path))

            # Check if database is healthy
            if not state_manager.health_check():
                self.logger.error("State database health check failed")

                # Detect corruption
                if state_manager.detect_corruption():
                    self.logger.error("State database corruption detected, attempting recovery...")

                    # Attempt automatic recovery
                    if state_manager.recover_from_corruption(self.vault_path):
                        self.logger.info("State database recovered successfully")
                    else:
                        self.logger.error("State database recovery failed - manual intervention required")
                else:
                    self.logger.warning("State database unhealthy but not corrupted - check logs")
            else:
                self.logger.debug("State database health check passed")

        except Exception as e:
            self.logger.error(f"State database health check error: {e}")

    def _shutdown(self):
        """Gracefully shutdown all watchers."""
        self.logger.info("Shutting down orchestrator...")

        # Stop all watchers
        for watcher in self.watchers.values():
            if watcher.process is not None:
                self._stop_watcher(watcher)

        self.logger.info("Orchestrator shutdown complete")


def main():
    """Main entry point for orchestrator."""
    import os
    from dotenv import load_dotenv

    # Load environment variables (override=True to refresh cached values)
    load_dotenv(override=True)

    vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))

    # Get list of watchers to run from config
    watcher_list = os.getenv("ORCHESTRATOR_WATCHERS", "gmail,filesystem").split(",")

    # Get common configuration
    state_db_path = os.getenv("STATE_DB_PATH", str(vault_path / "state.db"))

    # Configure watchers based on environment
    watchers = []

    if "gmail" in watcher_list:
        gmail_cmd = [
            sys.executable, "-m", "watchers.gmail_watcher",
            "--vault", str(vault_path),
            "--state-db", state_db_path,
            "--interval", os.getenv("GMAIL_CHECK_INTERVAL", "60")
        ]
        if os.getenv("GMAIL_CREDENTIALS_PATH"):
            gmail_cmd.extend(["--credentials", os.getenv("GMAIL_CREDENTIALS_PATH")])
        if os.getenv("GMAIL_TOKEN_PATH"):
            gmail_cmd.extend(["--token", os.getenv("GMAIL_TOKEN_PATH")])
        if os.getenv("GMAIL_QUERY"):
            gmail_cmd.extend(["--query", os.getenv("GMAIL_QUERY")])

        watchers.append({
            "name": "gmail",
            "command": gmail_cmd
        })

    if "filesystem" in watcher_list:
        watch_dir = os.getenv("WATCH_DIRECTORY", str(vault_path / "Watch"))
        watchers.append({
            "name": "filesystem",
            "command": [
                sys.executable, "-m", "watchers.filesystem_watcher",
                "--vault", str(vault_path),
                "--watch-dir", watch_dir,
                "--state-db", state_db_path,
                "--interval", os.getenv("FILESYSTEM_POLLING_INTERVAL", "5"),
                "--extensions", os.getenv("FILE_EXTENSIONS", "*")
            ]
        })

    if "linkedin" in watcher_list:
        linkedin_username = os.getenv("LINKEDIN_USERNAME")
        linkedin_password = os.getenv("LINKEDIN_PASSWORD")

        if linkedin_username and linkedin_password:
            watchers.append({
                "name": "linkedin",
                "command": [
                    sys.executable, "-m", "watchers.linkedin_watcher",
                    "--vault", str(vault_path),
                    "--username", linkedin_username,
                    "--password", linkedin_password,
                    "--state-db", state_db_path,
                    "--interval", os.getenv("LINKEDIN_POLLING_INTERVAL", "300")
                ]
            })
        else:
            logging.warning("LinkedIn credentials not found, skipping LinkedIn watcher")

    # Create and run orchestrator
    orchestrator = Orchestrator(
        vault_path=vault_path,
        watchers=watchers,
        health_check_interval=int(os.getenv("ORCHESTRATOR_HEALTH_CHECK_INTERVAL", "60")),
        restart_delay=int(os.getenv("ORCHESTRATOR_RESTART_DELAY", "5")),
        log_path=os.getenv("ORCHESTRATOR_LOG_PATH", str(vault_path / "Logs" / "orchestrator.log"))
    )

    orchestrator.run()


if __name__ == "__main__":
    main()
