# Data Model: Bronze Tier - Personal AI Employee Foundation

**Feature**: Bronze Tier Implementation
**Date**: 2026-03-07
**Status**: Complete

## Entity Definitions

### 1. Task File

**Description**: A markdown file representing work to be done, created by Watchers and processed by Claude Code.

**Attributes**:
- `type` (string, required): Category of task - `email`, `file_drop`, `transaction`
- `source` (string, required): Origin of task - email address or file path
- `timestamp` (ISO 8601 string, required): When task was created
- `priority` (enum, required): Urgency level - `high`, `medium`, `low`
- `status` (enum, required): Current state - `pending`, `in_progress`, `completed`
- `content` (markdown, required): Task details and context
- `suggested_actions` (list, optional): Recommended next steps

**File Location**: `/Needs_Action/` (pending), `/Done/` (completed)

**File Naming Convention**: `{TYPE}_{TIMESTAMP}_{SLUG}.md`
- Example: `EMAIL_20260307T103000Z_invoice-request.md`

**Lifecycle**:
1. Created by Watcher in `/Needs_Action/`
2. Read by Claude Code
3. Processed (Plan created in `/Plans/`)
4. Moved to `/Done/` when complete

**Validation Rules**:
- `type` must be one of: email, file_drop, transaction
- `timestamp` must be valid ISO 8601 format
- `priority` must be one of: high, medium, low
- `status` must be one of: pending, in_progress, completed
- `source` must be non-empty string
- `content` must be non-empty

**Relationships**:
- Created by: Watcher (1:N - one Watcher creates many Task Files)
- Processed by: Claude Code (N:1 - many Task Files processed by one Claude instance)
- Generates: Plan File (1:1 - one Task File generates one Plan File)

---

### 2. Watcher

**Description**: A Python process that monitors external sources and creates Task Files.

**Attributes**:
- `watcher_type` (enum, required): Type of watcher - `gmail`, `filesystem`
- `vault_path` (path, required): Absolute path to Obsidian vault
- `check_interval` (integer, required): Seconds between checks (default: 60 for Gmail, 5 for filesystem)
- `processed_items` (set, runtime): IDs of already-processed items (prevents duplicates)
- `status` (enum, runtime): Current state - `running`, `stopped`, `error`
- `last_check` (datetime, runtime): Timestamp of last successful check
- `error_count` (integer, runtime): Number of consecutive errors

**Configuration** (from .env):
- Gmail Watcher:
  - `GMAIL_CREDENTIALS_PATH`: Path to OAuth credentials
  - `GMAIL_TOKEN_PATH`: Path to stored token
  - `GMAIL_QUERY`: Search query (default: "is:unread is:important")
- Filesystem Watcher:
  - `WATCH_DIRECTORY`: Path to monitored folder
  - `FILE_EXTENSIONS`: Comma-separated list (default: "*" for all)

**Lifecycle**:
1. Initialize with configuration
2. Start monitoring loop
3. Check for new items at intervals
4. Create Task Files for new items
5. Log activity to `/Logs/`
6. Handle errors gracefully (log and continue)

**Validation Rules**:
- `vault_path` must exist and be writable
- `check_interval` must be > 0
- Gmail Watcher: credentials must be valid OAuth2
- Filesystem Watcher: watch directory must exist and be readable

**Relationships**:
- Creates: Task File (1:N - one Watcher creates many Task Files)
- Logs to: Log File (1:N - one Watcher creates many Log entries)

---

### 3. Plan File

**Description**: A markdown file in `/Plans/` describing action steps for a task, created by Claude Code.

**Attributes**:
- `objective` (string, required): What needs to be accomplished
- `steps` (list, required): Ordered action items with checkboxes
- `approval_required` (boolean, required): Whether human approval needed
- `created` (ISO 8601 string, required): When plan was created
- `related_task` (string, required): Filename of originating Task File

**File Location**: `/Plans/`

