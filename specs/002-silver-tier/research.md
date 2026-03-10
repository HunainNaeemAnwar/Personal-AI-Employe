# Research: Silver Tier - Enhanced Automation

**Feature**: 002-silver-tier
**Date**: 2026-03-09
**Status**: Phase 0 Complete

## Overview

This document captures technical research and decision rationale for Silver tier implementation. All decisions align with Bronze tier foundation and PROJECT_REFRENCE.md requirements.

## Research Topics

### 1. LinkedIn Integration Strategy

**Decision**: LinkedIn API with web scraping fallback

**Rationale**:
- LinkedIn API provides official access to messages and posting capabilities
- API rate limits (100 requests/hour) are sufficient for Silver tier scale (10+ messages/day)
- Web scraping fallback ensures functionality if API access unavailable
- Selenium + BeautifulSoup provides reliable scraping when needed

**Alternatives Considered**:
- **Web scraping only**: Rejected due to fragility (LinkedIn UI changes break scrapers)
- **Third-party services (Zapier, IFTTT)**: Rejected due to local-first architecture requirement
- **Manual LinkedIn checking**: Rejected - defeats automation purpose

**Implementation Notes**:
- Use `linkedin-api` Python library for official API access
- Implement `selenium` + `beautifulsoup4` as fallback
- Store LinkedIn session tokens in `.env` (never in vault)
- 5-minute polling interval balances responsiveness vs rate limits

---

### 2. Persistent State Management

**Decision**: SQLite embedded database

**Rationale**:
- Built-in to Python 3.13+ (no external dependencies)
- Local-first architecture (no network calls)
- ACID transactions prevent race conditions between watchers
- <100MB disk footprint for 1000+ processed items
- Simple schema: `processed_items(id, source, source_id, timestamp, status, task_path)`

**Alternatives Considered**:
- **PostgreSQL**: Rejected - overkill for single-user, requires separate server process
- **JSON files**: Rejected - no transaction support, race conditions with concurrent watchers
- **In-memory only**: Rejected - loses state on restart (violates FR-016)
- **Redis**: Rejected - requires separate server, adds complexity

**Implementation Notes**:
- Database path: `state.db` in project root
- Schema migration strategy: simple version table + ALTER TABLE statements
- Backup strategy: daily SQLite `.backup` command via cron
- Query optimization: index on `(source, source_id)` for duplicate detection

---

### 3. MCP Server Framework

**Decision**: FastMCP (Python)

**Rationale**:
- Official MCP SDK for Python with decorator-based API
- Integrates with FastAPI/Starlette (familiar to Python developers)
- Supports stdio, SSE, and streamable-http transports
- Active maintenance and documentation
- Consistent with Bronze tier Python stack

**Alternatives Considered**:
- **TypeScript MCP SDK**: Rejected - introduces Node.js dependency, breaks Python consistency
- **Custom MCP implementation**: Rejected - reinventing wheel, maintenance burden
- **Direct Gmail API calls**: Rejected - violates MCP server architecture principle

**Implementation Notes**:
- Use `@mcp.tool()` decorator for email sending function
- Stdio transport for local Claude Code integration
- Gmail API OAuth2 credentials stored in `.env`
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)

---

### 4. Automated Scheduling

**Decision**: Platform-specific native schedulers (cron/Task Scheduler)

**Rationale**:
- No additional dependencies (built into OS)
- Reliable 24/7 operation with system-level guarantees
- Survives Python process crashes
- Standard approach for production automation

**Alternatives Considered**:
- **Python APScheduler**: Rejected - requires persistent Python process, no crash recovery
- **Celery + Redis**: Rejected - massive overkill, violates simplicity principle
- **Custom event loop**: Rejected - reinventing wheel, no system-level reliability

**Implementation Notes**:
- Linux/Mac: `crontab -e` with Python script paths
- Windows: PowerShell `Register-ScheduledTask` cmdlet
- Setup scripts: `scheduler/cron_setup.py` and `scheduler/task_scheduler_setup.py`
- Log rotation: daily logs in `/Logs` folder, 30-day retention

---

### 5. Agent Skills Architecture

**Decision**: Claude Code Agent Skills with YAML frontmatter + markdown instructions

**Rationale**:
- Official Claude Code pattern (`.claude/skills/` directory)
- Reusable across different task types and sources
- Version-controlled with project code
- Clear separation of AI reasoning from watcher logic

**Alternatives Considered**:
- **Hardcoded prompts in Python**: Rejected - not reusable, hard to maintain
- **External prompt management service**: Rejected - violates local-first architecture
- **LangChain agents**: Rejected - adds complexity, not needed for Claude Code integration

