# Feature Specification: Bronze Tier - Personal AI Employee Foundation

**Feature Branch**: `001-bronze-tier`
**Created**: 2026-03-07
**Status**: Draft
**Input**: User description: "Create specifications for bronze tier. Take bronze tier details from PROJECT_REFERENCE.md and create perfect specs."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set Up Knowledge Base (Priority: P1)

As a user, I want to create an Obsidian vault with essential configuration files so that my AI Employee has a structured workspace to manage tasks and store information.

**Why this priority**: The knowledge base is the foundation for all AI Employee operations. Without it, no other functionality can work. This is the absolute minimum requirement to begin using the system.

**Independent Test**: Can be fully tested by creating the vault, verifying the folder structure exists, and confirming Dashboard.md and Company_Handbook.md are present with valid content. Delivers immediate value by providing a visual workspace for monitoring AI activity.

**Acceptance Scenarios**:

1. **Given** I have Obsidian installed, **When** I create a new vault named "AI_Employee_Vault", **Then** the vault is created successfully and opens in Obsidian
2. **Given** the vault is created, **When** I check the folder structure, **Then** I see folders: /Inbox, /Needs_Action, /Done, /Logs, /Plans, /Pending_Approval, /Approved, /Rejected
3. **Given** the vault exists, **When** I open Dashboard.md, **Then** I see a template with sections for: Recent Activity, Pending Tasks, System Status
4. **Given** the vault exists, **When** I open Company_Handbook.md, **Then** I see a template with sections for: Rules of Engagement, Approval Thresholds, Communication Guidelines

---

### User Story 2 - Monitor External Source (Priority: P2)

As a user, I want a Watcher script to monitor either my Gmail inbox or a file system folder so that the AI Employee can detect new tasks automatically without manual input.

**Why this priority**: Automated detection is what transforms Claude from a reactive chatbot into a proactive employee. This enables the core "perception" capability. Users can choose Gmail (for email-based workflows) or file system (for document-based workflows) based on their primary use case.

**Independent Test**: Can be fully tested by running the Watcher script, triggering a test event (sending an email or dropping a file), and verifying a .md file appears in /Needs_Action with correct metadata. Delivers value by eliminating manual task entry.

**Acceptance Scenarios**:

1. **Given** I have configured Gmail API credentials, **When** I run the Gmail Watcher script, **Then** it starts monitoring my inbox without errors
2. **Given** the Gmail Watcher is running, **When** an important email arrives, **Then** a .md file is created in /Needs_Action within 2 minutes with email metadata (from, subject, received timestamp)
3. **Given** I have configured a drop folder path, **When** I run the File System Watcher, **Then** it starts monitoring the folder without errors
4. **Given** the File System Watcher is running, **When** I drop a file into the monitored folder, **Then** a .md file is created in /Needs_Action within 30 seconds with file metadata (name, size, timestamp)
5. **Given** a Watcher encounters an error (network timeout, API limit), **When** the error occurs, **Then** the Watcher logs the error and continues running without crashing

---

### User Story 3 - AI Reads and Writes to Vault (Priority: P3)

As a user, I want Claude Code to read tasks from /Needs_Action and write results to the vault so that the AI Employee can process tasks and maintain a record of its work.

**Why this priority**: This establishes the basic reasoning loop. Without this, the AI cannot act on detected tasks. This is the "brain" connecting perception (Watchers) to the knowledge base.

**Independent Test**: Can be fully tested by manually creating a task file in /Needs_Action, running Claude Code with a prompt to process it, and verifying Claude reads the file, performs reasoning, and writes output to the appropriate folder. Delivers value by demonstrating end-to-end task processing.

**Acceptance Scenarios**:

1. **Given** a task file exists in /Needs_Action, **When** I run Claude Code with a prompt to "process tasks in /Needs_Action", **Then** Claude reads the file content successfully
2. **Given** Claude has read a task, **When** Claude determines the next action, **Then** Claude writes a Plan.md file to /Plans with clear action steps
3. **Given** Claude has completed a task, **When** Claude finishes processing, **Then** the original task file is moved from /Needs_Action to /Done
4. **Given** Claude encounters an unclear task, **When** Claude cannot determine the action, **Then** Claude writes a clarification request to /Pending_Approval explaining what information is needed
5. **Given** Claude is processing multiple tasks, **When** Claude works on tasks, **Then** each task is processed independently without interference

---

### User Story 4 - Create Agent Skill (Priority: P4)

As a user, I want at least one Agent Skill defined so that Claude has structured knowledge for performing specific AI Employee tasks consistently.

**Why this priority**: Agent Skills transform ad-hoc prompts into reusable capabilities. While not strictly required for basic operation, having at least one skill demonstrates the pattern and provides a foundation for future expansion.

**Independent Test**: Can be fully tested by creating a SKILL.md file with proper structure, triggering the skill's use case, and verifying Claude applies the skill's instructions. Delivers value by showing how to package AI functionality for reuse.

**Acceptance Scenarios**:

1. **Given** I want to create an email triage skill, **When** I create a SKILL.md file with proper YAML frontmatter (name, description), **Then** the file is valid and contains no syntax errors
2. **Given** the skill file exists, **When** Claude encounters an email task, **Then** Claude automatically applies the skill's instructions without explicit prompting
3. **Given** the skill has examples, **When** Claude uses the skill, **Then** Claude's output matches the pattern shown in the examples
4. **Given** I want to test the skill, **When** I create a test scenario matching the skill's trigger conditions, **Then** Claude invokes the skill and produces expected results

---

### Edge Cases

- What happens when the Obsidian vault is locked or inaccessible (file permissions, disk full)?
- How does the system handle malformed .md files in /Needs_Action (missing frontmatter, invalid YAML)?
- What happens when a Watcher script crashes or stops unexpectedly?
- How does Claude handle tasks that require external information not available in the vault?
- What happens when multiple task files are created simultaneously in /Needs_Action?
- How does the system handle very large files dropped into the monitored folder (>100MB)?
- What happens when Gmail API credentials expire or are revoked?
- How does Claude handle tasks that reference files or data that no longer exist?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create an Obsidian vault with the following folder structure: /Inbox, /Needs_Action, /Done, /Logs, /Plans, /Pending_Approval, /Approved, /Rejected
- **FR-002**: System MUST create Dashboard.md with sections for Recent Activity, Pending Tasks, and System Status
- **FR-003**: System MUST create Company_Handbook.md with sections for Rules of Engagement, Approval Thresholds, and Communication Guidelines
- **FR-004**: System MUST provide either a Gmail Watcher OR a File System Watcher (user chooses one)
- **FR-005**: Gmail Watcher MUST monitor the inbox for important/unread emails and create .md files in /Needs_Action with metadata (from, subject, received timestamp, priority, status)
- **FR-006**: File System Watcher MUST monitor a designated folder for new files and create .md files in /Needs_Action with metadata (original filename, size, timestamp, type)
- **FR-007**: Watcher scripts MUST handle errors gracefully (log error, continue running) without crashing
- **FR-008**: Watcher scripts MUST track processed items to avoid creating duplicate task files
- **FR-009**: Claude Code MUST be able to read .md files from /Needs_Action folder
- **FR-010**: Claude Code MUST be able to write .md files to /Plans, /Done, and /Pending_Approval folders
- **FR-011**: Claude Code MUST move completed task files from /Needs_Action to /Done
- **FR-012**: System MUST include at least one Agent Skill with valid SKILL.md structure (YAML frontmatter with name and description, Instructions section, Examples section)
- **FR-013**: Agent Skill MUST follow naming conventions (lowercase, hyphens only, max 64 chars, no reserved words)
- **FR-014**: Task files created by Watchers MUST include YAML frontmatter with type, source, timestamp, priority, and status fields
- **FR-015**: System MUST log Watcher activity to /Logs folder with timestamp, action, and result

