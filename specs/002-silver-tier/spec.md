# Feature Specification: Silver Tier - Enhanced Automation

**Feature Branch**: `002-silver-tier`
**Created**: 2026-03-09
**Status**: Draft
**Input**: User description: "Silver tier development with dual watchers (Gmail and File System) and email sending via MCP server, LinkedIn integration only (no WhatsApp)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simultaneous Multi-Source Monitoring (Priority: P1)

As a busy professional, I want the system to monitor both my email inbox and file drop folder simultaneously, so that I never miss important tasks regardless of how they arrive.

**Why this priority**: This is the foundational capability that distinguishes Silver tier from Bronze tier. Without dual watchers, users must choose between email or file monitoring, limiting the system's usefulness. This delivers immediate value by expanding task detection coverage.

**Independent Test**: Can be fully tested by sending an email and dropping a file within the same 2-minute window, then verifying both tasks are created in /Needs_Action without conflicts or missed detections.

**Acceptance Scenarios**:

1. **Given** both Gmail and File System watchers are running, **When** a new email arrives and a file is dropped simultaneously, **Then** both tasks are created in /Needs_Action with unique IDs and correct timestamps
2. **Given** both watchers are active, **When** one watcher encounters an error, **Then** the other watcher continues operating without interruption
3. **Given** both watchers are running, **When** the system is restarted, **Then** both watchers resume monitoring without processing duplicate items

---

### User Story 2 - Automated Email Response Execution (Priority: P2)

As a user who receives collaboration inquiries, I want the system to draft and send email responses on my behalf, so that I can maintain professional communication without manual email composition.

**Why this priority**: Email sending transforms the system from detection-only to execution-capable. This is the first step toward true automation and delivers tangible time savings. Without this, users must manually copy/paste Claude's drafts.

**Independent Test**: Can be fully tested by processing an email task that requires a response, approving the draft, and verifying the email is sent successfully with proper threading and formatting.

**Acceptance Scenarios**:

1. **Given** a task requires an email response, **When** Claude creates a draft and user approves it, **Then** the email is sent via Gmail API with correct recipient, subject, and threading
2. **Given** an email draft is created, **When** user rejects the draft, **Then** no email is sent and the task moves to /Rejected with rejection reason
3. **Given** email sending fails due to API error, **When** the system retries, **Then** the user is notified of the failure and the task remains in /Approved for manual handling

---

### User Story 3 - LinkedIn Integration for Business Development (Priority: P3)

As a business owner, I want the system to monitor LinkedIn messages AND automatically post business updates to generate sales leads, so that I can maintain professional visibility and respond to opportunities without manual effort.

**Why this priority**: LinkedIn is a critical professional communication channel for business development. This extends the system's capabilities to both receive inquiries (monitoring) and proactively generate leads (posting), creating a complete LinkedIn automation workflow.

**Independent Test**: Can be fully tested by (1) sending a LinkedIn message and verifying task creation, and (2) creating a business update task and verifying it's posted to LinkedIn with proper formatting and tracking.

**Acceptance Scenarios**:

1. **Given** LinkedIn watcher is configured and running, **When** a new message arrives in LinkedIn inbox, **Then** a task file is created in /Needs_Action with sender name, message content, and profile link
2. **Given** a business milestone is achieved, **When** Claude creates a LinkedIn post draft, **Then** the post is published to LinkedIn with proper formatting and hashtags
3. **Given** a LinkedIn post is published, **When** the system checks engagement, **Then** post performance metrics (views, likes, comments) are logged to /Logs folder
4. **Given** LinkedIn API rate limits are reached, **When** the watcher attempts to fetch messages or post content, **Then** the system waits for rate limit reset and logs the delay without crashing

---

### User Story 4 - Persistent State Management (Priority: P4)

As a user who restarts the system frequently, I want the watchers to remember which items they've already processed, so that I don't receive duplicate tasks after every restart.

**Why this priority**: Duplicate task creation is a critical usability issue that undermines trust in the system. Persistent state is essential for production use but can be implemented after core monitoring and execution capabilities are proven.

**Independent Test**: Can be fully tested by processing several tasks, restarting all watchers, and verifying no duplicate tasks are created for previously processed items.

