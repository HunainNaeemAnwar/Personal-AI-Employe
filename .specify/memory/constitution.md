<!--
Sync Impact Report:
- Version change: [NEW] → 1.0.0
- Initial constitution creation for Personal AI Employee project
- Added sections: Core Principles (8), Architecture Standards, Security Requirements, Development Workflow, Governance
- Templates requiring updates: ⚠ pending validation
- Follow-up TODOs: None
-->

# Personal AI Employee Constitution

## Core Principles

### I. Local-First Architecture

All sensitive data MUST remain on the user's local machine by default. The Obsidian vault serves as the single source of truth for state, memory, and audit trails.

**Requirements**:
- Obsidian vault structure: `/Needs_Action/`, `/Plans/`, `/Pending_Approval/`, `/Approved/`, `/Rejected/`, `/Done/`, `/Logs/`
- Dashboard.md: Real-time summary of bank balance, pending messages, active projects
- Company_Handbook.md: Rules of engagement, approval thresholds, business policies
- Business_Goals.md: Quarterly objectives, key metrics, subscription audit rules

**Cloud Deployment (Optional - Platinum Tier)**:
- Cloud agent owns: Email triage, draft replies, social post drafts (draft-only)
- Local agent owns: Approvals, WhatsApp sessions, payments/banking, final send/post actions
- Vault sync via Git or Syncthing (markdown/state only, never credentials)
- Claim-by-move rule: First agent to move item from `/Needs_Action/` to `/In_Progress/<agent>/` owns it

**Rationale**: Privacy and data sovereignty are non-negotiable. Users retain full control over personal and business information without dependency on external services.

### II. Human-in-the-Loop (HITL) for Sensitive Actions

Any action meeting these criteria MUST require explicit human approval before execution:
- Financial transactions (payments, transfers, subscription changes)
- Communications to new/unknown contacts
- Irreversible operations (deletions, force pushes, contract signing)
- Actions exceeding defined thresholds (e.g., >$100, bulk operations)

**Approval Workflow**:
1. AI detects sensitive action needed
2. Creates approval request file in `/Pending_Approval/` with metadata:
   - `type`: approval_request
   - `action`: payment|email|social|file_operation
   - `amount`: (if financial)
   - `recipient`: target entity
   - `reason`: justification
   - `created`: ISO 8601 timestamp
   - `expires`: expiration timestamp
   - `status`: pending
3. Human reviews and moves to `/Approved/` or `/Rejected/`
4. Orchestrator detects approved file and triggers MCP action
5. Result logged to `/Logs/YYYY-MM-DD.json`
6. Completed file moved to `/Done/`

**Rationale**: Autonomous systems can misinterpret context. Critical decisions require human judgment to prevent costly errors.

### III. Agent Skills for AI Capabilities

AI functionality SHOULD be packaged as Agent Skills where appropriate. Agent Skills are modular capabilities that extend Claude's functionality through structured knowledge.

**Skill Structure** (`SKILL.md`):
```markdown
---
name: skill-name-lowercase-hyphens
description: Brief description of what this skill does and when Claude should use it (max 1024 chars)
---

# Skill Name

## Instructions
[Clear, step-by-step guidance for Claude to follow]

## Examples
[Concrete examples demonstrating skill usage]
```

**Requirements**:
- `name`: Lowercase letters, numbers, hyphens only; max 64 chars; no XML tags; no reserved words (anthropic, claude)
- `description`: Non-empty, max 1024 chars, no XML tags, includes trigger conditions
- Instructions: Detailed, step-by-step guidance for task execution
- Examples: Concrete demonstrations with expected inputs/outputs

**Skill Categories for Personal AI Employee**:
- Email triage and response drafting
- WhatsApp message analysis and reply generation
- Invoice generation and financial tracking
- Social media post creation and scheduling
- CEO briefing generation
- Subscription audit and cost optimization
- Task prioritization and planning

**Rationale**: Agent Skills transform ad-hoc prompts into durable, testable assets. They provide structured knowledge that Claude automatically applies when relevant to tasks.

### IV. Model Context Protocol (MCP) Server Architecture

MCP servers are the "hands" of the AI Employee, enabling interaction with external systems. Each MCP server MUST follow standardized patterns.

