# ADR-0002: State Persistence Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-03-09
- **Feature:** 002-silver-tier
- **Context:** Silver tier introduces multiple concurrent watchers (Gmail, File System, LinkedIn) that must prevent duplicate task creation across system restarts. Bronze tier had no state persistence, causing duplicate tasks every time watchers restarted. The system needs a reliable, local-first solution that handles concurrent access from multiple watcher processes and provides ACID transaction guarantees to prevent race conditions.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? YES - Affects data integrity, system reliability, and user trust
     2) Alternatives: Multiple viable options considered with tradeoffs? YES - SQLite vs PostgreSQL vs JSON files vs Redis vs in-memory
     3) Scope: Cross-cutting concern (not an isolated detail)? YES - All watchers depend on state persistence, affects restart behavior and duplicate prevention
-->

## Decision

Use **SQLite embedded database** for persistent state management with file-based coordination.

**Technology Stack**:
- **Database**: SQLite3 (built-in to Python 3.13+, no external dependencies)
- **Location**: `state.db` in project root
- **Schema**: Single `processed_items` table with unique constraint on (source, source_id)
- **Access Pattern**: StateManager class in `watchers/state_manager.py` provides ACID transaction guarantees
- **Backup Strategy**: Daily SQLite `.backup` command via cron
- **Recovery Strategy**: Rebuild from vault files if database corrupted (scans /Needs_Action, /Done, /Rejected)

**Schema Design**:
```sql
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
```

## Consequences

### Positive

- **Zero Configuration**: Built-in to Python 3.13+, no installation or server setup required
- **Local-First**: No network calls, aligns with constitution principle
- **ACID Transactions**: Prevents race conditions when multiple watchers check/insert simultaneously
- **Lightweight**: <100MB disk footprint for 1000+ processed items, <10MB memory usage
- **Simple Schema**: Single table with 7 columns, easy to understand and maintain
- **Fast Queries**: Index on (source, source_id) provides O(1) duplicate detection
- **Backup/Recovery**: Simple `.backup` command for daily backups, rebuild from vault files if corrupted
- **Cross-Platform**: Works identically on Linux, macOS, Windows
- **No External Dependencies**: No separate database server to manage or monitor

### Negative

- **Single-Writer Limitation**: SQLite locks entire database during writes (acceptable for low-volume single-user scenario)
- **No Network Access**: Cannot be queried remotely (not a concern for local-first architecture)
- **Corruption Risk**: File-based database can corrupt on system crash (mitigated by daily backups and vault rebuild)
- **Limited Concurrency**: Multiple processes can read, but writes are serialized (acceptable for 3 watchers with 2-5 minute polling intervals)
- **No Built-in Replication**: Cannot replicate to other machines (not needed for Silver tier, may be issue for Platinum tier cloud deployment)
- **Manual Migration**: Schema changes require manual ALTER TABLE statements (acceptable for infrequent schema evolution)

## Alternatives Considered

### Alternative 1: PostgreSQL
- **Description**: Full-featured relational database with separate server process
- **Pros**: Better concurrency, network access, replication support, advanced features
- **Cons**: Requires separate server process, overkill for single-user scenario, violates simplicity principle, adds deployment complexity
- **Why Rejected**: Massive overkill for single-user operation with 3 watchers. SQLite's limitations (single-writer, no network access) are not constraints for Silver tier use case. PostgreSQL would add unnecessary complexity without delivering value.

### Alternative 2: JSON Files
- **Description**: Store processed items as JSON files in project directory
- **Pros**: Human-readable, no database dependency, simple to implement
- **Cons**: No transaction support (race conditions with concurrent watchers), no query optimization (O(n) duplicate detection), file locking issues on Windows, corruption risk on concurrent writes
- **Why Rejected**: Cannot provide ACID transaction guarantees needed for concurrent watcher access. Race conditions would cause duplicate task creation, violating FR-016 and FR-018.

### Alternative 3: In-Memory Only
- **Description**: Store processed items in Python dict/set, no disk persistence
- **Pros**: Fastest access (no I/O), simplest implementation, no corruption risk
- **Cons**: Loses all state on restart (violates FR-016), cannot prevent duplicates after restart, no audit trail
- **Why Rejected**: Completely fails to meet the core requirement of persistent state across restarts. Would cause duplicate tasks every time watchers restart, undermining user trust.

### Alternative 4: Redis
- **Description**: In-memory data store with optional persistence
- **Pros**: Fast access, good concurrency, pub/sub for watcher coordination
- **Cons**: Requires separate Redis server process, adds deployment complexity, overkill for single-user scenario, violates local-first principle (network dependency)
- **Why Rejected**: Requires separate server process and adds unnecessary complexity. Redis's strengths (high concurrency, pub/sub, distributed access) are not needed for single-user operation with 3 watchers.

## References

- Feature Spec: [specs/002-silver-tier/spec.md](../../specs/002-silver-tier/spec.md) (FR-016 to FR-019: Persistent State Management)
- Implementation Plan: [specs/002-silver-tier/plan.md](../../specs/002-silver-tier/plan.md)
- Research Document: [specs/002-silver-tier/research.md](../../specs/002-silver-tier/research.md) (Section 2: Persistent State Management)
- Data Model: [specs/002-silver-tier/data-model.md](../../specs/002-silver-tier/data-model.md) (Processed Item entity with SQLite schema)
- State Schema: [specs/002-silver-tier/contracts/watcher-state-schema.json](../../specs/002-silver-tier/contracts/watcher-state-schema.json)
- Related ADRs: ADR-0001 (MCP Server Framework Selection)
- Evaluator Evidence: [history/prompts/002-silver-tier/0002-silver-tier-architectural-design.plan.prompt.md](../prompts/002-silver-tier/0002-silver-tier-architectural-design.plan.prompt.md) (Planning phase with state persistence design)
