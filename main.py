#!/usr/bin/env python3
"""Main entry point for Personal AI Employee watchers.

This script launches the appropriate watcher based on the WATCHER_TYPE
environment variable.

Usage:
    python main.py              # Run in continuous mode
    python main.py --test       # Run test mode (single check)
"""

import argparse
import sys
from pathlib import Path

from watchers.config import load_config
from watchers.gmail_watcher import GmailWatcher
from watchers.filesystem_watcher import FilesystemWatcher


def run_gmail_watcher(config, test_mode: bool = False) -> int:
    """Run the Gmail Watcher.

    Args:
        config: WatcherConfig instance
        test_mode: If True, run single check and exit

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        watcher = GmailWatcher(
            vault_path=Path(config.vault_path),
            credentials_path=config.gmail_credentials_path,
            token_path=config.gmail_token_path,
            gmail_query=config.gmail_query,
            check_interval=120,  # 2 minutes
        )

        if test_mode:
            print("\n🧪 Running Gmail Watcher in test mode...")
            print(f"📧 Query: {config.gmail_query}")
            print(f"📁 Vault: {config.vault_path}\n")

            new_items = watcher.check_for_updates()
            print(f"\n✅ Test complete: Found {new_items} new emails")
            return 0
        else:
            watcher.run()
            return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Watcher stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def run_filesystem_watcher(config, test_mode: bool = False) -> int:
    """Run the File System Watcher.

    Args:
        config: WatcherConfig instance
        test_mode: If True, run single check and exit

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        watcher = FilesystemWatcher(
            vault_path=Path(config.vault_path),
            watch_directory=config.watch_directory,
            file_extensions=config.file_extensions,
            check_interval=5,  # 5 seconds
        )

        if test_mode:
            print("\n🧪 Running File System Watcher in test mode...")
            print(f"📂 Watching: {config.watch_directory}")
            print(f"📄 Extensions: {config.file_extensions}")
            print(f"📁 Vault: {config.vault_path}\n")

            print("Monitoring for 10 seconds...")
            import time

            watcher.observer.start()
            time.sleep(10)
            watcher.observer.stop()
            watcher.observer.join()

            new_items = watcher.check_for_updates()
            print(f"\n✅ Test complete: Processed {new_items} files")
            return 0
        else:
            watcher.run()
            return 0

    except KeyboardInterrupt:
        print("\n\n⏹️  Watcher stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Personal AI Employee Watcher - Monitor external sources for tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Run in continuous mode
  python main.py --test       # Run test mode (single check)

Environment Configuration:
  Set WATCHER_TYPE in .env to 'gmail' or 'filesystem'
  See .env.example for all configuration options
        """,
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode (single check, then exit)",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        print("\nPlease check your .env file and ensure all required variables are set.")
        print("See .env.example for reference.")
        return 1

    # Print startup banner
    print("\n" + "=" * 70)
    print("🤖 Personal AI Employee - Watcher")
    print("=" * 70)
    print(f"\n📍 Vault: {config.vault_path}")
    print(f"🔧 Watcher Type: {config.watcher_type}")

    if args.test:
        print("🧪 Mode: Test (single check)")
    else:
        print("🔄 Mode: Continuous monitoring")
        print("\nPress Ctrl+C to stop")

    print("\n" + "=" * 70 + "\n")

    # Launch appropriate watcher
    if config.watcher_type == "gmail":
        return run_gmail_watcher(config, test_mode=args.test)
    elif config.watcher_type == "filesystem":
        return run_filesystem_watcher(config, test_mode=args.test)
    else:
        print(
            f"❌ Invalid WATCHER_TYPE: {config.watcher_type}",
            file=sys.stderr,
        )
        print("Must be 'gmail' or 'filesystem'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
