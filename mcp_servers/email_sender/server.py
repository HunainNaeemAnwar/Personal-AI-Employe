#!/usr/bin/env python3
"""
Email Sender MCP Server - Python Implementation

Provides email sending capability via Gmail API through the Model Context Protocol.
Supports OAuth2 authentication, retry logic, and proper email threading.

Usage:
    python mcp_servers/email_sender/server.py
"""

import os
import sys
import base64
import logging
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
logger = logging.getLogger('email-mcp-server')

# Initialize FastMCP server
mcp = FastMCP(
    name="email-sender",
    instructions="MCP server for sending emails via Gmail API. Supports threading, CC/BCC, and retry logic."
)

# Gmail API configuration
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose"
]
CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "/home/hunain/.credentials/gmail-credentials.json")
TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "/home/hunain/.credentials/gmail-token.json")
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_BACKOFF_BASE = int(os.getenv("RETRY_BACKOFF_BASE", "1000"))  # milliseconds

_gmail_service = None


def get_gmail_service() -> Any:
    """Get or create Gmail API service with OAuth2 authentication."""
    global _gmail_service
    
    if _gmail_service:
        return _gmail_service
    
    creds = None
    
    # Load existing token
    token_path = Path(TOKEN_PATH)
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded existing Gmail token")
        except Exception as e:
            logger.warning(f"Failed to load token: {e}")
            creds = None
    
    # Refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired token...")
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")
                creds = None
        
        if not creds or not creds.valid:
            logger.info("Starting OAuth2 authentication flow...")
            if not Path(CREDENTIALS_PATH).exists():
                raise ValueError(f"Gmail credentials file not found: {CREDENTIALS_PATH}")
            
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save token
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "w") as f:
                f.write(creds.to_json())
            logger.info(f"Token saved to {token_path}")
    
    _gmail_service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail API service initialized")
    return _gmail_service


@mcp.tool()
async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    thread_id: Optional[str] = None,
    in_reply_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send an email via Gmail API.
    
    Args:
        recipients: List of recipient email addresses (required)
        subject: Email subject (required)
        body: Email body text (required)
        cc: Optional CC recipients
        bcc: Optional BCC recipients
        thread_id: Optional thread ID for threading
        in_reply_to: Optional message ID to reply to
    
    Returns:
        Dictionary with success status, message ID, and thread ID
    
    Examples:
        >>> send_email(
        ...     recipients=["user@example.com"],
        ...     subject="Hello",
        ...     body="This is a test email"
        ... )
        {'success': True, 'messageId': 'abc123', 'threadId': 'xyz789'}
    """
    logger.info(f"Sending email to {recipients} with subject: {subject}")
    
    last_error = None
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            service = get_gmail_service()
            
            # Create message
            message = MIMEMultipart()
            message["to"] = ", ".join(recipients)
            message["subject"] = subject
            message["from"] = "me"
            
            if cc:
                message["cc"] = ", ".join(cc)
            
            # Add threading headers if replying
            if in_reply_to:
                message["In-Reply-To"] = in_reply_to
                message["References"] = in_reply_to
            
            message.attach(MIMEText(body, "plain"))
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            
            # Send email
            sent_message = service.users().messages().send(
                userId="me",
                body={"raw": raw_message, "threadId": thread_id}
            ).execute()
            
            # Log success
            log_email_sent(
                recipients=recipients,
                subject=subject,
                message_id=sent_message["id"],
                thread_id=sent_message.get("threadId")
            )
            
            logger.info(f"Email sent successfully: {sent_message['id']}")
            
            return {
                "success": True,
                "messageId": sent_message["id"],
                "threadId": sent_message.get("threadId"),
                "timestamp": datetime.now().isoformat()
            }
            
        except HttpError as e:
            last_error = e
            if e.resp.status == 429:  # Rate limit
                wait_time = (RETRY_BACKOFF_BASE * (2 ** attempt)) / 1000
                logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
                time.sleep(wait_time)
            else:
                logger.error(f"Gmail API error: {e}")
                break
        except Exception as e:
            last_error = e
            logger.error(f"Failed to send email (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}): {e}")
            time.sleep(1)  # Brief pause before retry
    
    # All retries failed
    error_msg = str(last_error) if last_error else "Unknown error"
    logger.error(f"Email sending failed after {MAX_RETRY_ATTEMPTS} attempts: {error_msg}")
    
    return {
        "success": False,
        "error": error_msg,
        "timestamp": datetime.now().isoformat()
    }


def log_email_sent(recipients: List[str], subject: str, message_id: str, thread_id: Optional[str]):
    """Log sent email to vault logs."""
    logs_dir = Path("AI_Employee_Vault/Logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / "email_sent.log"
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "recipients": recipients,
        "subject": subject,
        "message_id": message_id,
        "thread_id": thread_id
    }
    
    with open(log_file, "a") as f:
        f.write(f"{log_entry}\n")
    
    logger.info(f"Logged email sent to {recipients}: {subject}")


@mcp.tool()
async def test_connection() -> Dict[str, Any]:
    """
    Test the Gmail API connection.

    Returns:
        Dictionary with connection status and user email
    """
    try:
        service = get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()

        return {
            "success": True,
            "email": profile["emailAddress"],
            "messagesTotal": profile["messagesTotal"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    # Run MCP server via stdio
    logger.info("Starting Email Sender MCP Server...")
    mcp.run()
