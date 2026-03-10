"""
State Manager for Silver Tier - Persistent state tracking to prevent duplicate task creation.

This module provides SQLite-based state persistence for tracking processed items
across watcher restarts. It ensures that emails, files, and LinkedIn messages are
only processed once, even if the system is restarted.
"""

import sqlite3
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class StateManager:
    """
    Manages persistent state for watchers using SQLite database.

    Responsibilities:
    - Track processed items (emails, files, LinkedIn messages)
    - Prevent duplicate task creation across restarts
    - Provide ACID transactions for concurrent watcher access
    - Handle database corruption and recovery
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = "state.db"):
        """
        Initialize StateManager with SQLite database.

        Args:
            db_path: Path to SQLite database file (default: state.db)
        """
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._init_database()

    def _init_database(self):
        """Initialize database schema if not exists."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Create schema_version table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Check current schema version
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                current_version = result[0] if result else 0

                if current_version < self.SCHEMA_VERSION:
                    self._apply_schema_migrations(conn, current_version)

                conn.commit()
                self.logger.info(f"Database initialized at {self.db_path} (schema v{self.SCHEMA_VERSION})")

        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def _apply_schema_migrations(self, conn: sqlite3.Connection, from_version: int):
        """Apply schema migrations from current version to latest."""
        cursor = conn.cursor()

        if from_version < 1:
            # Migration to version 1: Create processed_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL CHECK(source IN ('gmail', 'filesystem', 'linkedin')),
                    source_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'processed', 'failed')),
                    task_file_path TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(source, source_id)
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_source_item
                ON processed_items(source, source_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON processed_items(timestamp)
            """)

            # Record schema version
            cursor.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (1,)
            )

            self.logger.info("Applied schema migration to version 1")

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()

    def check_processed(self, source: str, source_id: str) -> bool:
        """
        Check if an item has already been processed.

        Args:
            source: Source type ('gmail', 'filesystem', 'linkedin')
            source_id: Source-specific identifier

        Returns:
            True if item exists in database, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM processed_items WHERE source = ? AND source_id = ?",
                    (source, source_id)
                )
                result = cursor.fetchone()
                return result is not None

        except sqlite3.Error as e:
            self.logger.error(f"Failed to check processed status: {e}")
            return False  # Fail open to avoid blocking new items

    def insert_item(
        self,
        source: str,
        source_id: str,
        timestamp: Optional[str] = None,
        status: str = "pending",
        task_file_path: Optional[str] = None
    ) -> Optional[int]:
        """
        Insert a new processed item into the database.

        Args:
            source: Source type ('gmail', 'filesystem', 'linkedin')
            source_id: Source-specific identifier
            timestamp: ISO 8601 timestamp (defaults to current time)
            status: Processing status ('pending', 'processed', 'failed')
            task_file_path: Relative path to task file in vault

        Returns:
            Inserted row ID on success, None on failure
        """
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat() + "Z"

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO processed_items (source, source_id, timestamp, status, task_file_path)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (source, source_id, timestamp, status, task_file_path)
                )
                conn.commit()
                row_id = cursor.lastrowid
                self.logger.info(f"Inserted item: {source}/{source_id} (ID: {row_id})")
                return row_id

        except sqlite3.IntegrityError:
            self.logger.warning(f"Item already exists: {source}/{source_id}")
            return None

        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert item: {e}")
            return None

    def update_item(
        self,
        source: str,
        source_id: str,
        status: Optional[str] = None,
        task_file_path: Optional[str] = None
    ) -> bool:
        """
        Update an existing processed item.

        Args:
            source: Source type ('gmail', 'filesystem', 'linkedin')
            source_id: Source-specific identifier
            status: New processing status (optional)
            task_file_path: New task file path (optional)

        Returns:
            True on success, False on failure
        """
        if status is None and task_file_path is None:
            self.logger.warning("No fields to update")
            return False

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Build dynamic UPDATE query
                updates = []
                params = []

                if status is not None:
                    updates.append("status = ?")
                    params.append(status)

                if task_file_path is not None:
                    updates.append("task_file_path = ?")
                    params.append(task_file_path)

                params.extend([source, source_id])

                query = f"""
                    UPDATE processed_items
                    SET {', '.join(updates)}
                    WHERE source = ? AND source_id = ?
                """

                cursor.execute(query, params)
                conn.commit()

                if cursor.rowcount > 0:
                    self.logger.info(f"Updated item: {source}/{source_id}")
                    return True
                else:
                    self.logger.warning(f"Item not found for update: {source}/{source_id}")
                    return False

        except sqlite3.Error as e:
            self.logger.error(f"Failed to update item: {e}")
            return False

    def get_item(self, source: str, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a processed item by source and source_id.

        Args:
            source: Source type ('gmail', 'filesystem', 'linkedin')
            source_id: Source-specific identifier

        Returns:
            Dictionary with item data, or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM processed_items WHERE source = ? AND source_id = ?",
                    (source, source_id)
                )
                row = cursor.fetchone()

                if row:
                    return dict(row)
                return None

        except sqlite3.Error as e:
            self.logger.error(f"Failed to get item: {e}")
            return None

    def get_items_by_status(self, status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve items by processing status.

        Args:
            status: Processing status ('pending', 'processed', 'failed')
            limit: Maximum number of items to return

        Returns:
            List of item dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM processed_items WHERE status = ? ORDER BY timestamp DESC LIMIT ?",
                    (status, limit)
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except sqlite3.Error as e:
            self.logger.error(f"Failed to get items by status: {e}")
            return []

    def health_check(self) -> bool:
        """
        Verify database is accessible and schema is valid.

        Returns:
            True if database is healthy, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Check schema_version table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
                )
                if not cursor.fetchone():
                    self.logger.error("schema_version table not found")
                    return False

                # Check processed_items table exists
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
                )
                if not cursor.fetchone():
                    self.logger.error("processed_items table not found")
                    return False

                # Verify schema version
                cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
                result = cursor.fetchone()
                if not result or result[0] != self.SCHEMA_VERSION:
                    self.logger.error(f"Schema version mismatch: expected {self.SCHEMA_VERSION}, got {result[0] if result else 'None'}")
                    return False

                return True

        except sqlite3.Error as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def backup_database(self, backup_path: Optional[str] = None) -> bool:
        """
        Create a backup of the state database.

        Args:
            backup_path: Optional path for backup file (default: state_backup_YYYYMMDD_HHMMSS.db)

        Returns:
            True on success, False on failure
        """
        if backup_path is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            backup_path = f"state_backup_{timestamp}.db"

        try:
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            # Use SQLite backup API for safe backup
            with self._get_connection() as source_conn:
                backup_conn = sqlite3.connect(str(backup_file))
                try:
                    source_conn.backup(backup_conn)
                    self.logger.info(f"Database backed up to {backup_path}")
                    return True
                finally:
                    backup_conn.close()

        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False

    def rebuild_from_vault(self, vault_path: Path) -> int:
        """
        Rebuild state database from vault task files.

        Scans /Needs_Action, /Done, and /Rejected folders to reconstruct
        the processed items state. Useful for recovery from corruption.

        Args:
            vault_path: Path to Obsidian vault

        Returns:
            Number of items rebuilt
        """
        self.logger.info("Rebuilding state database from vault files...")
        rebuilt_count = 0

        try:
            # Folders to scan
            folders = ["Needs_Action", "Done", "Rejected"]

            for folder_name in folders:
                folder_path = vault_path / folder_name
                if not folder_path.exists():
                    continue

                # Scan all markdown files
                for task_file in folder_path.glob("*.md"):
                    try:
                        # Read file content
                        content = task_file.read_text()

                        # Extract metadata from YAML frontmatter
                        if content.startswith("---"):
                            # Simple YAML parsing (extract type and source)
                            lines = content.split("\n")
                            file_type = None
                            source = None

                            for line in lines[1:]:
                                if line.strip() == "---":
                                    break
                                if line.startswith("type:"):
                                    file_type = line.split(":", 1)[1].strip()
                                if line.startswith("source:"):
                                    source = line.split(":", 1)[1].strip()

                            # Determine source type and ID
                            if file_type == "email":
                                source_type = "gmail"
                                # Extract Gmail message ID from content
                                for line in lines:
                                    if "Gmail Message ID" in line:
                                        source_id = line.split(":", 1)[1].strip()
                                        break
                                else:
                                    source_id = task_file.stem  # Fallback to filename

                            elif file_type == "file_drop":
                                source_type = "filesystem"
                                source_id = source or str(task_file)

                            elif file_type == "linkedin_message":
                                source_type = "linkedin"
                                # Extract conversation ID from content
                                for line in lines:
                                    if "Conversation ID" in line:
                                        source_id = line.split(":", 1)[1].strip()
                                        break
                                else:
                                    source_id = task_file.stem

                            else:
                                continue  # Skip unknown types

                            # Insert into database (ignore duplicates)
                            relative_path = task_file.relative_to(vault_path)
                            status = "processed" if folder_name in ["Done", "Rejected"] else "pending"

                            row_id = self.insert_item(
                                source=source_type,
                                source_id=source_id,
                                status=status,
                                task_file_path=str(relative_path)
                            )

                            if row_id:
                                rebuilt_count += 1

                    except Exception as e:
                        self.logger.warning(f"Failed to process {task_file}: {e}")
                        continue

            self.logger.info(f"Rebuilt {rebuilt_count} items from vault")
            return rebuilt_count

        except Exception as e:
            self.logger.error(f"Failed to rebuild from vault: {e}")
            return 0

    def detect_corruption(self) -> bool:
        """
        Detect database corruption.

        Returns:
            True if corruption detected, False if database is healthy
        """
        try:
            # Run integrity check
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()

                if result and result[0] == "ok":
                    return False
                else:
                    self.logger.error(f"Database corruption detected: {result}")
                    return True

        except sqlite3.Error as e:
            self.logger.error(f"Corruption check failed: {e}")
            return True

    def recover_from_corruption(self, vault_path: Path) -> bool:
        """
        Automatically recover from database corruption.

        Creates backup of corrupted database, deletes it, reinitializes schema,
        and rebuilds state from vault files.

        Args:
            vault_path: Path to Obsidian vault

        Returns:
            True on successful recovery, False on failure
        """
        self.logger.warning("Attempting automatic recovery from corruption...")

        try:
            # Backup corrupted database
            corrupted_backup = f"state_corrupted_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.db"
            if self.db_path.exists():
                import shutil
                shutil.copy(self.db_path, corrupted_backup)
                self.logger.info(f"Backed up corrupted database to {corrupted_backup}")

            # Delete corrupted database
            if self.db_path.exists():
                self.db_path.unlink()
                self.logger.info("Deleted corrupted database")

            # Reinitialize database
            self._init_database()
            self.logger.info("Reinitialized database schema")

            # Rebuild from vault
            rebuilt_count = self.rebuild_from_vault(vault_path)
            self.logger.info(f"Rebuilt {rebuilt_count} items from vault")

            # Verify recovery
            if self.health_check():
                self.logger.info("Recovery successful - database is healthy")
                return True
            else:
                self.logger.error("Recovery failed - database still unhealthy")
                return False

        except Exception as e:
            self.logger.error(f"Recovery failed: {e}")
            return False
