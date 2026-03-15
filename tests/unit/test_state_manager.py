"""
Unit tests for StateManager - State persistence and database operations.

Tests cover:
- Database initialization and schema creation
- Item insertion and retrieval
- Duplicate prevention
- Status updates
- Health checks
- Backup and recovery
- Corruption detection
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
from watchers.state_manager import StateManager


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def state_manager(temp_db):
    """Create StateManager instance with temporary database."""
    return StateManager(db_path=temp_db)


@pytest.fixture
def temp_vault():
    """Create temporary vault directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create vault structure
        (vault_path / "Needs_Action").mkdir()
        (vault_path / "Done").mkdir()
        (vault_path / "Rejected").mkdir()
        yield vault_path


class TestDatabaseInitialization:
    """Test database initialization and schema creation."""

    def test_database_created(self, state_manager, temp_db):
        """Test that database file is created."""
        assert Path(temp_db).exists()

    def test_schema_version_table_exists(self, state_manager):
        """Test that schema_version table is created."""
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_version'"
            )
            assert cursor.fetchone() is not None

    def test_processed_items_table_exists(self, state_manager):
        """Test that processed_items table is created."""
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='processed_items'"
            )
            assert cursor.fetchone() is not None

    def test_schema_version_correct(self, state_manager):
        """Test that schema version is set correctly."""
        with state_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            assert result[0] == StateManager.SCHEMA_VERSION


class TestItemInsertion:
    """Test item insertion operations."""

    def test_insert_gmail_item(self, state_manager):
        """Test inserting a Gmail item."""
        row_id = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            timestamp='2026-03-09T14:30:00Z',
            status='pending',
            task_file_path='Needs_Action/EMAIL_20260309T143000Z_test.md'
        )
        assert row_id is not None
        assert row_id > 0

    def test_insert_filesystem_item(self, state_manager):
        """Test inserting a file system item."""
        row_id = state_manager.insert_item(
            source='filesystem',
            source_id='/path/to/file.pdf',
            timestamp='2026-03-09T14:30:00Z',
            status='pending',
            task_file_path='Needs_Action/FILE_DROP_20260309T143000Z_file.md'
        )
        assert row_id is not None
        assert row_id > 0

    def test_insert_linkedin_item(self, state_manager):
        """Test inserting a LinkedIn item."""
        row_id = state_manager.insert_item(
            source='linkedin',
            source_id='conv_67890',
            timestamp='2026-03-09T14:30:00Z',
            status='pending',
            task_file_path='Needs_Action/LINKEDIN_MSG_20260309T143000Z_test.md'
        )
        assert row_id is not None
        assert row_id > 0

    def test_insert_duplicate_item_fails(self, state_manager):
        """Test that inserting duplicate item returns None."""
        # Insert first item
        row_id1 = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            timestamp='2026-03-09T14:30:00Z',
            status='pending'
        )
        assert row_id1 is not None

        # Try to insert duplicate
        row_id2 = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            timestamp='2026-03-09T14:30:00Z',
            status='pending'
        )
        assert row_id2 is None

    def test_insert_with_default_timestamp(self, state_manager):
        """Test inserting item with default timestamp."""
        row_id = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )
        assert row_id is not None

        # Verify timestamp was set
        item = state_manager.get_item('gmail', 'msg_12345')
        assert item['timestamp'] is not None


class TestItemRetrieval:
    """Test item retrieval operations."""

    def test_check_processed_existing_item(self, state_manager):
        """Test checking if existing item is processed."""
        state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='processed'
        )
        assert state_manager.check_processed('gmail', 'msg_12345') is True

    def test_check_processed_nonexistent_item(self, state_manager):
        """Test checking if nonexistent item is processed."""
        assert state_manager.check_processed('gmail', 'msg_99999') is False

    def test_get_item_existing(self, state_manager):
        """Test retrieving existing item."""
        state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            timestamp='2026-03-09T14:30:00Z',
            status='pending',
            task_file_path='Needs_Action/EMAIL_20260309T143000Z_test.md'
        )

        item = state_manager.get_item('gmail', 'msg_12345')
        assert item is not None
        assert item['source'] == 'gmail'
        assert item['source_id'] == 'msg_12345'
        assert item['status'] == 'pending'
        assert item['task_file_path'] == 'Needs_Action/EMAIL_20260309T143000Z_test.md'

    def test_get_item_nonexistent(self, state_manager):
        """Test retrieving nonexistent item."""
        item = state_manager.get_item('gmail', 'msg_99999')
        assert item is None

    def test_get_items_by_status(self, state_manager):
        """Test retrieving items by status."""
        # Insert items with different statuses
        state_manager.insert_item(source='gmail', source_id='msg_1', status='pending')
        state_manager.insert_item(source='gmail', source_id='msg_2', status='processed')
        state_manager.insert_item(source='gmail', source_id='msg_3', status='pending')
        state_manager.insert_item(source='gmail', source_id='msg_4', status='failed')

        # Get pending items
        pending = state_manager.get_items_by_status('pending')
        assert len(pending) == 2
        assert all(item['status'] == 'pending' for item in pending)

        # Get processed items
        processed = state_manager.get_items_by_status('processed')
        assert len(processed) == 1
        assert processed[0]['status'] == 'processed'


