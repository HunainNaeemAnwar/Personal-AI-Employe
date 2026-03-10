# Data Model: Silver Tier - Enhanced Automation

**Feature**: 002-silver-tier
**Date**: 2026-03-09
**Status**: Phase 1 Complete

## Overview

This document defines the core entities and their relationships for Silver tier. All entities are persisted either in SQLite (state management) or as markdown files in the Obsidian vault (task management).

---

## Entity Definitions

### 1. Processed Item

**Purpose**: Tracks items (emails, files, LinkedIn messages) that have been detected and processed to prevent duplicate task creation across system restarts.

**Storage**: SQLite database (`state.db`)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| `source` | TEXT | NOT NULL | Source type: "gmail", "filesystem", "linkedin" |
| `source_id` | TEXT | NOT NULL | Source-specific identifier (email ID, file path, LinkedIn message ID) |
| `timestamp` | TEXT | NOT NULL | ISO 8601 timestamp when item was first detected |
| `status` | TEXT | NOT NULL | Processing status: "pending", "processed", "failed" |
| `task_file_path` | TEXT | NULL | Relative path to created task file in vault (if applicable) |
| `created_at` | TEXT | NOT NULL DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

**Indexes**:
- `UNIQUE INDEX idx_source_item ON processed_items(source, source_id)` - Prevents duplicate entries
- `INDEX idx_timestamp ON processed_items(timestamp)` - Supports time-based queries

**Validation Rules**:
- `source` must be one of: "gmail", "filesystem", "linkedin"
- `status` must be one of: "pending", "processed", "failed"
- `source_id` must be unique within each source type
- `timestamp` must be valid ISO 8601 format

**State Transitions**:
```
pending → processed (successful task creation)
pending → failed (error during processing)
failed → pending (manual retry)
```

**Example**:
```json
{
  "id": 1,
  "source": "gmail",
  "source_id": "18d4f2a3b5c6e7f8",
  "timestamp": "2026-03-09T14:30:00Z",
  "status": "processed",
  "task_file_path": "Needs_Action/EMAIL_20260309T143000Z_client-inquiry.md",
  "created_at": "2026-03-09T14:30:05Z"
}
```

---

### 2. Email Draft

**Purpose**: Represents a composed email ready to be sent via the email MCP server.

**Storage**: Embedded in task file YAML frontmatter + body (Obsidian vault)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `recipients` | List[String] | NOT NULL, min 1 | Email addresses (To field) |
| `cc` | List[String] | OPTIONAL | CC recipients |
| `bcc` | List[String] | OPTIONAL | BCC recipients |
| `subject` | String | NOT NULL | Email subject line |
| `body` | String | NOT NULL | Email body (plain text or HTML) |
| `thread_id` | String | OPTIONAL | Gmail thread ID for replies (preserves conversation threading) |
| `in_reply_to` | String | OPTIONAL | Message-ID header for proper threading |
| `attachment_paths` | List[String] | OPTIONAL | Absolute paths to attachment files |
| `approval_status` | String | NOT NULL | "pending", "approved", "rejected", "sent" |
| `approved_by` | String | OPTIONAL | User identifier who approved |
| `approved_at` | String | OPTIONAL | ISO 8601 timestamp of approval |
| `sent_at` | String | OPTIONAL | ISO 8601 timestamp when email was sent |
| `gmail_message_id` | String | OPTIONAL | Gmail message ID after successful send |

**Validation Rules**:
- At least one recipient required (recipients list not empty)
- Email addresses must match RFC 5322 format
- `approval_status` must be one of: "pending", "approved", "rejected", "sent"
- `thread_id` required if replying to existing conversation
- Attachment files must exist and be readable

**State Transitions**:
```
pending → approved (user approval)
pending → rejected (user rejection)
approved → sent (successful email send via MCP)
approved → pending (send failure, retry)
```

**Example (YAML frontmatter)**:
```yaml
---
type: email_draft
recipients:
  - client@example.com
subject: "Re: Project Proposal"
thread_id: "18d4f2a3b5c6e7f8"
in_reply_to: "<CABcD1234@mail.gmail.com>"
approval_status: approved
approved_by: hunain
approved_at: "2026-03-09T15:00:00Z"
sent_at: "2026-03-09T15:00:05Z"
gmail_message_id: "18d4f2a3b5c6e7f9"
---

Hi [Client Name],

Thank you for your inquiry about the project proposal...
```

