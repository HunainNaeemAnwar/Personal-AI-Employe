"""
LinkedIn Watcher implementation for monitoring LinkedIn messages and posting updates.

This module implements a watcher that monitors LinkedIn for new messages and
provides capability to post business updates for lead generation.
"""

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from linkedin_api import Linkedin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from watchers.base_watcher import BaseWatcher


class LinkedInWatcher(BaseWatcher):
    """
    Watcher for monitoring LinkedIn messages and posting business updates.

    Attributes:
        linkedin_client: LinkedIn API client instance
        username: LinkedIn username/email
        password: LinkedIn password
        access_token: LinkedIn OAuth2 access token
        polling_interval: Seconds between LinkedIn API checks
        rate_limit_requests: Maximum requests per hour
        rate_limit_window: Rate limit window in seconds
        request_count: Current request count in window
        window_start: Start time of current rate limit window
        use_selenium_fallback: Whether to use Selenium when API unavailable
    """

    def __init__(
        self,
        vault_path: Path,
        username: str,
        password: str,
        access_token: Optional[str] = None,
        polling_interval: int = 300,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,
        check_interval: int = 300,
        state_db_path: str = "state.db",
    ):
        """Initialize LinkedIn Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            username: LinkedIn username/email
            password: LinkedIn password
            access_token: Optional LinkedIn OAuth2 access token
            polling_interval: Seconds between LinkedIn checks (default: 300 = 5 minutes)
            rate_limit_requests: Maximum requests per hour (default: 100)
            rate_limit_window: Rate limit window in seconds (default: 3600 = 1 hour)
            check_interval: Seconds between watcher checks (default: 300)
            state_db_path: Path to SQLite state database (default: state.db)
        """
        super().__init__(vault_path, check_interval, state_db_path)

        self.username = username
        self.password = password
        self.access_token = access_token
        self.polling_interval = polling_interval
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window

        # Rate limiting tracking
        self.request_count = 0
        self.window_start = time.time()

        # Initialize LinkedIn API client
        self.linkedin_client: Optional[Linkedin] = None
        self.use_selenium_fallback = False

        self._authenticate()

        self.logger.info("LinkedIn Watcher initialized")
        self.logger.info(f"Polling interval: {polling_interval} seconds")

    def _authenticate(self):
        """Authenticate with LinkedIn API or fall back to Selenium."""
        try:
            # Try LinkedIn API authentication
            self.linkedin_client = Linkedin(self.username, self.password)
            self.logger.info("LinkedIn API authentication successful")
            self.use_selenium_fallback = False

        except Exception as e:
            self.logger.warning(f"LinkedIn API authentication failed: {e}")
            self.logger.info("Will use Selenium fallback for LinkedIn access")
            self.use_selenium_fallback = True

    def _check_rate_limit(self) -> bool:
        """Check if rate limit allows another request.

        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()

        # Reset window if expired
        if current_time - self.window_start >= self.rate_limit_window:
            self.request_count = 0
            self.window_start = current_time

        # Check if under limit
        if self.request_count >= self.rate_limit_requests:
            wait_time = self.rate_limit_window - (current_time - self.window_start)
            self.logger.warning(
                f"LinkedIn rate limit reached ({self.rate_limit_requests} requests/hour). "
                f"Waiting {wait_time:.0f} seconds..."
            )
            return False

        return True

    def _increment_request_count(self):
        """Increment rate limit request counter."""
        self.request_count += 1

    def check_for_updates(self) -> int:
        """Check LinkedIn for new messages.

        Returns:
            Number of new messages found
        """
        # Check rate limit
        if not self._check_rate_limit():
            # Wait until rate limit resets
            current_time = time.time()
            wait_time = self.rate_limit_window - (current_time - self.window_start)
            time.sleep(wait_time)
            return 0

        try:
            if self.use_selenium_fallback:
                return self._check_messages_selenium()
            else:
                return self._check_messages_api()

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn messages: {e}")
            self.log_to_vault(
                action="check",
                result="failure",
                error_message=str(e),
            )
            return 0

    def _check_messages_api(self) -> int:
        """Check for new LinkedIn messages using API.

        Returns:
            Number of new messages found
        """
        if not self.linkedin_client:
            return 0

        self._increment_request_count()

        try:
            # Get conversations (LinkedIn API method)
            conversations = self.linkedin_client.get_conversations()

            new_count = 0

            for conversation in conversations[:10]:  # Limit to 10 most recent
                conversation_id = conversation.get("entityUrn", "")

                # Skip if already processed
                if self.is_processed(conversation_id):
                    continue

                # Get conversation details
                messages = self.linkedin_client.get_conversation(conversation_id)

                if messages and len(messages) > 0:
                    latest_message = messages[0]

                    # Create task file for new message
                    message_data = {
                        "conversation_id": conversation_id,
                        "sender": latest_message.get("from", {}).get("name", "Unknown"),
                        "message": latest_message.get("body", ""),
                        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                    }

                    task_file = self.create_action_file(message_data)
                    relative_path = task_file.relative_to(self.vault_path)
                    self.mark_processed(conversation_id, str(relative_path))
                    new_count += 1

            return new_count

        except Exception as e:
            self.logger.error(f"LinkedIn API error: {e}")
            # Fall back to Selenium on API failure
            self.use_selenium_fallback = True
            return 0

    def _check_messages_selenium(self) -> int:
        """Check for new LinkedIn messages using Selenium (fallback).

        Returns:
            Number of new messages found
        """
        # Selenium implementation for when API is unavailable
        # This is a simplified version - full implementation would need more robust scraping
        self.logger.info("Using Selenium fallback for LinkedIn message checking")

        # For now, return 0 and log that Selenium fallback is not fully implemented
        self.logger.warning("Selenium fallback not fully implemented yet")
        return 0

    def create_action_file(self, message_data: Dict[str, Any]) -> Path:
        """Create a task file for a LinkedIn message in the vault's Needs_Action folder.

        Args:
            message_data: Dictionary containing message information

        Returns:
            Path to the created task file
        """
        try:
            conversation_id = message_data["conversation_id"]
            sender = message_data["sender"]
            message = message_data["message"]
            timestamp = message_data["timestamp"]

            # Create filename
            filename = f"LINKEDIN_MSG_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}Z_{sender.replace(' ', '-')}.md"

            # Create task file content
            content = f"""---
