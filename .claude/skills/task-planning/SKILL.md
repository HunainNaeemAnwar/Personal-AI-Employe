---
description: Create structured Plan.md files for multi-step tasks with complete reasoning documentation
---

# SKILL: Task Planning

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `task-planning` skill when:**
- Task requires 3+ steps to complete
- Task involves multiple systems (email + LinkedIn + files)
- Task has dependencies or prerequisites
- User says: "plan this task", "create execution plan"
- **IMPORTANT:** After creating plan, ADD to Plan.md: "Use `<skill-name>` skill for execution"

**DO NOT use:** for simple single-step tasks (use email-triage directly)

## Skill Selection Matrix

| Task Complexity | Steps Required | Skill to Use |
|----------------|----------------|--------------|
| Simple (reply email) | 1-2 steps | `email-triage` |
| Medium (process file) | 2-3 steps | `email-triage` |
| Complex (multi-system) | 3+ steps | `task-planning` THEN specified skill |

## Plan.md Template - REQUIRED Format

**ALWAYS include in Plan.md:**

```markdown
## ⚠️ Required Skill for Execution

**Use this skill:** `<skill-name>`

Choose from:
- `email-triage` - For processing emails, LinkedIn messages, file drops
- `linkedin-posting` - For creating LinkedIn business posts
- `approval-workflow` - For approval/rejection decisions
- `inbox-triage` - For moving Inbox → Needs_Action
```

**How to determine which skill:**
1. Read the task file type
2. Check task location
3. Use Skill Selection Matrix above
4. **WRITE THE SKILL NAME in Plan.md**

**Example Plan.md Header:**
```markdown
---
task_id: LINKEDIN_MSG_hunain-naeem-anwar
created_at: 2026-03-13T01:00:00Z
status: pending
---

# Task Plan: Respond to LinkedIn Message

## ⚠️ Required Skill for Execution

**Use this skill:** `email-triage`

---

## Task Analysis
...
```

---

## When to Use This Skill

Use this skill when:
- Processing tasks from /Needs_Action that require multiple steps
- A task cannot be completed in a single action
- The task requires coordination across multiple systems or files
- The task involves complex decision-making or trade-offs
- You need to document reasoning for future reference
- The task has dependencies or prerequisites

## Persona

You are a strategic planner who excels at breaking down complex tasks into executable steps. You understand:
- How to identify the core objective and constraints of a task
- How to propose high-level actions in logical order
- How to break actions into concrete, executable steps
- How to track progress and document decisions
- How to capture reasoning and alternative approaches
- The importance of clear documentation for future reference

## Task Planning Workflow

### Step 1: Task Analysis

When you receive a task from /Needs_Action, analyze it to extract:

1. **Objective**: What is the end goal? What does success look like?
2. **Context**: What information is available? What systems are involved?
3. **Constraints**: What are the limitations? (time, resources, dependencies)
4. **Prerequisites**: What must be true before starting?
5. **Success Criteria**: How will you know the task is complete?

**Example Analysis:**

```markdown
## Task Analysis

**Objective**: Reply to client email about project timeline

**Context**:
- Client: John Doe (john@example.com)
- Project: Website redesign
- Current status: In development phase
- Client asking for updated timeline

**Constraints**:
- Must respond within 24 hours
- Need to check project management system for accurate dates
- Requires approval before sending (client communication threshold)

**Prerequisites**:
- Access to project management system
- Current project status information
- Client communication history

**Success Criteria**:
- Email drafted with accurate timeline
- Email approved by user
- Email sent successfully
- Response logged in vault
```

### Step 2: Action Proposal

Generate an ordered list of high-level actions needed to complete the task:

1. **Identify major phases**: What are the main stages of work?
2. **Order logically**: What must happen first? What can happen in parallel?
3. **Keep high-level**: Actions should be conceptual, not detailed steps
4. **Consider dependencies**: Note which actions depend on others

**Example Action Proposal:**

```markdown
## Proposed Actions

1. **Gather Information**
   - Retrieve current project status from project management system
   - Review client communication history
   - Identify key milestones and dates

2. **Draft Response**
   - Compose email with timeline update
   - Include next steps and deliverables
   - Add professional tone and reassurance

3. **Seek Approval**
   - Move task to /Pending_Approval
   - Wait for user approval command
   - Handle approval or rejection

4. **Send Email**
   - Use email MCP server to send response
   - Log sent email to /Logs/email_sent.log
   - Move task to /Done

**Dependencies**:
- Action 2 depends on Action 1 (need information before drafting)
- Action 3 depends on Action 2 (need draft before approval)
- Action 4 depends on Action 3 (need approval before sending)
```

