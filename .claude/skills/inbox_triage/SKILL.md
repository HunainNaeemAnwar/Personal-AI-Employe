---
name: inbox-triage
description: Move files from /Inbox/ subfolders to /Needs_Action/, assess initial priority, and prepare for processing
version: 1.0.0
---

# SKILL: Inbox Triage

## 🎯 PRIMARY MISSION

> "Process files created by watchers in `/Inbox/{source}/` folders, validate YAML frontmatter, assess initial priority, and move them to `/Needs_Action/` for further processing by `inbox-processor` skill."

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `inbox-triage` skill when:**
- User says: "triage inbox"
- User says: "process inbox"
- User says: "check inbox"
- Files exist in `/Inbox/gmail/`, `/Inbox/filesystem/`, or `/Inbox/linkedin/`
- Need to move files from `/Inbox/` → `/Needs_Action/`
- Watchers have created new task files overnight

**DO NOT use:**
- `inbox-processor` (that's for tasks ALREADY in `/Needs_Action/`)
- `vault-manager` (that's for general file operations, not inbox-specific triage)
- `approval-workflow` (that's for approval routing, use AFTER triage)

---

## 🔄 INBOX TRIAGE WORKFLOW

### Step 1: Scan All Inbox Subfolders

```python
# Scan all inbox subfolders
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
inbox_dir = vault_path / "Inbox"

# Get all source subfolders
source_folders = ["gmail", "filesystem", "linkedin"]

all_task_files = []
for source in source_folders:
    source_dir = inbox_dir / source
    if source_dir.exists():
        task_files = list(source_dir.glob("*.md"))
        all_task_files.extend(task_files)

print(f"Found {len(all_task_files)} files in /Inbox/")
```

### Step 2: Validate YAML Frontmatter

```python
import yaml

def validate_task_file(file_path: Path) -> tuple[bool, dict]:
    """Validate task file has required frontmatter fields."""
    
    content = file_path.read_text()
    
    # Check for YAML frontmatter delimiters
    if not content.startswith('---'):
        return False, {"error": "Missing YAML frontmatter"}
    
    # Parse frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, {"error": "Invalid YAML frontmatter structure"}
    
    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return False, {"error": f"YAML parse error: {e}"}
    
    # Check required fields
    required_fields = ['type', 'source', 'timestamp', 'priority', 'status']
    missing_fields = [f for f in required_fields if f not in frontmatter]
    
    if missing_fields:
        return False, {"error": f"Missing required fields: {missing_fields}"}
    
    # Validate field values
    valid_types = ['email', 'linkedin_message', 'file_drop']
    valid_priorities = ['high', 'medium', 'low']
    valid_statuses = ['pending', 'in_progress', 'completed']
    
    if frontmatter['type'] not in valid_types:
        return False, {"error": f"Invalid type: {frontmatter['type']}"}
    
    if frontmatter['priority'] not in valid_priorities:
        return False, {"error": f"Invalid priority: {frontmatter['priority']}"}
    
    if frontmatter['status'] not in valid_statuses:
        return False, {"error": f"Invalid status: {frontmatter['status']}"}
    
    return True, frontmatter
```

### Step 3: Move to /Needs_Action/

```python
import shutil
from datetime import datetime, timezone

def move_to_needs_action(file_path: Path) -> bool:
    """Move task file from /Inbox/ to /Needs_Action/"""
    
    needs_action_dir = vault_path / "Needs_Action"
    needs_action_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate new filename with triage timestamp
    content = file_path.read_text()
    frontmatter = yaml.safe_load(content.split('---')[1])
    
    # Keep original filename (watchers already use proper naming)
    new_path = needs_action_dir / file_path.name
    
    # Move file
    shutil.move(str(file_path), str(new_path))
    
    # Update frontmatter with triage metadata
    frontmatter['triaged_at'] = datetime.now(timezone.utc).isoformat() + 'Z'
    frontmatter['status'] = 'pending'
    
    # Rewrite file with updated frontmatter
    new_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    new_content += '---\n' + content.split('---')[2]
    new_path.write_text(new_content)
    
    return True
```

### Step 4: Log Triage Activity

```python
import json

def log_triage_result(source: str, filename: str, success: bool, error: str = None):
    """Log triage activity to /Logs/inbox_triage.log"""
    
    logs_dir = vault_path / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / "inbox_triage.log"
    
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat() + 'Z',
        "source": source,
        "filename": filename,
        "success": success,
        "error": error
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

---

## 📊 TRIAGE SUMMARY

After processing all files, generate a summary:

```markdown
## Inbox Triage Summary

**Date**: 2026-03-15 11:30 AM
**Total Files Processed**: 15

### By Source

| Source | Files Found | Moved to Needs_Action | Errors |
|--------|-------------|----------------------|--------|
| Gmail | 8 | 8 | 0 |
| File System | 5 | 5 | 0 |
| LinkedIn | 2 | 2 | 0 |
| **Total** | **15** | **15** | **0** |

### Priority Distribution

| Priority | Count |
|----------|-------|
| High | 3 |
| Medium | 10 |
| Low | 2 |

### Files Moved to /Needs_Action/

1. `EMAIL_20260315T083000Z_client-inquiry.md` (HIGH)
2. `EMAIL_20260315T091500Z_team-update.md` (MEDIUM)
3. `FILE_DROP_20260315T100000Z_invoice.pdf.md` (MEDIUM)
4. `LINKEDIN_MSG_20260315T103000Z_john-doe.md` (MEDIUM)
...

### Errors

None! All files processed successfully. ✓

---

**Next Step**: Run `claude "process tasks in Needs_Action"` to process triaged files.
```

---

## 🚨 ERROR HANDLING

| Error | Action |
|-------|--------|
| Missing YAML frontmatter | Log error, move to `/Logs/triage_errors/` for manual review |
| Invalid priority value | Default to 'medium', log warning, continue |
| Missing required fields | Log error, add default values, continue |
| File already in /Needs_Action/ | Skip, log as duplicate |
| Permission denied | Log error, notify user, skip file |
| Corrupted file | Move to `/Logs/triage_errors/`, log details |

---

## 📋 TRIAGE RULES

### Priority Inheritance

Watchers set initial priority based on:

**Gmail Watcher:**
- `high`: Subject contains urgent/asap/deadline/critical/important
- `medium`: Regular client emails, team communication
- `low`: Newsletters, notifications, automated emails

**File System Watcher:**
- `high`: Filename contains urgent/asap/critical
- `medium`: PDF, DOCX, XLSX files (business documents)
- `low`: TXT, LOG, other file types

**LinkedIn Watcher:**
- `high`: Connection requests from VIPs (detect by title/company)
- `medium`: Regular messages, inquiries
- `low`: Generic connection requests, spam-like messages

### Triage Time Targets

| Source | Target Time | SLA |
|--------|-------------|-----|
| Gmail | <2 minutes from receipt | 99% of emails |
| File System | <30 seconds from file drop | 95% of files |
| LinkedIn | <5 minutes from message | 90% of messages |

---

## 🔧 AUTOMATED TRIAGE (Optional)

For fully automated triage, add to `scheduled_tasks.yaml`:

```yaml
- id: "auto_triage_inbox"
  description: "Automatically triage inbox files every 5 minutes"
  schedule: "*/5 * * * *"  # Every 5 minutes
  command: "cd /home/hunain/personal-ai-employee && claude 'Triage inbox - move all files to Needs_Action with priority'"
  enabled: true
  retry_on_failure: true
  max_retries: 2
```

---

## 📝 EXAMPLE COMMANDS

```bash
# Full triage
claude "Triage inbox - move all files to Needs_Action with priority"

# Triage specific source
claude "Triage Gmail inbox only"
claude "Triage LinkedIn messages only"

# Check inbox status
claude "How many files in Inbox?"
claude "List files in Inbox/gmail/"

# Triage with summary
claude "Triage inbox and show summary"
```

---

## 📊 QUALITY CHECKLIST

Before completing inbox triage:

- [ ] All inbox subfolders scanned (`/Inbox/gmail/`, `/Inbox/filesystem/`, `/Inbox/linkedin/`)
- [ ] YAML frontmatter validated for each file
- [ ] Missing fields filled with defaults
- [ ] Files moved to `/Needs_Action/`
- [ ] Triage timestamp added to frontmatter
- [ ] Status set to 'pending'
- [ ] Triage summary generated
- [ ] Activity logged to `/Logs/inbox_triage.log`
- [ ] Errors logged and files moved to `/Logs/triage_errors/`
- [ ] User notified with next step command

---

## 📈 PERFORMANCE METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Triage latency | <1 minute per file | Timestamp from creation to move |
| Validation accuracy | 100% | All files have valid frontmatter |
| Error rate | <5% | Files with errors / total files |
| Inbox zero | Daily | No files left in /Inbox/ >24 hours |

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Processes tasks AFTER triage (in `/Needs_Action/`)
- `vault-manager` - General file operations (used internally)
- `email-handler` - Handles email tasks after processing
- `social-poster` - Handles LinkedIn tasks after processing
- `scheduler` - Can trigger automated triage every 5 minutes

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Inbox → Needs_Action Triage*
