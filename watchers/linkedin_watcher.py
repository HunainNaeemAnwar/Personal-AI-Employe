"""
LinkedIn Watcher implementation for monitoring LinkedIn messages and posting updates.

This module implements a watcher that monitors LinkedIn for new messages and
provides capability to post business updates for lead generation.

Uses Selenium browser automation for reliable LinkedIn access.
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
from bs4 import BeautifulSoup

from watchers.base_watcher import BaseWatcher


class LinkedInWatcher(BaseWatcher):
    """
    Watcher for monitoring LinkedIn messages and posting business updates.
    
    Uses Selenium browser automation to access LinkedIn since the official API
    is limited for personal accounts.

    Attributes:
        username: LinkedIn username/email
        password: LinkedIn password
        polling_interval: Seconds between LinkedIn checks
        driver: Selenium WebDriver instance
        session_path: Path to store Chrome session data
    """

    def __init__(
        self,
        vault_path: Path,
        username: str,
        password: str,
        polling_interval: int = 300,
        check_interval: int = 300,
        state_db_path: str = "state.db",
        session_path: Optional[str] = None,
    ):
        """Initialize LinkedIn Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            username: LinkedIn username/email
            password: LinkedIn password
            polling_interval: Seconds between LinkedIn checks (default: 300 = 5 minutes)
            check_interval: Seconds between watcher checks (default: 300)
            state_db_path: Path to SQLite state database (default: state.db)
            session_path: Path to store Chrome session data (default: .linkedin_session)
        """
        super().__init__(vault_path, check_interval, state_db_path)

        self.username = username
        self.password = password
        self.polling_interval = polling_interval
        self.session_path = session_path or str(vault_path / ".linkedin_session")
        
        # Rate limiting tracking
        self.request_count = 0
        self.window_start = time.time()
        self.rate_limit_requests = int(os.getenv("LINKEDIN_RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("LINKEDIN_RATE_LIMIT_WINDOW", "3600"))
        self.use_selenium_fallback = True  # Use Selenium for posting (no API access)

        # Initialize Selenium WebDriver
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False

        self._init_browser()

        self.logger.info("LinkedIn Watcher initialized (Selenium mode)")
        self.logger.info(f"Polling interval: {polling_interval} seconds")
        self.logger.info(f"Session path: {self.session_path}")

    def _init_browser(self):
        """Initialize Chrome WebDriver with LinkedIn session persistence."""
        try:
            # Configure Chrome options
            chrome_options = Options()
            # chrome_options.add_argument("--headless=new")  # Disabled for debugging
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Persist session data (cookies, local storage)
            chrome_options.add_argument(f"--user-data-dir={self.session_path}")
            
            # Initialize WebDriver
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            
            self.logger.info("Chrome WebDriver initialized")
            
            # Check if already logged in (session persisted)
            self._check_login_status()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise

    def _check_login_status(self):
        """Check if already logged into LinkedIn."""
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if we're on the feed page (logged in) or login page
            if "feed" in self.driver.current_url:
                self.is_logged_in = True
                self.logger.info("Already logged into LinkedIn (session persisted)")
            else:
                self.is_logged_in = False
                self.logger.info("LinkedIn session expired, will re-authenticate")
                
        except Exception as e:
            self.logger.warning(f"Error checking login status: {e}")
            self.is_logged_in = False

    def _ensure_logged_in(self) -> bool:
        """Ensure we're logged into LinkedIn.
        
        Returns:
            True if logged in, False otherwise
        """
        if not self.driver:
            if not self._init_driver():
                return False
        
        try:
            # Navigate to feed to check login state
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if we're on feed page (logged in) or login page
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                self.logger.info("Already logged into LinkedIn (session persisted)")
                self.is_logged_in = True
                return True
            elif "login" in self.driver.current_url:
                self.logger.info("Session expired, need to login")
                self.is_logged_in = False
                return False
            else:
                # Check for My Network page (also indicates logged in)
                if "mynetwork" in self.driver.current_url:
                    self.is_logged_in = True
                    return True
                # Unknown state, assume need login
                self.is_logged_in = False
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking login status: {e}")
            self.is_logged_in = False
            return False
    
    def _login(self):
        """Log into LinkedIn using Selenium."""
        if self.is_logged_in:
            return True
            
        try:
            self.logger.info("Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Find and fill username field (try multiple selectors)
            try:
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "session_key"))
                )
                username_field.clear()
                username_field.send_keys(self.username)
            except TimeoutException:
                self.logger.error("Login page did not load - username field not found")
                return False
            
            # Find and fill password field
            try:
                password_field = self.driver.find_element(By.NAME, "session_password")
                password_field.clear()
                password_field.send_keys(self.password)
            except TimeoutException:
                self.logger.error("Password field not found")
                return False
            
            # Submit login form
            try:
                sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                sign_in_button.click()
                time.sleep(5)  # Wait for login to complete
                
                # Check if login was successful
                if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url or "messaging" in self.driver.current_url:
                    self.is_logged_in = True
                    self.logger.info("Successfully logged into LinkedIn")
                    return True
                else:
                    self.logger.error("Login failed - redirected to: %s", self.driver.current_url)
                    return False
                    
            except TimeoutException:
                self.logger.error("Sign in button not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

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
        """Check LinkedIn for new messages using Selenium.

        Returns:
            Number of new messages found
        """
        try:
            # Ensure logged in by checking actual page state
            if not self._ensure_logged_in():
                self.logger.info("Not logged in, attempting login...")
                if not self._login():
                    self.logger.warning("LinkedIn login failed, skipping check")
                    return 0

            # Navigate to messaging INBOX - use feed first to avoid thread redirect
            self.logger.debug("Navigating to LinkedIn feed first...")
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Then click on messaging icon or navigate directly
            self.logger.debug("Navigating to messaging inbox...")
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(5)
            
            # Check if we're on a thread page (redirected)
            if "/messaging/thread/" in self.driver.current_url:
                self.logger.debug("Redirected to thread, navigating back to inbox...")
                # Go back to inbox
                self.driver.get("https://www.linkedin.com/messaging/")
                time.sleep(3)
            
            # Check if we were redirected to login
            if "login" in self.driver.current_url:
                self.logger.warning("Session expired, re-authenticating...")
                self.is_logged_in = False
                if not self._login():
                    return 0
                # Navigate to feed then messaging after login
                self.driver.get("https://www.linkedin.com/feed/")
                time.sleep(3)
                self.driver.get("https://www.linkedin.com/messaging/")
                time.sleep(5)

            # Parse messages from page
            return self._parse_messages()

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn messages: {e}")
            self.is_logged_in = False  # Force re-login on next check
            return 0

    def _mark_as_read(self, sender_name):
        """Mark a LinkedIn conversation as read by clicking on it.
        
        Args:
            sender_name: Name of the sender to mark as read
        """
        self.logger.info(f"Attempting to mark as read: {sender_name}")
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Find the conversation card by sender name
            xpath = f"//div[contains(@class, 'msg-conversation-card') and contains(., '{sender_name}')]"
            
            self.logger.debug(f"Looking for conversation card: {xpath}")
            
            conversation_card = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            
            if conversation_card:
                self.logger.info(f"Found conversation with {sender_name}, clicking to mark as read...")
                # Click on the card to mark as read
                conversation_card.click()
                time.sleep(3)
                
                # Go back to inbox
                self.driver.get("https://www.linkedin.com/messaging/")
                time.sleep(3)
                
                self.logger.info(f"✓ Marked conversation with {sender_name} as read")
                return True
            else:
                self.logger.warning(f"Could not find conversation with {sender_name}")
                return False
                    
        except Exception as e:
            self.logger.error(f"Error marking as read: {e}")
            return False

    def _parse_messages(self) -> int:
        """Parse LinkedIn messages from current page.

        Returns:
            Number of new messages found
        """
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            new_count = 0

            # Find all conversation cards
            conversations = soup.find_all(class_='msg-conversation-card')
            
            self.logger.info(f"Found {len(conversations)} conversations on page")

            for conv in conversations[:10]:
                try:
                    # Extract sender name from image alt text
                    name = None
                    name_elem = conv.find('img', alt=True)
                    if name_elem:
                        name = name_elem['alt']
                    
                    if not name:
                        # Try aria-label on link
                        link_elem = conv.find('a', attrs={'aria-label': True})
                        if link_elem:
                            aria_label = link_elem['aria-label']
                            if 'conversation with' in aria_label:
                                name = aria_label.split('conversation with')[-1].strip()
                    
                    # Extract message preview - get ALL text and parse it
                    # The card text contains: name, time, message, status
                    card_text = conv.get_text(separator=' ', strip=True)
                    
                    # Remove the name from the text to get just the message
                    if name and name in card_text:
                        # Remove name and get what comes after
                        parts = card_text.split(name, 1)
                        if len(parts) > 1:
                            message_text = parts[1]
                            # Remove timestamps (like "4:25 AM", "Mar 6")
                            import re
                            message_text = re.sub(r'\d{1,2}:\d{2}\s*[AP]M', '', message_text)
                            message_text = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}', '', message_text)
                            # Remove UI text
                            message_text = re.sub(r'\.\s*Active conversation', '', message_text)
                            message_text = re.sub(r'\.\s*Press return.*', '', message_text)
                            message_text = re.sub(r'\.\s*Open the options.*', '', message_text)
                            message_text = message_text.strip(' .\n\t')
                            message = message_text[:200] if message_text else "New LinkedIn conversation"
                        else:
                            message = "New LinkedIn conversation"
                    else:
                        message = card_text[:200] if card_text else "New LinkedIn conversation"
                    
                    if not name:
                        self.logger.debug(f"Could not find sender name in conversation")
                        continue

                    # Use stable hash (hashlib) instead of hash() which changes between runs
                    import hashlib
                    conversation_id = f"li_msg_{hashlib.md5(name.encode()).hexdigest()[:16]}"

                    # Skip if already processed
                    if self.is_processed(conversation_id):
                        self.logger.debug(f"Skipping already processed message from {name}")
                        continue

                    # Create task file
                    message_data = {
                        "sender": name,
                        "message": message,
                        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                        "conversation_id": conversation_id,
                        "source": "linkedin",
                    }

                    task_file = self.create_action_file(message_data)
                    relative_path = task_file.relative_to(self.vault_path)
                    self.mark_processed(conversation_id, str(relative_path))
                    
                    # Mark message as read on LinkedIn
                    self._mark_as_read(name)
                    
                    new_count += 1
                    self.logger.info(f"✓ Created task for LinkedIn message from: {name}")

                except Exception as e:
                    self.logger.debug(f"Error parsing conversation: {e}")
                    continue

            if new_count == 0:
                self.logger.info("No new LinkedIn messages found")
            else:
                self.logger.info(f"Found {new_count} new LinkedIn message(s)")

            return new_count

        except Exception as e:
            self.logger.error(f"Parse error: {e}")
            return 0

    def post_to_linkedin(self, content: str, hashtags: Optional[List[str]] = None) -> bool:
        """Post update to LinkedIn.

        Args:
            content: Post content text
            hashtags: Optional list of hashtags to add

        Returns:
            True if post successful, False otherwise
        """
        try:
            # Ensure logged in
            if not self.is_logged_in:
                if not self._login():
                    return False

            # Navigate to feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)

            # Click post creation box
            try:
                post_box = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'share-box-feed-entry')]"))
                )
                post_box.click()
                time.sleep(2)

                # Find text area and enter content
                text_area = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                text_area.send_keys(content)

                # Add hashtags if provided
                if hashtags:
                    for tag in hashtags:
                        text_area.send_keys(f" {tag}")

                # Click post button
                post_button = self.driver.find_element(
                    By.XPATH,
                    "//button[contains(@class, 'share-actions__primary-action')]"
                )
                post_button.click()
                time.sleep(3)

                self.logger.info("LinkedIn post published successfully")
                return True

            except TimeoutException:
                self.logger.error("Post creation UI not found")
                return False

        except Exception as e:
            self.logger.error(f"Post error: {e}")
            return False

    def __del__(self):
        """Cleanup browser on deletion."""
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass

    def create_action_file(self, message_data: Dict[str, Any]) -> Path:
        """Create a task file for a LinkedIn message in the vault's Inbox/linkedin folder.

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

            # Create filename using sender name (slugified for filesystem safety)
            sender_slug = sender.replace(' ', '-').lower()
            filename = f"LINKEDIN_MSG_{sender_slug}.md"

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

            # Write to Inbox/linkedin folder (NOT Needs_Action)
            inbox_dir = self.get_inbox_subfolder()

            task_file = inbox_dir / filename
            task_file.write_text(content)

            self.logger.info(f"Created task file in Inbox: {filename}")
            self.log_to_vault(
                action="create_task",
                result="success",
                details={
                    "filename": filename,
                    "sender": sender,
                    "conversation_id": conversation_id,
                    "location": "Inbox/linkedin",
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
        
        try:
            # Navigate to LinkedIn feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Find the post creation box and click it
            try:
                # Look for the "Start a post" button
                post_button = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Start a post')]")
                post_button.click()
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Could not find post button: {e}")
                # Try alternative selector
                try:
                    post_button = self.driver.find_element(By.XPATH, "//div[contains(@class, 'share-box-feed-entry')]")
                    post_button.click()
                    time.sleep(2)
                except Exception as e2:
                    self.logger.error(f"Alternative post button also failed: {e2}")
                    return {"success": False, "error": "Could not open post composer"}
            
            # Find the text area and enter content
            try:
                # LinkedIn uses a contenteditable div for the post text
                text_area = self.driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                text_area.click()
                time.sleep(1)
                
                # Clear any existing text
                text_area.clear()
                time.sleep(0.5)
                
                # Type the content (use send_keys for reliability)
                for char in content:
                    text_area.send_keys(char)
                    time.sleep(0.01)  # Small delay to simulate typing
                
                time.sleep(2)
            except Exception as e:
                self.logger.error(f"Could not enter post content: {e}")
                return {"success": False, "error": "Could not enter post content"}
            
            # Find and click the post button
            try:
                # Look for the "Post" button
                post_submit = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Post')]")
                post_submit.click()
                time.sleep(3)
                
                self.logger.info("LinkedIn post published successfully")
                
                # Log the post
                self._log_post(content)
                
                return {"success": True, "post_id": f"selenium_{int(time.time())}"}
            except Exception as e:
                self.logger.error(f"Could not submit post: {e}")
                return {"success": False, "error": "Could not submit post"}
                
        except Exception as e:
            self.logger.error(f"Error posting to LinkedIn: {e}")
            return {"success": False, "error": str(e)}
    
    def _log_post(self, content: str):
        """Log the post to the vault."""
        try:
            log_file = self.vault_path / "Logs" / "linkedin_posts.log"
            timestamp = datetime.now(timezone.utc).isoformat()
            with open(log_file, "a") as f:
                f.write(f"\n---\nTimestamp: {timestamp}\nContent:\n{content[:200]}...\n")
        except Exception as e:
            self.logger.error(f"Could not log post: {e}")


if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv

    # Load environment variables from .env file (override=True to refresh cache)
    load_dotenv(override=True)

    parser = argparse.ArgumentParser(description="LinkedIn Watcher")
    parser.add_argument("--vault", default=os.getenv("VAULT_PATH", "vault"), help="Path to Obsidian vault")
    parser.add_argument("--username", default=os.getenv("LINKEDIN_USERNAME"), help="LinkedIn username")
    parser.add_argument("--password", default=os.getenv("LINKEDIN_PASSWORD"), help="LinkedIn password")
    parser.add_argument("--interval", type=int, default=int(os.getenv("LINKEDIN_POLLING_INTERVAL", "300")), help="Check interval in seconds")
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
