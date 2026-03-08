---
description: "Implementation tasks for Bronze Tier - Personal AI Employee Foundation"
---

# Tasks: Bronze Tier - Personal AI Employee Foundation

**Input**: Design documents from `/specs/001-bronze-tier/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/task-file-schema.json, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded. Manual integration testing will be performed using quickstart.md validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Bronze tier uses single project structure at repository root:
- `watchers/` - Python watcher scripts
- `vault_setup/` - Vault initialization scripts
- `.claude/skills/` - Agent Skills
- `tests/` - Testing (manual integration tests)
- `docs/` - Documentation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: watchers/, vault_setup/, .claude/skills/, tests/, docs/
- [X] T002 Initialize Python project with pyproject.toml and uv.lock using uv package manager
- [X] T003 [P] Create .env.example with VAULT_PATH, GMAIL_CREDENTIALS_PATH, GMAIL_TOKEN_PATH, GMAIL_QUERY, WATCH_DIRECTORY, FILE_EXTENSIONS, WATCHER_TYPE
- [X] T004 [P] Create .gitignore to exclude .env, .venv/, __pycache__/, *.pyc, .credentials/, *.log
- [X] T005 [P] Create README.md with project overview, setup instructions, and Bronze tier scope

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create watchers/__init__.py to make it a Python package
- [X] T007 Create vault_setup/__init__.py to make it a Python package
- [X] T008 [P] Create watchers/config.py to load environment variables from .env using python-dotenv
- [X] T009 [P] Install dependencies: google-auth, google-auth-oauthlib, google-api-python-client, watchdog, pyyaml, python-dotenv using uv

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Set Up Knowledge Base (Priority: P1) 🎯 MVP

**Goal**: Create an Obsidian vault with essential configuration files so the AI Employee has a structured workspace

**Independent Test**: Create vault, verify folder structure exists, confirm Dashboard.md and Company_Handbook.md are present with valid content

### Implementation for User Story 1

- [X] T010 [P] [US1] Create vault_setup/folder_structure.py with function to create vault folders: Inbox, Needs_Action, Done, Logs, Plans, Pending_Approval, Approved, Rejected
- [X] T011 [P] [US1] Create vault_setup/templates/dashboard_template.md with sections: Recent Activity, Pending Tasks, System Status
- [X] T012 [P] [US1] Create vault_setup/templates/handbook_template.md with sections: Rules of Engagement, Approval Thresholds, Communication Guidelines
- [X] T013 [P] [US1] Create vault_setup/templates/task_template.md with YAML frontmatter structure matching task-file-schema.json
- [X] T014 [US1] Create vault_setup/create_vault.py script with CLI arguments (--path) to initialize complete vault structure
- [X] T015 [US1] Add vault path validation in vault_setup/create_vault.py to ensure directory is writable
- [X] T016 [US1] Add success confirmation output in vault_setup/create_vault.py showing created folders and files

**Checkpoint**: At this point, User Story 1 should be fully functional - user can run create_vault.py and get a complete Obsidian vault

---

## Phase 4: User Story 2 - Monitor External Source (Priority: P2)

**Goal**: Implement Watcher script to monitor either Gmail inbox or file system folder for automated task detection

**Independent Test**: Run Watcher script, trigger test event (send email or drop file), verify .md file appears in /Needs_Action with correct metadata

### Implementation for User Story 2

- [X] T017 [P] [US2] Create watchers/base_watcher.py with abstract BaseWatcher class defining check_for_updates() and create_action_file() methods
- [X] T018 [P] [US2] Add processed_items set tracking in watchers/base_watcher.py to prevent duplicate task files
- [X] T019 [P] [US2] Add logging infrastructure in watchers/base_watcher.py to write JSON logs to vault /Logs folder
- [X] T020 [US2] Create watchers/gmail_watcher.py implementing GmailWatcher class extending BaseWatcher
- [X] T021 [US2] Implement OAuth2 authentication flow in watchers/gmail_watcher.py using google-auth-oauthlib
- [X] T022 [US2] Implement check_for_updates() in watchers/gmail_watcher.py to query Gmail API with GMAIL_QUERY filter
- [X] T023 [US2] Implement create_action_file() in watchers/gmail_watcher.py to create task .md files in /Needs_Action with email metadata
- [X] T024 [US2] Add exponential backoff for Gmail API rate limits in watchers/gmail_watcher.py
- [X] T025 [US2] Add error handling in watchers/gmail_watcher.py to log errors and continue running without crashing
- [X] T026 [P] [US2] Create watchers/filesystem_watcher.py implementing FilesystemWatcher class extending BaseWatcher
- [X] T027 [US2] Implement file monitoring using watchdog.observers.Observer in watchers/filesystem_watcher.py
- [X] T028 [US2] Implement on_created event handler in watchers/filesystem_watcher.py with 1-second debouncing
- [X] T029 [US2] Implement create_action_file() in watchers/filesystem_watcher.py to create task .md files in /Needs_Action with file metadata
- [X] T030 [US2] Add file extension filtering in watchers/filesystem_watcher.py based on FILE_EXTENSIONS config
- [X] T031 [US2] Add error handling in watchers/filesystem_watcher.py to log errors and continue running without crashing
- [X] T032 [US2] Create main.py entry point to launch selected watcher based on WATCHER_TYPE environment variable
- [X] T033 [US2] Add --test flag to main.py for testing watcher without continuous monitoring

**Checkpoint**: At this point, User Story 2 should be fully functional - user can run either Gmail or File System Watcher and see task files created

---

## Phase 5: User Story 3 - AI Reads and Writes to Vault (Priority: P3)

**Goal**: Enable Claude Code to read tasks from /Needs_Action and write results to the vault

**Independent Test**: Manually create task file in /Needs_Action, run Claude Code with prompt to process it, verify Claude reads file, performs reasoning, and writes output to appropriate folder

### Implementation for User Story 3

- [X] T034 [P] [US3] Create vault_setup/validators.py with validate_task_file() function to check YAML frontmatter against task-file-schema.json
- [X] T035 [P] [US3] Create vault_setup/validators.py with validate_yaml_frontmatter() function to ensure proper YAML syntax
- [X] T036 [US3] Add file path utilities in vault_setup/validators.py to generate proper task file names: {TYPE}_{TIMESTAMP}_{SLUG}.md
- [X] T037 [US3] Update watchers/base_watcher.py to use validators before writing task files
- [X] T038 [US3] Create docs/claude_integration.md with instructions for running Claude Code commands on vault folders
- [X] T039 [US3] Add example prompts in docs/claude_integration.md: "Process all tasks in /Needs_Action", "Create plan for EMAIL_xxx.md"

**Checkpoint**: At this point, User Story 3 should be fully functional - Claude Code can read/write vault files with proper validation

---

## Phase 6: User Story 4 - Create Agent Skill (Priority: P4)

**Goal**: Create at least one Agent Skill with valid SKILL.md structure for reusable AI capabilities

**Independent Test**: Create SKILL.md file with proper structure, trigger skill's use case, verify Claude applies skill's instructions

### Implementation for User Story 4

- [X] T040 [US4] Create .claude/skills/email-triage/ directory with subdirectories: examples/, references/
- [X] T041 [US4] Create .claude/skills/email-triage/SKILL.md with YAML frontmatter: name: email-triage, description: "Analyze incoming emails and categorize by urgency and action required. Use when processing email tasks from /Needs_Action."
- [X] T042 [US4] Add Instructions section to .claude/skills/email-triage/SKILL.md with 7 steps: read task, extract info, analyze urgency, categorize priority, suggest actions, create Plan.md, move to /Done
- [X] T043 [US4] Add Examples section to .claude/skills/email-triage/SKILL.md with Example 1: High Priority Client Email (input/output)
- [X] T044 [US4] Add Examples section to .claude/skills/email-triage/SKILL.md with Example 2: Low Priority Newsletter (input/output)
- [X] T045 [P] [US4] Create .claude/skills/email-triage/examples/sample_email.md with realistic email task file
- [X] T046 [P] [US4] Create .claude/skills/email-triage/references/triage_rules.md with urgency keywords and priority criteria
- [X] T047 [US4] Create vault_setup/validators.py with validate_skill() function to check SKILL.md structure (YAML frontmatter, Instructions, Examples)

**Checkpoint**: At this point, User Story 4 should be fully functional - email-triage skill is created and can be invoked by Claude

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T048 [P] Create docs/setup_guide.md with step-by-step setup instructions (consolidated from quickstart.md)
- [ ] T049 [P] Create docs/gmail_api_setup.md with detailed Gmail API credential setup instructions
- [ ] T050 [P] Create docs/troubleshooting.md with common issues and solutions for each watcher type
- [ ] T051 [P] Add inline code comments to all Python modules for clarity
- [ ] T052 Create tests/integration/test_vault_creation.py with manual test checklist for vault setup
- [ ] T053 Create tests/integration/test_watcher_to_vault.py with manual test checklist for watcher → task file creation
- [ ] T054 Create tests/integration/test_claude_integration.py with manual test checklist for Claude → vault interaction
- [ ] T055 Update README.md with Bronze tier completion checklist and next steps (Silver tier preview)
- [ ] T056 Run quickstart.md validation: complete all steps and verify 24-hour continuous operation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (but needs vault path from US1 for testing)
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (vault) and US2 (task files) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- **US1**: All tasks marked [P] can run in parallel (templates), then create_vault.py integrates them
- **US2**: BaseWatcher first, then GmailWatcher and FilesystemWatcher in parallel, then main.py integrates
- **US3**: Validators can be built in parallel, then integrated into watchers
- **US4**: Skill directory, SKILL.md, examples, and references can be built in parallel

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003, T004, T005)
- All Foundational tasks marked [P] can run in parallel (T008, T009)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within US1: T010, T011, T012, T013 can run in parallel
- Within US2: T017, T018, T019 can run in parallel; T020-T025 (Gmail) and T026-T031 (Filesystem) can run in parallel
- Within US3: T034, T035 can run in parallel
- Within US4: T045, T046 can run in parallel
- All Polish tasks marked [P] can run in parallel (T048, T049, T050, T051)

---

## Parallel Example: User Story 1

```bash
# Launch all templates for User Story 1 together:
Task: "Create vault_setup/templates/dashboard_template.md"
Task: "Create vault_setup/templates/handbook_template.md"
Task: "Create vault_setup/templates/task_template.md"
Task: "Create vault_setup/folder_structure.py"