**File Naming Convention**: `PLAN_{TASK_ID}_{SLUG}.md`
- Example: `PLAN_EMAIL_20260307T103000Z_invoice-request.md`

**Lifecycle**:
1. Created by Claude Code after reading Task File
2. User reviews plan
3. If approval required, user moves to `/Pending_Approval/`
4. Otherwise, Claude executes steps
5. Moved to `/Done/` when complete

**Validation Rules**:
- `objective` must be non-empty
- `steps` must contain at least one item
- `created` must be valid ISO 8601 format
- `related_task` must reference existing Task File

**Relationships**:
- Generated from: Task File (1:1 - one Task File generates one Plan File)
- Created by: Claude Code (N:1 - many Plans created by one Claude instance)

---

### 4. Agent Skill

**Description**: A structured capability defined in SKILL.md that Claude automatically applies when relevant.

**Attributes**:
- `name` (string, required): Skill identifier (lowercase-with-hyphens)
- `description` (string, required): What skill does and when to use it (max 1024 chars)
- `instructions` (markdown, required): Step-by-step guidance
- `examples` (markdown, required): Concrete demonstrations
- `trigger_conditions` (implicit): Patterns that activate skill

**File Location**: `.claude/skills/{skill-name}/SKILL.md`

**File Structure**:
```markdown
---
name: skill-name
description: Brief description (max 1024 chars)
---

# Skill Name

## Instructions
[Step-by-step guidance]

## Examples
[Concrete demonstrations]
```

**Lifecycle**:
1. Created by developer/user
2. Auto-discovered by Claude Code on startup
3. Applied automatically when trigger conditions match
4. Updated/refined based on usage

**Validation Rules**:
- `name`: lowercase, hyphens only, max 64 chars, no reserved words (anthropic, claude)
- `description`: non-empty, max 1024 chars, no XML tags
- `instructions`: must be present and non-empty
- `examples`: must be present and non-empty
- YAML frontmatter must be valid

**Relationships**:
- Used by: Claude Code (N:1 - many Skills used by one Claude instance)
- Applies to: Task File (N:N - many Skills can apply to many Task Files)

---

### 5. Log Entry

**Description**: A JSON record of Watcher activity stored in `/Logs/YYYY-MM-DD.json`.

**Attributes**:
- `timestamp` (ISO 8601 string, required): When event occurred
- `watcher_type` (enum, required): Which watcher - `gmail`, `filesystem`
- `action` (enum, required): What happened - `check`, `create_task`, `error`
- `result` (enum, required): Outcome - `success`, `failure`
- `details` (object, optional): Additional context
- `error_message` (string, optional): Error details if result is failure

**File Location**: `/Logs/YYYY-MM-DD.json`

**File Format**: JSON array of log entries
```json
[
  {
    "timestamp": "2026-03-07T10:30:00Z",
    "watcher_type": "gmail",
    "action": "check",
    "result": "success",
    "details": {
      "emails_found": 2,
      "tasks_created": 2
    }
  }
]
```

**Lifecycle**:
1. Created by Watcher on each action
2. Appended to daily log file
3. Retained for 90 days (per constitution)
4. Rotated daily (new file each day)

**Validation Rules**:
- `timestamp` must be valid ISO 8601 format
- `watcher_type` must be one of: gmail, filesystem
- `action` must be one of: check, create_task, error
- `result` must be one of: success, failure
- If `result` is failure, `error_message` should be present

**Relationships**:
- Created by: Watcher (N:1 - many Log Entries created by one Watcher)

---

## Entity Relationship Diagram

