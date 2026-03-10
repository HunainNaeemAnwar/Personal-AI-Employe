"""Base watcher class for monitoring external sources.

This module provides the abstract base class for all watcher implementations.
Watchers monitor external sources (Gmail, file system, etc.) and create task
files in the Obsidian vault when new items are detected.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set

from watchers.state_manager import StateManager


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations.

    Attributes:
        vault_path: Path to the Obsidian vault
        check_interval: Seconds between checks
        processed_items: Set of already-processed item IDs
        logger: Logger instance for this watcher
    """

    def __init__(self, vault_path: Path, check_interval: int = 60, state_db_path: str = "state.db"):
        """Initialize the base watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 60)
            state_db_path: Path to SQLite state database (default: state.db)

        Raises:
            ValueError: If vault_path doesn't exist or isn't a directory
        """
        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")
        if not vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault_path}")

        self.vault_path = vault_path
        self.check_interval = check_interval
        self.processed_items: Set[str] = set()  # In-memory cache for performance

        # Setup logging first
        self.logger = self._setup_logging()

        # Get heartbeat interval from environment or use default
        import os
        self.heartbeat_interval = int(os.getenv("WATCHER_HEARTBEAT_INTERVAL", "60"))

        # Initialize StateManager for persistent state tracking
        self.state_manager = StateManager(db_path=state_db_path)
        self.logger.info(f"StateManager initialized with database: {state_db_path}")

        # Get watcher source type from class name (e.g., "GmailWatcher" -> "gmail")
        self.source_type = self.__class__.__name__.replace("Watcher", "").lower()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for this watcher.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def log_to_vault(
        self, action: str, result: str, details: Optional[Dict[str, Any]] = None, error_message: Optional[str] = None
    ) -> None:
        """Write a log entry to the vault's Logs folder.

        Args:
            action: Action performed (check, create_task, error)
            result: Result of action (success, failure)
            details: Optional additional details
            error_message: Optional error message if result is failure
        """
        # Build log entry with timestamp and watcher type
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            # Extract watcher type from class name (e.g., "GmailWatcher" -> "gmail")
            "watcher_type": self.__class__.__name__.replace("Watcher", "").lower(),
            "action": action,
            "result": result,
        }

        # Add optional fields if provided
        if details:
            log_entry["details"] = details

        if error_message:
            log_entry["error_message"] = error_message

        # Get today's log file path (one JSON file per day)
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(exist_ok=True)

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = log_dir / f"{today}.json"

        # Read existing logs or create new array if file doesn't exist
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                # Handle corrupted JSON by starting fresh
                logs = []
        else:
            logs = []

        # Append new log entry to array
        logs.append(log_entry)

        # Write entire log array back to file (pretty-printed with indent=2)
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

    def is_processed(self, item_id: str) -> bool:
        """Check if an item has already been processed.

        Uses both in-memory cache and persistent StateManager for duplicate detection.

        Args:
            item_id: Unique identifier for the item

        Returns:
            True if item has been processed, False otherwise
        """
        # Check in-memory cache first (fast path)
        if item_id in self.processed_items:
            return True

        # Check persistent state database (handles restarts)
        if self.state_manager.check_processed(self.source_type, item_id):
            # Update in-memory cache for future checks
            self.processed_items.add(item_id)
            return True

        return False

    def mark_processed(self, item_id: str, task_file_path: Optional[str] = None) -> None:
        """Mark an item as processed to prevent duplicates.

        Persists to both in-memory cache and StateManager database.

        Args:
            item_id: Unique identifier for the item
            task_file_path: Optional relative path to created task file
        """
        # Add to in-memory cache
        self.processed_items.add(item_id)

        # Persist to database
        row_id = self.state_manager.insert_item(
            source=self.source_type,
            source_id=item_id,
            status="processed",
            task_file_path=task_file_path
        )

        if row_id:
            self.logger.debug(f"Marked item as processed: {item_id} (DB ID: {row_id})")
        else:
            self.logger.warning(f"Failed to persist processed item: {item_id}")

    @abstractmethod
    def check_for_updates(self) -> int:
        """Check for new items from the external source.

        This method should be implemented by subclasses to check their
        specific external source (Gmail, file system, etc.) for new items.

        Returns:
            Number of new items found

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement check_for_updates()")

    @abstractmethod
    def create_action_file(self, item_data: Dict[str, Any]) -> Path:
        """Create a task file in the vault's Needs_Action folder.

        This method should be implemented by subclasses to create task files
        with appropriate metadata for their item type.

        Args:
            item_data: Dictionary containing item information

        Returns:
            Path to the created task file

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement create_action_file()")

    def run(self) -> None:
        """Run the watcher in continuous monitoring mode.

        This method runs an infinite loop that checks for updates at the
        configured interval. It should be called by subclasses after
        initialization.
        """
        import time

        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Monitoring with check interval: {self.check_interval} seconds")
        self.logger.info(f"Vault path: {self.vault_path}")

        # Write initial heartbeat immediately on startup
        self._write_heartbeat()

        # Initialize heartbeat tracking
        last_heartbeat = time.time()
        heartbeat_interval = self.heartbeat_interval  # Use configurable interval

        try:
            # Infinite loop - runs until interrupted or fatal error
            while True:
                try:
                    # Call subclass-specific check implementation
                    new_items = self.check_for_updates()

                    # Log successful checks with item count
                    if new_items > 0:
                        self.logger.info(f"Found {new_items} new items")
                        self.log_to_vault(
                            action="check",
                            result="success",
                            details={"items_found": new_items},
                        )
                    else:
                        self.logger.debug("No new items found")

                except Exception as e:
                    # Log check errors but continue running (resilient to transient failures)
                    self.logger.error(f"Error during check: {e}")
                    self.log_to_vault(
                        action="check",
                        result="failure",
                        error_message=str(e),
                    )

                # Write heartbeat log every 60 seconds for health monitoring
                current_time = time.time()
                if current_time - last_heartbeat >= heartbeat_interval:
                    self._write_heartbeat()
                    last_heartbeat = current_time

                # Wait before next check (prevents API rate limiting and excessive CPU usage)
                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            # Graceful shutdown on Ctrl+C
            self.logger.info("Watcher stopped by user")
        except Exception as e:
            # Fatal errors that should stop the watcher
            self.logger.error(f"Fatal error: {e}")
            self.log_to_vault(
                action="error",
                result="failure",
                error_message=str(e),
            )
            raise

    def _write_heartbeat(self) -> None:
        """Write heartbeat file for health monitoring by orchestrator.

        Creates/updates a heartbeat file in /Logs with current timestamp.
        The orchestrator reads these files to detect crashed watchers.
        """
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(exist_ok=True)

        heartbeat_file = log_dir / f"{self.source_type}_watcher_heartbeat.txt"

        try:
            with open(heartbeat_file, "w") as f:
                # Write ISO format timestamp with timezone (+00:00)
                # Don't add "Z" suffix as isoformat() already includes timezone
                f.write(datetime.now(timezone.utc).isoformat())

            self.logger.debug(f"Heartbeat written to {heartbeat_file}")

        except Exception as e:
            self.logger.warning(f"Failed to write heartbeat: {e}")