### Step 3: Execution Step Breakdown

Break each action into concrete, executable steps:

1. **Be specific**: Each step should be a single, clear operation
2. **Include commands**: Specify exact commands or tool calls where applicable
3. **Add validation**: Include checks to verify each step succeeded
4. **Estimate effort**: Note if a step is quick (<1min) or slow (>5min)

**Example Execution Steps:**

```markdown
## Execution Steps

### Action 1: Gather Information

**Step 1.1**: Read project management data
- **Command**: `read_file("projects/website_redesign/status.md")`
- **Validation**: File exists and contains current milestone dates
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 1.2**: Review client communication history
- **Command**: `grep -r "john@example.com" AI_Employee_Vault/Done/`
- **Validation**: Found previous email threads
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 1.3**: Extract key dates and milestones
- **Command**: Parse status.md for dates, create timeline summary
- **Validation**: Timeline includes all major milestones
- **Effort**: Quick (<1min)
- **Status**: pending

### Action 2: Draft Response

**Step 2.1**: Create email template
- **Command**: Use email template from vault_setup/templates/
- **Validation**: Template includes all required sections
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 2.2**: Fill in timeline details
- **Command**: Insert milestone dates and descriptions
- **Validation**: All dates are accurate and formatted correctly
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 2.3**: Add professional tone and reassurance
- **Command**: Review and refine language
- **Validation**: Tone is professional, reassuring, and clear
- **Effort**: Quick (<1min)
- **Status**: pending

### Action 3: Seek Approval

**Step 3.1**: Move task to /Pending_Approval
- **Command**: `mv AI_Employee_Vault/Needs_Action/EMAIL_*.md AI_Employee_Vault/Pending_Approval/`
- **Validation**: File moved successfully
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 3.2**: Update task metadata with approval request
- **Command**: Add approval_required: true to YAML frontmatter
- **Validation**: Metadata updated correctly
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 3.3**: Wait for approval command
- **Command**: Monitor for `claude "approve task TASK_ID"` or `claude "reject task TASK_ID"`
- **Validation**: Approval or rejection received
- **Effort**: Variable (depends on user response time)
- **Status**: pending

### Action 4: Send Email

**Step 4.1**: Call email MCP server
- **Command**: `send_email(to="john@example.com", subject="...", body="...", thread_id="...")`
- **Validation**: Email sent successfully (200 response)
- **Effort**: Quick (<5s)
- **Status**: pending

**Step 4.2**: Log sent email
- **Command**: Append to /Logs/email_sent.log with timestamp and details
- **Validation**: Log entry created
- **Effort**: Quick (<1min)
- **Status**: pending

**Step 4.3**: Move task to /Done
- **Command**: `mv AI_Employee_Vault/Pending_Approval/EMAIL_*.md AI_Employee_Vault/Done/`
- **Validation**: File moved successfully
- **Effort**: Quick (<1min)
- **Status**: pending
```

### Step 4: Create Plan.md File

Write the complete plan to `/Plans/PLAN_[TASK_ID].md`:

**File Structure:**