---

### 3. LinkedIn Message

**Purpose**: Represents a message received via LinkedIn inbox that requires action.

**Storage**: Task file in Obsidian vault (/Needs_Action)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `sender_profile_url` | String | NOT NULL | LinkedIn profile URL of sender |
| `sender_name` | String | NOT NULL | Display name of sender |
| `message_content` | String | NOT NULL | Full message text |
| `timestamp` | String | NOT NULL | ISO 8601 timestamp when message was received |
| `conversation_id` | String | NOT NULL | LinkedIn conversation identifier |
| `message_id` | String | NOT NULL | Unique message identifier |
| `is_connection_request` | Boolean | NOT NULL DEFAULT false | True if this is a connection request, not a message |
| `connection_note` | String | OPTIONAL | Note included with connection request |

**Validation Rules**:
- `sender_profile_url` must be valid LinkedIn URL format
- `message_content` cannot be empty
- `conversation_id` and `message_id` must be unique
- If `is_connection_request` is true, `connection_note` may be present

**Example (YAML frontmatter)**:
```yaml
---
type: linkedin_message
sender_profile_url: "https://www.linkedin.com/in/john-doe-123456/"
sender_name: "John Doe"
timestamp: "2026-03-09T16:00:00Z"
conversation_id: "2-ABC123XYZ"
message_id: "MSG-789DEF"
is_connection_request: false
priority: medium
status: pending
---

Hi Hunain,

I came across your profile and was impressed by your work in AI automation...
```

---

### 4. LinkedIn Post

**Purpose**: Represents a business update to be posted to LinkedIn for lead generation.

