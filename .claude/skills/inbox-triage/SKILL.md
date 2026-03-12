---
name: inbox-triage
description: Triage inbox items and move to Needs_Action for processing
version: 1.0.0
---

# Inbox Triage Skill

## Purpose

Files created by watchers are stored in `/Inbox/<source>/` folders. This skill triages those files and moves them to `/Needs_Action/` for processing.

## Inbox Structure

```
AI_Employee_Vault/Inbox/
├── gmail/
│   └── EMAIL_<subject-slug>.md
├── filesystem/
│   └── FILE_DROP_<filename-slug>.md
└── linkedin/
    └── LINKEDIN_MSG_<sender-slug>.md
```

## Triage Workflow

### Step 1: Check Inbox Folders

List files in each inbox subfolder:
```bash
ls AI_Employee_Vault/Inbox/gmail/
ls AI_Employee_Vault/Inbox/filesystem/
ls AI_Employee_Vault/Inbox/linkedin/
```

### Step 2: Review Each File

For each file in Inbox:

1. **Read the file** to understand content
2. **Determine priority** based on:
   - **High**: Urgent keywords, client emails, deadlines
   - **Medium**: Regular communications, important files
   - **Low**: Newsletters, notifications, FYI items

3. **Check if action is needed**:
   - If NO action needed (FYI only) → Move to `/Done/`
   - If action needed → Move to `/Needs_Action/`

### Step 3: Move to Needs_Action

For files requiring action:

```bash
# Move from Inbox to Needs_Action
mv AI_Employee_Vault/Inbox/gmail/EMAIL_*.md AI_Employee_Vault/Needs_Action/
mv AI_Employee_Vault/Inbox/filesystem/FILE_DROP_*.md AI_Employee_Vault/Needs_Action/
mv AI_Employee_Vault/Inbox/linkedin/LINKEDIN_MSG_*.md AI_Employee_Vault/Needs_Action/
```

### Step 4: Add Triage Notes (Optional)

Add triage metadata to the file:

```markdown
---
triaged_at: 2026-03-12T12:00:00Z
triage_priority: high
triage_notes: "Client email - respond within 4 hours"
---
```

## ⚠️ IMPORTANT: Execution Rules

**DO NOT move to /Done/ until action is ACTUALLY completed:**

| Task Type | When to Move to Done |
|-----------|---------------------|
| Email reply | ✅ AFTER sending via Gmail MCP |
| LinkedIn message | ✅ AFTER sending via LinkedIn |
| File processing | ✅ AFTER file is processed/extracted |
| FYI/Informational | ✅ Immediately (no action needed) |

**Wrong Workflow** ❌:
```
Read message → Draft response → Move to Done
                          ↓
                  (Never actually sent!)
```

**Correct Workflow** ✅:
```
Read message → Draft response → Execute (send) → Move to Done
                                    ↓
                          Actually send the message!
```

## Execution Commands

### For LinkedIn Messages:
```bash
# 1. Draft response (in task file)
# 2. Send via LinkedIn MCP Server
claude "Send LinkedIn message using MCP server"

# MCP will:
# - Login to LinkedIn (if not already)
# - Find the recipient
# - Send the drafted message
# - Log to /Logs/linkedin_sent.log

# 3. After sending confirmed, move to Done
mv AI_Employee_Vault/Needs_Action/linkedin/LINKEDIN_MSG_*.md AI_Employee_Vault/Done/linkedin/
```

**Example MCP Command:**
```bash
claude "Use linkedin-sender MCP to send this message:
Recipient: Hunain Naeem Anwar
Message: Hi! Thanks for reaching out. How can I help you today?"
```

### For Email Replies:
```bash
# 1. Draft response
# 2. Send via Email MCP Server
claude "Send email using MCP: [draft content]"

# 3. After sending, move to Done
```

## Priority Guidelines

### High Priority (Process Immediately)
- Client emails with deadlines
- Keywords: urgent, asap, deadline, critical, emergency
- Financial matters (invoices, payments)
- Legal documents requiring signature

### Medium Priority (Process Within 24 Hours)
- Regular client communications
- Internal team requests
- Document reviews
- Important file attachments (PDF, DOCX, XLSX)

### Low Priority (Process When Convenient)
- Newsletters and informational emails
- Non-urgent updates
- General inquiries
- FYI notifications

## Automation Rule

**Run this triage automatically when:**
1. New files appear in any `/Inbox/` folder
2. User runs: `claude "Triage inbox"`
3. Scheduled triage time (e.g., every hour)

## Example Commands

```bash
# Triage all inbox folders
claude "Triage inbox - move all files to Needs_Action with priority assessment"

# Triage specific folder
claude "Triage Gmail inbox only"

# Check inbox status
claude "How many items are in Inbox?"
```

## Triage Report Format

After triage, create a summary:

```markdown
## Triage Report - 2026-03-12 12:00

### Processed
- Gmail: 3 files → Moved to Needs_Action
- Filesystem: 1 file → Moved to Needs_Action
- LinkedIn: 2 files → Moved to Needs_Action

### Priority Breakdown
- High: 2 items
- Medium: 3 items
- Low: 1 item

### Next Actions
- 2 items require immediate attention
- 3 items scheduled for today
- 1 item can wait
```

## Important Notes

1. **Never delete inbox files** - Always move to Done/Rejected if no action needed
2. **Preserve filenames** - Don't rename during triage
3. **Add context** - Include triage notes for complex items
4. **Check duplicates** - If same item already in Needs_Action, skip

## Error Handling

If file move fails:
1. Log error to `/Logs/triage_errors.log`
2. Keep file in Inbox
3. Retry on next triage cycle
4. Alert user if persistent failures

---

**Mnemonic**: Inbox = Raw incoming | Needs_Action = Ready to work
