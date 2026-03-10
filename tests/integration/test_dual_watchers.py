"""
Integration tests for Dual Watchers - Concurrent watcher operation with orchestrator.

Tests cover:
- Orchestrator starting multiple watchers
- Concurrent task detection across watchers
- State database coordination
- Heartbeat monitoring
- Automatic watcher restart
- Graceful shutdown
"""

import pytest
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
import tempfile
import os


@pytest.fixture
def temp_vault():
    """Create temporary vault for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_path = Path(tmpdir)
        # Create vault structure
        folders = ["Needs_Action", "Done", "Rejected", "Pending_Approval", "Approved", "Logs", "Plans", "Briefings"]
        for folder in folders:
            (vault_path / folder).mkdir()
        yield vault_path


@pytest.fixture
def temp_watch_dir():
    """Create temporary watch directory for file system watcher."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_env(temp_vault, temp_watch_dir):
    """Create test environment configuration."""
    env = os.environ.copy()
    env['VAULT_PATH'] = str(temp_vault)
    env['WATCH_DIRECTORY'] = str(temp_watch_dir)
    env['WATCHER_TYPE'] = 'orchestrator'
    env['ORCHESTRATOR_WATCHERS'] = 'filesystem'  # Only filesystem for testing
    env['ORCHESTRATOR_HEALTH_CHECK_INTERVAL'] = '5'
    env['ORCHESTRATOR_RESTART_DELAY'] = '2'
    env['FILESYSTEM_POLLING_INTERVAL'] = '2'
    env['WATCHER_HEARTBEAT_INTERVAL'] = '2'  # Short interval for testing
    env['STATE_DB_PATH'] = str(temp_vault / 'test_state.db')
    return env


class TestOrchestratorStartup:
    """Test orchestrator startup and watcher initialization."""

    def test_orchestrator_starts_watchers(self, test_env):
        """Test that orchestrator starts configured watchers."""
        # Start orchestrator
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            # Wait for startup
            time.sleep(3)

            # Check orchestrator is running
            assert proc.poll() is None

            # Check heartbeat file exists
            vault_path = Path(test_env['VAULT_PATH'])
            heartbeat_file = vault_path / "Logs" / "filesystem_watcher_heartbeat.txt"

            # Wait for heartbeat file
            for _ in range(10):
                if heartbeat_file.exists():
                    break
                time.sleep(1)

            assert heartbeat_file.exists()

        finally:
            # Cleanup
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)

    def test_orchestrator_creates_log_files(self, test_env):
        """Test that orchestrator creates log files for watchers."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            vault_path = Path(test_env['VAULT_PATH'])
            log_file = vault_path / "Logs" / "filesystem_watcher.log"

            # Wait for log file
            for _ in range(10):
                if log_file.exists():
                    break
                time.sleep(1)

            assert log_file.exists()

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)


class TestConcurrentTaskDetection:
    """Test concurrent task detection across multiple watchers."""

    def test_filesystem_watcher_detects_file(self, test_env):
        """Test that file system watcher detects dropped files."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Drop a file
            watch_dir = Path(test_env['WATCH_DIRECTORY'])
            test_file = watch_dir / "test_document.txt"
            test_file.write_text("Test content")

            # Wait for detection
            time.sleep(5)

            # Check task file created
            vault_path = Path(test_env['VAULT_PATH'])
            needs_action = vault_path / "Needs_Action"
            task_files = list(needs_action.glob("FILE_DROP_*.md"))

            assert len(task_files) > 0

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)

    def test_no_duplicate_tasks_after_restart(self, test_env):
        """Test that no duplicate tasks are created after watcher restart."""
        # Start orchestrator
        proc1 = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Drop a file
            watch_dir = Path(test_env['WATCH_DIRECTORY'])
            test_file = watch_dir / "test_document.txt"
            test_file.write_text("Test content")

            # Wait for detection
            time.sleep(5)

            # Count task files
            vault_path = Path(test_env['VAULT_PATH'])
            needs_action = vault_path / "Needs_Action"
            task_files_before = list(needs_action.glob("FILE_DROP_*.md"))
            count_before = len(task_files_before)

            # Stop orchestrator
            proc1.send_signal(signal.SIGTERM)
            proc1.wait(timeout=5)

            # Restart orchestrator
            proc2 = subprocess.Popen(
                ['python', '-m', 'watchers.orchestrator'],
                env=test_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            try:
                time.sleep(5)

                # Count task files again
                task_files_after = list(needs_action.glob("FILE_DROP_*.md"))
                count_after = len(task_files_after)

                # Should be same count (no duplicates)
                assert count_after == count_before

            finally:
                proc2.send_signal(signal.SIGTERM)
                proc2.wait(timeout=5)

        finally:
            if proc1.poll() is None:
                proc1.send_signal(signal.SIGTERM)
                proc1.wait(timeout=5)


class TestStateDatabaseCoordination:
    """Test state database coordination across watchers."""

    def test_state_database_created(self, test_env):
        """Test that state database is created."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Check state database exists
            state_db = Path(test_env['STATE_DB_PATH'])
            assert state_db.exists()

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)

    def test_processed_items_tracked(self, test_env):
        """Test that processed items are tracked in state database."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Drop a file
            watch_dir = Path(test_env['WATCH_DIRECTORY'])
            test_file = watch_dir / "test_document.txt"
            test_file.write_text("Test content")

            # Wait for detection
            time.sleep(5)

            # Check state database
            from watchers.state_manager import StateManager
            state_manager = StateManager(db_path=test_env['STATE_DB_PATH'])

            # Should have at least one processed item
            items = state_manager.get_items_by_status('pending', limit=100)
            assert len(items) > 0

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)