**Storage**: Task file in Obsidian vault (/Needs_Action or /Approved)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `post_content` | String | NOT NULL, max 3000 chars | Post text content |
| `hashtags` | List[String] | OPTIONAL | Hashtags to include (without # prefix) |
| `scheduled_time` | String | OPTIONAL | ISO 8601 timestamp for scheduled posting |
| `publication_timestamp` | String | OPTIONAL | ISO 8601 timestamp when post was published |
| `post_url` | String | OPTIONAL | LinkedIn post URL after publication |
| `performance_metrics` | Object | OPTIONAL | Engagement metrics |
| `performance_metrics.views` | Integer | OPTIONAL | Number of post views |
| `performance_metrics.likes` | Integer | OPTIONAL | Number of likes |
| `performance_metrics.comments` | Integer | OPTIONAL | Number of comments |
| `performance_metrics.shares` | Integer | OPTIONAL | Number of shares |
| `performance_metrics.last_updated` | String | OPTIONAL | ISO 8601 timestamp of last metrics fetch |
| `approval_status` | String | NOT NULL | "pending", "approved", "rejected", "published" |

**Validation Rules**:
- `post_content` length: 1-3000 characters (LinkedIn limit)
- Hashtags must be alphanumeric (no spaces or special chars)
- `scheduled_time` must be in the future if specified
- `approval_status` must be one of: "pending", "approved", "rejected", "published"

**State Transitions**:
```
pending → approved (user approval)
pending → rejected (user rejection)
approved → published (successful LinkedIn API post)
approved → pending (API failure, retry)
```

**Example (YAML frontmatter)**:
```yaml
---
type: linkedin_post
post_content: |
  Excited to share that our AI automation system just processed its 1000th task!

  Key achievements:
  - 99% uptime over 30 days
  - 50% reduction in email triage time
  - Zero duplicate tasks after 10 system restarts

  Building autonomous systems that actually work is incredibly rewarding.
hashtags:
  - AIAutomation
  - ProductivityHacks
  - TechInnovation
scheduled_time: "2026-03-10T09:00:00Z"
approval_status: approved
approved_at: "2026-03-09T17:00:00Z"
publication_timestamp: "2026-03-10T09:00:05Z"
post_url: "https://www.linkedin.com/posts/hunain-naeem-anwar_aiautomation-activity-123456789"
performance_metrics:
  views: 1250
  likes: 87
  comments: 12
  shares: 5
  last_updated: "2026-03-10T18:00:00Z"
---
```

---

### 5. Plan

**Purpose**: Represents a structured execution plan for multi-step tasks, documenting Claude's reasoning process.

**Storage**: Markdown file in Obsidian vault (/Plans)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_id` | String | NOT NULL | Reference to originating task file |
| `objective` | String | NOT NULL | High-level goal of the plan |
| `context` | String | NOT NULL | Background information and constraints |
| `proposed_actions` | List[String] | NOT NULL, min 1 | Ordered list of actions to execute |
| `execution_steps` | List[Object] | NOT NULL | Detailed execution steps with status |
| `execution_steps[].step_number` | Integer | NOT NULL | Sequential step number |
| `execution_steps[].description` | String | NOT NULL | What this step does |
| `execution_steps[].status` | String | NOT NULL | "pending", "in_progress", "completed", "failed" |
| `execution_steps[].started_at` | String | OPTIONAL | ISO 8601 timestamp when step started |
| `execution_steps[].completed_at` | String | OPTIONAL | ISO 8601 timestamp when step completed |
| `execution_steps[].error_message` | String | OPTIONAL | Error details if step failed |
| `completion_status` | String | NOT NULL | "in_progress", "completed", "failed" |
| `reasoning_notes` | String | OPTIONAL | Claude's reasoning and decision rationale |
| `alternative_approaches` | List[String] | OPTIONAL | Other approaches considered and why rejected |

**Validation Rules**:
- `task_id` must reference an existing task file
- `execution_steps` must be ordered sequentially (step_number 1, 2, 3...)
- Step `status` must be one of: "pending", "in_progress", "completed", "failed"
- `completion_status` must be one of: "in_progress", "completed", "failed"
- Steps cannot be marked completed without `completed_at` timestamp

**State Transitions**:
```
in_progress → completed (all steps completed successfully)
in_progress → failed (critical step failed, cannot proceed)
```

**Example**:
```markdown
---
task_id: "EMAIL_20260309T143000Z_client-inquiry"
objective: "Respond to client inquiry about project timeline and pricing"
context: "Client is interested in AI automation project. Budget: $50k-$100k. Timeline: 3 months."
completion_status: completed
created_at: "2026-03-09T14:35:00Z"
updated_at: "2026-03-09T15:05:00Z"
---

# Plan: Client Inquiry Response

## Proposed Actions

1. Research client's company and industry
2. Draft project timeline with milestones
3. Prepare pricing breakdown
4. Compose professional email response
5. Request approval for sending

## Execution Steps

### Step 1: Research Client Company
- **Status**: completed
- **Started**: 2026-03-09T14:35:00Z
- **Completed**: 2026-03-09T14:40:00Z
- **Findings**: Client is in healthcare tech, 50-person startup, raised Series A

### Step 2: Draft Project Timeline
- **Status**: completed
- **Started**: 2026-03-09T14:40:00Z
- **Completed**: 2026-03-09T14:50:00Z
- **Timeline**: 3 months (Bronze → Silver → Gold tiers)

### Step 3: Prepare Pricing Breakdown
- **Status**: completed
- **Started**: 2026-03-09T14:50:00Z
- **Completed**: 2026-03-09T14:55:00Z
- **Pricing**: $75k total ($25k per tier)

### Step 4: Compose Email Response
- **Status**: completed
- **Started**: 2026-03-09T14:55:00Z
- **Completed**: 2026-03-09T15:00:00Z
- **Draft**: Created in task file

### Step 5: Request Approval
- **Status**: completed
- **Started**: 2026-03-09T15:00:00Z
- **Completed**: 2026-03-09T15:05:00Z
- **Result**: Task moved to /Pending_Approval

## Reasoning Notes

Client's healthcare background requires emphasis on HIPAA compliance and data security. Pricing positioned at mid-range ($75k) to balance value and competitiveness. Timeline structured in tiers to allow early wins and iterative feedback.

## Alternative Approaches Considered

- **Single-phase delivery**: Rejected - too risky, no early feedback
- **Lower pricing ($50k)**: Rejected - undervalues expertise, sets wrong expectations
- **Longer timeline (6 months)**: Rejected - client needs faster results
```

---

### 6. Scheduled Task

**Purpose**: Represents a recurring task configured for automatic execution at specified intervals.

**Storage**: Configuration file in project root (`scheduled_tasks.yaml`) + cron/Task Scheduler entries

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_name` | String | NOT NULL, UNIQUE | Human-readable task identifier |
| `task_type` | String | NOT NULL | Type: "briefing", "report", "audit", "cleanup" |
| `schedule` | String | NOT NULL | Cron expression (Linux/Mac) or interval (Windows) |
| `command` | String | NOT NULL | Shell command to execute |
| `last_execution_time` | String | OPTIONAL | ISO 8601 timestamp of last execution |
| `next_execution_time` | String | NOT NULL | ISO 8601 timestamp of next scheduled execution |
| `execution_status` | String | NOT NULL | "scheduled", "running", "completed", "failed" |
| `retry_count` | Integer | NOT NULL DEFAULT 0 | Number of retry attempts after failure |
| `max_retries` | Integer | NOT NULL DEFAULT 3 | Maximum retry attempts before giving up |
| `enabled` | Boolean | NOT NULL DEFAULT true | Whether task is active |

**Validation Rules**:
- `task_name` must be unique across all scheduled tasks
- `schedule` must be valid cron expression (5 fields) or Windows interval
- `command` must be executable shell command
- `execution_status` must be one of: "scheduled", "running", "completed", "failed"
- `retry_count` cannot exceed `max_retries`

**State Transitions**:
```
scheduled → running (execution started)
running → completed (successful execution)
running → failed (execution error)
failed → scheduled (retry attempt)
```

**Example**:
```yaml
- task_name: "daily_morning_briefing"
  task_type: "briefing"
  schedule: "0 8 * * *"  # Every day at 8:00 AM
  command: "cd /home/hunain/personal-ai-employee && claude 'Generate morning briefing'"
  last_execution_time: "2026-03-09T08:00:00Z"
  next_execution_time: "2026-03-10T08:00:00Z"
  execution_status: "completed"
  retry_count: 0
  max_retries: 3
  enabled: true

- task_name: "weekly_linkedin_post"
  task_type: "report"
  schedule: "0 9 * * 1"  # Every Monday at 9:00 AM
  command: "cd /home/hunain/personal-ai-employee && claude 'Create weekly business update LinkedIn post'"
  last_execution_time: "2026-03-08T09:00:00Z"
  next_execution_time: "2026-03-15T09:00:00Z"
  execution_status: "scheduled"
  retry_count: 0
  max_retries: 3
  enabled: true
```

---

### 7. Approval Request

**Purpose**: Represents a task awaiting user approval before execution (HITL workflow).

**Storage**: Task file in Obsidian vault (/Pending_Approval)

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `task_id` | String | NOT NULL, UNIQUE | Unique task identifier |
| `task_type` | String | NOT NULL | Type: "email", "linkedin_post", "payment", "contract" |
| `approval_threshold_exceeded` | String | NOT NULL | Which threshold triggered approval requirement |
| `requested_timestamp` | String | NOT NULL | ISO 8601 timestamp when approval was requested |
| `approver` | String | OPTIONAL | User identifier who made approval decision |
| `approval_decision` | String | NOT NULL | "pending", "approved", "rejected" |
| `decision_timestamp` | String | OPTIONAL | ISO 8601 timestamp when decision was made |
| `rejection_reason` | String | OPTIONAL | User-provided reason for rejection |
| `reminder_sent` | Boolean | NOT NULL DEFAULT false | Whether 24-hour reminder was sent |

**Validation Rules**:
- `task_id` must reference an existing task file
- `approval_decision` must be one of: "pending", "approved", "rejected"
- If `approval_decision` is "approved" or "rejected", `decision_timestamp` and `approver` are required
- If `approval_decision` is "rejected", `rejection_reason` should be provided
- `approval_threshold_exceeded` must match a threshold defined in Company_Handbook.md

**State Transitions**:
```
pending → approved (user approves)
pending → rejected (user rejects)
```

**Example (YAML frontmatter)**:
```yaml
---
type: approval_request
task_id: "EMAIL_20260309T143000Z_client-inquiry"
task_type: "email"
approval_threshold_exceeded: "client_communication"
requested_timestamp: "2026-03-09T15:00:00Z"
approver: "hunain"
approval_decision: "approved"
decision_timestamp: "2026-03-09T15:05:00Z"
reminder_sent: false
---

# Approval Required: Client Email Response

**Threshold Exceeded**: Client Communication (requires approval per Company_Handbook.md)

**Email Draft**:
- To: client@example.com
- Subject: Re: Project Proposal
- Body: [See email draft in task file]

**Approval Options**:
- Approve: `claude "approve task EMAIL_20260309T143000Z_client-inquiry"`
- Reject: `claude "reject task EMAIL_20260309T143000Z_client-inquiry --reason 'Pricing too high'"`
```

---

## Entity Relationships

```
Processed Item (1) ──creates──> (1) Task File
                                      │
                                      ├──contains──> (0..1) Email Draft
                                      ├──contains──> (0..1) LinkedIn Message
                                      ├──contains──> (0..1) LinkedIn Post
                                      └──triggers──> (0..1) Plan

Task File (1) ──requires──> (0..1) Approval Request

Plan (1) ──references──> (1) Task File

Scheduled Task (1) ──creates──> (0..*) Task Files
```

**Key Relationships**:
1. Each Processed Item creates exactly one Task File (1:1)
2. Task Files may contain Email Drafts, LinkedIn Messages, or LinkedIn Posts (0..1 each)
3. Complex tasks trigger Plan creation (0..1)
4. Sensitive tasks require Approval Requests (0..1)
5. Scheduled Tasks can create multiple Task Files over time (1:*)

---

## Database Schema (SQLite)

```sql
-- Processed Items Table
CREATE TABLE processed_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL CHECK(source IN ('gmail', 'filesystem', 'linkedin')),
    source_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'processed', 'failed')),
    task_file_path TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, source_id)
);

CREATE INDEX idx_source_item ON processed_items(source, source_id);
CREATE INDEX idx_timestamp ON processed_items(timestamp);
CREATE INDEX idx_status ON processed_items(status);

-- Schema Version Table (for migrations)
CREATE TABLE schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO schema_version (version) VALUES (1);
```

---

## File Naming Conventions

All task files follow this pattern:
```
{TYPE}_{TIMESTAMP}_{SLUG}.md
```

**Examples**:
- `EMAIL_20260309T143000Z_client-inquiry.md`
- `LINKEDIN_MSG_20260309T160000Z_john-doe-inquiry.md`
- `LINKEDIN_POST_20260309T170000Z_milestone-announcement.md`
- `FILE_20260309T180000Z_invoice-review.md`

**Plan files**:
```
PLAN_{TASK_ID}.md
```

**Example**: `PLAN_EMAIL_20260309T143000Z_client-inquiry.md`

---

## Validation & Integrity

**Referential Integrity**:
- Task files reference Processed Items via `task_file_path`
- Plans reference Task Files via `task_id`
- Approval Requests reference Task Files via `task_id`

**Consistency Checks**:
1. Every Processed Item with status "processed" must have a valid `task_file_path`
2. Every Plan must reference an existing Task File
3. Every Approval Request must reference an existing Task File in /Pending_Approval
4. Scheduled Tasks must have valid cron expressions or intervals

**Orphan Detection**:
- Task files without corresponding Processed Items (manual creation)
- Plans without corresponding Task Files (deleted tasks)
- Approval Requests for non-existent tasks (deleted before approval)

---

## Migration Strategy

**Version 1 → Version 2** (example future migration):
```sql
-- Add priority field to processed_items
ALTER TABLE processed_items ADD COLUMN priority TEXT DEFAULT 'medium'
    CHECK(priority IN ('low', 'medium', 'high'));

-- Update schema version
INSERT INTO schema_version (version) VALUES (2);
```

**Rollback Strategy**:
- Daily SQLite backups via cron: `sqlite3 state.db ".backup state_backup_$(date +%Y%m%d).db"`
- Rebuild from vault files if database corrupted: scan /Needs_Action, /Done, /Rejected for task files
