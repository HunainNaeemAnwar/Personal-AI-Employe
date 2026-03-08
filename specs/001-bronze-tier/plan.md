# Implementation Plan: Bronze Tier - Personal AI Employee Foundation

**Branch**: `001-bronze-tier` | **Date**: 2026-03-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-bronze-tier/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build the foundational Personal AI Employee system with four core components: (1) Obsidian vault knowledge base with structured folders and configuration files, (2) one Watcher script (Gmail OR File System) for automated task detection, (3) Claude Code integration for reading/writing vault files and task processing, and (4) at least one Agent Skill for reusable AI capabilities. This Bronze tier establishes the perception-reasoning-memory loop that transforms Claude from reactive assistant to proactive employee, targeting 8-12 hours implementation time with manual Claude triggering (automation comes in Silver tier).

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**:
- Obsidian v1.10.6+ (knowledge base GUI)
- Claude Code CLI (reasoning engine)
- google-auth, google-auth-oauthlib, google-api-python-client (Gmail Watcher option)
- watchdog (File System Watcher option)
- pathlib, logging, time, json (Python standard library)

**Storage**: Local file system (Obsidian vault as markdown files with YAML frontmatter)
**Testing**: pytest for Python Watcher scripts, manual integration testing for Claude Code workflows
**Target Platform**: Cross-platform desktop (Windows 10+, macOS 11+, Linux with Python 3.13+)
**Project Type**: Single project (Python scripts + Obsidian vault structure)
**Performance Goals**:
- Watcher detection latency: <2 minutes for Gmail, <30 seconds for File System
- Continuous operation: 24 hours without crashes
- Task processing: Handle 10 concurrent tasks without file conflicts

**Constraints**:
- Local-first: All data remains on user's machine
- Manual triggering: User runs Claude Code commands (no orchestrator in Bronze tier)
- Single Watcher: Choose ONE (Gmail OR File System), not both
- No external actions: No MCP servers for sending emails/posting (Silver tier feature)

**Scale/Scope**:
- Single user system
- ~10-20 tasks per day
- Vault size: <1GB (logs, task files, plans)
- One Agent Skill minimum (expandable in future tiers)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle Compliance

**✅ COMPLIANT Principles:**

- **I. Local-First Architecture**: All data stored in Obsidian vault on local machine. No cloud dependencies in Bronze tier.
- **III. Agent Skills**: Minimum one Agent Skill with valid SKILL.md structure (YAML frontmatter, Instructions, Examples).
- **V. Watcher Pattern**: BaseWatcher class with check_for_updates() and create_action_file() methods. Gmail and File System implementations.
- **VII. Audit Logging**: Watcher activity logged to /Logs with timestamp, action, result.
- **VIII. Security-First**: Credentials in .env file (never committed), Gmail OAuth tokens in secure location.

**⚠️ DEFERRED Principles (By Design - Higher Tiers):**

- **II. Human-in-the-Loop (HITL)**: Not required in Bronze tier. Manual Claude triggering provides implicit human control. HITL approval workflow is Silver tier feature.
- **IV. MCP Server Architecture**: Not required in Bronze tier. No external actions (email sending, browser automation). MCP servers introduced in Silver tier.
- **VI. Ralph Wiggum Loop**: Not required in Bronze tier. Manual Claude execution is sufficient. Autonomous multi-step execution is Gold tier feature.

**📋 PARTIAL Compliance:**

- **VII. Comprehensive Audit Logging**: Bronze tier implements basic Watcher logging. Full audit trail with action approval chain is Silver/Gold tier feature.

### Gate Evaluation