**Acceptance Scenarios**:

1. **Given** watchers have processed 10 items, **When** the system is restarted, **Then** no duplicate tasks are created for those 10 items
2. **Given** a watcher crashes mid-processing, **When** it restarts, **Then** it resumes from the last successfully processed item without duplicates
3. **Given** state database is corrupted, **When** watcher starts, **Then** it rebuilds state from existing task files in vault and continues monitoring

---

### User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P5)

As a cautious user, I want to review and approve high-stakes actions before they're executed, so that I maintain control over important decisions like client communications and financial transactions.

**Why this priority**: Approval workflow is a safety mechanism that prevents costly mistakes. While important for production use, it can be implemented after core automation capabilities are working, as users can manually review tasks in the interim.

**Independent Test**: Can be fully tested by creating a task that exceeds approval thresholds (e.g., client email), verifying it moves to /Pending_Approval, approving it, and confirming execution proceeds.

**Acceptance Scenarios**:

1. **Given** a task requires client communication, **When** Claude creates an execution plan, **Then** the task moves to /Pending_Approval instead of /Approved
2. **Given** a task is in /Pending_Approval, **When** user approves it via command, **Then** the task moves to /Approved and execution proceeds
3. **Given** a task is in /Pending_Approval for 24 hours, **When** no approval is received, **Then** user receives a notification reminder

---

### User Story 6 - Claude Reasoning Loop with Structured Planning (Priority: P6)

As a user processing complex tasks, I want Claude to create structured Plan.md files that document the reasoning process and execution steps, so that I can understand how decisions were made and track multi-step task completion.

**Why this priority**: Structured planning provides transparency and auditability. Plan.md files serve as both execution guides and historical records, enabling users to understand Claude's reasoning and verify task completion. This extends the Bronze tier planning pattern to all Silver tier tasks.

**Independent Test**: Can be fully tested by creating a complex task (e.g., multi-recipient email campaign), verifying a Plan.md file is created in /Plans with reasoning steps, and confirming execution follows the documented plan.

**Acceptance Scenarios**:

1. **Given** a task requires multi-step execution, **When** Claude analyzes the task, **Then** a Plan.md file is created in /Plans folder with objective, context, proposed actions, and next steps
2. **Given** a Plan.md file exists, **When** Claude executes the plan, **Then** each step is marked as completed in the plan file with timestamps
3. **Given** a plan execution fails, **When** Claude encounters an error, **Then** the Plan.md file is updated with error details and alternative approaches

---

### User Story 7 - Automated Scheduled Task Execution (Priority: P7)

As a user who wants hands-free operation, I want the system to automatically execute scheduled tasks at configured intervals, so that routine operations (daily briefings, weekly reports) run without manual triggering.

**Why this priority**: Automated scheduling transforms the system from reactive to proactive. This enables true "set it and forget it" operation for recurring tasks, reducing manual intervention and ensuring consistent execution of routine operations.

**Independent Test**: Can be fully tested by configuring a daily task (e.g., "Generate morning briefing at 8 AM"), waiting for scheduled time, and verifying the task executes automatically with results logged to vault.

**Acceptance Scenarios**:

1. **Given** a scheduled task is configured via cron (Linux/Mac) or Task Scheduler (Windows), **When** the scheduled time arrives, **Then** the task executes automatically and results are logged to /Logs folder
2. **Given** multiple scheduled tasks exist, **When** their execution times overlap, **Then** tasks execute sequentially without conflicts
3. **Given** a scheduled task fails, **When** the next scheduled time arrives, **Then** the task retries and failure is logged with error details

---

### Edge Cases

- What happens when Gmail API quota is exhausted while File System watcher is still active?
- How does the system handle email sending failures due to network issues or API downtime?
- What happens when LinkedIn session expires during monitoring or posting?
- How does the system handle LinkedIn posting failures when API quota is exceeded?
- What happens when a scheduled task execution time is missed due to system downtime?
- How does the system handle overlapping scheduled tasks with long execution times?
- What happens when Plan.md file creation fails due to disk space issues?
- How does the system handle conflicting tasks from different sources (e.g., email about a file that was also dropped)?
- What happens when state database becomes corrupted or inaccessible?
- How does the system handle tasks that require approval but user is unavailable for extended periods?
- What happens when a watcher detects an item but vault is not writable?
- How does the system handle Agent Skill failures or missing skill definitions?
- What happens when cron/Task Scheduler service is not running or misconfigured?

