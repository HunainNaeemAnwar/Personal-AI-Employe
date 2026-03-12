# Tasks: Silver Tier - Enhanced Automation

**Input**: Design documents from `/specs/002-silver-tier/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested in the specification, so test tasks are omitted. Integration validation is included in quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Repository root with `watchers/`, `mcp_servers/`, `.claude/skills/`, `scheduler/`, `tests/`
- MCP server is separate Node.js/TypeScript project in `mcp_servers/email_sender/`
- Paths follow structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency updates for Silver tier

- [X] T001 Update pyproject.toml with Silver tier Python dependencies (linkedin-api, selenium, beautifulsoup4, pytest, pytest-asyncio)
- [X] T002 [P] Update .env.example with LinkedIn API credentials and scheduling settings
- [X] T003 [P] Create mcp_servers/email_sender/ directory for Node.js MCP server
- [X] T004 [P] Create scheduler/ directory with __init__.py for cron and Task Scheduler setup scripts
- [X] T005 [P] Update vault_setup/templates/ with plan_template.md for Plan.md file generation
- [X] T006 Install Silver tier Python dependencies via `uv pip install -e .`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create watchers/state_manager.py with StateManager class for SQLite state persistence
- [X] T008 Implement SQLite schema creation in state_manager.py (processed_items table, schema_version table)
- [X] T009 Implement state query methods in state_manager.py (check_processed, insert_item, update_item)
- [X] T010 [P] Update watchers/base_watcher.py to integrate StateManager for duplicate prevention
- [X] T011 [P] Add health check heartbeat logging to watchers/base_watcher.py (writes to /Logs every 60s)
- [X] T012 [P] Update vault_setup/folder_structure.py to add /Pending_Approval folder to vault structure
- [X] T013 [P] Update Company_Handbook.md template with approval thresholds section (client communications, payments >$500, social media posts)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Simultaneous Multi-Source Monitoring (Priority: P1) 🎯 MVP

**Goal**: Enable Gmail and File System watchers to run concurrently without conflicts or duplicate task creation

**Independent Test**: Send an email and drop a file within the same 2-minute window, then verify both tasks are created in /Needs_Action with unique IDs and no duplicates after restart

### Implementation for User Story 1

- [X] T014 [P] [US1] Update watchers/gmail_watcher.py to use StateManager for duplicate prevention
- [X] T015 [P] [US1] Update watchers/filesystem_watcher.py to use StateManager for duplicate prevention
- [X] T016 [US1] Create watchers/orchestrator.py to launch and manage multiple watcher processes via subprocess.Popen
- [X] T017 [US1] Implement health check monitoring in orchestrator.py (reads heartbeat files every 60s)
- [X] T018 [US1] Implement watcher restart logic in orchestrator.py (restarts crashed watchers after 5s delay)
- [X] T019 [US1] Add graceful shutdown handler in orchestrator.py (SIGTERM handler for clean state persistence)
- [X] T020 [US1] Update watchers/config.py with orchestrator settings (watcher list, restart policy, health check interval)
- [X] T021 [US1] Add separate log files for each watcher in /Logs folder (gmail_watcher.log, filesystem_watcher.log, orchestrator.log)

**Checkpoint**: At this point, dual watchers should run concurrently for 1 hour without crashes, and no duplicate tasks should be created after restart

---

## Phase 4: User Story 2 - Automated Email Response Execution (Priority: P2)

**Goal**: Enable Claude to draft and send email responses via MCP server with proper threading and retry logic

**Independent Test**: Process an email task requiring a response, approve the draft, and verify the email is sent successfully with correct recipient, subject, and threading

### Implementation for User Story 2

- [X] T022 [P] [US2] Create mcp_servers/email_sender/package.json with @modelcontextprotocol/server and googleapis dependencies
- [X] T023 [P] [US2] Create mcp_servers/email_sender/tsconfig.json for TypeScript configuration
- [X] T024 [P] [US2] Create mcp_servers/email_sender/.env.example for Gmail API credentials
- [X] T025 [US2] Create mcp_servers/email_sender/src/index.ts with McpServer initialization and StdioServerTransport
- [X] T026 [US2] Create mcp_servers/email_sender/src/gmail-client.ts with GmailClient class wrapping Gmail API
- [X] T027 [US2] Implement sendEmail method in gmail-client.ts with OAuth2 authentication and threading support
- [X] T028 [US2] Implement retry logic in gmail-client.ts (3 attempts with exponential backoff: 1s, 2s, 4s)
- [X] T029 [US2] Register send_email tool in index.ts using server.registerTool() with Zod input/output schemas
- [X] T030 [US2] Implement send_email tool handler in index.ts following contracts/email-mcp-api.yaml spec
- [X] T031 [US2] Add error handling in send_email tool for validation errors, auth errors, rate limits, and network errors
- [X] T032 [US2] Implement email logging in send_email tool (writes sent email details to /Logs/email_sent.log)
- [X] T033 [US2] Create mcp_servers/email_sender/build.sh script for TypeScript compilation
- [X] T034 [US2] Update .env with Gmail API send permissions (gmail.send, gmail.compose scopes)
- [X] T035 [US2] Create docs/mcp_server_setup.md with Node.js MCP server installation and testing instructions

**Checkpoint**: At this point, email sending should work end-to-end with <5 second latency from approval to delivery, and 99% delivery success rate

---

## Phase 5: User Story 3 - LinkedIn Integration for Business Development (Priority: P3)

**Goal**: Monitor LinkedIn messages and automatically post business updates for lead generation

**Independent Test**: (1) Send a LinkedIn message and verify task creation, and (2) create a business update task and verify it's posted to LinkedIn with proper formatting and tracking

### Implementation for User Story 3

- [X] T036 [P] [US3] Create watchers/linkedin_watcher.py with LinkedInWatcher class extending BaseWatcher
- [X] T037 [US3] Implement LinkedIn API authentication in linkedin_watcher.py (OAuth2 with token storage in .env)
- [X] T038 [US3] Implement check_for_updates method in linkedin_watcher.py for message monitoring (5-minute polling)
- [X] T039 [US3] Implement create_action_file method in linkedin_watcher.py for LinkedIn message tasks (LINKEDIN_MSG_* files)
- [X] T040 [US3] Implement LinkedIn posting capability in linkedin_watcher.py (post_to_linkedin method)
- [X] T041 [US3] Implement performance metrics tracking in linkedin_watcher.py (views, likes, comments, shares)
- [X] T042 [US3] Add LinkedIn rate limit handling in linkedin_watcher.py (waits for reset, logs delay)
- [X] T043 [US3] Implement Selenium + BeautifulSoup fallback in linkedin_watcher.py for when API unavailable
- [X] T044 [US3] Update watchers/orchestrator.py to include LinkedIn watcher in managed processes
- [X] T045 [US3] Create .claude/skills/linkedin-posting/SKILL.md with LinkedIn post generation instructions
- [X] T046 [US3] Add LinkedIn post template to linkedin-posting skill (hook, value, context, call-to-action structure)
- [X] T047 [US3] Create docs/linkedin_api_setup.md with LinkedIn API credential setup instructions

**Checkpoint**: At this point, LinkedIn messages should be detected within 10 minutes and posts should publish with 95% success rate

---

## Phase 6: User Story 4 - Persistent State Management (Priority: P4)

**Goal**: Ensure watchers remember processed items across restarts to prevent duplicate task creation

**Independent Test**: Process 10 items, restart all watchers, and verify no duplicate tasks are created for those 10 items

### Implementation for User Story 4

**Note**: Core state persistence was implemented in Phase 2 (Foundational). This phase adds state recovery and corruption handling.

- [X] T048 [US4] Implement state database backup in watchers/state_manager.py (daily SQLite .backup command)
- [X] T049 [US4] Implement state rebuild from vault files in state_manager.py (scans /Needs_Action, /Done, /Rejected)
- [X] T050 [US4] Add corruption detection in state_manager.py (validates schema_version table on startup)
- [X] T051 [US4] Implement automatic state rebuild on corruption in state_manager.py (rebuilds from vault, logs warning)
- [X] T052 [US4] Add state database health check to watchers/orchestrator.py (verifies state.db accessible every 5 minutes)
- [X] T053 [US4] Update docs/troubleshooting.md with state database recovery procedures

**Checkpoint**: At this point, zero duplicate tasks should be created after 10 restart cycles, and state should rebuild automatically if database corrupted

---

## Phase 7: User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P5)

**Goal**: Enable user review and approval of high-stakes actions before execution

**Independent Test**: Create a task exceeding approval thresholds (e.g., client email), verify it moves to /Pending_Approval, approve it, and confirm execution proceeds

### Implementation for User Story 5

- [X] T054 [P] [US5] Create .claude/skills/approval-workflow/SKILL.md with approval threshold evaluation logic
- [X] T055 [US5] Implement threshold checking in approval-workflow skill (reads Company_Handbook.md for thresholds)
- [X] T056 [US5] Implement task move logic in approval-workflow skill (/Needs_Action → /Pending_Approval)
- [X] T057 [US5] Add approval request YAML frontmatter to approval-workflow skill (task_id, threshold_exceeded, requested_timestamp)
- [X] T058 [US5] Implement approval command handler in approval-workflow skill (claude "approve task TASK_ID")
- [X] T059 [US5] Implement rejection command handler in approval-workflow skill (claude "reject task TASK_ID --reason 'reason'")
- [X] T060 [US5] Add approval decision logging in approval-workflow skill (writes to /Logs/approvals.log)
- [X] T061 [US5] Implement 24-hour reminder system in approval-workflow skill (checks pending tasks daily, writes reminder to Dashboard.md)
- [X] T062 [US5] Update Company_Handbook.md with approval workflow documentation (commands, thresholds, examples)

**Checkpoint**: At this point, 100% of high-stakes actions should require approval, and approval workflow should reduce unauthorized actions to zero

---

## Phase 8: User Story 6 - Claude Reasoning Loop with Structured Planning (Priority: P6)

**Goal**: Create structured Plan.md files documenting Claude's reasoning process and execution steps for multi-step tasks

**Independent Test**: Create a complex task (e.g., multi-recipient email campaign), verify a Plan.md file is created in /Plans with reasoning steps, and confirm execution follows the documented plan

### Implementation for User Story 6

- [X] T063 [P] [US6] Create .claude/skills/task-planning/SKILL.md with Plan.md creation instructions
- [X] T064 [US6] Implement task analysis logic in task-planning skill (identifies objective, context, constraints)
- [X] T065 [US6] Implement action proposal logic in task-planning skill (generates ordered list of high-level actions)
- [X] T066 [US6] Implement execution step breakdown in task-planning skill (breaks actions into executable steps)
- [X] T067 [US6] Add Plan.md file creation in task-planning skill (writes to /Plans/PLAN_[TASK_ID].md)
- [X] T068 [US6] Implement step status tracking in task-planning skill (marks steps as pending/in_progress/completed/failed)
- [X] T069 [US6] Add timestamp tracking in task-planning skill (started_at, completed_at for each step)
- [X] T070 [US6] Implement reasoning notes documentation in task-planning skill (captures decision rationale)
- [X] T071 [US6] Add alternative approaches section in task-planning skill (documents rejected alternatives)
- [X] T072 [US6] Update vault_setup/templates/plan_template.md with complete Plan.md structure

**Checkpoint**: At this point, 100% of multi-step tasks should have Plan.md files with complete reasoning documentation

---

## Phase 9: User Story 7 - Automated Scheduled Task Execution (Priority: P7)

**Goal**: Enable automatic execution of recurring tasks at configured intervals without manual triggering

**Independent Test**: Configure a daily task (e.g., "Generate morning briefing at 8 AM"), wait for scheduled time, and verify the task executes automatically with results logged to vault

### Implementation for User Story 7

- [X] T073 [P] [US7] Create scheduler/cron_setup.py with cron configuration functions for Linux/Mac
- [X] T074 [P] [US7] Create scheduler/task_scheduler_setup.py with Task Scheduler configuration functions for Windows
- [X] T075 [US7] Implement scheduled_tasks.yaml configuration file in project root (task definitions with cron expressions)
- [X] T076 [US7] Implement cron job creation in cron_setup.py (reads scheduled_tasks.yaml, writes to crontab)
- [X] T077 [US7] Implement Task Scheduler job creation in task_scheduler_setup.py (reads scheduled_tasks.yaml, uses Register-ScheduledTask)
- [X] T078 [US7] Add scheduled task execution wrapper in scheduler/ (handles task execution, logging, error handling)
- [X] T079 [US7] Implement overlapping task prevention in scheduler/ (sequential execution when times overlap)
- [X] T080 [US7] Add scheduled task retry logic in scheduler/ (retries failed tasks at next scheduled time)
- [X] T081 [US7] Implement scheduled task logging in scheduler/ (writes execution results to /Logs/scheduled_tasks.log)
- [X] T082 [US7] Create docs/scheduling_setup.md with cron and Task Scheduler setup instructions
- [X] T083 [US7] Add example scheduled tasks to scheduled_tasks.yaml (daily morning briefing, weekly LinkedIn post)

**Checkpoint**: At this point, scheduled tasks should execute at configured times with 99% reliability over 30-day period

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T084 [P] Update README.md with Silver tier status, version 0.2.0, and feature summary
- [X] T085 [P] Update docs/setup_guide.md with Silver tier setup instructions
- [X] T086 [P] Update docs/troubleshooting.md with Silver tier common issues (LinkedIn rate limits, state database locked, MCP server not found)
- [X] T087 [P] Create tests/unit/test_state_manager.py for state persistence unit tests
- [X] T088 [P] Create tests/integration/test_dual_watchers.py for concurrent watcher integration tests
- [X] T089 [P] Create tests/integration/test_approval_workflow.py for HITL approval workflow tests
- [X] T090 [P] Create tests/integration/test_scheduled_tasks.py for scheduling integration tests
- [X] T091 Run complete quickstart.md validation (all 9 steps, verify all checkboxes pass)
- [X] T092 Perform 24-hour continuous operation test (all watchers, verify 99% uptime)
- [X] T093 Validate performance benchmarks (email detection <2min, LinkedIn polling 5min, email sending <5s)
- [X] T094 [P] Add Silver tier completion checklist to README.md (dual watchers, email sending, LinkedIn, state persistence, approval, planning, scheduling)
- [X] T095 Update PROJECT_REFRENCE.md with Silver tier completion status

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6 → P7)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (orchestrator) but independently testable
- **User Story 4 (P4)**: Core implemented in Foundational (Phase 2) - This phase adds recovery features
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 7 (P7)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models/entities before services
- Services before endpoints/features
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T010, T011, T012, T013)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story, tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch parallel tasks for User Story 1:
Task T014: "Update watchers/gmail_watcher.py to use StateManager"
Task T015: "Update watchers/filesystem_watcher.py to use StateManager"

# These can run simultaneously since they modify different files
```

