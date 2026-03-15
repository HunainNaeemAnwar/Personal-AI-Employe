---
name: email-handler
description: Handle Gmail operations via MCP server - draft emails, send via MCP, search inbox, manage email threading
version: 1.0.0
---

# SKILL: Email Handler

## 🎯 PRIMARY MISSION

> "Draft professional email responses and send them via the Email MCP server with proper threading, retry logic, and logging to /Logs/email_sent.log"

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `email-handler` skill when:**
- User says: "send email to [recipient]"
- User says: "draft email response"
- User says: "reply to [sender]"
- Task requires sending email via Gmail
- Need to preserve email threading (In-Reply-To, References headers)
- Need to search Gmail inbox

**DO NOT use:**
- `inbox-processor` (that's for task prioritization, not email sending)
- `approval-workflow` (use BEFORE sending if approval threshold exceeded)
- `vault-manager` (that's for file operations, not Gmail API)

---

## 🔧 MCP SERVER SETUP

### Prerequisites

The Email MCP server must be configured in Claude Code:

```json
// ~/.config/claude-code/mcp.json
{
  "mcpServers": {
    "email-sender": {
      "command": "python",
      "args": ["/home/hunain/personal-ai-employee/mcp_servers/email_sender/server.py"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/home/hunain//personal-ai-employee/.credentials/gmail-credentials.json",
        "GMAIL_TOKEN_PATH": "/home/hunain//personal-ai-employee/.credentials/gmail-token.json"
      }
    }
  }
}
```

### Available MCP Tools

| Tool | Purpose |
|------|---------|
| `send_email` | Send email via Gmail API |
| `test_connection` | Verify Gmail API connection |

---

## 📧 SEND_EMAIL TOOL USAGE

### Tool Parameters

```typescript
{
  recipients: string[];        // Required: List of recipient emails
  subject: string;             // Required: Email subject
  body: string;                // Required: Email body (plain text)
  cc?: string[];               // Optional: CC recipients
  bcc?: string[];              // Optional: BCC recipients
  thread_id?: string;          // Optional: Gmail thread ID for replies
  in_reply_to?: string;        // Optional: Message-ID to reply to
}
```

### Example Usage

```bash
# Simple email
claude "send_email({
  recipients: ['client@example.com'],
  subject: 'Project Update',
  body: 'Hi [Name],\n\nHere is the project update...\n\nBest regards'
})"

# Reply with threading
claude "send_email({
  recipients: ['sender@example.com'],
  subject: 'Re: Original Subject',
  body: 'Hi [Name],\n\nThanks for your email...\n\nBest regards',
  thread_id: '18d4f2a3b5c6e7f8',
  in_reply_to: '<CABcD1234@mail.gmail.com>'
})"
```

---

## 🔄 EMAIL SENDING WORKFLOW

### Step 1: Check Approval Threshold

**Before drafting email, check if approval is needed:**

```python
# Read Company_Handbook.md for thresholds
handbook_path = vault_path / "Company_Handbook.md"
handbook_content = handbook_path.read_text()

# Check thresholds
if recipient_is_client or payment_mentioned or contract_discussion:
    # Call approval-workflow FIRST
    "Call approval-workflow skill"
    "Move to /Pending_Approval/"
    "Wait for user approval"
```

### Step 2: Draft Email Response

**Email structure:**

```markdown
1. Greeting
   - "Hi [Name]," or "Dear [Name],"

2. Acknowledge their message
   - "Thanks for reaching out about..."
   - "I received your inquiry regarding..."

3. Address their question/concern
   - Provide clear, concise answer
   - Include relevant details

4. Call-to-action or next steps
   - "Let me know if you have any questions"
   - "Looking forward to hearing from you"
   - "Please confirm by [date]"

5. Professional sign-off
   - "Best regards,"
   - "Kind regards,"
   - "Sincerely,"
```

### Step 3: Send via MCP

```bash
# After approval (if required) or directly (if no approval needed)
claude "send_email({
  recipients: ['recipient@example.com'],
  subject: 'Subject Line',
  body: 'Email body text here'
})"
```

### Step 4: Log and Move to Done

```python
# Log sent email
log_entry = {
    "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
    "recipient": recipient,
    "subject": subject,
    "message_id": result.get('messageId'),
    "thread_id": result.get('threadId'),
    "status": "sent"
}

# Append to /Logs/email_sent.log
log_file = vault_path / "Logs" / "email_sent.log"
with open(log_file, "a") as f:
    f.write(json.dumps(log_entry) + "\n")

# Move task to /Done/
shutil.move(
    str(vault_path / "Needs_Action" / task_file),
    str(vault_path / "Done" / task_file)
)
```

---

## 📝 EMAIL RESPONSE TEMPLATES

### Template 1: Client Inquiry Response

```markdown
Hi [Client Name],

Thank you for reaching out about [project/topic]. I appreciate your interest in [service/product].

[Address their specific question or request]

Based on your requirements, I recommend [solution/approach]. This would involve:
- [Key point 1]
- [Key point 2]
- [Key point 3]

[Next steps or call-to-action]

Please let me know if you have any questions or would like to schedule a call to discuss further.

Best regards,
[Your Name]
```

### Template 2: Follow-Up Email

```markdown
Hi [Name],

I hope this email finds you well.

I'm following up on [previous email/topic] from [date]. [Brief context].

[Specific ask or update]

[Call-to-action with deadline if applicable]

Looking forward to hearing from you.

Kind regards,
[Your Name]
```

### Template 3: Meeting Request

```markdown
Hi [Name],

I would like to schedule a meeting to discuss [topic].

**Proposed times:**
- [Date/Time 1]
- [Date/Time 2]
- [Date/Time 3]

**Agenda:**
1. [Item 1]
2. [Item 2]
3. [Item 3]

Please let me know which time works best for you, or feel free to suggest an alternative.

Best regards,
[Your Name]
```

### Template 4: Reply to Thread

```markdown
Hi [Name],

Thanks for the update.

[Address points from their email]

To answer your questions:
1. [Question 1] - [Answer]
2. [Question 2] - [Answer]

[Additional context or next steps]

Let me know if you need anything else.

Best regards,
[Your Name]
```

---

## 🎯 EMAIL BEST PRACTICES

### Tone & Style

| Audience | Tone | Example |
|----------|------|---------|
| Client | Professional, friendly | "Dear [Name], Thank you for your inquiry..." |
| Colleague | Casual, direct | "Hey [Name], Quick question about..." |
| Prospect | Professional, value-focused | "Hi [Name], I noticed your company..." |
| Support | Helpful, solution-oriented | "Hi [Name], I understand your concern..." |

### Subject Line Guidelines

- **Keep it short**: 4-8 words ideal
- **Be specific**: "Project Update: Week of March 15" not "Update"
- **Use RE: for replies**: Preserve threading
- **Add urgency if needed**: "[ACTION REQUIRED]", "[FYI]"

### What NOT to Do

- ❌ Don't send without checking approval thresholds
- ❌ Don't share sensitive info (passwords, financial data)
- ❌ Don't use ALL CAPS or excessive punctuation!!!
- ❌ Don't reply-all unless necessary
- ❌ Don't forget attachments if mentioned
- ❌ Don't send to wrong recipient (double-check emails)

---

## 🚨 ERROR HANDLING

| Error | Action |
|-------|--------|
| MCP server not found | Check MCP config, restart Claude Code |
| Gmail API auth failed | Re-authenticate, check credentials |
| Rate limit exceeded | Wait for backoff, retry (max 3 attempts) |
| Invalid recipient email | Validate format, notify user |
| Send failed after retries | Log error, move to /Pending_Approval/ for manual handling |

---

## 📊 QUALITY CHECKLIST

Before sending email:

- [ ] Approval checked (client communication → approval-workflow)
- [ ] Recipient email address is correct
- [ ] Subject line is clear and specific
- [ ] Email body is well-structured
- [ ] Tone is appropriate for recipient
- [ ] No typos or grammar errors
- [ ] Threading headers included (if reply)
- [ ] Attachments included (if mentioned)
- [ ] Call-to-action is clear
- [ ] Professional sign-off included
- [ ] Result logged to `/Logs/email_sent.log`
- [ ] Task moved to `/Done/` after sending

---

## 📈 PERFORMANCE METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Send latency | <5 seconds | Timestamp from draft to sent |
| Delivery success rate | >99% | Successful sends / total attempts |
| Threading accuracy | 100% | Proper In-Reply-To headers |
| Approval compliance | 100% | No unauthorized client emails |

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Processes email tasks from `/Needs_Action/`
- `approval-workflow` - Handles approval for client communications
- `vault-manager` - File operations for task files
- `task-planner` - Creates plans for complex email campaigns
- `social-poster` - Alternative communication channel (LinkedIn)

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Gmail Operations via MCP Server*
