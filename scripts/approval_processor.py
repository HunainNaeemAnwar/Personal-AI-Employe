#!/usr/bin/env python3
"""
Approval Workflow Processor

Monitors the /Approved folder and executes approved actions via MCP servers.
Currently supports email sending approval workflow.

Usage:
    python scripts/approval_processor.py
"""

import json
import logging
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger('approval-processor')


class ApprovalHandler(FileSystemEventHandler):
    """Handle file events in Approved folder."""
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.logs_dir = vault_path / "Logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def on_moved(self, event):
        """Handle file move events (when file is moved to Approved)."""
        if event.is_directory:
            return
        
        dest_path = Path(event.dest_path)
        
        # Only process markdown files
        if dest_path.suffix != '.md':
            return
        
        logger.info(f"File moved to Approved: {dest_path.name}")
        self.process_approval(dest_path)
    
    def process_approval(self, file_path: Path):
        """Process an approved task file."""
        try:
            # Read task file
            content = file_path.read_text()
            
            # Parse YAML frontmatter
            task_data = self.parse_frontmatter(content)
            
            if not task_data:
                logger.warning(f"No frontmatter found in {file_path.name}")
                return
            
            # Check task type
            task_type = task_data.get('type', '')
            
            if task_type == 'email_response':
                self.send_approved_email(task_data, file_path)
            elif task_type == 'approval_request':
                # Generic approval request
                action = task_data.get('action', '')
                if action == 'email' or action == 'send_email':
                    self.send_approved_email(task_data, file_path)
                else:
                    logger.info(f"Approval action '{action}' noted but not automated yet")
            else:
                logger.info(f"Task type '{task_type}' noted but not automated yet")
            
        except Exception as e:
            logger.error(f"Error processing approval {file_path.name}: {e}")
            self.log_approval_result(file_path.name, False, str(e))
    
    def parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse YAML frontmatter from markdown file."""
        try:
            # Find frontmatter between --- markers
            if not content.startswith('---'):
                return None
            
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                return None
            
            frontmatter_text = content[3:end_marker]
            frontmatter = yaml.safe_load(frontmatter_text)
            
            return frontmatter if isinstance(frontmatter, dict) else None
            
        except Exception as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
            return None
    
    def send_approved_email(self, task_data: Dict[str, Any], file_path: Path):
        """Send email for approved task."""
        logger.info(f"Sending approved email from task: {file_path.name}")
        
        try:
            # Extract email details from task data
            recipients = []
            
            # Get recipient from various possible fields
            if 'to' in task_data:
                recipients = task_data['to'] if isinstance(task_data['to'], list) else [task_data['to']]
            elif 'recipients' in task_data:
                recipients = task_data['recipients'] if isinstance(task_data['recipients'], list) else [task_data['recipients']]
            elif 'email' in task_data:
                recipients = [task_data['email']]
            
            if not recipients:
                # Try to extract from filename
                # EMAIL_20260310T015002Z_hunain-thanks-for-being-a-valued-member.md
                # This is a reply, so we need to get original email info
                logger.warning(f"No recipient found in task data, checking original email task...")
                # For now, skip if no recipient
                return
            
            subject = task_data.get('subject', 'No Subject')
            body = task_data.get('body', '')
            
            # Get threading info if replying
            thread_id = task_data.get('thread_id')
            in_reply_to = task_data.get('in_reply_to')
            
            # Call MCP server to send email
            # For now, we'll use a simple subprocess call to the MCP server
            # In production, you'd use the MCP SDK client
            result = self.call_mcp_send_email(
                recipients=recipients,
                subject=subject,
                body=body,
                thread_id=thread_id,
                in_reply_to=in_reply_to
            )
            
            if result.get('success'):
                logger.info(f"Email sent successfully: {result.get('messageId')}")
                self.log_approval_result(file_path.name, True, f"Email sent: {result.get('messageId')}")
                
                # Move to Done folder
                done_folder = self.vault_path / "Done"
                done_folder.mkdir(parents=True, exist_ok=True)
                dest_path = done_folder / file_path.name
                file_path.rename(dest_path)
                logger.info(f"Task moved to Done: {dest_path.name}")
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Email sending failed: {error_msg}")
                self.log_approval_result(file_path.name, False, error_msg)
                
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            self.log_approval_result(file_path.name, False, str(e))
    
    def call_mcp_send_email(
        self,
        recipients: list,
        subject: str,
        body: str,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call MCP server to send email.
        
        This uses a simple HTTP/subprocess approach.
        For production, use the official MCP SDK client.
        """
        import subprocess
        import json
        
        try:
            # Create a Python script to call the MCP server
            mcp_call_script = f'''
import asyncio
import sys
sys.path.insert(0, '{Path(__file__).parent.parent}')

from mcp_servers.email_sender.server import send_email

async def main():
    result = await send_email(
        recipients={json.dumps(recipients)},
        subject={json.dumps(subject)},
        body={json.dumps(body)},
        thread_id={json.dumps(thread_id) if thread_id else 'None'},
        in_reply_to={json.dumps(in_reply_to) if in_reply_to else 'None'}
    )
    print(json.dumps(result))

asyncio.run(main())
'''
            
            # Write temp script
            temp_script = Path('/tmp/mcp_email_call.py')
            temp_script.write_text(mcp_call_script)
            
            # Execute script
            result = subprocess.run(
                ['python', str(temp_script)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse result
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return {
                    'success': False,
                    'error': f"MCP call failed: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'MCP server timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def log_approval_result(self, task_name: str, success: bool, message: str):
        """Log approval processing result."""
        log_file = self.logs_dir / "approval_results.log"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task_name,
            "success": success,
            "message": message
        }
        
        with open(log_file, "a") as f:
            f.write(f"{log_entry}\n")
        
        logger.info(f"Approval result logged: {task_name} - {'SUCCESS' if success else 'FAILED'}")


def main():
    """Main entry point."""
    vault_path = Path("AI_Employee_Vault")
    
    if not vault_path.exists():
        logger.error(f"Vault path not found: {vault_path}")
        return
    
    approved_folder = vault_path / "Approved"
    approved_folder.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting approval processor, watching: {approved_folder}")
    
    # Setup watchdog observer
    event_handler = ApprovalHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, str(approved_folder), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping approval processor...")
        observer.stop()
    
    observer.join()
    logger.info("Approval processor stopped")


if __name__ == "__main__":
    main()