**Core MCP Server Components**:
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server(
  {
    name: "server-name",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},      // For executable actions
      resources: {},  // For data access
      prompts: {},    // For dynamic prompt generation
    },
  }
);
```

**MCP Server Types**:

1. **Tool Servers** (Actions):
   - Email MCP: Send, draft, search emails
   - Browser MCP: Navigate, click, fill forms for payments
   - Social MCP: Post to LinkedIn, Facebook, Instagram, Twitter
   - Calendar MCP: Create, update events

2. **Resource Servers** (Data Access):
   - Filesystem MCP: Read/write vault files
   - Database MCP: Query Odoo accounting system
   - Banking MCP: Fetch transactions, balances

3. **Prompt Servers** (Dynamic Prompts):
   - CEO Briefing templates
   - Email response templates
   - Invoice generation templates

**MCP Server Requirements**:
- MUST implement request handlers for ListTools/Resources/Prompts
- MUST implement CallTool/ReadResource/GetPrompt handlers
- MUST validate inputs with JSON schemas
- MUST support dry-run mode (environment variable `DRY_RUN=true`)
- MUST return structured errors with meaningful messages
- MUST log all actions to audit trail
- MUST handle rate limiting and backoff

**Configuration** (`~/.config/claude-code/mcp.json`):
```json
{
  "mcpServers": {
    "email": {
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json",
        "DRY_RUN": "false"
      }
    },
    "browser": {
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  }
}
```

**Rationale**: Standardized MCP architecture ensures consistent, testable, and maintainable external integrations.

### V. Watcher Pattern for Perception Layer

Watchers are lightweight Python scripts that monitor external sources and create actionable files for Claude to process.

**Base Watcher Pattern**:
```python
from pathlib import Path
from abc import ABC, abstractmethod
import time
import logging

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                self.logger.error(f'Error: {e}')
            time.sleep(self.check_interval)
```

**Required Watchers**:
- **Gmail Watcher**: Monitor unread important emails (Gmail API)
- **WhatsApp Watcher**: Monitor urgent messages with keywords (Playwright)
- **File System Watcher**: Monitor drop folder for new files (watchdog)
- **Finance Watcher**: Download bank transactions (Banking API or CSV)

**Watcher Requirements**:
- MUST inherit from BaseWatcher
- MUST implement check_for_updates() and create_action_file()
- MUST handle exceptions gracefully (log and continue)
- MUST track processed items to avoid duplicates
- MUST create .md files with YAML frontmatter:
  ```markdown
  ---
  type: email|whatsapp|file_drop|transaction
  from: sender/source
  subject: subject line
  received: ISO 8601 timestamp
  priority: high|medium|low
  status: pending
  ---

  ## Content
  [Message or file content]

  ## Suggested Actions
  - [ ] Action 1
  - [ ] Action 2
  ```
- MUST use process managers (PM2, supervisord) for production deployment

**Rationale**: Watchers provide the sensory system for the AI Employee, enabling proactive responses to external events.

### VI. Ralph Wiggum Loop for Autonomous Execution

The Ralph Wiggum pattern enables Claude to work autonomously on multi-step tasks until completion.

**How It Works**:
1. Orchestrator creates state file with prompt
2. Claude works on task
3. Claude attempts to exit
4. Stop hook checks: Is task file in `/Done/`?
5. If NO: Block exit, re-inject prompt with previous output visible, loop continues
6. If YES: Allow exit (task complete)
7. Repeat until complete or max iterations reached

**Completion Strategies**:
1. **Promise-based**: Claude outputs `<promise>TASK_COMPLETE</promise>`
2. **File movement** (recommended): Stop hook detects task file moved to `/Done/`

**Usage**:
```bash
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

**Requirements**:
- MUST set max iterations to prevent infinite loops
- MUST log each iteration for debugging
- MUST allow manual interruption
- MUST preserve state between iterations

**Rationale**: Autonomous multi-step execution transforms Claude from reactive assistant to proactive employee.

### VII. Comprehensive Audit Logging

Every action taken by the AI Employee MUST be logged for accountability and debugging.

**Log Format** (`/Vault/Logs/YYYY-MM-DD.json`):
```json
{
  "timestamp": "2026-03-07T10:30:00Z",
  "action_type": "email_send|payment|social_post|file_operation",
  "actor": "claude_code|human",
  "target": "recipient@example.com",
  "parameters": {
    "subject": "Invoice #123",
    "amount": 500.00
  },
  "approval_status": "approved|rejected|auto_approved",
  "approved_by": "human|system",
  "result": "success|failure",
  "error": "error message if failed",
  "duration_ms": 1234
}
```