## Requirements *(mandatory)*

### Functional Requirements

**Dual Watcher Operations**:
- **FR-001**: System MUST run Gmail Watcher and File System Watcher concurrently in separate processes
- **FR-002**: System MUST create unique task IDs for items from different sources to prevent conflicts
- **FR-003**: System MUST continue operating if one watcher fails while the other remains functional
- **FR-004**: System MUST log watcher activity to separate log files for troubleshooting

**Email Sending Capability**:
- **FR-005**: System MUST provide an MCP server for sending emails via Gmail API
- **FR-006**: System MUST preserve email threading when sending responses (Reply-To headers)
- **FR-007**: System MUST support email drafts with recipient, subject, body, and optional attachments
- **FR-008**: System MUST retry failed email sends up to 3 times with exponential backoff
- **FR-009**: System MUST log all sent emails with timestamp, recipient, and status

**LinkedIn Integration**:
- **FR-010**: System MUST monitor LinkedIn inbox for new messages every 5 minutes
- **FR-011**: System MUST create tasks for LinkedIn messages with sender profile, message content, and timestamp
- **FR-012**: System MUST detect LinkedIn connection requests and create tasks with requester information
- **FR-013**: System MUST automatically post business updates to LinkedIn based on completed tasks and milestones
- **FR-014**: System MUST track LinkedIn post performance metrics (views, likes, comments, shares)
- **FR-015**: System MUST handle LinkedIn API rate limits gracefully without crashing

**Persistent State Management**:
- **FR-016**: System MUST maintain a persistent database of processed items across restarts
- **FR-017**: System MUST record item ID, source, timestamp, and processing status for each item
- **FR-018**: System MUST check processed items database before creating new tasks to prevent duplicates
- **FR-019**: System MUST rebuild state from existing vault files if database is corrupted or missing

**Claude Reasoning Loop & Planning**:
- **FR-020**: System MUST create Plan.md files in /Plans folder for each task requiring multi-step execution
- **FR-021**: Claude MUST follow reasoning loop pattern: analyze task → create plan → execute steps → verify completion
- **FR-022**: System MUST update Plan.md files with execution progress, marking completed steps with timestamps
- **FR-023**: System MUST document reasoning decisions and alternative approaches in Plan.md files

**Automated Scheduling**:
- **FR-024**: System MUST support scheduled task execution via cron (Linux/Mac) or Task Scheduler (Windows)
- **FR-025**: System MUST execute scheduled tasks at configured intervals (daily, weekly, monthly)
- **FR-026**: System MUST log scheduled task execution results to /Logs folder with timestamps
- **FR-027**: System MUST handle overlapping scheduled tasks by executing them sequentially

**Human-in-the-Loop Approval**:
- **FR-028**: System MUST move tasks to /Pending_Approval when they exceed approval thresholds defined in Company_Handbook.md
- **FR-029**: System MUST support approval commands that move tasks from /Pending_Approval to /Approved or /Rejected
- **FR-030**: System MUST track approval timestamp and approver for audit purposes
- **FR-031**: System MUST send notification reminders for tasks pending approval longer than 24 hours

**Error Handling & Resilience**:
- **FR-032**: System MUST continue operating when API rate limits are reached, waiting for reset
- **FR-033**: System MUST log all errors with context (source, item ID, error message, timestamp)
- **FR-034**: System MUST recover gracefully from transient failures (network issues, API timeouts)
- **FR-035**: System MUST provide health check endpoint showing status of all watchers

**Agent Skills Implementation**:
- **FR-036**: All AI reasoning capabilities MUST be implemented as Claude Code Agent Skills
- **FR-037**: System MUST include agent skills for: email triage, LinkedIn posting, task planning, and approval workflow
- **FR-038**: Agent skills MUST be reusable across different task types and sources

