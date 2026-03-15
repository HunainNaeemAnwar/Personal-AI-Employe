---
name: approval-workflow
description: Handle Human-in-the-Loop (HITL) approval workflow - move tasks to /Pending_Approval/, process approvals/rejections, track decisions
version: 1.0.0
---

# SKILL: Approval Workflow

## 🎯 PRIMARY MISSION

> "Manage Human-in-the-Loop (HITL) approval workflow by moving high-stakes tasks to /Pending_Approval/, processing user approval/rejection commands, and ensuring no sensitive actions execute without authorization."

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `approval-workflow` skill when:**
- User says: "approve task TASK_ID"
- User says: "reject task TASK_ID"
- Task exceeds approval thresholds (client email, payment >$500, LinkedIn post)
- Need to move task to `/Pending_Approval/`
- Need to track approval decisions for audit trail

**DO NOT use:**
- `inbox-processor` (that's for initial priority assessment - it CALLS this skill)
- `email-handler` (use AFTER approval for email sending)
- `social-poster` (use AFTER approval for LinkedIn posting)

---

## 📋 APPROVAL THRESHOLDS

**Read from `Company_Handbook.md`:**

| Threshold Category | Requires Approval | Examples |
|-------------------|-------------------|----------|
| **Client Communication** | ✅ YES | Any email to clients, prospects, partners |
| **Payment >$500** | ✅ YES | Invoices, payments, financial commitments |
| **LinkedIn Posts** | ✅ YES | All LinkedIn content before publishing |
| **Contract/Legal** | ✅ YES | Agreements, terms, legal language |
| **Data Deletion** | ✅ YES | Bulk delete, database modifications |
| **Internal Team** | ❌ NO | Routine team communication |
| **File Processing** | ❌ NO | Extracting data, organizing files |

---

## 🔄 APPROVAL WORKFLOW

### Step 1: Identify Tasks Requiring Approval

```python
# Read task file
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
task_file = vault_path / "Needs_Action" / "TASK_ID.md"
content = task_file.read_text()
frontmatter = yaml.safe_load(content.split('---')[1])

# Check thresholds
requires_approval = False
threshold_exceeded = ""

if frontmatter.get('type') == 'email':
    if is_client_email(frontmatter.get('source')):
        requires_approval = True
        threshold_exceeded = "client_communication"

if frontmatter.get('type') == 'linkedin_post':
    requires_approval = True
    threshold_exceeded = "social_media_post"

if 'payment' in content.lower() and extract_amount(content) > 500:
    requires_approval = True
    threshold_exceeded = "payment_over_500"
```

### Step 2: Move to /Pending_Approval/

```python
# Add approval request frontmatter
approval_frontmatter = f"""
type: approval_request
task_id: {task_id}
task_type: {frontmatter.get('type')}
approval_threshold_exceeded: {threshold_exceeded}
requested_timestamp: {datetime.now(timezone.utc).isoformat()}Z
approval_decision: pending
"""

# Update task file
task_file.write_text(approval_frontmatter + '\n---\n' + content.split('---')[2])

# Move to Pending_Approval
import shutil
shutil.move(
    str(task_file),
    str(vault_path / "Pending_Approval" / f"{task_file.name}")
)

# Log approval request
log_approval_request(task_id, threshold_exceeded)
```

### Step 3: Process Approval Command

**User runs:** `claude "approve task TASK_ID"`

```python
# Find task in Pending_Approval
pending_dir = vault_path / "Pending_Approval"
task_file = pending_dir / f"{task_id}.md"

if not task_file.exists():
    return "Task not found in /Pending_Approval/"

# Update frontmatter with approval decision
content = task_file.read_text()
frontmatter = yaml.safe_load(content.split('---')[1])

frontmatter['approver'] = get_current_user()
frontmatter['approval_decision'] = 'approved'
frontmatter['decision_timestamp'] = datetime.now(timezone.utc).isoformat() + 'Z'

# Update file
update_frontmatter(task_file, frontmatter)

# Move to Approved folder
shutil.move(
    str(task_file),
    str(vault_path / "Approved" / f"{task_file.name}")
)

# Execute the task (send email, post LinkedIn, etc.)
execute_approved_task(task_file)

# Log approval decision
log_approval_decision(task_id, 'approved', get_current_user())

# Move to Done after execution
shutil.move(
    str(vault_path / "Approved" / f"{task_file.name}"),
    str(vault_path / "Done" / f"{task_file.name}")
)
```

### Step 4: Process Rejection Command

**User runs:** `claude "reject task TASK_ID --reason 'reason here'"`

```python
# Find task in Pending_Approval
pending_dir = vault_path / "Pending_Approval"
task_file = pending_dir / f"{task_id}.md"

if not task_file.exists():
    return "Task not found in /Pending_Approval/"

# Update frontmatter with rejection decision
content = task_file.read_text()
frontmatter = yaml.safe_load(content.split('---')[1])

frontmatter['approver'] = get_current_user()
frontmatter['approval_decision'] = 'rejected'
frontmatter['decision_timestamp'] = datetime.now(timezone.utc).isoformat() + 'Z'
frontmatter['rejection_reason'] = rejection_reason

# Update file
update_frontmatter(task_file, frontmatter)

# Move to Rejected folder
shutil.move(
    str(task_file),
    str(vault_path / "Rejected" / f"{task_file.name}")
)

# Log rejection decision
log_approval_decision(task_id, 'rejected', get_current_user(), rejection_reason)
```

---

## 📝 APPROVAL COMMAND SYNTAX

### Approve Task

```bash
# Basic approval
claude "approve task TASK_ID"

# With custom message (optional)
claude "approve task TASK_ID --message 'Looks good, send it'"
```

### Reject Task

```bash
# Basic rejection
claude "reject task TASK_ID"

# With reason (recommended)
claude "reject task TASK_ID --reason 'Pricing too high for this client'"
claude "reject task TASK_ID --reason 'Need to revise tone before sending'"
```

### Check Pending Tasks

```bash
# List all pending approvals
claude "what tasks are pending approval"

# Check specific task status
claude "status of task TASK_ID"
```

---

## 📊 APPROVAL REQUEST TEMPLATE

```markdown
---
type: approval_request
task_id: EMAIL_20260315T143000Z_client-inquiry
task_type: email
approval_threshold_exceeded: client_communication
requested_timestamp: 2026-03-15T15:00:00Z
approver: hunain (after approval)
approval_decision: pending (or approved/rejected)
decision_timestamp: 2026-03-15T15:05:00Z (after decision)
rejection_reason: Reason text (if rejected)
---

# Approval Required: Client Email Response

**Threshold Exceeded**: Client Communication (requires approval per Company_Handbook.md)

**Email Details**:
- **To**: client@example.com
- **Subject**: Re: Project Proposal
- **Type**: Client communication

**Email Draft**:

Hi [Client Name],

Thank you for your inquiry about the project proposal...

[Full email body]

---

**Approval Options**:

✅ **Approve**: `claude "approve task EMAIL_20260315T143000Z_client-inquiry"`

❌ **Reject**: `claude "reject task EMAIL_20260315T143000Z_client-inquiry --reason 'reason here'"`
```

---

## 🚨 24-HOUR REMINDER SYSTEM

**For tasks pending approval >24 hours:**

```python
# Check pending tasks daily
pending_dir = vault_path / "Pending_Approval"
reminder_sent_log = vault_path / "Logs" / "approval_reminders.log"

for task_file in pending_dir.glob("*.md"):
    content = task_file.read_text()
    frontmatter = yaml.safe_load(content.split('---')[1])
    
    if frontmatter.get('approval_decision') == 'pending':
        requested = datetime.fromisoformat(frontmatter['requested_timestamp'].replace('Z', '+00:00'))
        age = datetime.now(timezone.utc) - requested
        
        if age > timedelta(hours=24):
            # Check if reminder already sent
            if not reminder_already_sent(task_file.name, reminder_sent_log):
                # Add reminder to Dashboard.md
                add_to_dashboard(f"⏰ Pending Approval: {task_file.name} (waiting {age.hours}h)")
                log_reminder_sent(task_file.name)
```

---

## 📋 APPROVAL LOGGING

### Log File: /Logs/approvals.log

```json
{
  "timestamp": "2026-03-15T15:05:00Z",
  "task_id": "EMAIL_20260315T143000Z_client-inquiry",
  "task_type": "email",
  "threshold_exceeded": "client_communication",
  "decision": "approved",
  "approver": "hunain",
  "decision_timestamp": "2026-03-15T15:05:00Z",
  "rejection_reason": null
}
```

### Log File: /Logs/pending_approvals.json

```json
[
  {
    "task_id": "EMAIL_20260315T143000Z_client-inquiry",
    "requested_at": "2026-03-15T15:00:00Z",
    "threshold": "client_communication",
    "status": "pending",
    "reminder_sent": false
  }
]
```

---

## 🎯 QUALITY CHECKLIST

Before completing approval workflow:

- [ ] Correct threshold identified (client_communication, payment_over_500, social_media_post)
- [ ] Task moved to `/Pending_Approval/` (not `/Approved/` directly)
- [ ] Approval request frontmatter added with all required fields
- [ ] User notified of pending approval with clear commands
- [ ] **On approval:** Task moved to `/Approved/` → Executed → Logged → `/Done/`
- [ ] **On rejection:** Task moved to `/Rejected/` with reason logged
- [ ] Approval decision logged to `/Logs/approvals.log`
- [ ] 24-hour reminder sent if pending >24 hours
- [ ] No high-stakes action executed without approval

---

## 📈 PERFORMANCE METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Approval Accuracy | 100% | Zero unauthorized high-stakes actions |
| Response Time (High) | <4 hours | Approval request to decision |
| Response Time (Medium) | <24 hours | Approval request to decision |
| Reminder Compliance | 100% | All pending >24h get reminders |
| Audit Trail | 100% | All decisions logged |

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Calls this skill when approval is needed
- `email-handler` - Executes email sending AFTER approval
- `social-poster` - Executes LinkedIn posting AFTER approval
- `vault-manager` - File operations for moving tasks between folders
- `task-planner` - Creates plans that may require approval steps

---

## 🚨 SECURITY NOTES

**CRITICAL: Never bypass approval workflow for:**

- ❌ Client communications (always require approval)
- ❌ Payments over $500 (always require approval)
- ❌ LinkedIn posts (always require approval)
- ❌ Contract/legal language (always require approval)

**If user asks to skip approval:**

> "I cannot skip approval for this task as it exceeds the [threshold] threshold defined in Company_Handbook.md. This is a security measure to prevent unauthorized actions. Please approve the task using: `claude 'approve task TASK_ID'`"

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Human-in-the-Loop Approval Management*
