---
name: task-planner
description: Create structured Plan.md files with execution steps, checkboxes, and progress tracking for multi-step tasks
version: 1.0.0
---

# SKILL: Task Planner

## 🎯 PRIMARY MISSION

> "Analyze complex tasks and create structured Plan.md files in /Plans/ folder with clear objectives, ordered execution steps, checkboxes for tracking, and reasoning documentation."

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `task-planner` skill when:**
- Task requires 3+ steps to complete
- User says: "create a plan for TASK_ID"
- Task involves multiple actions (email campaign, multi-step research, complex response)
- Need to document reasoning for audit trail
- Task has dependencies between steps

**DO NOT use:**
- For simple single-step tasks (execute directly instead)
- `inbox-processor` (that's for priority assessment, not planning)
- `approval-workflow` (that's for approval routing, use after planning if needed)

---

## 📋 PLAN.MD FILE STRUCTURE

```markdown
---
task_id: EMAIL_20260315T103000Z_client-inquiry
objective: Clear, measurable goal
completion_status: in_progress|completed|failed
created_at: 2026-03-15T10:35:00Z
updated_at: 2026-03-15T10:40:00Z
---

# Plan: [Brief Title]

## Objective

[Restate the goal in 1-2 sentences]

## Context

[Background information, constraints, key details from original task]

## Proposed Actions

1. [High-level action 1]
2. [High-level action 2]
3. [High-level action 3]

## Execution Steps

### Step 1: [Step Name]
- [ ] **Status**: pending|in_progress|completed|failed
- **Started**: [ISO timestamp]
- **Completed**: [ISO timestamp]
- **Notes**: [Findings, decisions, blockers]

### Step 2: [Step Name]
- [ ] **Status**: pending|in_progress|completed|failed
- **Started**: [ISO timestamp]
- **Completed**: [ISO timestamp]
- **Notes**: [Findings, decisions, blockers]

### Step 3: [Step Name]
- [ ] **Status**: pending|in_progress|completed|failed
- **Started**: [ISO timestamp]
- **Completed**: [ISO timestamp]
- **Notes**: [Findings, decisions, blockers]

## Reasoning Notes

[Why these steps were chosen, decision rationale, trade-offs considered]

## Alternative Approaches

- **[Alternative 1]**: Why rejected
- **[Alternative 2]**: Why rejected

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | Low/Med/High | Low/Med/High | [How to mitigate] |
```

---

## 🔄 PLANNING WORKFLOW

### Step 1: Analyze the Task

```python
# Read original task file
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
task_file = vault_path / "Needs_Action" / "TASK_ID.md"
content = task_file.read_text()

# Extract key information
frontmatter = yaml.safe_load(content.split('---')[1])
task_type = frontmatter.get('type')
subject = frontmatter.get('subject')
```

### Step 2: Identify Objective

**Good objectives are SMART:**
- **S**pecific - Clear and unambiguous
- **M**easurable - Can verify completion
- **A**chievable - Realistic given constraints
- **R**elevant - Aligned with user goals
- **T**ime-bound - Has deadline or timeframe

**Examples:**

| Task | Good Objective | Bad Objective |
|------|----------------|---------------|
| Client inquiry email | "Respond to client with timeline and pricing within 24 hours" | "Handle email" |
| LinkedIn post | "Create and publish business milestone post by Monday 9 AM" | "Post something" |
| File processing | "Extract key data from invoice and log to spreadsheet" | "Process file" |

### Step 3: Break Down into Actions

**High-level actions (3-5 max):**

```markdown
## Proposed Actions

1. Research client background and industry
2. Draft project timeline with milestones
3. Prepare pricing breakdown
4. Compose professional email response
5. Request approval and send
```

### Step 4: Create Execution Steps

**Each step should be:**
- **Atomic**: One discrete action
- **Actionable**: Clear what to do
- **Testable**: Can verify completion
- **Time-boxed**: Estimated duration

**Example:**

```markdown
### Step 1: Research Client Company
- [ ] **Status**: completed
- **Started**: 2026-03-15T14:35:00Z
- **Completed**: 2026-03-15T14:40:00Z
- **Notes**: Client is in healthcare tech, 50-person startup, raised Series A. HIPAA compliance will be important.
```

### Step 5: Document Reasoning

**Capture:**
- Why this approach was chosen
- What alternatives were considered
- Key decisions and trade-offs
- Assumptions made

```markdown
## Reasoning Notes

Client's healthcare background requires emphasis on HIPAA compliance and data security. 
Pricing positioned at mid-range ($75k) to balance value and competitiveness. 
Timeline structured in tiers to allow early wins and iterative feedback.
```

---

## ✅ STEP STATUS TRACKING

Update step status as execution progresses:

| Status | When to Use |
|--------|-------------|
| `pending` | Step not yet started |
| `in_progress` | Currently working on this step |
| `completed` | Step finished successfully |
| `failed` | Step encountered error, cannot proceed |

**Update Plan.md during execution:**

```python
# Read plan
plan_file = vault_path / "Plans" / f"PLAN_{task_id}.md"
content = plan_file.read_text()

# Update step status
content = content.replace(
    "- [ ] **Status**: pending",
    "- [x] **Status**: completed\n- **Completed**: 2026-03-15T14:40:00Z"
)

# Write updated plan
plan_file.write_text(content)
```

---

## 📊 EXAMPLE PLAN.MD

```markdown
---
task_id: EMAIL_20260315T143000Z_client-inquiry
objective: Respond to client inquiry about AI automation project with timeline and pricing
completion_status: completed
created_at: 2026-03-15T14:35:00Z
updated_at: 2026-03-15T15:05:00Z
---

# Plan: Client Inquiry Response

## Objective

Respond to [Client Name]'s inquiry about AI automation project with detailed timeline (3 months) and pricing breakdown ($75k total).

## Context

Client reached out via email interested in Bronze → Silver → Gold tier implementation. Budget mentioned: $50k-$100k. Timeline: 3 months. Client is in healthcare technology sector.

## Proposed Actions

1. Research client's company and industry requirements
2. Draft project timeline with phase milestones
3. Prepare detailed pricing breakdown
4. Compose professional email response
5. Request approval for sending (client communication threshold)

## Execution Steps

### Step 1: Research Client Company
- [x] **Status**: completed
- **Started**: 2026-03-15T14:35:00Z
- **Completed**: 2026-03-15T14:40:00Z
- **Notes**: Client is in healthcare tech, 50-person startup, raised Series A. HIPAA compliance critical. Competitors include [X], [Y].

### Step 2: Draft Project Timeline
- [x] **Status**: completed
- **Started**: 2026-03-15T14:40:00Z
- **Completed**: 2026-03-15T14:50:00Z
- **Notes**: 
  - Month 1: Bronze tier (foundation, watchers, basic automation)
  - Month 2: Silver tier (dual watchers, email sending, LinkedIn)
  - Month 3: Gold tier (advanced automation, Odoo integration)

### Step 3: Prepare Pricing Breakdown
- [x] **Status**: completed
- **Started**: 2026-03-15T14:50:00Z
- **Completed**: 2026-03-15T14:55:00Z
- **Notes**: 
  - Bronze: $25k
  - Silver: $25k
  - Gold: $25k
  - Total: $75k (within their $50k-$100k budget)

### Step 4: Compose Email Response
- [x] **Status**: completed
- **Started**: 2026-03-15T14:55:00Z
- **Completed**: 2026-03-15T15:00:00Z
- **Notes**: Draft created in task file. Tone: professional but friendly. Emphasized HIPAA compliance expertise.

### Step 5: Request Approval
- [x] **Status**: completed
- **Started**: 2026-03-15T15:00:00Z
- **Completed**: 2026-03-15T15:05:00Z
- **Notes**: Task moved to /Pending_Approval/ (client communication threshold exceeded)

## Reasoning Notes

Client's healthcare background requires emphasis on HIPAA compliance and data security. Pricing positioned at mid-range ($75k) to balance value and competitiveness. Timeline structured in tiers to allow early wins and iterative feedback.

## Alternative Approaches

- **Single-phase delivery**: Rejected - too risky, no early feedback opportunities
- **Lower pricing ($50k)**: Rejected - undervalues expertise, sets wrong expectations for scope
- **Longer timeline (6 months)**: Rejected - client needs faster results, competitive pressure

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | Medium | High | Fixed scope per tier, change requests require approval |
| HIPAA compliance gaps | Low | High | Third-party security audit before launch |
| Timeline delays | Medium | Medium | Buffer weeks built into each phase |
```

---

## 🎯 QUALITY CHECKLIST

Before finalizing a Plan.md:

- [ ] Objective is SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- [ ] Context provides sufficient background
- [ ] Proposed actions are high-level (3-5 max)
- [ ] Execution steps are atomic and actionable
- [ ] Each step has status checkbox
- [ ] Timestamps are ISO 8601 format
- [ ] Reasoning notes explain decision rationale
- [ ] Alternative approaches documented
- [ ] Risks identified with mitigations
- [ ] Plan.md saved to `/Plans/` folder
- [ ] File naming: `PLAN_{TASK_ID}.md`

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Assesses priority, triggers planning for complex tasks
- `vault-manager` - File operations for reading/writing Plan.md
- `approval-workflow` - Routes plans requiring approval
- `email-handler` - Executes email-related steps in plan
- `social-poster` - Executes LinkedIn-related steps in plan

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Structured Plan.md Creation*