type: linkedin_message
source: {sender}
timestamp: {timestamp}
priority: medium
status: pending
subject: LinkedIn message from {sender}
---

## LinkedIn Message

**From**: {sender}
**Received**: {timestamp}

{message}

## Metadata

- **Conversation ID**: {conversation_id}
- **Created**: {timestamp}
- **Priority**: medium

## Suggested Actions

- [ ] Review message content
- [ ] Determine required response
- [ ] Draft response
- [ ] Send reply via LinkedIn
- [ ] Move to /Done when finished
"""

            # Write to Needs_Action folder
            needs_action_dir = self.vault_path / "Needs_Action"
            needs_action_dir.mkdir(exist_ok=True)

            task_file = needs_action_dir / filename
            task_file.write_text(content)

            self.logger.info(f"Created task file: {filename}")
            self.log_to_vault(
                action="create_task",
                result="success",
                details={
                    "filename": filename,
                    "sender": sender,
                    "conversation_id": conversation_id,
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

    def post_to_linkedin(
        self,
        content: str,
        visibility: str = "PUBLIC"
    ) -> Dict[str, Any]:
        """Post a business update to LinkedIn.

        Args:
            content: Post content text
            visibility: Post visibility (PUBLIC, CONNECTIONS, LOGGED_IN)

        Returns:
            Dictionary with post result (success, post_id, error)
        """
        # Check rate limit
        if not self._check_rate_limit():
            return {
                "success": False,
                "error": "Rate limit exceeded",
            }

        try:
            if self.use_selenium_fallback:
                return self._post_selenium(content, visibility)
            else:
                return self._post_api(content, visibility)

        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def _post_api(self, content: str, visibility: str) -> Dict[str, Any]:
        """Post to LinkedIn using API.

        Args:
            content: Post content text
            visibility: Post visibility

        Returns:
            Dictionary with post result
        """
        if not self.linkedin_client:
            return {
                "success": False,
                "error": "LinkedIn client not initialized",
            }

        self._increment_request_count()

        try:
            # Post using LinkedIn API
            result = self.linkedin_client.post_update(content, visibility=visibility)

            post_id = result.get("id", "unknown")

            self.logger.info(f"Posted to LinkedIn successfully: {post_id}")
            self.log_to_vault(
                action="linkedin_post",
                result="success",
                details={
                    "post_id": post_id,
                    "content_length": len(content),
                    "visibility": visibility,
                },
            )

            return {
                "success": True,
                "post_id": post_id,
            }

        except Exception as e:
            self.logger.error(f"LinkedIn API post error: {e}")
            # Fall back to Selenium
            self.use_selenium_fallback = True
            return {
                "success": False,
                "error": str(e),
            }

    def _post_selenium(self, content: str, visibility: str) -> Dict[str, Any]:
        """Post to LinkedIn using Selenium (fallback).

        Args:
            content: Post content text
            visibility: Post visibility

        Returns:
            Dictionary with post result
        """
        self.logger.info("Using Selenium fallback for LinkedIn posting")
        self.logger.warning("Selenium fallback not fully implemented yet")

        return {
            "success": False,
            "error": "Selenium fallback not implemented",
        }


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="LinkedIn Watcher")
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "vault"), help="Path to Obsidian vault")
    parser.add_argument("--username", default=os.getenv("LINKEDIN_USERNAME"), help="LinkedIn username")
    parser.add_argument("--password", default=os.getenv("LINKEDIN_PASSWORD"), help="LinkedIn password")
    parser.add_argument("--interval", type=int, default=int(os.getenv("LINKEDIN_CHECK_INTERVAL", "300")), help="Check interval in seconds")
    parser.add_argument("--state-db", default=os.getenv("STATE_DB_PATH", "state.db"), help="Path to state database")

    args = parser.parse_args()

    if not args.username or not args.password:
        print("Error: LinkedIn credentials required. Set LINKEDIN_USERNAME and LINKEDIN_PASSWORD environment variables.")
        exit(1)

    watcher = LinkedInWatcher(
        vault_path=Path(args.vault),
        username=args.username,
        password=args.password,
        check_interval=args.interval,
        state_db_path=args.state_db
    )

    watcher.run()
