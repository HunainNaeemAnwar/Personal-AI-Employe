# Implementation Plan: Silver Tier - Enhanced Automation

**Branch**: `002-silver-tier` | **Date**: 2026-03-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-silver-tier/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Silver tier transforms the Bronze tier foundation into a fully functional autonomous assistant by adding:
- **Dual/Multiple Watchers**: Gmail, File System, and LinkedIn monitoring running concurrently
- **Email Sending**: MCP server for automated email responses via Gmail API
- **LinkedIn Integration**: Message monitoring + automatic business posting for lead generation
- **Persistent State**: SQLite database preventing duplicate task creation across restarts
- **Human-in-the-Loop**: Approval workflow for sensitive actions (client communications, payments)
- **Claude Reasoning Loop**: Structured Plan.md files documenting multi-step task execution
- **Automated Scheduling**: Cron (Linux/Mac) or Task Scheduler (Windows) for recurring tasks
- **Agent Skills**: All AI reasoning capabilities implemented as reusable Claude Code Agent Skills

This tier delivers true automation with 24/7 operation capability while maintaining local-first architecture and human oversight for critical decisions.

## Technical Context

**Language/Version**: Python 3.13+ (consistent with Bronze tier foundation)
**Primary Dependencies**:
- Gmail API (`google-api-python-client`, `google-auth-oauthlib`) for email monitoring and sending
- LinkedIn API or web scraping fallback (`selenium`, `beautifulsoup4`) for message monitoring and posting
- FastMCP for MCP server implementation (email sending capability)
- SQLite3 (built-in) for persistent state management
- Claude Code CLI for AI reasoning and task processing
- Agent Skills framework (`.claude/skills/`) for reusable AI capabilities
- `python-dotenv` for environment configuration
- `pyyaml` for YAML frontmatter parsing

**Storage**:
- SQLite database (`state.db`) for processed items tracking (prevents duplicates)
- Obsidian vault (markdown files with YAML frontmatter) for task management
- Vault structure: /Needs_Action, /Plans, /Pending_Approval, /Approved, /Rejected, /Done, /Logs

**Testing**: pytest with integration tests for watcher detection, state persistence, and MCP server functionality

**Target Platform**: Cross-platform (Linux, macOS, Windows) with platform-specific scheduling:
- Linux/Mac: cron for scheduled tasks
- Windows: Task Scheduler for scheduled tasks

**Project Type**: Single project with multiple concurrent processes (watchers + MCP server)

**Performance Goals**:
- Email detection: <2 minutes from receipt to task file creation
- LinkedIn monitoring: <5 minutes polling interval
- File system detection: <30 seconds from file drop to task creation
- Email sending: <5 seconds from approval to delivery
- Watcher uptime: 99% over 7-day continuous operation
- Zero duplicate tasks after system restarts

**Constraints**:
- Local-first architecture (no cloud dependencies for core functionality)
- Human approval required for sensitive actions (client communications, payments >$500)
- API rate limits: Gmail (250 emails/day quota), LinkedIn (100 requests/hour)
- Network resilience: graceful degradation during API outages
- Memory footprint: <200MB per watcher process
- Disk space: <100MB for state database and logs

**Scale/Scope**:
- Single user operation
- 100+ emails/day processing capacity
- 10+ LinkedIn messages/day monitoring
- 24/7 continuous operation capability
- 10+ concurrent scheduled tasks
- 1000+ processed items in state database

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Initial Check (Pre-Research) ✅