```
┌─────────────┐
│   Watcher   │
│             │
│ - type      │
│ - vault_path│
│ - interval  │
└──────┬──────┘
       │ creates (1:N)
       ▼
┌─────────────┐      generates (1:1)      ┌─────────────┐
│  Task File  │─────────────────────────▶│  Plan File  │
│             │                           │             │
│ - type      │                           │ - objective │
│ - source    │                           │ - steps     │
│ - timestamp │                           │ - approval  │
│ - priority  │                           └─────────────┘
│ - status    │
│ - content   │
└──────┬──────┘
       │ processed by (N:1)
       ▼
┌─────────────┐      uses (N:1)      ┌─────────────┐
│ Claude Code │◀─────────────────────│Agent Skill  │
│             │                       │             │
│             │                       │ - name      │
│             │                       │ - description│
│             │                       │ - instructions│
└─────────────┘                       └─────────────┘

┌─────────────┐
│   Watcher   │
│             │
└──────┬──────┘
       │ logs to (1:N)
       ▼
┌─────────────┐
│ Log Entry   │
│             │
│ - timestamp │
│ - action    │
│ - result    │
└─────────────┘
```

---

## State Transitions

### Task File States

```
pending ──▶ in_progress ──▶ completed
   │                            │
   │                            ▼
   └────────────────────▶  /Done/
```

**Transitions**:
- `pending` → `in_progress`: Claude starts processing
- `in_progress` → `completed`: Claude finishes processing
- `pending` → `completed`: Simple task completed immediately
- Any state → `/Done/`: File moved when task complete

### Watcher States

```
stopped ──▶ running ──▶ error
   ▲           │          │
   │           │          │
   └───────────┴──────────┘
```

**Transitions**:
- `stopped` → `running`: Watcher starts
- `running` → `error`: Exception occurs
- `error` → `running`: Error handled, continues
- `running` → `stopped`: Manual shutdown
- `error` → `stopped`: Too many consecutive errors

---

## Data Validation

### Task File Validation

```python
def validate_task_file(task_data: dict) -> bool:
    required_fields = ['type', 'source', 'timestamp', 'priority', 'status']
    valid_types = ['email', 'file_drop', 'transaction']
    valid_priorities = ['high', 'medium', 'low']
    valid_statuses = ['pending', 'in_progress', 'completed']

    # Check required fields
    if not all(field in task_data for field in required_fields):
        return False

    # Validate enums
    if task_data['type'] not in valid_types:
        return False
    if task_data['priority'] not in valid_priorities:
        return False
    if task_data['status'] not in valid_statuses:
        return False

    # Validate timestamp format
    try:
        datetime.fromisoformat(task_data['timestamp'])
    except ValueError:
        return False

    return True
```

### Agent Skill Validation

```python
def validate_skill(skill_path: Path) -> bool:
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False

    content = skill_md.read_text()

    # Check YAML frontmatter
    if not content.startswith('---'):
        return False

    # Parse frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False

    frontmatter = yaml.safe_load(parts[1])

    # Validate required fields
    if 'name' not in frontmatter or 'description' not in frontmatter:
        return False

    # Validate name format
    name = frontmatter['name']
    if not re.match(r'^[a-z0-9-]+$', name):
        return False
    if len(name) > 64:
        return False
    if name in ['anthropic', 'claude']:
        return False

    # Validate description length
    if len(frontmatter['description']) > 1024:
        return False

    # Check for required sections
    body = parts[2]
    if '## Instructions' not in body or '## Examples' not in body:
        return False

    return True
```

---

## Storage Considerations

### File System Layout

- **Task Files**: ~1KB each, ~10-20 per day = ~7MB per year
- **Plan Files**: ~2KB each, ~10-20 per day = ~14MB per year
- **Log Files**: ~10KB per day = ~3.6MB per year
- **Agent Skills**: ~5KB each, ~5 skills = ~25KB total

**Total Storage (1 year)**: ~25MB (well within <1GB constraint)

### Backup Strategy

- Obsidian vault should be backed up regularly (user responsibility)
- Git repository for code and skills (version controlled)
- Log rotation: Keep 90 days, delete older (per constitution)
- Task/Plan files: Archive to `/Archive/YYYY/` after 90 days (optional)
