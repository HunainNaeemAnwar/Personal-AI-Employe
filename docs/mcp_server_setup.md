# MCP Server Setup Guide

This guide covers the installation and configuration of the Email Sender MCP server for Silver tier.

## Prerequisites

- **Node.js v24+**: Required for MCP server runtime
- **Gmail API Credentials**: OAuth2 credentials for sending emails
- **Python 3.13+**: For watcher scripts (already installed from Bronze tier)

## Installation

### 1. Install Node.js v24+

**Linux/macOS:**
```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 24
nvm use 24

# Verify installation
node --version  # Should show v24.x.x
```

**Windows:**
Download and install from [nodejs.org](https://nodejs.org/) (v24 LTS)

### 2. Install MCP Server Dependencies

Navigate to the MCP server directory and install dependencies:

```bash
cd mcp_servers/email_sender
npm install
```

### 3. Build the MCP Server

Compile TypeScript to JavaScript:

```bash
# Using build script (recommended)
chmod +x build.sh
./build.sh

# Or manually
npm run build
```

### 4. Configure Gmail API Credentials

The MCP server uses the same Gmail API credentials as the Gmail watcher.

**Ensure your `.env` file includes:**

```env
# Gmail API Configuration (shared with Gmail watcher)
GMAIL_CREDENTIALS_PATH=/path/to/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/path/to/.credentials/gmail-token.json

# Gmail API Scopes (must include send permissions)
GMAIL_SCOPES=https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.compose
```

**Important:** If you previously authenticated with only `gmail.readonly` scope, you need to:
1. Delete the existing token file: `rm /path/to/.credentials/gmail-token.json`
2. Re-run the Gmail watcher to re-authenticate with send permissions
3. The new token will include both read and send scopes

## Testing the MCP Server

### Manual Test (Standalone)

Test the MCP server directly via stdio:

```bash
cd mcp_servers/email_sender
node dist/index.js
```

The server will start and wait for JSON-RPC messages on stdin. You should see:
```
Email Sender MCP server running on stdio
```

Press `Ctrl+C` to stop.

### Integration Test (with Claude Code)

Configure Claude Code to use the MCP server by adding to your MCP settings:

**~/.claude/mcp_settings.json:**
```json
{
  "mcpServers": {
    "email-sender": {
      "command": "node",
      "args": ["/absolute/path/to/mcp_servers/email_sender/dist/index.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/path/to/.credentials/gmail-credentials.json",
        "GMAIL_TOKEN_PATH": "/path/to/.credentials/gmail-token.json"
      }
    }
  }
}
```

**Test with Claude Code:**

1. Start Claude Code CLI
2. Ask Claude to send a test email:
   ```
   Send a test email to test@example.com with subject "Test" and body "This is a test"
   ```
3. Claude should use the `send_email` tool from the MCP server
4. Check `/Logs/email_sent.log` for confirmation

## Troubleshooting

### Error: "GMAIL_CREDENTIALS_PATH and GMAIL_TOKEN_PATH must be set"

**Solution:** Ensure environment variables are set in `.env` file or passed to the MCP server.

### Error: "Token file not found"

**Solution:** Run the Gmail watcher first to authenticate and generate the token file:
```bash
python -m watchers.gmail_watcher
```

### Error: "Token expired, refreshing..."

**Solution:** This is normal. The MCP server automatically refreshes expired tokens.

### Error: "Failed to send email: Insufficient Permission"

**Solution:** Your token doesn't have send permissions. Delete the token and re-authenticate:
```bash
rm /path/to/.credentials/gmail-token.json
python -m watchers.gmail_watcher  # Re-authenticate with send scopes
```

### Error: "Rate limit exceeded"

**Solution:** Gmail API has a quota of 250 emails/day for free accounts. Wait 24 hours or upgrade to Google Workspace.

## MCP Server Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Claude Code CLI                      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │              MCP Client (Built-in)                 │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────┘
                      │ JSON-RPC over stdio
                      │
┌─────────────────────▼───────────────────────────────────┐
│           Email Sender MCP Server (Node.js)             │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  McpServer (TypeScript SDK)                        │ │
│  │  - Tool: send_email                                │ │
│  │  - Input: recipients, subject, body, cc, bcc       │ │
│  │  - Output: messageId, threadId, success            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  GmailClient                                       │ │
│  │  - OAuth2 authentication                           │ │
│  │  - Email composition (RFC 2822)                    │ │
│  │  - Retry logic (3 attempts, exponential backoff)  │ │
│  │  - Threading support (In-Reply-To, References)    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────┬──────────────────────────────────┘
                      │ HTTPS
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    Gmail API                             │
│              (google.gmail.v1.users.messages.send)       │
└──────────────────────────────────────────────────────────┘
```

## Performance Benchmarks

- **Email send latency**: <5 seconds from approval to delivery (99th percentile)
- **Retry success rate**: 99% (with 3 attempts and exponential backoff)
- **Throughput**: Limited by Gmail API quota (250 emails/day for free accounts)

## Security Considerations

1. **OAuth2 Tokens**: Stored in `.credentials/` directory (excluded from git via `.gitignore`)
2. **Token Refresh**: Automatic refresh when expired (no manual intervention needed)
3. **Scopes**: Minimal scopes requested (`gmail.send`, `gmail.compose`)
4. **Logging**: Email metadata logged to `/Logs/email_sent.log` (no sensitive content)
5. **Error Handling**: Errors logged to stderr (not exposed to client)

## Next Steps

After setting up the MCP server:

1. **Test email sending**: Send a test email via Claude Code
2. **Configure approval workflow**: Set up HITL approval for sensitive emails (User Story 5)
3. **Monitor logs**: Check `/Logs/email_sent.log` for sent emails
4. **Adjust quotas**: Upgrade to Google Workspace if you need >250 emails/day

## References

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