| Principle | Status | Evidence |
|-----------|--------|----------|
| **Local-First Architecture** | ✅ PASS | SQLite for state, local vault storage, no cloud dependencies for core functionality |
| **Human-in-the-Loop (HITL)** | ✅ PASS | /Pending_Approval workflow (FR-028 to FR-031), approval thresholds from Company_Handbook.md |
| **Agent Skills** | ✅ PASS | All AI reasoning as Agent Skills (FR-036 to FR-038): email-triage, linkedin-posting, task-planning, approval-workflow |
| **MCP Server Architecture** | ✅ PASS | Email sending MCP server (FR-005 to FR-009) with Gmail API integration |
| **Watcher Pattern** | ✅ PASS | Multiple concurrent watchers (FR-001 to FR-004): Gmail, File System, LinkedIn |
| **Ralph Wiggum Loop** | ⏭️ DEFERRED | Intentionally out of scope for Silver tier - reserved for Gold tier per PROJECT_REFRENCE.md |
| **Audit Logging** | ✅ PASS | /Logs folder for all operations (FR-026, FR-033), JSON-formatted logs with timestamps |
| **Security-First Design** | ✅ PASS | OAuth2 credentials, .env for secrets, approval workflow for sensitive actions, no hardcoded tokens |

### Post-Design Re-Check (After Phase 1) ✅

| Principle | Status | Evidence from Design Artifacts |
|-----------|--------|--------------------------------|
| **Local-First Architecture** | ✅ PASS | data-model.md confirms SQLite schema, no external services. All data persists locally in vault or state.db |
| **Human-in-the-Loop (HITL)** | ✅ PASS | Approval Request entity in data-model.md with full workflow. quickstart.md documents approval commands |
| **Agent Skills** | ✅ PASS | quickstart.md includes 4 complete Agent Skills with YAML frontmatter and instructions |
| **MCP Server Architecture** | ✅ PASS | email-mcp-api.yaml provides complete OpenAPI spec with OAuth2 security, retry logic, error handling |
| **Watcher Pattern** | ✅ PASS | watcher-state-schema.json defines state persistence preventing duplicates. Orchestrator coordinates 3 watchers |
| **Ralph Wiggum Loop** | ⏭️ DEFERRED | Confirmed out of scope - no design artifacts for autonomous loop |
| **Audit Logging** | ✅ PASS | data-model.md includes logging in Processed Item, Plan, and Scheduled Task entities |
| **Security-First Design** | ✅ PASS | email-mcp-api.yaml uses OAuth2. quickstart.md stores secrets in .env. No credentials in vault |

### Architecture Standards

| Standard | Status | Evidence from Design |
|----------|--------|---------------------|
| **Orchestrator Pattern** | ✅ PASS | orchestrator.py in project structure coordinates watchers. Data flow: Watcher → State Manager → Task File → Claude → MCP → Logs |
| **Error Recovery** | ✅ PASS | email-mcp-api.yaml includes retry logic (3 attempts, exponential backoff). Orchestrator restarts crashed watchers |
| **Test-Driven Development** | ✅ PASS | tests/ directory in project structure with unit and integration tests. quickstart.md includes validation steps |
| **Complexity Budget** | ✅ PASS | Single project structure maintained. 7 entities in data-model.md (reasonable for scope). No over-engineering |

### Gate Decision: **APPROVED** ✅

**Initial Check**: All mandatory principles satisfied before research.

**Post-Design Check**: Design artifacts (data-model.md, contracts/, quickstart.md) confirm all principles are implemented correctly. No design drift detected. Ralph Wiggum loop deferral remains intentional per PROJECT_REFRENCE.md tier structure.

**Proceed to Phase 2**: Ready for `/sp.tasks` command to generate actionable task breakdown.

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

## Project Structure

### Documentation (this feature)