---

## Parallel Example: User Story 2

```bash
# Launch parallel tasks for User Story 2:
Task T022: "Create mcp_servers/email_sender/package.json"
Task T023: "Create mcp_servers/email_sender/tsconfig.json"
Task T024: "Create mcp_servers/email_sender/.env.example"

# These can run simultaneously since they create different files
```

---

## Parallel Example: User Story 3

```bash
# Launch parallel tasks for User Story 3:
Task T036: "Create watchers/linkedin_watcher.py"
Task T045: "Create .claude/skills/linkedin-posting/SKILL.md"

# These can run simultaneously since they modify different files
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T014-T021)
4. **STOP and VALIDATE**: Test User Story 1 independently (dual watchers run for 1 hour, no duplicates after restart)
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Dual watchers working)
3. Add User Story 2 → Test independently → Deploy/Demo (Email sending working)
4. Add User Story 3 → Test independently → Deploy/Demo (LinkedIn integration working)
5. Add User Story 4 → Test independently → Deploy/Demo (State recovery working)
6. Add User Story 5 → Test independently → Deploy/Demo (Approval workflow working)
7. Add User Story 6 → Test independently → Deploy/Demo (Planning loop working)
8. Add User Story 7 → Test independently → Deploy/Demo (Scheduling working)
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T013)
2. Once Foundational is done:
   - Developer A: User Story 1 (T014-T021) - Dual watchers
   - Developer B: User Story 2 (T022-T035) - Email MCP server (Node.js/TypeScript)
   - Developer C: User Story 3 (T036-T047) - LinkedIn integration
   - Developer D: User Story 5 (T054-T062) - Approval workflow
   - Developer E: User Story 6 (T063-T072) - Planning loop
   - Developer F: User Story 7 (T073-T083) - Scheduling
3. Stories complete and integrate independently
4. User Story 4 (state recovery) can be done by any developer after US1 completes

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 95 (6 setup + 7 foundational + 70 user story implementation + 12 polish)
- Estimated implementation time: 20-30 hours (per PROJECT_REFRENCE.md Silver tier estimate)
- MVP scope: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 21 tasks
- Full Silver tier: All 95 tasks
- MCP server uses Node.js/TypeScript with @modelcontextprotocol/server SDK (per PROJECT_REFRENCE.md Node.js v24+ prerequisite)
