# LinkedIn MCP Server Setup Guide

## Overview

The LinkedIn MCP Server enables automated LinkedIn messaging via Selenium browser automation.

⚠️ **WARNING**: Automated LinkedIn actions may violate LinkedIn's Terms of Service. Use at your own risk!

---

## Installation

### 1. Dependencies Already Installed

The following are already installed as part of Silver Tier:
- `selenium` - Browser automation
- `beautifulsoup4` - HTML parsing
- `mcp` - MCP server framework

### 2. Configure Credentials

Edit `.env` file with your LinkedIn credentials:

```bash
# LinkedIn Credentials
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Session path (Chrome profile storage)
LINKEDIN_SESSION_PATH=AI_Employee_Vault/.linkedin_session

# Vault path
VAULT_PATH=AI_Employee_Vault
```

---

## Usage

### Option 1: Run as Standalone MCP Server

```bash
# Start LinkedIn MCP server
python mcp_servers/linkedin_sender/server.py
```

### Option 2: Configure in Claude Code

Add to your Claude Code MCP configuration (`~/.config/claude-code/mcp.json`):

```json
{
  "mcpServers": {
    "linkedin-sender": {
      "command": "python",
      "args": ["/home/hunain/personal-ai-employee/mcp_servers/linkedin_sender/server.py"],
      "env": {
        "LINKEDIN_USERNAME": "your_email@example.com",
        "LINKEDIN_PASSWORD": "your_password",
        "LINKEDIN_SESSION_PATH": "AI_Employee_Vault/.linkedin_session"
      }
    }
  }
}
```

---

## Available Tools

### 1. `send_linkedin_message`

Send a LinkedIn message to a connection.

**Parameters:**
- `recipient` (string): Name of the LinkedIn connection
- `message` (string): Message text (max 3000 characters)

**Example:**
```bash
claude "Send LinkedIn message using MCP server:
Recipient: Hunain Naeem Anwar
Message: Hi! Thanks for connecting. Looking forward to staying in touch."
```

**Returns:**
```json
{
  "success": true,
  "recipient": "Hunain Naeem Anwar",
  "message_length": 62,
  "timestamp": "2026-03-13T01:45:00",
  "sent_at": "2026-03-13T01:45:03"
}
```

### 2. `test_linkedin_connection`

Test LinkedIn connection and login status.

**Example:**
```bash
claude "Test LinkedIn connection"
```

**Returns:**
```json
{
  "connected": true,
  "logged_in": true,
  "username": "your_email@example.com",
  "timestamp": "2026-03-13T01:45:00"
}
```

---

## Complete Workflow Example

### Scenario: Process LinkedIn Messages

```bash
# 1. Triage inbox
claude "Triage inbox - move all files to Needs_Action with priority"

# 2. Process tasks
claude "Process all LinkedIn messages in Needs_Action"

# Qwen will:
# - Read each message
# - Draft appropriate response
# - Use MCP server to send reply
# - Move task to Done after sending
# - Log to /Logs/linkedin_sent.log
```

### Manual Send Command

```bash
# Send specific message
claude "Use linkedin-sender MCP to send:
Recipient: John Doe
Message: Hi John, great connecting with you!"
```

---

## How It Works

### 1. First Login (Manual)

```
Start MCP server
  ↓
Opens LinkedIn in headless Chrome
  ↓
You login manually (first time only)
  ↓
Session saved to .linkedin_session/
  ↓
Future runs auto-login ✅
```

### 2. Sending Messages

```
Receive send_linkedin_message() call
  ↓
Check if logged in (auto-login if needed)
  ↓
Navigate to LinkedIn Messaging
  ↓
Search for recipient by name
  ↓
Click on conversation
  ↓
Type message (human-like typing)
  ↓
Click send button
  ↓
Log to /Logs/linkedin_sent.log
  ↓
Return success/failure
```

---

## Logging

All sent messages are logged to:

```
AI_Employee_Vault/Logs/linkedin_sent.log
```

**Format:**
```
2026-03-13T01:45:03 - Sent to Hunain Naeem Anwar
2026-03-13T01:50:12 - Sent to John Doe
```

---

## Troubleshooting

### Issue: "Failed to login to LinkedIn"

**Solution:**
1. Check credentials in `.env`
2. Try manual login first:
   ```bash
   python -c "from mcp_servers.linkedin_sender.server import LinkedInClient; c = LinkedInClient(); c._login()"
   ```
3. Delete session and re-login:
   ```bash
   rm -rf AI_Employee_Vault/.linkedin_session/
   python mcp_servers/linkedin_sender/server.py
   ```

### Issue: "Could not find recipient"

**Causes:**
- Recipient name doesn't match exactly
- Person is not in your connections
- LinkedIn search didn't return results

**Solution:**
- Use exact name as it appears on LinkedIn
- Ensure you're connected with the person
- Try shorter name (e.g., "John" instead of "John Smith")

### Issue: "Message not sending"

**Possible causes:**
- LinkedIn rate limiting
- Browser automation detected
- Network issues

**Solution:**
- Wait 5-10 minutes between messages
- Check LinkedIn for CAPTCHA
- Verify internet connection

---

## ⚠️ Safety Guidelines

### To Reduce Ban Risk:

1. **Limit Daily Messages**: Send max 20-30 messages/day
2. **Add Delays**: Wait 2-5 minutes between messages
3. **Human-Like**: Use natural language, vary message length
4. **Avoid Spam**: Don't send identical messages repeatedly
5. **Monitor Account**: Check for LinkedIn warnings/restrictions

### When NOT to Use:

- ❌ Sending to people you're not connected with
- ❌ Bulk messaging campaigns
- ❌ Automated connection requests + messages
- ❌ Messages with links/URLs (looks like spam)

---

## Alternative: Manual Send

If you prefer not to use automation:

```bash
# 1. Qwen drafts response
claude "Process LinkedIn messages"

# 2. Qwen shows draft:
"Draft reply to Hunain: 'Hi! Thanks for reaching out...'"

# 3. You copy draft, open LinkedIn, paste & send manually

# 4. Tell Qwen:
claude "I sent the reply. Move to Done."
```

---

## API Reference

### `send_linkedin_message(recipient, message)`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| recipient | string | Yes | LinkedIn connection name |
| message | string | Yes | Message text (max 3000 chars) |

**Returns:**
```typescript
{
  success: boolean
  recipient: string
  message_length: number
  timestamp: string (ISO 8601)
  sent_at?: string (ISO 8601)
  error?: string
}
```

**Errors:**
- `"Recipient name is required"` - Empty recipient
- `"Message is required"` - Empty message
- `"Message exceeds 3000 character limit"` - Too long
- `"Failed to login to LinkedIn"` - Auth failed
- `"Could not find recipient"` - Search failed

---

## Support

- **Logs**: Check `/Logs/linkedin_sent.log`
- **Debug**: Run with `--verbose` flag
- **Issues**: Check Selenium console output

---

*Last updated: 2026-03-13*
*Version: 1.0.0*