class TestHeartbeatMonitoring:
    """Test heartbeat monitoring and health checks."""

    def test_heartbeat_file_updated(self, test_env):
        """Test that heartbeat file is updated regularly."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            vault_path = Path(test_env['VAULT_PATH'])
            heartbeat_file = vault_path / "Logs" / "filesystem_watcher_heartbeat.txt"

            # Wait for heartbeat file
            for _ in range(10):
                if heartbeat_file.exists():
                    break
                time.sleep(1)

            # Read initial timestamp
            timestamp1 = heartbeat_file.read_text().strip()

            # Wait for update
            time.sleep(3)

            # Read updated timestamp
            timestamp2 = heartbeat_file.read_text().strip()

            # Timestamps should be different
            assert timestamp1 != timestamp2

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)


class TestGracefulShutdown:
    """Test graceful shutdown of orchestrator and watchers."""

    def test_sigterm_shutdown(self, test_env):
        """Test that SIGTERM triggers graceful shutdown."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Send SIGTERM
            proc.send_signal(signal.SIGTERM)

            # Wait for shutdown
            return_code = proc.wait(timeout=10)

            # Should exit cleanly
            assert return_code == 0

        except subprocess.TimeoutExpired:
            proc.kill()
            pytest.fail("Orchestrator did not shut down gracefully")

    def test_sigint_shutdown(self, test_env):
        """Test that SIGINT (Ctrl+C) triggers graceful shutdown."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Send SIGINT
            proc.send_signal(signal.SIGINT)

            # Wait for shutdown
            return_code = proc.wait(timeout=10)

            # Should exit cleanly
            assert return_code == 0

        except subprocess.TimeoutExpired:
            proc.kill()
            pytest.fail("Orchestrator did not shut down gracefully")


class TestPerformance:
    """Test performance benchmarks for dual watchers."""

    def test_file_detection_latency(self, test_env):
        """Test that file detection latency is under 5 seconds."""
        proc = subprocess.Popen(
            ['python', '-m', 'watchers.orchestrator'],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        try:
            time.sleep(3)

            # Drop a file and measure detection time
            watch_dir = Path(test_env['WATCH_DIRECTORY'])
            test_file = watch_dir / "test_document.txt"

            start_time = time.time()
            test_file.write_text("Test content")

            # Wait for task file
            vault_path = Path(test_env['VAULT_PATH'])
            needs_action = vault_path / "Needs_Action"

            detected = False
            for _ in range(50):  # 5 seconds max
                task_files = list(needs_action.glob("FILE_DROP_*.md"))
                if len(task_files) > 0:
                    detected = True
                    break
                time.sleep(0.1)

            end_time = time.time()
            latency = end_time - start_time

            assert detected, "File not detected"
            assert latency < 5.0, f"Detection latency {latency:.2f}s exceeds 5s threshold"

        finally:
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=5)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