**Implementation Notes**:
- Four new skills: `linkedin-posting`, `task-planning`, `approval-workflow` (plus existing `email-triage`)
- Each skill has YAML frontmatter (name, description, version) + Instructions + Examples sections
- Skills reference Company_Handbook.md for approval thresholds
- Skills write Plan.md files to `/Plans` folder for multi-step tasks

---

### 6. Multi-Watcher Orchestration

**Decision**: Independent processes with file-based coordination

**Rationale**:
- Watchers run as separate Python processes (no shared memory)
- Coordination via vault folders (/Needs_Action, /In_Progress, /Done)
- SQLite state manager prevents duplicate task creation
- Process isolation: one watcher crash doesn't affect others

**Alternatives Considered**:
- **Single process with threading**: Rejected - GIL limits concurrency, one crash kills all
- **Message queue (RabbitMQ, Kafka)**: Rejected - overkill, violates simplicity
- **Shared memory**: Rejected - complex synchronization, platform-specific

**Implementation Notes**:
- `orchestrator.py` launches watcher processes via `subprocess.Popen`
- Health check: each watcher writes heartbeat to `/Logs/watcher_<name>_heartbeat.json` every 60s
- Restart policy: orchestrator restarts crashed watchers after 5s delay
- Graceful shutdown: SIGTERM handler for clean state persistence

---

### 7. Human-in-the-Loop Approval Workflow

**Decision**: File-based approval with /Pending_Approval folder

**Rationale**:
- Consistent with Bronze tier vault-based architecture
- User reviews tasks in Obsidian (familiar interface)
- Approval commands: `claude "approve task TASK_ID"` or `claude "reject task TASK_ID"`
- Audit trail: approval timestamp and decision logged in task file

**Alternatives Considered**:
- **Web UI for approvals**: Rejected - adds frontend complexity, out of scope for Silver tier
- **Email-based approvals**: Rejected - creates circular dependency (email watcher needs approval)
- **Slack/Discord bot**: Rejected - requires external service, violates local-first

**Implementation Notes**:
- Approval thresholds defined in Company_Handbook.md (e.g., "client emails require approval")
- Task moves: /Needs_Action → /Pending_Approval → /Approved or /Rejected
- Reminder system: daily cron job checks for tasks pending >24 hours, writes reminder to Dashboard.md
- Approval workflow Agent Skill handles threshold evaluation and folder moves

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.13+ | Consistent with Bronze tier |
| Gmail API | google-api-python-client | Latest | Official Google SDK |
| LinkedIn | linkedin-api + selenium | Latest | API with scraping fallback |
| MCP Server | FastMCP | Latest | Official Python MCP SDK |
| State DB | SQLite | 3.x (built-in) | Local-first, zero-config |
| Scheduling | cron / Task Scheduler | OS built-in | Native, reliable |
| Testing | pytest | Latest | Python standard |
| Vault | Obsidian | 1.10.6+ | Bronze tier foundation |
| AI Engine | Claude Code CLI | Latest | Bronze tier foundation |

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LinkedIn API rate limits | Medium | Medium | 5-min polling + web scraping fallback |
| Gmail API quota exhaustion | Low | High | Monitor quota, implement backoff, user notification |
| SQLite corruption | Low | High | Daily backups, rebuild from vault files |
| Watcher process crashes | Medium | Medium | Orchestrator auto-restart, health checks |
| Approval workflow bypass | Low | Critical | Code review, audit logging, no override flags |
| Scheduling failures | Low | Medium | Cron/Task Scheduler logs, health monitoring |

---

## Performance Benchmarks

Based on Bronze tier experience and Silver tier requirements:

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Email detection latency | <2 minutes | Timestamp diff: email received → task file created |
| LinkedIn polling interval | 5 minutes | Watcher config setting |
| File system detection | <30 seconds | Watchdog library event handling |
| Email sending latency | <5 seconds | Timestamp diff: approval → Gmail API response |
| Watcher uptime | 99% over 7 days | Health check logs analysis |
| Duplicate task rate | 0% | SQLite state query after 10 restart cycles |
| Memory per watcher | <200MB | `psutil` monitoring |
| State DB size | <100MB | SQLite `.dbstat` for 1000+ items |

---

## Open Questions

**None.** All technical decisions finalized based on:
- Bronze tier implementation experience
- PROJECT_REFRENCE.md Silver tier requirements
- Constitution principles alignment
- Spec.md functional requirements (FR-001 to FR-038)

---

## Next Steps

Proceed to **Phase 1: Design & Contracts**:
1. Generate `data-model.md` (entities: Processed Item, Email Draft, LinkedIn Message, LinkedIn Post, Plan, Scheduled Task, Approval Request)
2. Create API contracts in `/contracts/` (email MCP server OpenAPI spec, watcher state schema)
3. Generate `quickstart.md` (step-by-step Silver tier setup guide)
4. Update agent context with new technologies