### Key Entities

- **Processed Item**: Represents an item (email, file, LinkedIn message) that has been detected and processed. Attributes: unique ID, source type, source-specific ID, timestamp, processing status, task file path
- **Email Draft**: Represents a composed email ready to be sent. Attributes: recipient(s), subject, body, thread ID (for replies), attachment paths, approval status
- **LinkedIn Message**: Represents a message received via LinkedIn. Attributes: sender profile URL, sender name, message content, timestamp, conversation ID
- **LinkedIn Post**: Represents a business update posted to LinkedIn. Attributes: post content, hashtags, scheduled time, publication timestamp, performance metrics (views, likes, comments, shares)
- **Plan**: Represents a structured execution plan for multi-step tasks. Attributes: task ID, objective, context, proposed actions, execution steps with timestamps, completion status, reasoning notes
- **Scheduled Task**: Represents a recurring task configured for automatic execution. Attributes: task name, schedule (cron expression or interval), last execution time, next execution time, execution status, retry count
- **Approval Request**: Represents a task awaiting user approval. Attributes: task ID, approval threshold exceeded, requested timestamp, approver, approval decision, decision timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully processes tasks from both Gmail and File System sources simultaneously without conflicts or missed detections for 24 hours continuous operation
- **SC-002**: Users can send email responses within 5 minutes of task approval, with 99% delivery success rate
- **SC-003**: LinkedIn messages are detected and converted to tasks within 10 minutes of receipt
- **SC-004**: LinkedIn posts are published automatically based on business milestones with 95% success rate
- **SC-005**: Zero duplicate tasks are created after system restarts, verified across 10 restart cycles
- **SC-006**: Plan.md files are created for 100% of multi-step tasks with complete reasoning documentation
- **SC-007**: Scheduled tasks execute at configured times with 99% reliability over 30-day period
- **SC-008**: Approval workflow reduces unauthorized actions by 100% (no high-stakes actions execute without approval)
- **SC-009**: System maintains 99% uptime for all watchers over 7-day continuous operation period
- **SC-010**: Users report 50% reduction in time spent on email triage and response tasks
- **SC-011**: System handles API rate limits and transient failures without requiring manual intervention in 95% of cases
- **SC-012**: All AI reasoning capabilities are implemented as reusable Agent Skills

## Assumptions

- Gmail API credentials are properly configured with send email permissions
- LinkedIn API access is available for both message monitoring and post publishing (or web scraping fallback is acceptable if API unavailable)
- Users have Obsidian vault accessible and writable by watcher processes
- Company_Handbook.md defines clear approval thresholds for different task types
- Users will check /Pending_Approval folder at least once per day
- Network connectivity is generally stable (transient failures are acceptable)
- SQLite is acceptable for state persistence (no need for external database)
- Cron (Linux/Mac) or Task Scheduler (Windows) is available for scheduled task execution
- All AI reasoning capabilities will be implemented as Claude Code Agent Skills following Bronze tier pattern
- Users have sufficient LinkedIn API quota for both monitoring and posting operations
- Business milestones and achievements are tracked in vault files for automated LinkedIn posting

## Dependencies

- Bronze tier implementation must be complete and stable
- Gmail API OAuth2 credentials with send email scope
- LinkedIn API credentials with permissions for message monitoring and post publishing
- MCP server framework for email sending integration
- SQLite or similar embedded database for state persistence
- Claude Code CLI for task processing, email draft generation, and plan creation
- Cron daemon (Linux/Mac) or Task Scheduler service (Windows) for scheduled execution
- Agent Skills framework for implementing AI reasoning capabilities (email-triage, linkedin-posting, task-planning, approval-workflow)

## Out of Scope

- WhatsApp integration (explicitly excluded per user request)
- Social media posting capabilities (reserved for Gold tier)
- Odoo ERP integration (reserved for Gold tier)
- Ralph Wiggum autonomous loop (reserved for Gold tier)
- Multi-user support (reserved for Platinum tier)
- Cloud deployment (reserved for Platinum tier)
- Real-time notifications (push notifications, SMS alerts)
- Mobile app interface
- Advanced analytics dashboard
