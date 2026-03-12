"""Gmail Watcher implementation for monitoring Gmail inbox.

This module implements a watcher that monitors Gmail inbox for new emails
and creates task files in the Obsidian vault.
"""

import base64
import os
import pickle
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from watchers.base_watcher import BaseWatcher

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class GmailWatcher(BaseWatcher):
    """Watcher for monitoring Gmail inbox.

    Attributes:
        credentials_path: Path to OAuth2 credentials file
        token_path: Path to stored token file
        gmail_query: Gmail search query filter
        service: Gmail API service instance
    """

    def __init__(
        self,
        vault_path: Path,
        credentials_path: str,
        token_path: str,
        gmail_query: str = "is:unread is:important",
        check_interval: int = 120,
        state_db_path: str = "state.db",
    ):
        """Initialize Gmail Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load token
            gmail_query: Gmail search query (default: "is:unread is:important")
            check_interval: Seconds between checks (default: 120)
            state_db_path: Path to SQLite state database (default: state.db)

        Raises:
            ValueError: If credentials file doesn't exist
        """
        super().__init__(vault_path, check_interval, state_db_path)

        self.credentials_path = credentials_path
        self.token_path = token_path
        self.gmail_query = gmail_query

        # Authenticate and build service
        self.service = self._authenticate()

        self.logger.info(f"Gmail Watcher initialized with query: {gmail_query}")

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2.

        Returns:
            Gmail API service instance

        Raises:
            ValueError: If authentication fails
        """
        creds = None

        # Load existing token if available (avoids re-authentication)
        token_path = Path(self.token_path)
        if token_path.exists():
            with open(token_path, "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate or refresh
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Token expired but can be refreshed (no user interaction needed)
                self.logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                # No token or refresh failed - start full OAuth2 flow
                self.logger.info("Starting OAuth2 authentication flow...")
                if not Path(self.credentials_path).exists():
                    raise ValueError(f"Credentials file not found: {self.credentials_path}")

                # Run local server for OAuth callback (opens browser automatically)
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token for future use (persists across watcher restarts)
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "wb") as token:
                pickle.dump(creds, token)

            self.logger.info("Authentication successful")

        # Build and return Gmail API service client
        return build("gmail", "v1", credentials=creds)

    def _exponential_backoff(self, attempt: int) -> None:
        """Implement exponential backoff for rate limiting.

        Args:
            attempt: Current retry attempt number
        """
        # Calculate wait time: 2^attempt seconds (1s, 2s, 4s, 8s, 16s, 32s, 60s max)
        wait_time = min(2**attempt, 60)  # Cap at 60 seconds to avoid excessive delays
        self.logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
        time.sleep(wait_time)

    def check_for_updates(self) -> int:
        """Check Gmail inbox for new emails matching the query.

        Returns:
            Number of new emails found

        Raises:
            Exception: If Gmail API call fails after retries
        """
        self.logger.debug("Checking Gmail for new messages...")
        max_retries = 3
        attempt = 0

        while attempt < max_retries:
            try:
                # Query Gmail API for messages matching the configured query
                # maxResults=10 limits to 10 most recent emails per check
                self.logger.debug(f"Executing Gmail API query: {self.gmail_query}")
                results = (
                    self.service.users()
                    .messages()
                    .list(userId="me", q=self.gmail_query, maxResults=10)
                    .execute()
                )

                messages = results.get("messages", [])
                self.logger.debug(f"Found {len(messages)} messages from API")
                new_count = 0

                # Process each message
                processed_count = 0
                for message in messages:
                    message_id = message["id"]

                    # Skip if already processed (prevents duplicate task files)
                    if self.is_processed(message_id):
                        self.logger.debug(f"Skipping already processed message: {message_id}")
                        processed_count += 1
                        continue

                    # Get full message details (headers, body, etc.)
                    # format="full" returns complete message with payload
                    msg = (
                        self.service.users()
                        .messages()
                        .get(userId="me", id=message_id, format="full")
                        .execute()
                    )

                    # Create task file and mark as processed with file path
                    task_file = self.create_action_file(msg)
                    # Store relative path from vault root for state tracking
                    relative_path = task_file.relative_to(self.vault_path)
                    self.mark_processed(message_id, str(relative_path))
                    new_count += 1

                if new_count > 0:
                    self.logger.info(f"Created {new_count} new task file(s)")
                elif processed_count > 0:
                    self.logger.info(f"No new emails found ({processed_count} already processed)")
                else:
                    self.logger.info(f"No new emails found (API returned {len(messages)} messages)")

                return new_count

            except HttpError as e:
                # Handle rate limiting with exponential backoff
                if e.resp.status == 429:  # HTTP 429 = Too Many Requests
                    attempt += 1
                    if attempt < max_retries:
                        self._exponential_backoff(attempt)
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} retries")
                else:
                    # Other HTTP errors (auth, network, etc.) - don't retry
                    raise

            except Exception as e:
                self.logger.error(f"Error checking Gmail: {e}")
                raise

        # This line should never be reached, but satisfies type checker
        return 0

    def _get_header(self, headers: List[Dict[str, str]], name: str) -> str:
        """Extract header value from email headers.

        Args:
            headers: List of header dictionaries with 'name' and 'value' keys
            name: Header name to find

        Returns:
            Header value or empty string if not found
        """
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return ""

    def _decode_body(self, payload: Dict) -> str:
        """Decode email body from payload.

        Args:
            payload: Email payload dictionary

        Returns:
            Decoded email body text
        """
        # Try simple body (single-part message)
        if "body" in payload and "data" in payload["body"]:
            data = payload["body"]["data"]
            # Gmail uses URL-safe base64 encoding
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        # Try multipart message (email with attachments or HTML)
        if "parts" in payload:
            for part in payload["parts"]:
                # Look for plain text part (prefer over HTML)
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        data = part["body"]["data"]
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        # Fallback if body cannot be decoded
        return "[Email body could not be decoded]"

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

    def _determine_priority(self, subject: str, sender: str) -> str:
        """Determine email priority based on content.

        Args:
            subject: Email subject line
            sender: Email sender address

        Returns:
            Priority level: high, medium, or low
        """
        urgent_keywords = ["urgent", "asap", "deadline", "critical", "emergency", "important"]
        subject_lower = subject.lower()

        if any(keyword in subject_lower for keyword in urgent_keywords):
            return "high"

        # Add more sophisticated logic here based on sender, etc.
        return "medium"

    def create_action_file(self, message_data: Dict[str, Any]) -> Path:
        """Create a task file for an email in the vault's Inbox/gmail folder.

        Args:
            message_data: Gmail message data from API

        Returns:
            Path to the created task file
        """
        try:
            # Extract email metadata
            headers = message_data["payload"]["headers"]
            subject = self._get_header(headers, "Subject") or "[No Subject]"
            sender = self._get_header(headers, "From")
            date_str = self._get_header(headers, "Date")
            message_id = message_data["id"]

            # Parse date
            try:
                # Gmail date format is complex, use current time as fallback
                timestamp = datetime.now(timezone.utc).isoformat() + "Z"
            except:
                timestamp = datetime.now(timezone.utc).isoformat() + "Z"

            # Decode body
            body = self._decode_body(message_data["payload"])

            # Determine priority
            priority = self._determine_priority(subject, sender)

            # Create filename using subject (slugified for filesystem safety)
            slug = self._slugify(subject)
            filename = f"EMAIL_{slug}.md"

            # Create task file content
            content = f"""---
