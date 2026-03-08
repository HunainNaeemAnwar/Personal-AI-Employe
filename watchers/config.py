"""Configuration loader for watcher scripts.

Loads environment variables from .env file and provides configuration
for Gmail and File System watchers.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class WatcherConfig:
    """Configuration for watcher scripts."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        # Vault configuration
        self.vault_path = self._get_required("VAULT_PATH")

        # Watcher type selection
        self.watcher_type = self._get_required("WATCHER_TYPE")

        # Gmail Watcher configuration
        self.gmail_credentials_path = os.getenv("GMAIL_CREDENTIALS_PATH")
        self.gmail_token_path = os.getenv("GMAIL_TOKEN_PATH")
        self.gmail_query = os.getenv("GMAIL_QUERY", "is:unread is:important")

        # File System Watcher configuration
        self.watch_directory = os.getenv("WATCH_DIRECTORY")
        self.file_extensions = os.getenv("FILE_EXTENSIONS", "*")

    def _get_required(self, key: str) -> str:
        """Get required environment variable or raise error.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ValueError: If environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} is not set")
        return value

    def validate_gmail_config(self) -> None:
        """Validate Gmail Watcher configuration.

        Raises:
            ValueError: If Gmail configuration is invalid
        """
        if not self.gmail_credentials_path:
            raise ValueError("GMAIL_CREDENTIALS_PATH is required for Gmail Watcher")
        if not self.gmail_token_path:
            raise ValueError("GMAIL_TOKEN_PATH is required for Gmail Watcher")

        credentials_path = Path(self.gmail_credentials_path)
        if not credentials_path.exists():
            raise ValueError(f"Gmail credentials file not found: {credentials_path}")

    def validate_filesystem_config(self) -> None:
        """Validate File System Watcher configuration.

        Raises:
            ValueError: If File System configuration is invalid
        """
        if not self.watch_directory:
            raise ValueError("WATCH_DIRECTORY is required for File System Watcher")

        watch_dir = Path(self.watch_directory)
        if not watch_dir.exists():
            raise ValueError(f"Watch directory not found: {watch_dir}")
        if not watch_dir.is_dir():
            raise ValueError(f"Watch directory is not a directory: {watch_dir}")

    def validate(self) -> None:
        """Validate configuration based on watcher type.

        Raises:
            ValueError: If configuration is invalid
        """
        vault = Path(self.vault_path)
        if not vault.exists():
            raise ValueError(f"Vault path not found: {vault}")
        if not vault.is_dir():
            raise ValueError(f"Vault path is not a directory: {vault}")

        if self.watcher_type == "gmail":
            self.validate_gmail_config()
        elif self.watcher_type == "filesystem":
            self.validate_filesystem_config()
        else:
            raise ValueError(
                f"Invalid WATCHER_TYPE: {self.watcher_type}. Must be 'gmail' or 'filesystem'"
            )


def load_config() -> WatcherConfig:
    """Load and validate watcher configuration.

    Returns:
        WatcherConfig instance

    Raises:
        ValueError: If configuration is invalid
    """
    config = WatcherConfig()
    config.validate()
    return config