class TestItemUpdate:
    """Test item update operations."""

    def test_update_status(self, state_manager):
        """Test updating item status."""
        state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )

        success = state_manager.update_item(
            source='gmail',
            source_id='msg_12345',
            status='processed'
        )
        assert success is True

        item = state_manager.get_item('gmail', 'msg_12345')
        assert item['status'] == 'processed'

    def test_update_task_file_path(self, state_manager):
        """Test updating task file path."""
        state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )

        success = state_manager.update_item(
            source='gmail',
            source_id='msg_12345',
            task_file_path='Done/EMAIL_20260309T143000Z_test.md'
        )
        assert success is True

        item = state_manager.get_item('gmail', 'msg_12345')
        assert item['task_file_path'] == 'Done/EMAIL_20260309T143000Z_test.md'

    def test_update_both_fields(self, state_manager):
        """Test updating both status and task file path."""
        state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )

        success = state_manager.update_item(
            source='gmail',
            source_id='msg_12345',
            status='processed',
            task_file_path='Done/EMAIL_20260309T143000Z_test.md'
        )
        assert success is True

        item = state_manager.get_item('gmail', 'msg_12345')
        assert item['status'] == 'processed'
        assert item['task_file_path'] == 'Done/EMAIL_20260309T143000Z_test.md'

    def test_update_nonexistent_item(self, state_manager):
        """Test updating nonexistent item."""
        success = state_manager.update_item(
            source='gmail',
            source_id='msg_99999',
            status='processed'
        )
        assert success is False


class TestHealthCheck:
    """Test database health check operations."""

    def test_health_check_healthy_database(self, state_manager):
        """Test health check on healthy database."""
        assert state_manager.health_check() is True

    def test_health_check_missing_table(self, state_manager, temp_db):
        """Test health check with missing table."""
        # Drop processed_items table
        with state_manager._get_connection() as conn:
            conn.execute("DROP TABLE processed_items")
            conn.commit()

        assert state_manager.health_check() is False

    def test_detect_corruption_healthy(self, state_manager):
        """Test corruption detection on healthy database."""
        assert state_manager.detect_corruption() is False


class TestBackupAndRecovery:
    """Test backup and recovery operations."""

    def test_backup_database(self, state_manager, temp_db):
        """Test database backup."""
        # Insert some data
        state_manager.insert_item(source='gmail', source_id='msg_1', status='pending')
        state_manager.insert_item(source='gmail', source_id='msg_2', status='processed')

        # Create backup
        backup_path = temp_db + '.backup'
        success = state_manager.backup_database(backup_path)
        assert success is True
        assert Path(backup_path).exists()

        # Verify backup contains data
        backup_conn = sqlite3.connect(backup_path)
        cursor = backup_conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM processed_items")
        count = cursor.fetchone()[0]
        backup_conn.close()
        assert count == 2

        # Cleanup
        Path(backup_path).unlink()

    def test_rebuild_from_vault(self, state_manager, temp_vault):
        """Test rebuilding database from vault files."""
        # Create task files in vault
        email_task = temp_vault / "Done" / "EMAIL_20260309T143000Z_test.md"
        email_task.write_text("""---
type: email
source: gmail
---

# Email Task

Gmail Message ID: msg_12345
""")

        file_task = temp_vault / "Needs_Action" / "FILE_DROP_20260309T143000Z_test.md"
        file_task.write_text("""---
type: file_drop
source: /path/to/file.pdf
---

# File Drop Task
""")

        # Rebuild database
        count = state_manager.rebuild_from_vault(temp_vault)
        assert count == 2

        # Verify items were inserted
        assert state_manager.check_processed('gmail', 'msg_12345') is True
        assert state_manager.check_processed('filesystem', '/path/to/file.pdf') is True

    def test_recover_from_corruption(self, state_manager, temp_vault, temp_db):
        """Test automatic recovery from corruption."""
        # Create task files in vault
        email_task = temp_vault / "Done" / "EMAIL_20260309T143000Z_test.md"
        email_task.write_text("""---
type: email
source: gmail
---

# Email Task

Gmail Message ID: msg_12345
""")

        # Simulate corruption by deleting database
        Path(temp_db).unlink()

        # Attempt recovery
        success = state_manager.recover_from_corruption(temp_vault)
        assert success is True

        # Verify database is healthy
        assert state_manager.health_check() is True

        # Verify data was recovered
        assert state_manager.check_processed('gmail', 'msg_12345') is True


class TestConcurrency:
    """Test concurrent access to database."""

    def test_multiple_inserts_same_item(self, state_manager):
        """Test multiple concurrent inserts of same item."""
        # First insert should succeed
        row_id1 = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )
        assert row_id1 is not None

        # Second insert should fail (duplicate)
        row_id2 = state_manager.insert_item(
            source='gmail',
            source_id='msg_12345',
            status='pending'
        )
        assert row_id2 is None

        # Verify only one item exists
        items = state_manager.get_items_by_status('pending')
        assert len([i for i in items if i['source_id'] == 'msg_12345']) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