```markdown
---
task_id: EMAIL_20260309T143000Z_client-timeline
created_at: 2026-03-09T14:30:00Z
status: in_progress
total_steps: 12
completed_steps: 0
failed_steps: 0
---

# Task Plan: Reply to Client Email About Project Timeline

## Task Analysis

[Insert analysis from Step 1]

## Proposed Actions

[Insert actions from Step 2]

## Execution Steps

[Insert steps from Step 3]

## Progress Tracking

**Overall Status**: in_progress
**Started At**: 2026-03-09T14:30:00Z
**Completed At**: null
**Total Steps**: 12
**Completed Steps**: 0
**Failed Steps**: 0

## Reasoning Notes

### Decision: Use Email MCP Server Instead of Manual Gmail
**Rationale**: Email MCP server provides retry logic, threading support, and automatic logging. Manual Gmail would require more error handling and logging code.

**Trade-offs**:
- Pro: Automated retry on failure (3 attempts with exponential backoff)
- Pro: Automatic threading (In-Reply-To and References headers)
- Pro: Centralized logging to /Logs/email_sent.log
- Con: Requires MCP server to be running and configured
- Con: Additional dependency (Node.js, Gmail API credentials)

**Decision**: Proceed with MCP server (benefits outweigh costs)

### Decision: Seek Approval Before Sending
**Rationale**: Client communication exceeds approval threshold (new/sensitive communication). Company_Handbook.md requires approval for client communications.

**Trade-offs**:
- Pro: Prevents unauthorized or inappropriate client communication
- Pro: Allows user to review and refine message before sending
- Pro: Maintains audit trail of approval decisions
- Con: Adds latency (requires user to approve)
- Con: Task cannot complete autonomously

**Decision**: Proceed with approval workflow (required by policy)

## Alternative Approaches

### Alternative 1: Send Email Without Approval
**Description**: Skip approval workflow and send email directly

**Pros**:
- Faster completion (no waiting for user)
- Fully autonomous execution

**Cons**:
- Violates approval policy for client communication
- Risk of sending inappropriate or inaccurate information
- No human oversight for sensitive communication

**Rejected Because**: Violates Company_Handbook.md approval thresholds

### Alternative 2: Use Manual Gmail Instead of MCP Server
**Description**: Compose email manually and send via Gmail web interface

**Pros**:
- No dependency on MCP server
- Simpler setup (no Node.js or Gmail API)

**Cons**:
- No automated retry logic
- No automatic threading support
- Manual logging required
- More error-prone

**Rejected Because**: MCP server provides better reliability and automation

## Execution Log

[This section is updated as steps are executed]

**2026-03-09T14:30:00Z**: Plan created
**2026-03-09T14:31:00Z**: Step 1.1 completed - Read project status
**2026-03-09T14:31:30Z**: Step 1.2 completed - Reviewed client history
**2026-03-09T14:32:00Z**: Step 1.3 completed - Extracted timeline
...
```

### Step 5: Update Step Status

As you execute each step, update its status in the Plan.md file:

**Status Values**:
- `pending`: Step not yet started
- `in_progress`: Step currently executing
- `completed`: Step finished successfully
- `failed`: Step encountered an error

**Update Process**:

1. Before starting a step, mark it as `in_progress`
2. Add `started_at` timestamp
3. Execute the step
4. If successful, mark as `completed` and add `completed_at` timestamp
5. If failed, mark as `failed` and add `error` message
6. Update overall progress counters (completed_steps, failed_steps)

**Example Status Update:**

```markdown
**Step 1.1**: Read project management data
- **Command**: `read_file("projects/website_redesign/status.md")`
- **Validation**: File exists and contains current milestone dates
- **Effort**: Quick (<1min)
- **Status**: completed
- **Started At**: 2026-03-09T14:31:00Z
- **Completed At**: 2026-03-09T14:31:15Z
```

### Step 6: Document Reasoning

Throughout execution, capture decision rationale in the Reasoning Notes section:

**What to Document**:
- Why you chose a particular approach
- Trade-offs you considered
- Assumptions you made
- Risks you identified
- Constraints that influenced your decision

**Format**:

```markdown
### Decision: [Brief Decision Title]
**Rationale**: [Why you made this decision]

**Trade-offs**:
- Pro: [Benefit 1]
- Pro: [Benefit 2]
- Con: [Drawback 1]
- Con: [Drawback 2]

**Decision**: [Final decision and justification]
```

### Step 7: Document Alternatives

For significant decisions, document alternative approaches you considered but rejected:

**What to Document**:
- Alternative approaches you evaluated
- Pros and cons of each alternative
- Why you rejected each alternative

**Format**:

```markdown
### Alternative [N]: [Brief Title]
**Description**: [What this alternative would involve]

**Pros**:
- [Benefit 1]
- [Benefit 2]

**Cons**:
- [Drawback 1]
- [Drawback 2]

**Rejected Because**: [Clear reason for rejection]
```

## Plan.md Template Structure

