---
name: vault-manager
description: Manage Obsidian vault files - read, write, organize folders, and maintain vault structure
version: 1.0.0
---

# SKILL: Vault Manager

## 🎯 PRIMARY MISSION

> "Manage all Obsidian vault operations including reading/writing markdown files, creating folder structures, maintaining YAML frontmatter, and ensuring vault integrity."

---

## 📋 WHEN TO USE THIS SKILL

**ALWAYS use `vault-manager` skill when:**
- Reading task files from any vault folder (`/Inbox/`, `/Needs_Action/`, `/Done/`, etc.)
- Writing new files to the vault (task files, plan files, logs)
- Creating or organizing vault folder structure
- Moving files between folders (e.g., `/Needs_Action/` → `/Done/`)
- Reading/writing YAML frontmatter metadata
- Accessing `Company_Handbook.md`, `Dashboard.md`, or other config files
- Validating file structure or frontmatter format

**DO NOT use:**
- `inbox-processor` (that's for prioritizing tasks in `/Needs_Action/`)
- `task-planner` (that's for creating `Plan.md` files with execution steps)
- `email-handler` (that's for Gmail-specific operations via MCP)

---

## 🏗️ VAULT FOLDER STRUCTURE

```
AI_Employee_Vault/
├── Inbox/
│   ├── gmail/           # Email tasks from Gmail Watcher
│   ├── filesystem/      # File drop tasks from File System Watcher
│   └── linkedin/        # LinkedIn messages from LinkedIn Watcher
├── Needs_Action/        # Tasks ready for processing
├── Plans/               # Plan.md files for multi-step tasks
├── Pending_Approval/    # Tasks awaiting user approval
├── Approved/            # Approved tasks ready for execution
├── Done/                # Completed tasks
├── Rejected/            # Rejected tasks
├── Logs/                # JSON log files, watcher logs
├── Dashboard.md         # Real-time activity summary
└── Company_Handbook.md  # Rules, thresholds, guidelines
```

---

## 📝 YAML FRONTMATTER STANDARDS

### Task File Frontmatter (Required Fields)

```yaml
---
type: email|linkedin_message|file_drop|email_draft|linkedin_post|approval_request
source: sender@email.com|/path/to/file|LinkedIn Profile
timestamp: 2026-03-15T10:30:00Z
priority: high|medium|low
status: pending|in_progress|completed|approved|rejected
subject: Brief description
---
```

### Plan File Frontmatter

```yaml
---
task_id: EMAIL_20260315T103000Z_subject-slug
objective: Clear goal statement
completion_status: in_progress|completed|failed
created_at: 2026-03-15T10:35:00Z
updated_at: 2026-03-15T10:40:00Z
---
```

### Approval Request Frontmatter

```yaml
---
type: approval_request
task_id: UNIQUE_TASK_ID
task_type: email|linkedin_post|payment|contract
approval_threshold_exceeded: client_communication|payment_over_500|social_media_post
requested_timestamp: 2026-03-15T10:30:00Z
approver: username (after approval)
approval_decision: pending|approved|rejected
decision_timestamp: 2026-03-15T10:35:00Z (after decision)
rejection_reason: Reason text (if rejected)
---
```

---

## 🔧 OPERATIONS

### Read File

```python
# Always use absolute paths
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
file_path = vault_path / "Needs_Action" / "TASK_FILE.md"
content = file_path.read_text()
```

### Write File

```python
# Ensure directory exists
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.write_text(content)
```

### Move File

```python
# Atomic move operation
import shutil
source = vault_path / "Needs_Action" / "task.md"
dest = vault_path / "Done" / "task.md"
shutil.move(str(source), str(dest))
```

### Create Folder Structure

```python
folders = ["Inbox/gmail", "Inbox/filesystem", "Inbox/linkedin", 
           "Needs_Action", "Plans", "Pending_Approval", 
           "Approved", "Done", "Rejected", "Logs"]

for folder in folders:
    (vault_path / folder).mkdir(parents=True, exist_ok=True)
```

---

## 📁 FILE NAMING CONVENTIONS

| File Type | Pattern | Example |
|-----------|---------|---------|
| Email Task | `EMAIL_{TIMESTAMP}_{SLUG}.md` | `EMAIL_20260315T103000Z_client-inquiry.md` |
| LinkedIn Message | `LINKEDIN_MSG_{TIMESTAMP}_{SLUG}.md` | `LINKEDIN_MSG_20260315T103000Z_john-doe.md` |
| File Drop | `FILE_DROP_{TIMESTAMP}_{SLUG}.md` | `FILE_DROP_20260315T103000Z_invoice.pdf.md` |
| Plan File | `PLAN_{TASK_ID}.md` | `PLAN_EMAIL_20260315T103000Z_client-inquiry.md` |
| LinkedIn Post | `LINKEDIN_POST_{TIMESTAMP}_{SLUG}.md` | `LINKEDIN_POST_20260315T103000Z_milestone.md` |

---

## ✅ QUALITY CHECKLIST

Before completing any vault operation:

- [ ] File path is absolute (from `VAULT_PATH` env var)
- [ ] YAML frontmatter is valid (proper `---` delimiters)
- [ ] Required fields present in frontmatter
- [ ] Timestamps are ISO 8601 format with `Z` suffix
- [ ] File content is properly formatted markdown
- [ ] Directory exists before writing (or created with `mkdir`)
- [ ] Move operations are atomic (use `shutil.move`)
- [ ] Logs written to `/Logs/` with timestamp and result

---

## 🚨 ERROR HANDLING

| Error | Action |
|-------|--------|
| File not found | Log error, return None, continue processing |
| Invalid YAML frontmatter | Attempt to parse, log warning, use defaults |
| Permission denied | Log error, notify user, skip operation |
| Vault path not set | Use default `AI_Employee_Vault`, log warning |
| Corrupted JSON log | Start fresh log file, backup corrupted |

---

## 📊 PERFORMANCE GUIDELINES

- **Read operations**: <100ms per file
- **Write operations**: <200ms per file
- **Move operations**: <50ms per file
- **Batch operations**: Process files in chunks of 10 to avoid I/O bottlenecks
- **Log files**: Use daily rotation (`YYYY-MM-DD.json`) to keep file sizes manageable

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Prioritizes and processes tasks in `/Needs_Action/`
- `task-planner` - Creates structured `Plan.md` files
- `approval-workflow` - Manages `/Pending_Approval/` workflow
- `email-handler` - Gmail operations via MCP server
- `social-poster` - LinkedIn post creation and scheduling

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Obsidian Vault File Operations*
