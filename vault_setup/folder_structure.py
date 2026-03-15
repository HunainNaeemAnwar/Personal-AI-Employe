"""Folder structure creation for Obsidian vault.

This module provides utilities to create the required folder structure
for the Personal AI Employee Obsidian vault.
"""

from pathlib import Path
from typing import List


def get_vault_folders() -> List[str]:
    """Get list of required vault folders.

    Returns:
        List of folder names to create in the vault
    """
    return [
        "Inbox",
        "Needs_Action",
        "Done",
        "Logs",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Rejected",
    ]


def create_vault_folders(vault_path: Path) -> List[Path]:
    """Create all required folders in the vault.

    Args:
        vault_path: Path to the Obsidian vault

    Returns:
        List of created folder paths

    Raises:
        OSError: If folder creation fails
    """
    folders = get_vault_folders()
    created_folders = []

    for folder_name in folders:
        folder_path = vault_path / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)
        created_folders.append(folder_path)

    return created_folders


def create_watch_directory(vault_path: Path) -> Path:
    """Create the watch directory for file system watcher.

    Creates AI_Employee_Dropbox folder in the same directory as the vault.
    This is where users drop files to be processed by the AI Employee.

    Args:
        vault_path: Path to the Obsidian vault

    Returns:
        Path to created watch directory

    Raises:
        OSError: If directory creation fails
    """
    # Create watch directory in same parent as vault
    parent_dir = vault_path.parent
    watch_dir = parent_dir / "AI_Employee_Dropbox"
    watch_dir.mkdir(parents=True, exist_ok=True)
    
    return watch_dir


def validate_vault_structure(vault_path: Path) -> bool:
    """Validate that all required folders exist in the vault.

    Args:
        vault_path: Path to the Obsidian vault

    Returns:
        True if all folders exist, False otherwise
    """
    folders = get_vault_folders()
    return all((vault_path / folder).exists() for folder in folders)
