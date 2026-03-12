# Inbox Workflow - Updated Architecture

## What Changed

**Before (Silver Tier):**
```
Watcher → Creates file directly in /Needs_Action/
```

**After (Updated):**
```
Watcher → Creates file in /Inbox/<source>/ → Claude triages → Moves to /Needs_Action/
```

---

## New Inbox Structure

```
AI_Employee_Vault/
├── Inbox/                    # NEW: Raw incoming items
│   ├── gmail/               # Gmail emails (subject-based filenames)
│   │   └── EMAIL_<subject-slug>.md
│   ├── filesystem/          # File drops (filename-based)
│   │   └── FILE_DROP_<filename-slug>.md
│   └── linkedin/            # LinkedIn messages (sender-based)
│       └── LINKEDIN_MSG_<sender-slug>.md
│
├── Needs_Action/            # Tasks ready for processing
├── Pending_Approval/        # Awaiting approval
├── Done/                    # Completed tasks
└── ...
```

---

## File Naming Convention

### Gmail Emails
**Format**: `EMAIL_<subject-slug>.md`

**Examples**:
- `EMAIL_project-proposal-meeting.md`
- `EMAIL_urgent-invoice-123.md`
- `EMAIL_no-subject.md`

### File Drops
**Format**: `FILE_DROP_<filename-slug>.md`

**Examples**:
- `FILE_DROP_contract-pdf.md`
- `FILE_DROP_budget-2026-xlsx.md`

### LinkedIn Messages
**Format**: `LINKEDIN_MSG_<sender-slug>.md`

**Examples**:
- `LINKEDIN_MSG_john-doe.md`
- `LINKEDIN_MSG_jane-smith-recruiter.md`

---

## Complete Workflow

### 1. Email Arrives
```
Gmail Watcher detects email (every 60s)
  ↓
Creates: /Inbox/gmail/EMAIL_<subject>.md
  ↓
File contains: From, Subject, Body, Priority
```

### 2. Triage (Claude)
```
Claude checks /Inbox/ folders
  ↓
Reads each file, assesses priority
  ↓
If action needed → Move to /Needs_Action/
If spam/FYI → Move to /Done/ or /Rejected/
```

### 3. Processing (You + Claude)
```
You see task in /Needs_Action/
  ↓
Instruct Claude: "Process this email"
  ↓
Claude executes → Moves to /Done/
```

---

## Why This Is Better

| Aspect | Old (Direct to Needs_Action) | New (Inbox First) |
|--------|------------------------------|-------------------|
| **Organization** | All files mixed together | Separated by source |
| **Naming** | Timestamp-based (hard to read) | Subject-based (readable) |
| **Triage** | No filtering | Claude filters spam/FYI |
| **Duplicates** | Possible | Prevented by subject matching |
| **Search** | Hard to find specific email | Search by subject name |
| **Review** | Everything demands attention | Triage first, then act |

---

## Commands

### Triage Inbox
```bash
# Triage all inbox folders
claude "Triage inbox - move all files to Needs_Action"

# Triage specific folder
claude "Triage Gmail inbox only"

# Check inbox count
claude "How many items in Inbox?"
```

### Check Inbox Status
```bash
# List Gmail items
ls AI_Employee_Vault/Inbox/gmail/

# List file drops
ls AI_Employee_Vault/Inbox/filesystem/

# List LinkedIn messages
ls AI_Employee_Vault/Inbox/linkedin/
```

---

## Updated Skills

### New: inbox-triage Skill
**Location**: `.claude/skills/inbox-triage/SKILL.md`

**Purpose**: Automatically triage inbox items and move to Needs_Action

**Features**:
- Priority assessment (high/medium/low)
- Source-based filtering
- Duplicate detection
- Triage reporting

---

## Testing

### Test Gmail Watcher
```bash
# Start watcher
python -m watchers.gmail_watcher

# Send test email to yourself
# Check: AI_Employee_Vault/Inbox/gmail/EMAIL_*.md
```

### Test Filesystem Watcher
```bash
# Drop file in watch directory
cp test.pdf AI_Employee_Dropbox/

# Check: AI_Employee_Vault/Inbox/filesystem/FILE_DROP_*.md
```

### Test LinkedIn Watcher
```bash
# Start watcher
python -m watchers.linkedin_watcher

# Send LinkedIn message
# Check: AI_Employee_Vault/Inbox/linkedin/LINKEDIN_MSG_*.md
```

---

## Migration

### Existing Files in Needs_Action

Files already in `/Needs_Action/` will continue to work. No migration needed.

### Going Forward

All NEW files from watchers will be created in `/Inbox/<source>/`

---

## Summary

**Inbox** = Raw incoming items (like your email inbox)  
**Needs_Action** = Prioritized task list (like your todo list)

This separation makes the system more organized and easier to manage!
