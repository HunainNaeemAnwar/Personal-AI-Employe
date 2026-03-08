# Research: Bronze Tier - Personal AI Employee Foundation

**Feature**: Bronze Tier Implementation
**Date**: 2026-03-07
**Status**: Complete

## Research Areas

### 1. Gmail API Integration Best Practices

**Decision**: Use OAuth2 with installed application flow, store tokens in user's home directory

**Rationale**:
- OAuth2 is the only supported authentication method for Gmail API (Basic Auth deprecated)
- Installed application flow is appropriate for desktop scripts (vs web application flow)
- Token storage in `~/.credentials/` follows Google's quickstart pattern
- Refresh tokens enable long-running operation without re-authentication

**Implementation Details**:
- Use `google-auth-oauthlib` for OAuth2 flow
- Store credentials in `~/.credentials/gmail-token.json` (outside repo)
- Implement token refresh logic in watcher
- Handle quota limits: 250 quota units per user per second, 1 billion per day
- Use exponential backoff for rate limit errors (HTTP 429)

**Alternatives Considered**:
- Service Account: Rejected - requires Google Workspace domain, not suitable for personal Gmail
- API Key: Rejected - not supported for Gmail API user data access

**References**:
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail API Quotas](https://developers.google.com/gmail/api/reference/quota)

---

### 2. File System Monitoring Patterns

**Decision**: Use `watchdog` library with event-driven monitoring

**Rationale**:
- Event-driven is more efficient than polling (no CPU waste on empty checks)
- `watchdog` is cross-platform (Windows, macOS, Linux) with native OS APIs
- Mature library (10+ years, 6k+ stars) with active maintenance
- Handles edge cases: file moves, renames, temporary files

**Implementation Details**:
- Use `watchdog.observers.Observer` with `FileSystemEventHandler`
- Monitor `on_created` event for new files
- Implement debouncing (wait 1 second) to handle multi-part file writes
- Filter by file extension if needed (e.g., only `.pdf`, `.docx`)
- Log all events to `/Logs` for debugging

**Alternatives Considered**:
- Polling with `os.listdir()`: Rejected - inefficient, high CPU usage, misses rapid changes
- `inotify` (Linux only): Rejected - not cross-platform
- `fsevents` (macOS only): Rejected - not cross-platform

**References**:
- [watchdog Documentation](https://python-watchdog.readthedocs.io/)
- [File System Events Best Practices](https://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes)

---

### 3. Obsidian Vault Structure

**Decision**: Use flat folder structure with YAML frontmatter for metadata

**Rationale**:
- Obsidian works best with flat folders (easier navigation, search)
- YAML frontmatter is Obsidian's native metadata format
- Folder-based workflow (Needs_Action → Plans → Done) is intuitive
- Dashboard.md as "home page" follows Obsidian community patterns

**Implementation Details**:
- Folder structure: `/Inbox`, `/Needs_Action`, `/Done`, `/Logs`, `/Plans`, `/Pending_Approval`, `/Approved`, `/Rejected`
- YAML frontmatter schema:
  ```yaml
  ---
  type: email|file_drop|transaction
  source: sender@example.com|/path/to/file
  timestamp: 2026-03-07T10:30:00Z
  priority: high|medium|low
  status: pending|in_progress|completed
  ---
  ```
- File naming: `{TYPE}_{ID}_{SLUG}.md` (e.g., `EMAIL_001_invoice-request.md`)
- Dashboard.md uses Dataview plugin syntax for dynamic queries (optional)

**Alternatives Considered**:
- Nested folders by date: Rejected - harder to navigate, breaks flat workflow
- JSON metadata: Rejected - not Obsidian native, harder to edit manually
- Tags instead of folders: Rejected - less visual, harder to track workflow state

**References**:
- [Obsidian YAML Frontmatter](https://help.obsidian.md/Editing+and+formatting/Properties)
- [Obsidian Folder Structure Best Practices](https://forum.obsidian.md/t/best-practices-for-folder-structure/)

---

### 4. Agent Skill Design Patterns

**Decision**: Use SKILL.md with YAML frontmatter, Instructions, and Examples sections

**Rationale**:
- SKILL.md is Claude Code's standard format (auto-discovered from `.claude/skills/`)
- YAML frontmatter provides structured metadata for skill discovery
- Instructions section gives Claude step-by-step guidance
- Examples section provides concrete demonstrations for pattern matching

**Implementation Details**:
- Skill structure:
  ```markdown
  ---
  name: email-triage
  description: Analyze incoming emails and categorize by urgency and action required
  ---

  # Email Triage

  ## Instructions
  1. Read email metadata (from, subject, received timestamp)
  2. Analyze content for urgency indicators (keywords: urgent, asap, deadline)
  3. Categorize: high/medium/low priority
  4. Suggest actions: reply, forward, archive, flag for follow-up
  5. Write analysis to Plan.md

  ## Examples
  [Concrete examples with input/output]
  ```
- Naming convention: lowercase-with-hyphens (e.g., `email-triage`, `task-prioritization`)
- Store supporting files in skill subdirectories: `examples/`, `references/`, `scripts/`

**Alternatives Considered**:
- JSON skill definition: Rejected - not Claude Code standard, harder to edit
- Inline prompts: Rejected - not reusable, no version control
- Separate instruction files: Rejected - breaks skill encapsulation

**References**:
- [Claude Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Claude Code Plugin Structure](https://github.com/anthropics/claude-code/blob/main/plugins/README.md)

---

### 5. Python Project Structure & Package Management

**Decision**: Use `uv` for package management with `pyproject.toml`

**Rationale**:
- `uv` is 10-100x faster than pip (Rust-based)
- Modern Python standard (PEP 621) with `pyproject.toml`
- Deterministic dependency resolution (lock file)
- Compatible with existing pip workflows
- Project already uses `uv` (per PROJECT_REFERENCE.md)

**Implementation Details**:
- Use `pyproject.toml` for project metadata and dependencies
- Use `uv.lock` for deterministic builds (commit to repo)
- Testing with `pytest` (industry standard)
- Code formatting with `black` (optional, for consistency)
- Linting with `ruff` (fast, modern alternative to flake8/pylint)

**Dependencies**:
```toml
[project]
name = "personal-ai-employee"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-api-python-client>=2.0.0",
    "watchdog>=3.0.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
```

**Alternatives Considered**:
- pip + requirements.txt: Rejected - slower, no lock file, less modern
- poetry: Rejected - slower than uv, more complex
- conda: Rejected - overkill for pure Python project, slower

**References**:
- [uv Documentation](https://github.com/astral-sh/uv)
- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Language | Python | 3.13+ | Modern features, async support, type hints |
| Package Manager | uv | Latest | Fast, modern, deterministic |
| Gmail Integration | google-api-python-client | 2.0+ | Official Google library |
| File Monitoring | watchdog | 3.0+ | Cross-platform, event-driven |
| Testing | pytest | 7.0+ | Industry standard, rich ecosystem |
| Knowledge Base | Obsidian | 1.10.6+ | Local-first, markdown-based |
| AI Engine | Claude Code | Latest | Agentic coding, skill support |

---

## Implementation Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gmail API quota exceeded | High - Watcher stops | Implement exponential backoff, document limits, provide File System alternative |
| watchdog platform issues | Medium - Watcher fails | Test on all platforms, provide fallback polling mode |
| Obsidian vault corruption | High - Data loss | Document backup procedures, validate YAML before writes |
| Python version incompatibility | Medium - Setup fails | Pin to Python 3.13+, test on multiple versions |
| Credential exposure | High - Security breach | Use .env, .gitignore, document secure storage |

---

## Next Steps (Phase 1)

1. Create data-model.md defining entities (Task File, Watcher, Agent Skill)
2. Generate contracts/ with JSON schemas for task file format
3. Create quickstart.md with step-by-step setup instructions
4. Update agent context with technology decisions