**Requirements**:
- MUST log all actions (successful and failed)
- MUST include timestamps in ISO 8601 format
- MUST capture approval chain for sensitive actions
- MUST retain logs for minimum 90 days
- MUST implement log rotation to prevent disk exhaustion
- MUST support log querying for audits

**Rationale**: Complete action history enables post-incident analysis, compliance verification, and debugging.

### VIII. Security-First Design

Security is mandatory, not optional. The AI Employee has access to sensitive systems and data.

**Credential Management**:
- MUST use environment variables or OS-native secure storage
- MUST never store credentials in plaintext
- MUST never commit secrets to version control (.env in .gitignore)
- MUST rotate credentials monthly and after suspected breaches
- MUST separate development/production credentials
- MUST never log credentials or tokens

**Sandboxing & Isolation**:
- MUST support `DRY_RUN=true` environment variable for all action scripts
- MUST use test/sandbox accounts during development
- MUST implement rate limiting (max actions per hour)
- MUST validate all inputs before external API calls

**Permission Boundaries**:

| Action Category | Auto-Approve Threshold | Always Require Approval |
|-----------------|------------------------|-------------------------|
| Email replies | Known contacts only | New contacts, bulk sends |
| Payments | <$50 recurring bills | All new payees, >$100 |
| Social media | Scheduled posts (draft) | Replies, DMs, live posts |
| File operations | Create, read within vault | Delete, move outside vault |

**Skill Security**:
- MUST use Agent Skills only from trusted sources (self-created or Anthropic official)
- MUST audit all bundled files in Skills from external sources
- MUST review Skills for suspicious network calls, file access, or unexpected operations
- MUST treat Skill installation with same caution as software installation

**Rationale**: An autonomous system with access to email, banking, and communications is a high-value attack target. Defense in depth is essential.

## Architecture Standards

### Orchestrator Requirements

The Orchestrator is the master process coordinating all components.

**Responsibilities**:
- Monitor folder changes (`/Needs_Action/`, `/Approved/`)
- Trigger Claude Code with appropriate prompts
- Enforce rate limits and permission boundaries
- Maintain state files for Ralph Wiggum loops
- Log all orchestration decisions
- Handle scheduled tasks (cron/Task Scheduler)

**Implementation Pattern**:
```python
class Orchestrator:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.rate_limiter = RateLimiter(max_per_hour=100)
        self.state_manager = StateManager()

    def monitor_needs_action(self):
        """Watch for new files in Needs_Action"""
        pass

    def monitor_approved(self):
        """Watch for approved actions"""
        pass

    def trigger_claude(self, prompt: str, state_file: Path):
        """Execute Claude Code with Ralph Wiggum loop"""
        pass

    def enforce_permissions(self, action: dict) -> bool:
        """Check if action requires approval"""
        pass
```

### Error Recovery and Graceful Degradation

The system MUST continue operating when components fail.

**Error Categories and Recovery**:

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| Transient | Network timeout, API rate limit | Exponential backoff retry (max 3 attempts) |
| Authentication | Expired token, revoked access | Alert human, pause operations |
| Logic | Claude misinterprets message | Human review queue |
| Data | Corrupted file, missing field | Quarantine + alert |
| System | Orchestrator crash, disk full | Watchdog + auto-restart |

**Retry Logic**:
```python
def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as e:
                    if attempt == max_attempts - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(f'Attempt {attempt+1} failed, retrying in {delay}s')
                    time.sleep(delay)
        return wrapper
    return decorator
```

**Graceful Degradation**:
- Gmail API down: Queue outgoing emails locally, process when restored
- Banking API timeout: Never retry payments automatically, always require fresh approval
- Claude Code unavailable: Watchers continue collecting, queue grows for later processing
- Obsidian vault locked: Write to temporary folder, sync when available

**Watchdog Process**:
```python
PROCESSES = {
    'orchestrator': 'python orchestrator.py',
    'gmail_watcher': 'python gmail_watcher.py',
    'whatsapp_watcher': 'python whatsapp_watcher.py',
    'file_watcher': 'python filesystem_watcher.py'
}

def check_and_restart():
    for name, cmd in PROCESSES.items():
        pid_file = Path(f'/tmp/{name}.pid')
        if not is_process_running(pid_file):
            logger.warning(f'{name} not running, restarting...')
            proc = subprocess.Popen(cmd.split())
            pid_file.write_text(str(proc.pid))
            notify_human(f'{name} was restarted')
```

