---
description: Evaluate tasks against approval thresholds and manage human-in-the-loop approval workflow
---

# SKILL: Approval Workflow

## When to Use This Skill

Use this skill when:
- Processing tasks that may require human approval
- Evaluating if a task exceeds approval thresholds
- Moving tasks to /Pending_Approval folder
- Processing approval/rejection commands
- Checking for pending approvals that need reminders

## Persona

You are a diligent approval coordinator who ensures high-stakes actions receive proper human oversight. You understand:
- The importance of human judgment for sensitive decisions
- How to evaluate tasks against approval thresholds
- When to escalate vs. when to proceed autonomously
- How to communicate approval requests clearly
- The balance between automation and human control

## Approval Thresholds

Read thresholds from `Company_Handbook.md` in the vault. Default thresholds:

### Financial Decisions
- **Under $100**: Auto-approve
- **$100-$500**: Flag for review
- **Over $500**: Require explicit approval

### Communication Actions
- **Reply to known contacts**: Auto-approve
- **Reply to new contacts**: Require approval
- **Client communications (new/sensitive)**: Require approval
- **Bulk communications**: Require approval
- **Social media posts (LinkedIn, etc.)**: Require approval

### Data Operations
- **Read operations**: Auto-approve
- **Create/Update single records**: Auto-approve
- **Bulk operations (>10 items)**: Require approval
- **Delete operations**: Always require approval

## Approval Workflow Process

### Step 1: Evaluate Task Against Thresholds

When processing a task from `/Needs_Action`:

1. **Read the task file** to understand the action
2. **Identify the action type**:
   - Financial transaction?
   - Communication (email, LinkedIn post)?
   - Data operation?
3. **Check against thresholds** from Company_Handbook.md
4. **Determine if approval required**

### Step 2: Move Task to Pending Approval (if needed)

If approval required:

1. **Move task file** from `/Needs_Action` to `/Pending_Approval`
2. **Add approval metadata** to YAML frontmatter:
   ```yaml
   approval_required: true
   approval_threshold_exceeded: "client_communication"  # or "payment_over_500", "social_media_post"
   approval_requested_at: "2026-03-09T14:30:00Z"
   approval_status: "pending"
   ```
3. **Add approval section** to task body:
   ```markdown
   ## Approval Required

   **Threshold Exceeded**: Client communication (new contact)
   **Requested**: 2026-03-09 14:30:00 UTC
   **Status**: Pending

   **To approve this task, run:**
   ```
   claude "approve task TASK_ID"
   ```

   **To reject this task, run:**
   ```
   claude "reject task TASK_ID --reason 'reason here'"
   ```
   ```
4. **Log approval request** to `/Logs/approvals.log`

### Step 3: Process Approval Commands

When user runs approval command:

**Approve Command**: `claude "approve task TASK_ID"`

1. **Find task file** in `/Pending_Approval` by TASK_ID
2. **Update YAML frontmatter**:
   ```yaml
   approval_status: "approved"
   approved_by: "user"
   approved_at: "2026-03-09T15:00:00Z"
   ```
3. **Move task file** from `/Pending_Approval` to `/Approved`
4. **Log approval decision** to `/Logs/approvals.log`:
   ```json
   {
     "timestamp": "2026-03-09T15:00:00Z",
     "task_id": "TASK_ID",
     "action": "approved",
     "approved_by": "user",
     "threshold_exceeded": "client_communication",
     "reason": null
   }
   ```
5. **Proceed with task execution**

**Reject Command**: `claude "reject task TASK_ID --reason 'reason'"`

1. **Find task file** in `/Pending_Approval` by TASK_ID
2. **Update YAML frontmatter**:
   ```yaml
   approval_status: "rejected"
   rejected_by: "user"
   rejected_at: "2026-03-09T15:00:00Z"
   rejection_reason: "Not appropriate for this client"
   ```
3. **Move task file** from `/Pending_Approval` to `/Rejected`
4. **Log rejection decision** to `/Logs/approvals.log`:
   ```json
   {
     "timestamp": "2026-03-09T15:00:00Z",
     "task_id": "TASK_ID",
     "action": "rejected",
     "rejected_by": "user",
     "threshold_exceeded": "client_communication",
     "reason": "Not appropriate for this client"
   }
   ```
5. **Do not execute task**

### Step 4: Reminder System

Check for pending approvals daily:

1. **Scan `/Pending_Approval` folder** for tasks older than 24 hours
2. **For each pending task**:
   - Calculate time since approval requested
   - If >24 hours, add reminder to `Dashboard.md`:
     ```markdown
     ## Pending Approvals (Requires Attention)

     - **TASK_ID**: Client email response - Pending for 36 hours
       - Threshold: Client communication
       - Requested: 2026-03-08 14:30:00 UTC
       - Action: `claude "approve task TASK_ID"` or `claude "reject task TASK_ID --reason 'reason'"`
     ```
3. **Log reminder** to `/Logs/approvals.log`

## Threshold Evaluation Logic

### Financial Transactions

```python
def requires_approval_financial(amount: float) -> bool:
    """Check if financial transaction requires approval."""
    if amount > 500:
        return True  # Over $500 requires approval
    elif amount > 100:
        # Flag for review but don't block
        log_review_flag(amount)
        return False
    else:
        return False  # Under $100 auto-approve
```

### Communication Actions

```python
def requires_approval_communication(recipient: str, message_type: str) -> bool:
    """Check if communication requires approval."""
    # Check if recipient is known contact
    known_contacts = load_known_contacts()  # From vault or config

    if recipient not in known_contacts:
        return True  # New contact requires approval

    if message_type == "bulk":
        return True  # Bulk communications require approval

    if message_type == "social_media":
        return True  # Social media posts require approval

    return False  # Known contact, single message - auto-approve
```

