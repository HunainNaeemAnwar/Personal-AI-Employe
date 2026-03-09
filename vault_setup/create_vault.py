#!/usr/bin/env python3
"""Create and initialize an Obsidian vault for Personal AI Employee.

This script creates the complete vault structure with all required folders
and configuration files.

Usage:
    python vault_setup/create_vault.py --path ~/AI_Employee_Vault
"""

import argparse
import sys
from pathlib import Path
from shutil import copy2
from typing import List, Tuple

from vault_setup.folder_structure import create_vault_folders, validate_vault_structure


def validate_vault_path(vault_path: Path) -> Tuple[bool, str]:
    """Validate that the vault path is suitable for creation.

    Args:
        vault_path: Path to the vault directory

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if path is absolute
    if not vault_path.is_absolute():
        return False, f"Path must be absolute: {vault_path}"

    # Check if parent directory exists
    parent = vault_path.parent
    if not parent.exists():
        return False, f"Parent directory does not exist: {parent}"

    # Check if parent is writable
    if not parent.is_dir():
        return False, f"Parent path is not a directory: {parent}"

    # Check write permissions on parent
    try:
        test_file = parent / ".write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError) as e:
        return False, f"Parent directory is not writable: {e}"

    # If vault already exists, check if it's a directory
    if vault_path.exists():
        if not vault_path.is_dir():
            return False, f"Path exists but is not a directory: {vault_path}"
        # Warn but allow if directory exists
        print(f"⚠️  Warning: Vault directory already exists: {vault_path}")
        print("    Existing files will be preserved, missing folders will be created.")

    return True, ""


def copy_template_file(template_name: str, vault_path: Path) -> Path:
    """Copy a template file to the vault root.

    Args:
        template_name: Name of the template file (without .md extension)
        vault_path: Path to the vault directory

    Returns:
        Path to the created file

    Raises:
        FileNotFoundError: If template file doesn't exist
    """
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    template_dir = script_dir / "templates"

    # Source template file
    template_file = template_dir / f"{template_name}_template.md"
    if not template_file.exists():
        raise FileNotFoundError(f"Template file not found: {template_file}")

    # Destination file (remove _template suffix)
    dest_file = vault_path / f"{template_name.replace('_', ' ').title().replace(' ', '_')}.md"

    # Copy template to vault
    copy2(template_file, dest_file)
    return dest_file


def create_vault(vault_path: Path) -> Tuple[List[Path], List[Path]]:
    """Create complete vault structure with folders and configuration files.

    Args:
        vault_path: Path to the vault directory

    Returns:
        Tuple of (created_folders, created_files)

    Raises:
        OSError: If vault creation fails
    """
    # Create vault directory if it doesn't exist
    vault_path.mkdir(parents=True, exist_ok=True)

    # Create folder structure
    created_folders = create_vault_folders(vault_path)

    # Copy template files
    created_files = []
    templates = ["dashboard", "handbook", "business_goals"]

    for template in templates:
        try:
            file_path = copy_template_file(template, vault_path)
            created_files.append(file_path)
        except FileNotFoundError as e:
            print(f"⚠️  Warning: Could not copy template: {e}")

    return created_folders, created_files


def print_success_summary(
    vault_path: Path, created_folders: List[Path], created_files: List[Path]
) -> None:
    """Print success confirmation with details of created items.

    Args:
        vault_path: Path to the vault directory
        created_folders: List of created folder paths
        created_files: List of created file paths
    """
    print("\n" + "=" * 70)
    print("✅ Vault Created Successfully!")
    print("=" * 70)
    print(f"\n📁 Vault Location: {vault_path}")
    print(f"\n📂 Created {len(created_folders)} folders:")
    for folder in sorted(created_folders):
        print(f"   • {folder.name}/")

    print(f"\n📄 Created {len(created_files)} configuration files:")
    for file in sorted(created_files):
        print(f"   • {file.name}")

    print("\n" + "=" * 70)
    print("Next Steps:")
    print("=" * 70)
    print("\n1. Open Obsidian and select 'Open folder as vault'")
    print(f"   Choose: {vault_path}")
    print("\n2. Configure your environment:")
    print("   • Copy .env.example to .env")
    print(f"   • Set VAULT_PATH={vault_path}")
    print("   • Configure your chosen Watcher (Gmail or File System)")
    print("\n3. Start your Watcher:")
    print("   • Gmail: python watchers/gmail_watcher.py")
    print("   • File System: python watchers/filesystem_watcher.py")
    print("\n4. Process tasks with Claude Code:")
    print(f"   • cd {vault_path}")
    print('   • claude "Process all tasks in /Needs_Action"')
    print("\n" + "=" * 70)


def main() -> int:
    """Main entry point for vault creation script.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Create and initialize an Obsidian vault for Personal AI Employee",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vault_setup/create_vault.py --path ~/AI_Employee_Vault
  python vault_setup/create_vault.py --path /Users/john/Documents/AI_Vault
        """,
    )

    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Absolute path where the vault should be created",
    )

    args = parser.parse_args()

    # Convert to Path object and expand user home directory
    vault_path = Path(args.path).expanduser().resolve()

    print(f"\n🚀 Creating Personal AI Employee Vault...")
    print(f"📍 Target location: {vault_path}\n")

    # Validate vault path
    is_valid, error_message = validate_vault_path(vault_path)
    if not is_valid:
        print(f"❌ Error: {error_message}", file=sys.stderr)
        return 1

    # Create vault
    try:
        created_folders, created_files = create_vault(vault_path)
    except OSError as e:
        print(f"❌ Error creating vault: {e}", file=sys.stderr)
        return 1

    # Validate structure
    if not validate_vault_structure(vault_path):
        print("❌ Error: Vault structure validation failed", file=sys.stderr)
        return 1

    # Print success summary
    print_success_summary(vault_path, created_folders, created_files)

    return 0


if __name__ == "__main__":
    sys.exit(main())
