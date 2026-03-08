"""File System Watcher implementation for monitoring a directory.

This module implements a watcher that monitors a file system directory for
new files and creates task files in the Obsidian vault.
"""

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from watchers.base_watcher import BaseWatcher


class CustomFileSystemEventHandler(FileSystemEventHandler):
    """Event handler for file system events.

    Attributes:
        watcher: Reference to the FilesystemWatcher instance
        debounce_time: Seconds to wait before processing a file
        pending_files: Dictionary of pending files with their timestamps
    """

    def __init__(self, watcher: "FilesystemWatcher", debounce_time: float = 1.0):
        """Initialize the event handler.

        Args:
            watcher: Reference to the FilesystemWatcher instance
            debounce_time: Seconds to wait before processing (default: 1.0)
        """
        super().__init__()
        self.watcher = watcher
        self.debounce_time = debounce_time
        self.pending_files: Dict[str, float] = {}

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Args:
            event: File creation event
        """
        # Ignore directory creation events
        if event.is_directory:
            return

        # Convert src_path to string to handle both bytes and str types
        file_path = Path(str(event.src_path))

        # Check if file matches extension filter (e.g., only .pdf, .docx)
        if not self.watcher._matches_extension_filter(file_path):
            return

        # Add to pending files with current timestamp (for debouncing)
        # Debouncing prevents processing files that are still being written
        self.pending_files[str(file_path)] = time.time()

    def process_pending_files(self) -> None:
        """Process files that have been pending for debounce_time."""
        current_time = time.time()
        files_to_process = []

        # Find files ready to process (waited at least debounce_time seconds)
        # This prevents processing files that are still being written/modified
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= self.debounce_time:
                files_to_process.append(file_path)
                del self.pending_files[file_path]

        # Process each file that's ready
        for file_path in files_to_process:
            try:
                path = Path(file_path)
                # Check file still exists (might have been deleted during debounce period)
                if path.exists():
                    self.watcher._process_file(path)
            except Exception as e:
                self.watcher.logger.error(f"Error processing file {file_path}: {e}")


class FilesystemWatcher(BaseWatcher):
    """Watcher for monitoring a file system directory.

    Attributes:
        watch_directory: Path to directory being monitored
        file_extensions: List of file extensions to monitor (or "*" for all)
        observer: Watchdog observer instance
        event_handler: File system event handler
    """

    def __init__(
        self,
        vault_path: Path,
        watch_directory: str,
        file_extensions: str = "*",
        check_interval: int = 5,
    ):
        """Initialize File System Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            watch_directory: Path to directory to monitor
            file_extensions: Comma-separated extensions or "*" for all (default: "*")
            check_interval: Seconds between checks (default: 5)

        Raises:
            ValueError: If watch directory doesn't exist
        """
        super().__init__(vault_path, check_interval)

        self.watch_directory = Path(watch_directory)
        if not self.watch_directory.exists():
            raise ValueError(f"Watch directory does not exist: {watch_directory}")
        if not self.watch_directory.is_dir():
            raise ValueError(f"Watch directory is not a directory: {watch_directory}")

        # Parse file extensions from comma-separated string
        # "*" means accept all files
        if file_extensions == "*":
            self.file_extensions = ["*"]
        else:
            # Split by comma and ensure each extension starts with "."
            # Example: "pdf,docx" becomes [".pdf", ".docx"]
            self.file_extensions = [
                ext.strip() if ext.startswith(".") else f".{ext.strip()}"
                for ext in file_extensions.split(",")
            ]

        # Setup watchdog observer
        # Create event handler for file system events
        self.event_handler = CustomFileSystemEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, str(self.watch_directory), recursive=False)

        self.logger.info(f"File System Watcher initialized")
        self.logger.info(f"Watching directory: {self.watch_directory}")
        self.logger.info(f"File extensions: {', '.join(self.file_extensions)}")

    def _matches_extension_filter(self, file_path: Path) -> bool:
        """Check if file matches extension filter.

        Args:
            file_path: Path to file

        Returns:
            True if file matches filter, False otherwise
        """
        if "*" in self.file_extensions:
            return True

        return file_path.suffix.lower() in [ext.lower() for ext in self.file_extensions]

    def _slugify(self, text: str) -> str:
        """Convert text to URL-safe slug.

        Args:
            text: Text to slugify

        Returns:
            Slugified text
        """
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text[:50]  # Limit length

    def _determine_priority(self, file_path: Path) -> str:
        """Determine file priority based on name and extension.

        Args:
            file_path: Path to file

        Returns:
            Priority level: high, medium, or low
        """
        filename_lower = file_path.name.lower()
        urgent_keywords = ["urgent", "asap", "deadline", "critical", "important"]

        if any(keyword in filename_lower for keyword in urgent_keywords):
            return "high"

        # High priority for certain file types
        high_priority_extensions = [".pdf", ".docx", ".xlsx"]
        if file_path.suffix.lower() in high_priority_extensions:
            return "medium"

        return "low"

    def _process_file(self, file_path: Path) -> None:
        """Process a new file and create task file.

        Args:
            file_path: Path to the new file
        """
        file_id = str(file_path)

        # Skip if already processed
        if self.is_processed(file_id):
            return

        try:
            # Get file metadata
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Determine priority
            priority = self._determine_priority(file_path)

            # Create task file
            item_data = {
                "filename": file_path.name,
                "path": str(file_path),
                "size": file_size,
                "extension": file_path.suffix,
                "timestamp": timestamp,
                "priority": priority,
            }

            self.create_action_file(item_data)
            self.mark_processed(file_id)

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            self.log_to_vault(
                action="create_task",
                result="failure",
                error_message=str(e),
                details={"file_path": str(file_path)},
            )

    def check_for_updates(self) -> int:
        """Check for pending files to process.

        This method processes files that have been pending for the debounce time.

        Returns:
            Number of files processed
        """
        try:
            # Count pending files before processing
            initial_count = len(self.event_handler.pending_files)

            # Process files that have waited long enough (debounce period elapsed)
            self.event_handler.process_pending_files()

            # Calculate how many files were actually processed
            processed_count = initial_count - len(self.event_handler.pending_files)

            return processed_count

        except Exception as e:
            self.logger.error(f"Error checking for updates: {e}")
            raise

    def create_action_file(self, item_data: Dict[str, Any]) -> Path:
        """Create a task file for a dropped file in the vault's Needs_Action folder.

        Args:
            item_data: Dictionary containing file information

        Returns:
            Path to the created task file
        """
        try:
            filename = item_data["filename"]
            file_path = item_data["path"]
            file_size = item_data["size"]
            file_extension = item_data["extension"]
            timestamp = item_data["timestamp"]
            priority = item_data["priority"]

            # Create task filename
            slug = self._slugify(Path(filename).stem)
            task_filename = (
                f"FILE_DROP_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}Z_{slug}.md"
            )

            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"

            # Create task file content
            content = f"""---