# Then integrate with:
Task: "Create vault_setup/create_vault.py script"
```

---

## Parallel Example: User Story 2

```bash
# Build base infrastructure:
Task: "Create watchers/base_watcher.py with abstract BaseWatcher class"
Task: "Add processed_items set tracking"
Task: "Add logging infrastructure"

# Then build watchers in parallel:
# Developer A:
Task: "Create watchers/gmail_watcher.py"
Task: "Implement OAuth2 authentication flow"
Task: "Implement check_for_updates() for Gmail"
Task: "Implement create_action_file() for Gmail"
Task: "Add exponential backoff for Gmail API"
Task: "Add error handling for Gmail"

# Developer B (simultaneously):
Task: "Create watchers/filesystem_watcher.py"
Task: "Implement file monitoring using watchdog"
Task: "Implement on_created event handler"
Task: "Implement create_action_file() for filesystem"
Task: "Add file extension filtering"
Task: "Add error handling for filesystem"

# Then integrate:
Task: "Create main.py entry point"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T009)
3. Complete Phase 3: User Story 1 (T010-T016)
4. **STOP and VALIDATE**: Run create_vault.py, verify vault structure in Obsidian
5. Demo vault setup capability

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T009)
2. Add User Story 1 → Test independently → Demo vault creation (T010-T016) ✅ MVP!
3. Add User Story 2 → Test independently → Demo watcher detection (T017-T033)
4. Add User Story 3 → Test independently → Demo Claude integration (T034-T039)
5. Add User Story 4 → Test independently → Demo agent skill (T040-T047)
6. Polish → Complete Bronze tier (T048-T056)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (T010-T016) - 2-3 hours
   - Developer B: User Story 2 (T017-T033) - 4-5 hours
   - Developer C: User Story 4 (T040-T047) - 1-2 hours
3. Developer A (after US1): User Story 3 (T034-T039) - 1-2 hours
4. All developers: Polish (T048-T056) - 2-3 hours

**Total Estimated Time**: 10-15 hours (within 8-12 hour Bronze tier target with parallel execution)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are manual integration tests (no automated test suite in Bronze tier)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

---

## Success Criteria Mapping

Tasks map to success criteria from spec.md:

- **SC-001** (Setup in <2 hours): T001-T009, T048-T050 (documentation)
- **SC-002** (Watcher detection <2 min): T017-T033 (Watcher implementation)
- **SC-003** (Claude reads/writes 100%): T034-T039 (validation and integration)
- **SC-004** (24-hour operation): T025, T031 (error handling), T056 (validation)
- **SC-005** (Agent Skill created): T040-T047 (email-triage skill)
- **SC-006** (Visual monitoring): T011 (Dashboard.md template)
- **SC-007** (Required metadata 100%): T013, T034-T037 (validation)
- **SC-008** (10 concurrent tasks): T018 (processed_items tracking), T037 (validation)