```markdown
---
task_id: [TASK_ID from filename]
created_at: [ISO 8601 timestamp]
status: [pending|in_progress|completed|failed]
total_steps: [Number of execution steps]
completed_steps: [Number of completed steps]
failed_steps: [Number of failed steps]
---

# Task Plan: [Task Title]

## Task Analysis

**Objective**: [End goal]

**Context**:
- [Context item 1]
- [Context item 2]

**Constraints**:
- [Constraint 1]
- [Constraint 2]

**Prerequisites**:
- [Prerequisite 1]
- [Prerequisite 2]

**Success Criteria**:
- [Criterion 1]
- [Criterion 2]

## Proposed Actions

1. **[Action 1 Title]**
   - [Action 1 description]

2. **[Action 2 Title]**
   - [Action 2 description]

**Dependencies**:
- [Dependency description]

## Execution Steps

### Action 1: [Action Title]

**Step 1.1**: [Step description]
- **Command**: [Exact command or tool call]
- **Validation**: [How to verify success]
- **Effort**: [Quick (<1min) | Slow (>5min)]
- **Status**: [pending|in_progress|completed|failed]
- **Started At**: [ISO 8601 timestamp or null]
- **Completed At**: [ISO 8601 timestamp or null]
- **Error**: [Error message if failed, or null]

[Repeat for all steps]

## Progress Tracking

**Overall Status**: [pending|in_progress|completed|failed]
**Started At**: [ISO 8601 timestamp or null]
**Completed At**: [ISO 8601 timestamp or null]
**Total Steps**: [Number]
**Completed Steps**: [Number]
**Failed Steps**: [Number]

## Reasoning Notes

### Decision: [Decision Title]
**Rationale**: [Why]

**Trade-offs**:
- Pro: [Benefit]
- Con: [Drawback]

**Decision**: [Final decision]

[Repeat for all significant decisions]

## Alternative Approaches

### Alternative 1: [Title]
**Description**: [What]

**Pros**:
- [Benefit]

**Cons**:
- [Drawback]

**Rejected Because**: [Reason]

[Repeat for all alternatives]

## Execution Log

[Chronological log of execution events]

**[Timestamp]**: [Event description]
```

## When to Create a Plan.md

Create a Plan.md file when:

1. **Task complexity**: Task requires more than 3 steps
2. **Multiple systems**: Task involves coordination across multiple systems (email, LinkedIn, file system, database)
3. **Decision points**: Task requires making choices between alternatives
4. **Approval required**: Task needs human approval (HITL workflow)
5. **Long duration**: Task will take more than 5 minutes to complete
6. **Error-prone**: Task has high risk of failure or requires retry logic
7. **Documentation needed**: Task reasoning should be preserved for future reference

## When NOT to Create a Plan.md

Skip Plan.md for:

1. **Simple tasks**: Single-step operations (e.g., "Move file to /Done")
2. **Routine operations**: Well-established patterns with no decisions (e.g., "Mark email as processed")
3. **Quick actions**: Tasks that complete in under 1 minute
4. **No alternatives**: Tasks with only one obvious approach
5. **No reasoning needed**: Tasks that don't require explanation

## Integration with Task Execution

When executing a task with a Plan.md:

1. **Before starting**: Create Plan.md with complete analysis and proposed steps
2. **During execution**: Update step statuses and timestamps in real-time
3. **On completion**: Mark overall status as completed and add final timestamp
4. **On failure**: Mark failed steps, document errors, and propose recovery steps
5. **After completion**: Keep Plan.md in /Plans/ for future reference

## Example: Complete Plan.md

See `/Plans/PLAN_EMAIL_20260309T143000Z_client-timeline.md` for a complete example.

## Performance Metrics

Track planning effectiveness:

- **Plan accuracy**: % of steps that execute as planned
- **Plan completeness**: % of tasks that complete without adding new steps
- **Reasoning quality**: % of decisions that are well-justified
- **Alternative coverage**: % of significant decisions with documented alternatives

**Target metrics**:
- Plan accuracy: >90% (most steps execute as planned)
- Plan completeness: >85% (few tasks require additional steps)
- Reasoning quality: 100% (all decisions have clear rationale)
- Alternative coverage: >80% (most decisions document alternatives)

## Notes

- Plans are living documents - update them as execution progresses
- Reasoning notes are for future reference - be thorough
- Alternative approaches help explain why you chose your approach
- Execution logs provide audit trail for debugging
- Plans enable better collaboration between AI and human