```text
specs/002-silver-tier/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── email-mcp-api.yaml
│   └── watcher-state-schema.json
├── checklists/
│   └── requirements.md  # Quality validation (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
personal-ai-employee/
├── watchers/
│   ├── __init__.py
│   ├── base_watcher.py          # Abstract base class for all watchers
│   ├── gmail_watcher.py          # Gmail monitoring (Bronze tier - existing)
│   ├── filesystem_watcher.py    # File system monitoring (Bronze tier - existing)
│   ├── linkedin_watcher.py      # NEW: LinkedIn message monitoring + posting
│   ├── state_manager.py         # NEW: SQLite state persistence
│   ├── config.py                # Configuration management
│   └── orchestrator.py          # NEW: Multi-watcher coordination
│
├── mcp_servers/
│   ├── __init__.py
│   └── email_sender/            # NEW: Email sending MCP server
│       ├── __init__.py
│       ├── server.py            # FastMCP server implementation
│       ├── gmail_client.py      # Gmail API wrapper
│       └── config.py
│
├── .claude/
│   └── skills/
│       ├── email-triage/        # Bronze tier - existing
│       │   └── SKILL.md
│       ├── linkedin-posting/    # NEW: LinkedIn post generation
│       │   └── SKILL.md
│       ├── task-planning/       # NEW: Plan.md creation
│       │   └── SKILL.md
│       └── approval-workflow/   # NEW: HITL approval logic
│           └── SKILL.md
│
├── vault_setup/
│   ├── __init__.py
│   ├── create_vault.py          # Bronze tier - existing
│   ├── folder_structure.py      # Bronze tier - existing
│   └── templates/
│       ├── dashboard_template.md
│       ├── handbook_template.md
│       ├── task_template.md
│       └── plan_template.md     # NEW: Plan.md template
│
├── scheduler/
│   ├── __init__.py
│   ├── cron_setup.py            # NEW: Linux/Mac cron configuration
│   └── task_scheduler_setup.py # NEW: Windows Task Scheduler configuration
│
├── tests/
│   ├── unit/
│   │   ├── test_state_manager.py
│   │   ├── test_linkedin_watcher.py
│   │   └── test_email_mcp.py
│   ├── integration/
│   │   ├── test_dual_watchers.py
│   │   ├── test_approval_workflow.py
│   │   └── test_scheduled_tasks.py
│   └── fixtures/
│       ├── sample_emails.json
│       └── sample_linkedin_messages.json
│
├── docs/
│   ├── setup_guide.md           # Bronze tier - existing
│   ├── gmail_api_setup.md       # Bronze tier - existing
│   ├── linkedin_api_setup.md    # NEW: LinkedIn API credentials
│   ├── mcp_server_setup.md      # NEW: Email MCP server setup
│   ├── scheduling_setup.md      # NEW: Cron/Task Scheduler setup
│   └── troubleshooting.md       # Bronze tier - existing (to be updated)
│
├── pyproject.toml               # Bronze tier - existing (to be updated)
├── .env.example                 # Bronze tier - existing (to be updated)
├── README.md                    # Bronze tier - existing (to be updated)
└── state.db                     # NEW: SQLite database (created at runtime)
```

**Structure Decision**: Single project architecture selected because:
1. All components are Python-based backend services (no frontend)
2. Watchers, MCP server, and scheduler are tightly coupled through shared vault
3. No API boundaries between components (file-based communication via vault)
4. Deployment is local-first (no separate frontend/backend deployment)
5. Consistent with Bronze tier foundation (extends existing structure)

**Key Additions for Silver Tier**:
- `linkedin_watcher.py`: Third watcher for LinkedIn integration
- `state_manager.py`: SQLite persistence preventing duplicate tasks
- `orchestrator.py`: Coordinates multiple concurrent watchers
- `mcp_servers/email_sender/`: MCP server for Gmail API email sending
- `scheduler/`: Cron and Task Scheduler setup scripts
- Four new Agent Skills: linkedin-posting, task-planning, approval-workflow (email-triage exists from Bronze)
- `state.db`: Runtime SQLite database for processed items tracking

## Complexity Tracking

**No violations detected.** All constitution principles and architecture standards are satisfied without requiring complexity budget exceptions.

Constitution Check shows full alignment with local-first architecture, HITL approval, Agent Skills pattern, MCP server architecture, watcher pattern, audit logging, and security-first design. Ralph Wiggum loop is intentionally deferred to Gold tier per PROJECT_REFRENCE.md phasing strategy.