### Key Entities

- **Obsidian Vault**: The central knowledge base containing all folders, files, and AI Employee state. Attributes: vault path, folder structure, configuration files (Dashboard.md, Company_Handbook.md)
- **Task File**: A markdown file representing work to be done. Attributes: type (email/file_drop/transaction), source (sender/path), timestamp, priority (high/medium/low), status (pending/in_progress/completed), content, suggested actions
- **Watcher Script**: A Python process monitoring external sources. Attributes: watcher type (Gmail/FileSystem), check interval, processed items set, vault path, status (running/stopped/error)
- **Agent Skill**: A structured capability defined in SKILL.md. Attributes: name, description, instructions, examples, trigger conditions
- **Plan File**: A markdown file in /Plans describing action steps. Attributes: objective, steps (with checkboxes), approval requirements, created timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can set up the complete Bronze tier system (vault + watcher + Claude integration) in under 2 hours following documentation
- **SC-002**: Watcher script detects and creates task files within 2 minutes of trigger event (email arrival or file drop) with 100% reliability
- **SC-003**: Claude Code successfully reads task files from /Needs_Action and writes output files to appropriate folders in 100% of test cases
- **SC-004**: System operates continuously for 24 hours without Watcher crashes or data loss
- **SC-005**: At least one Agent Skill is created with valid structure and can be successfully invoked by Claude
- **SC-006**: User can visually monitor AI Employee activity through Obsidian Dashboard.md in real-time
- **SC-007**: Task files contain all required metadata fields (type, source, timestamp, priority, status) in 100% of cases
- **SC-008**: System handles at least 10 concurrent tasks in /Needs_Action without file conflicts or data corruption

## Assumptions

- User has Obsidian v1.10.6+ installed and knows basic Obsidian navigation
- User has Python 3.13+ installed for running Watcher scripts
- User has Claude Code installed and configured with valid API credentials
- For Gmail Watcher: User has Google Cloud project with Gmail API enabled and OAuth credentials
- For File System Watcher: User has a designated folder with read/write permissions
- User has basic command-line familiarity for running Python scripts
- User's system has stable internet connection for API calls
- User has at least 1GB free disk space for vault and logs

## Out of Scope

- Multiple simultaneous Watchers (Bronze tier includes ONE watcher only)
- Human-in-the-loop approval workflow (Silver tier feature)
- MCP servers for external actions (Silver tier feature)
- Automated scheduling via cron/Task Scheduler (Silver tier feature)
- Ralph Wiggum loop for autonomous multi-step execution (Gold tier feature)
- Error recovery and watchdog processes (Gold tier feature)
- Cloud deployment (Platinum tier feature)
- Integration with external services beyond Gmail or file system
- Advanced Agent Skills library (Bronze tier requires minimum one skill)
- Orchestrator process for coordinating components (Silver tier feature)

## Dependencies

- Obsidian desktop application (v1.10.6+)
- Python 3.13+ with pip package manager
- Claude Code CLI with valid subscription or API key
- Gmail API credentials (if choosing Gmail Watcher option)
- Python packages: google-auth, google-auth-oauthlib, google-api-python-client (for Gmail Watcher)
- Python packages: watchdog (for File System Watcher)

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
| :---- | :---- | :---- | :---- |
| Gmail API quota limits reached | High - Watcher stops detecting emails | Medium | Implement exponential backoff, document quota limits, provide File System Watcher alternative |
| Obsidian vault corruption | High - Data loss | Low | Document backup procedures, implement file validation before writes |
| Watcher script crashes | Medium - Tasks not detected | Medium | Implement error handling, logging, and recovery instructions |
| Claude Code API rate limits | Medium - Processing delays | Medium | Document rate limits, implement queuing for tasks |
| User lacks technical skills | Medium - Setup failure | High | Provide detailed step-by-step documentation with screenshots |
| File permission issues | Medium - Cannot write to vault | Low | Document required permissions, provide troubleshooting guide |