type: file_drop
source: {file_path}
timestamp: {timestamp}
priority: {priority}
status: pending
subject: {filename}
---

## File Details

**Filename**: {filename}
**Location**: {file_path}
**Size**: {size_str}
**Type**: {file_extension}
**Detected**: {timestamp}

## Description

New file detected in monitored directory. Review and process as needed.

## Metadata

- **File Size**: {file_size} bytes
- **Extension**: {file_extension}
- **Priority**: {priority}

## Suggested Actions

- [ ] Review file contents
- [ ] Determine required processing
- [ ] Extract relevant information
- [ ] Create execution plan if needed
- [ ] Move to /Done when finished

## Notes

[Add any additional context or notes here]
"""

            # Write to Needs_Action folder
            needs_action_dir = self.vault_path / "Needs_Action"
            needs_action_dir.mkdir(exist_ok=True)

            task_file = needs_action_dir / task_filename
            task_file.write_text(content)

            self.logger.info(f"Created task file: {task_filename}")
            self.log_to_vault(
                action="create_task",
                result="success",
                details={
                    "filename": task_filename,
                    "original_file": filename,
                    "file_size": file_size,
                    "priority": priority,
                },
            )

            return task_file

        except Exception as e:
            self.logger.error(f"Error creating task file: {e}")
            self.log_to_vault(
                action="create_task",
                result="failure",
                error_message=str(e),
            )
            raise

    def run(self) -> None:
        """Run the watcher in continuous monitoring mode.

        This method starts the watchdog observer and runs the check loop.
        """
        self.logger.info(f"Starting {self.__class__.__name__}")
        self.logger.info(f"Monitoring directory: {self.watch_directory}")
        self.logger.info(f"Check interval: {self.check_interval} seconds")

        try:
            # Start observer
            self.observer.start()
            self.logger.info("Observer started")

            # Run check loop
            super().run()

        except KeyboardInterrupt:
            self.logger.info("Watcher stopped by user")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise
        finally:
            # Stop observer
            self.observer.stop()
            self.observer.join()
            self.logger.info("Observer stopped")