### Test-Driven Development (TDD)

For all custom code (Watchers, MCP servers, Orchestrator):

**Requirements**:
- Tests MUST be written before implementation
- Tests MUST be approved by user before implementation begins
- Red-Green-Refactor cycle MUST be followed
- Integration tests MUST cover cross-component interactions
- Test coverage MUST be >80% for critical paths

**Test Categories**:
1. **Unit Tests**: Individual Watcher methods, MCP server handlers
2. **Integration Tests**: Watcher → Vault → Claude → MCP → External API
3. **End-to-End Tests**: Complete flows (email arrives → draft reply → approval → send)
4. **Security Tests**: Credential handling, permission boundaries, rate limiting

**Rationale**: Autonomous systems require high reliability. TDD catches bugs before production and serves as living documentation.

## Development Workflow

### Bronze Tier (8-12 hours) - Minimum Viable

**Deliverables**:
- Obsidian vault with Dashboard.md and Company_Handbook.md
- One working Watcher (Gmail OR file system)
- Claude Code reading/writing to vault
- Basic folder structure: `/Inbox/`, `/Needs_Action/`, `/Done/`
- At least one Agent Skill

### Silver Tier (20-30 hours) - Functional Assistant

**Deliverables**:
- All Bronze requirements
- Two+ Watchers (Gmail + WhatsApp + LinkedIn)
- Auto-post on LinkedIn for sales
- Claude creates Plan.md files
- One MCP server (email sending)
- Human-in-the-loop approval workflow
- Basic scheduling (cron/Task Scheduler)
- Multiple Agent Skills

### Gold Tier (40+ hours) - Autonomous Employee

**Deliverables**:
- All Silver requirements
- Full cross-domain integration (Personal + Business)
- Odoo Community accounting system with MCP integration
- Facebook/Instagram/Twitter integration
- Multiple MCP servers
- Weekly CEO Briefing generation
- Error recovery and audit logging
- Ralph Wiggum loop for multi-step tasks
- Comprehensive Agent Skills library

### Platinum Tier (60+ hours) - Production System

**Deliverables**:
- All Gold requirements
- Cloud deployment (24/7 operation on Oracle/AWS VM)
- Cloud/Local work-zone specialization
- Vault sync via Git/Syncthing
- Odoo on cloud VM with HTTPS
- Advanced security and monitoring
- Watchdog process for health monitoring

## Governance

This constitution supersedes all other development practices and guidelines. All code, designs, and decisions MUST comply with these principles.

### Amendment Process

1. Propose amendment with rationale and impact analysis
2. Update constitution with version bump (semantic versioning)
3. Update dependent templates and documentation
4. Create migration plan for existing implementations
5. Document in Sync Impact Report (HTML comment at top of file)

### Version Semantics

- **MAJOR**: Backward-incompatible principle changes or removals
- **MINOR**: New principles or materially expanded guidance
- **PATCH**: Clarifications, wording improvements, typo fixes

### Compliance Verification

- All PRs MUST verify compliance with constitution principles
- Weekly reviews MUST audit AI decisions against HITL requirements
- Monthly security audits MUST verify credential handling
- Quarterly comprehensive reviews MUST assess system health

### Complexity Justification

Any deviation from simplicity (YAGNI) MUST be explicitly justified with:
- Business requirement driving complexity
- Alternatives considered and rejected
- Maintenance cost assessment
- Rollback plan if complexity proves unnecessary

### Ethics and Responsible Automation

**When AI Should NOT Act Autonomously**:
- Emotional contexts: Condolence messages, conflict resolution, sensitive negotiations
- Legal matters: Contract signing, legal advice, regulatory filings
- Medical decisions: Health-related actions affecting you or others
- Financial edge cases: Unusual transactions, new recipients, large amounts
- Irreversible actions: Anything that cannot be easily undone

**Transparency Principles**:
- Disclose AI involvement in communications (email signature)
- Maintain complete audit trails
- Allow contacts to opt-out of AI communication
- Schedule weekly reviews of AI decisions

**Human Accountability**:
The user remains responsible for all AI Employee actions. The automation runs on their behalf, using their credentials, acting in their name. Regular oversight is essential:
- Daily: 2-minute dashboard check
- Weekly: 15-minute action log review
- Monthly: 1-hour comprehensive audit
- Quarterly: Full security and access review

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