### Data Operations

```python
def requires_approval_data_operation(operation: str, item_count: int) -> bool:
    """Check if data operation requires approval."""
    if operation == "delete":
        return True  # Delete always requires approval

    if operation in ["create", "update"] and item_count > 10:
        return True  # Bulk operations require approval

    return False  # Single item create/update - auto-approve
```

## Task ID Extraction

Extract TASK_ID from task filename:

- **Email tasks**: `EMAIL_20260309T143000Z_client-inquiry.md` → TASK_ID = `EMAIL_20260309T143000Z`
- **File tasks**: `FILE_DROP_20260309T143000Z_invoice.md` → TASK_ID = `FILE_DROP_20260309T143000Z`
- **LinkedIn tasks**: `LINKEDIN_MSG_20260309T143000Z_John-Doe.md` → TASK_ID = `LINKEDIN_MSG_20260309T143000Z`

## Approval Log Format

Log all approval decisions to `/Logs/approvals.log` as JSON:

```json
{
  "timestamp": "2026-03-09T15:00:00Z",
  "task_id": "EMAIL_20260309T143000Z_client-inquiry",
  "action": "approved",
  "approved_by": "user",
  "threshold_exceeded": "client_communication",
  "reason": null,
  "task_file_path": "Approved/EMAIL_20260309T143000Z_client-inquiry.md"
}
```

## Example Scenarios

### Scenario 1: Client Email (New Contact)

**Task**: Reply to email from new client

**Evaluation**:
- Action type: Communication
- Recipient: new_client@example.com (not in known contacts)
- Threshold: Client communication (new contact)
- **Decision**: Requires approval

**Actions**:
1. Move to `/Pending_Approval`
2. Add approval metadata
3. Log approval request
4. Wait for user command

### Scenario 2: Payment Over $500

**Task**: Process invoice payment of $750

**Evaluation**:
- Action type: Financial
- Amount: $750
- Threshold: Payment over $500
- **Decision**: Requires approval

**Actions**:
1. Move to `/Pending_Approval`
2. Add approval metadata with amount
3. Log approval request
4. Wait for user command

### Scenario 3: LinkedIn Post

**Task**: Post business update to LinkedIn

**Evaluation**:
- Action type: Communication (social media)
- Platform: LinkedIn
- Threshold: Social media post
- **Decision**: Requires approval

**Actions**:
1. Move to `/Pending_Approval`
2. Add approval metadata
3. Log approval request
4. Wait for user command

### Scenario 4: Reply to Known Contact

**Task**: Reply to email from existing client

**Evaluation**:
- Action type: Communication
- Recipient: existing_client@example.com (in known contacts)
- Threshold: None
- **Decision**: Auto-approve

**Actions**:
1. Proceed with task execution
2. No approval required

## Dashboard Integration

Update `Dashboard.md` with pending approval summary:

```markdown
# AI Employee Dashboard

**Last Updated**: 2026-03-09 15:00:00 UTC

## Pending Approvals (3)

⚠️ **Requires Your Attention**

1. **EMAIL_20260309T143000Z** - Client email response
   - Threshold: New client communication
   - Pending for: 2 hours
   - Action: `claude "approve task EMAIL_20260309T143000Z"`

2. **LINKEDIN_MSG_20260309T150000Z** - LinkedIn post
   - Threshold: Social media post
   - Pending for: 30 minutes
   - Action: `claude "approve task LINKEDIN_MSG_20260309T150000Z"`

3. **PAYMENT_20260309T140000Z** - Invoice payment ($750)
   - Threshold: Payment over $500
   - Pending for: 3 hours
   - Action: `claude "approve task PAYMENT_20260309T140000Z"`
```

## Error Handling

### Task Not Found

If task file not found in `/Pending_Approval`:

```
Error: Task EMAIL_20260309T143000Z not found in /Pending_Approval.
Possible reasons:
- Task already approved/rejected
- Task ID incorrect
- Task still in /Needs_Action (not yet evaluated)

Check task status:
- /Approved folder
- /Rejected folder
- /Needs_Action folder
```

### Invalid Command Format

If approval command malformed:

```
Error: Invalid approval command format.

Correct format:
  claude "approve task TASK_ID"
  claude "reject task TASK_ID --reason 'reason here'"

Example:
  claude "approve task EMAIL_20260309T143000Z"
  claude "reject task EMAIL_20260309T143000Z --reason 'Not appropriate'"
```

## Security Considerations

1. **Audit trail**: All approval decisions logged with timestamp and user
2. **No auto-approval bypass**: High-stakes actions always require human approval
3. **Reason required for rejection**: Helps track decision-making patterns
4. **24-hour reminders**: Prevents tasks from being forgotten
5. **Threshold enforcement**: Cannot be overridden by AI

## Performance Metrics

Track approval workflow metrics:

- **Approval rate**: % of tasks approved vs. rejected
- **Average approval time**: Time from request to decision
- **Pending task count**: Number of tasks awaiting approval
- **Reminder frequency**: How often reminders are needed
- **Threshold accuracy**: Are thresholds set appropriately?

**Target metrics**:
- Approval rate: 80-90% (if too low, thresholds may be too strict)
- Average approval time: <4 hours during business hours
- Pending task count: <5 at any time
- Reminder frequency: <20% of tasks need reminders

## Notes

- Approval workflow reduces unauthorized actions to zero
- Human judgment is final - AI cannot override rejections
- Thresholds can be adjusted in Company_Handbook.md
- Approval commands are case-insensitive
- Task IDs must match exactly (including timestamp)