type: email
source: {sender}
timestamp: {timestamp}
priority: {priority}
status: pending
subject: {subject}
---

## Email Content

**From**: {sender}
**Subject**: {subject}
**Received**: {date_str}

{body}

## Metadata

- **Gmail Message ID**: {message_id}
- **Created**: {timestamp}
- **Priority**: {priority}

## Suggested Actions

- [ ] Review email content
- [ ] Determine required response
- [ ] Create execution plan
- [ ] Complete actions
- [ ] Move to /Done when finished
"""

            # Write to Inbox/gmail folder (NOT Needs_Action)
            inbox_dir = self.get_inbox_subfolder()
            
            task_file = inbox_dir / filename
            task_file.write_text(content)

            self.logger.info(f"Created task file in Inbox: {filename}")
            self.log_to_vault(
                action="create_task",
                result="success",
                details={
                    "filename": filename,
                    "subject": subject,
                    "sender": sender,
                    "priority": priority,
                    "location": "Inbox/gmail",
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


if __name__ == "__main__":
    import argparse
    import os
    from dotenv import load_dotenv

    # Load environment variables from .env file (override=True to refresh cache)
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="Gmail Watcher")
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "vault"), help="Path to Obsidian vault")
    parser.add_argument("--credentials", default=os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json"), help="Path to Gmail credentials")
    parser.add_argument("--token", default=os.getenv("GMAIL_TOKEN_PATH", "token.pickle"), help="Path to Gmail token")
    parser.add_argument("--query", default=os.getenv("GMAIL_QUERY", "is:unread"), help="Gmail search query")
    parser.add_argument("--interval", type=int, default=int(os.getenv("GMAIL_CHECK_INTERVAL", "60")), help="Check interval in seconds")
    parser.add_argument("--state-db", default=os.getenv("STATE_DB_PATH", "state.db"), help="Path to state database")

    args = parser.parse_args()

    watcher = GmailWatcher(
        vault_path=Path(args.vault),
        credentials_path=args.credentials,
        token_path=args.token,
        gmail_query=args.query,
        check_interval=args.interval,
        state_db_path=args.state_db
    )

    watcher.run()