**PASS** - Bronze tier appropriately scopes to foundation features. Deferred principles are explicitly planned for higher tiers per constitution's Development Workflow section (Bronze: 8-12 hours, Silver: 20-30 hours, Gold: 40+ hours, Platinum: 60+ hours).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Bronze Tier Structure (Claude Code Project)
personal-ai-employee/
├── .claude/
│   ├── skills/
│   │   └── email-triage/
│   │       ├── SKILL.md              # Email triage Agent Skill
│   │       ├── examples/
│   │       │   └── sample_email.md
│   │       └── references/
│   │           └── triage_rules.md
│   ├── commands/                     # Future: custom slash commands
│   └── hooks/                        # Future: event handlers
│
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py               # Abstract base class
│   ├── gmail_watcher.py              # Gmail API integration
│   ├── filesystem_watcher.py         # File system monitoring
│   └── config.py                     # Watcher configuration
│
├── vault_setup/
│   ├── __init__.py
│   ├── create_vault.py               # Script to initialize Obsidian vault
│   ├── templates/
│   │   ├── dashboard_template.md
│   │   ├── handbook_template.md
│   │   └── task_template.md
│   └── folder_structure.py           # Creates vault folders
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_base_watcher.py
│   │   ├── test_gmail_watcher.py
│   │   └── test_filesystem_watcher.py
│   ├── integration/
│   │   ├── test_vault_creation.py
│   │   ├── test_watcher_to_vault.py
│   │   └── test_claude_integration.py
│   └── fixtures/
│       ├── sample_email.json
│       └── sample_task.md
│
├── docs/
│   ├── setup_guide.md                # Step-by-step setup instructions
│   ├── gmail_api_setup.md            # Gmail API credential setup
│   ├── obsidian_setup.md             # Obsidian vault setup
│   └── troubleshooting.md
│
├── .env.example                      # Template for environment variables
├── .gitignore                        # Ignore .env, credentials, etc.
├── requirements.txt                  # Python dependencies
├── pyproject.toml                    # Project configuration (uv)
├── README.md                         # Project overview
└── main.py                           # Entry point for running watchers
```

**Obsidian Vault Structure** (Created by vault_setup scripts, separate from repo):

```text
AI_Employee_Vault/                    # User creates this in Obsidian
├── Inbox/
├── Needs_Action/
├── Done/
├── Logs/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Dashboard.md                      # Real-time activity summary
└── Company_Handbook.md               # User's rules and policies
```

**Structure Decision**:
- **Claude Code Integration**: `.claude/skills/` directory contains Agent Skills that Claude automatically discovers
- **Python Watchers**: Separate `watchers/` module for perception layer scripts
- **Vault Setup**: `vault_setup/` module with scripts and templates to initialize Obsidian vault
- **Separation of Concerns**: Repository contains code and skills; Obsidian vault is user's data (not in repo)
- **Testing**: Organized by type (unit/integration) with fixtures for test data

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations - Bronze tier complies with all applicable constitution principles. Deferred principles (HITL, MCP, Ralph Wiggum) are intentionally scoped for higher tiers per constitution's Development Workflow section.

## Phase 0: Research & Technology Decisions

**Status**: ✅ Complete

**Artifacts Generated**:
- `research.md`: Comprehensive research on Gmail API, file system monitoring, Obsidian vault structure, Agent Skills, and Python project structure

**Key Decisions**:
1. **Gmail API**: OAuth2 with installed application flow, tokens in `~/.credentials/`
2. **File System Monitoring**: `watchdog` library with event-driven monitoring
3. **Obsidian Vault**: Flat folder structure with YAML frontmatter metadata
4. **Agent Skills**: SKILL.md format with YAML frontmatter, Instructions, Examples
5. **Package Management**: `uv` for fast, deterministic dependency resolution

**Technology Stack Finalized**:
- Python 3.13+ with uv package manager
- google-api-python-client for Gmail integration
- watchdog for file system monitoring
- pytest for testing
- Obsidian v1.10.6+ for knowledge base
- Claude Code for AI reasoning

---

## Phase 1: Design & Contracts

**Status**: ✅ Complete

**Artifacts Generated**:
1. `data-model.md`: Entity definitions for Task File, Watcher, Plan File, Agent Skill, Log Entry
2. `contracts/task-file-schema.json`: JSON schema for task file validation
3. `quickstart.md`: Step-by-step setup guide (1-2 hours)
4. `CLAUDE.md`: Updated with Python 3.13+ and Local file system technologies

**Data Model Summary**:
- **5 Core Entities**: Task File, Watcher, Plan File, Agent Skill, Log Entry
- **State Machines**: Task File (pending → in_progress → completed), Watcher (stopped → running → error)
- **Validation**: JSON schema for task files, Python validators for skills
- **Storage**: ~25MB per year (well within <1GB constraint)

**API Contracts**:
- Task File schema with required fields: type, source, timestamp, priority, status
- YAML frontmatter format for all markdown files
- Log entry format: JSON array in daily files

**Agent Context Updated**:
- Added Python 3.13+ to active technologies
- Added Local file system (Obsidian vault) to database technologies

---

## Phase 2: Implementation Planning (Next Steps)

**Status**: ⏭️ Ready for `/sp.tasks`

**Implementation Approach**:
Bronze tier will be implemented in 4 parallel tracks:

### Track 1: Vault Setup (Priority: P1)
- Create vault initialization scripts
- Generate Dashboard.md and Company_Handbook.md templates
- Implement folder structure creation
- **Estimated**: 2-3 hours

### Track 2: Watcher Implementation (Priority: P2)
- Implement BaseWatcher abstract class
- Build Gmail Watcher with OAuth2 flow
- Build File System Watcher with watchdog
- Add error handling and logging
- **Estimated**: 4-5 hours

### Track 3: Agent Skill Creation (Priority: P3)
- Create email-triage skill with SKILL.md
- Add examples and references
- Validate skill structure
- **Estimated**: 1-2 hours

### Track 4: Testing & Documentation (Priority: P4)
- Write unit tests for Watchers
- Write integration tests for vault → Claude workflow
- Create setup documentation
- **Estimated**: 2-3 hours

**Total Estimated Time**: 9-13 hours (within 8-12 hour Bronze tier target)

**Dependencies**:
- Track 1 must complete before Track 2 (Watchers need vault path)
- Track 3 can run in parallel with Track 1 & 2
- Track 4 runs after all implementation tracks

---

## Constitution Check (Post-Design)

**Re-evaluation after Phase 1 design**:

### Compliance Status

**✅ FULLY COMPLIANT**:
- **I. Local-First Architecture**: All data in Obsidian vault, no cloud dependencies
- **III. Agent Skills**: email-triage skill with valid SKILL.md structure
- **V. Watcher Pattern**: BaseWatcher class with Gmail and FileSystem implementations
- **VII. Audit Logging**: JSON logs in /Logs with timestamp, action, result
- **VIII. Security-First**: OAuth2 tokens in ~/.credentials/, .env for config (gitignored)

**⚠️ DEFERRED (By Design)**:
- **II. HITL**: Manual Claude triggering provides implicit control (Silver tier: automated approval workflow)
- **IV. MCP Servers**: No external actions in Bronze tier (Silver tier: email MCP, browser MCP)
- **VI. Ralph Wiggum Loop**: Manual execution sufficient (Gold tier: autonomous multi-step)

**📋 PARTIAL**:
- **VII. Comprehensive Audit Logging**: Basic Watcher logging implemented. Full audit trail with approval chain is Silver/Gold tier.

### Design Validation

**No new violations introduced**. Design maintains Bronze tier scope:
- Single Watcher (user chooses Gmail OR File System)
- Manual Claude triggering (no orchestrator)
- Local-only operation (no cloud components)
- Basic logging (no advanced monitoring)

**Gate Status**: ✅ PASS - Ready for implementation

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gmail API quota exceeded | Medium | High | Exponential backoff, document limits, File System alternative |
| Watcher crashes | Medium | Medium | Error handling, logging, recovery instructions in docs |
| Obsidian vault corruption | Low | High | Backup procedures in docs, YAML validation before writes |
| User setup complexity | High | Medium | Detailed quickstart guide, automated vault setup script |
| Python version issues | Low | Medium | Pin to 3.13+, test on multiple platforms |
| Credential exposure | Low | High | .env in .gitignore, OAuth tokens outside repo, security docs |

---

## Success Metrics

Bronze tier is successful when:

1. **Setup Time**: User completes setup in <2 hours following quickstart.md
2. **Detection Speed**: Watcher creates task files within 2 minutes (Gmail) or 30 seconds (File System)
3. **Reliability**: System runs 24 hours without crashes
4. **Task Processing**: Claude successfully processes 10 concurrent tasks
5. **Skill Validation**: email-triage skill passes validation and is invoked by Claude
6. **User Satisfaction**: User can visually monitor activity in Obsidian Dashboard

---

## Next Command

Run `/sp.tasks` to generate actionable, dependency-ordered tasks for Bronze tier implementation.

