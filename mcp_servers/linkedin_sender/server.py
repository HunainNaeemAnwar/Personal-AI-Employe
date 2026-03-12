#!/usr/bin/env python3
"""
LinkedIn Sender MCP Server - Python Implementation

Provides LinkedIn message sending capability via Selenium automation.
WARNING: Use at your own risk - automated LinkedIn actions may violate ToS.

Usage:
    python mcp_servers/linkedin_sender/server.py
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: FastMCP not installed. Run: pip install mcp")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('linkedin-mcp-server')

# Initialize FastMCP server
mcp = FastMCP(
    name="linkedin-sender",
    instructions="""
    LinkedIn Messenger MCP Server
    
    This server provides automated LinkedIn messaging via Selenium.
    
    ⚠️  WARNING: Automated LinkedIn actions may violate LinkedIn's Terms of Service.
    Use at your own risk. Consider manual sending for important messages.
    
    Available tools:
    - send_linkedin_message: Send a message to a LinkedIn connection
    """,
)


class LinkedInClient:
    """LinkedIn client using Selenium for automation."""
    
    def __init__(self):
        self.username = os.getenv('LINKEDIN_USERNAME')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.session_path = os.getenv('LINKEDIN_SESSION_PATH', 
                                      'AI_Employee_Vault/.linkedin_session')
        self.driver = None
        self.is_logged_in = False
        
    def _init_driver(self):
        """Initialize Selenium WebDriver with session persistence."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use persistent session
            chrome_options.add_argument(f"--user-data-dir={self.session_path}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Chrome WebDriver initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False
    
    def _ensure_logged_in(self) -> bool:
        """Ensure we're logged into LinkedIn."""
        if not self.driver:
            if not self._init_driver():
                return False
        
        try:
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Check if we're on feed page (logged in) or login page
            if "feed" in self.driver.current_url:
                logger.info("Already logged in to LinkedIn")
                self.is_logged_in = True
                return True
            else:
                # Need to login
                return self._login()
                
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False
    
    def _login(self) -> bool:
        """Login to LinkedIn."""
        if not self.username or not self.password:
            logger.error("LinkedIn credentials not configured")
            return False
        
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Find and fill username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit login form
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for redirect to feed
            time.sleep(5)
            
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                logger.info("Successfully logged in to LinkedIn")
                self.is_logged_in = True
                return True
            else:
                logger.error("Login failed - check credentials")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def send_message(self, recipient_name: str, message: str) -> Dict[str, Any]:
        """
        Send a LinkedIn message to a connection.
        
        Args:
            recipient_name: Name of the LinkedIn connection
            message: Message text to send
            
        Returns:
            Dictionary with success status and details
        """
        result = {
            "success": False,
            "recipient": recipient_name,
            "message_length": len(message),
            "timestamp": datetime.now().isoformat(),
            "error": None
        }
        
        try:
            # Ensure logged in
            if not self._ensure_logged_in():
                result["error"] = "Failed to login to LinkedIn"
                return result
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.keys import Keys
            
            # Go to messaging page
            self.driver.get("https://www.linkedin.com/messaging/")
            time.sleep(3)
            
            # Search for the recipient
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[aria-label='Search messaging conversations']"))
            )
            search_box.clear()
            search_box.send_keys(recipient_name)
            time.sleep(2)
            
            # Click on the first search result
            first_result = self.driver.find_element(By.CSS_SELECTOR, "ul[role='listbox'] li button")
            first_result.click()
            time.sleep(2)
            
            # Find message input box
            message_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
            )
            
            # Type message
            message_box.click()
            time.sleep(1)
            
            # Clear any existing text
            from selenium.webdriver import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
            actions.send_keys(Keys.DELETE).perform()
            
            # Type the message
            for char in message:
                message_box.send_keys(char)
                time.sleep(0.05)  # Simulate human typing
            
            time.sleep(1)
            
            # Click send button
            send_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Send message']")
            send_button.click()
            
            # Wait for confirmation
            time.sleep(2)
            
            logger.info(f"Message sent to {recipient_name}")
            
            result["success"] = True
            result["sent_at"] = datetime.now().isoformat()
            
            # Log to vault
            self._log_sent_message(recipient_name, message)
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            result["error"] = str(e)
            return result
    
    def _log_sent_message(self, recipient: str, message: str):
        """Log sent message to vault."""
        try:
            vault_path = Path(os.getenv('VAULT_PATH', 'AI_Employee_Vault'))
            log_file = vault_path / "Logs" / "linkedin_sent.log"
            log_file.parent.mkdir(exist_ok=True)
            
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "recipient": recipient,
                "message_length": len(message),
                "message_preview": message[:100] + "..." if len(message) > 100 else message
            }
            
            with open(log_file, "a") as f:
                f.write(f"{log_entry['timestamp']} - Sent to {recipient}\n")
                
            logger.info(f"Logged sent message to {log_file}")
            
        except Exception as e:
            logger.error(f"Failed to log sent message: {e}")
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except:
                pass


# Create global client instance
linkedin_client = LinkedInClient()


@mcp.tool()
async def send_linkedin_message(
    recipient: str,
    message: str
) -> dict:
    """
    Send a LinkedIn message to a connection.
    
    ⚠️  WARNING: Automated LinkedIn messaging may violate LinkedIn's Terms of Service.
    Use at your own risk.
    
    Args:
        recipient: Name of the LinkedIn connection to message
        message: Message text to send (max 3000 characters)
        
    Returns:
        Dictionary with:
        - success: bool - Whether message was sent successfully
        - recipient: str - Recipient name
        - timestamp: str - ISO timestamp when sent
        - error: str|null - Error message if failed
        
    Example:
        send_linkedin_message(
            recipient="John Doe",
            message="Hi John, thanks for connecting! Looking forward to staying in touch."
        )
    """
    logger.info(f"Sending LinkedIn message to {recipient}")
    
    # Validate inputs
    if not recipient or len(recipient.strip()) == 0:
        return {
            "success": False,
            "error": "Recipient name is required"
        }
    
    if not message or len(message.strip()) == 0:
        return {
            "success": False,
            "error": "Message is required"
        }
    
    if len(message) > 3000:
        return {
            "success": False,
            "error": "Message exceeds 3000 character limit"
        }
    
    # Send message
    result = linkedin_client.send_message(recipient, message)
    
    return result


@mcp.tool()
async def test_linkedin_connection() -> dict:
    """
    Test LinkedIn connection and login status.
    
    Returns:
        Dictionary with connection status
    """
    logger.info("Testing LinkedIn connection")
    
    success = linkedin_client._ensure_logged_in()
    
    return {
        "connected": success,
        "logged_in": linkedin_client.is_logged_in,
        "username": linkedin_client.username,
        "timestamp": datetime.now().isoformat()
    }


# Cleanup on exit
import atexit
atexit.register(linkedin_client.close)


if __name__ == "__main__":
    logger.info("Starting LinkedIn Sender MCP Server...")
    logger.warning("⚠️  WARNING: Automated LinkedIn actions may violate LinkedIn's Terms of Service.")
    logger.info("Use at your own risk!")
    
    # Run the MCP server
    mcp.run()
