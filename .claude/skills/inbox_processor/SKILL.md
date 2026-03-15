---
name: inbox-processor
description: Process and prioritize items in /Needs_Action folder, assess urgency, route to appropriate workflow
version: 1.0.0
---

# SKILL: Inbox Processor

## 🎯 PRIMARY MISSION

> "Read task files from /Needs_Action, assess priority using Company_Handbook.md rules, check approval thresholds, then either execute directly OR route to approval-workflow skill for high-stakes tasks."

---

## ⚠️ REQUIRED: USE THIS SKILL FOR

**ALWAYS use `inbox-processor` skill when:**
- User says: "process tasks in Needs_Action"
- User says: "what needs attention"
- Files exist in `/Needs_Action/` folder
- Task type is: `email`, `linkedin_message`, `file_drop`
- Need to assess priority (high/medium/low)
- Need to check approval thresholds

**DO NOT use:**
- `vault-manager` (that's for file operations only, not task processing)
- `task-planner` (that's for creating Plan.md AFTER priority assessment)
- `approval-workflow` (use ONLY after determining approval is needed)

---

## 🔄 PROCESSING WORKFLOW

### Step 1: Scan /Needs_Action Folder

```python
# Get all task files
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
needs_action_dir = vault_path / "Needs_Action"
task_files = list(needs_action_dir.glob("*.md"))
```

### Step 2: Read and Parse Each Task

```python
# Extract frontmatter
content = task_file.read_text()
frontmatter = yaml.safe_load(content.split('---')[1])

# Required fields
task_type = frontmatter.get('type')
source = frontmatter.get('source')
priority = frontmatter.get('priority', 'medium')
subject = frontmatter.get('subject', 'No subject')
```

### Step 3: Assess Priority

| Priority | Response Time | Criteria |
|----------|---------------|----------|
| **HIGH** | <4 hours | Urgent keywords (urgent, asap, deadline, critical), client with active project, financial/legal matters, team blocked |
| **MEDIUM** | <24 hours | Meeting requests, project updates, feedback requests, sales inquiries |
| **LOW** | <7 days | Newsletters, FYI updates, notifications, promotional content |

### Step 4: Check Approval Thresholds

**Refer to `Company_Handbook.md` for thresholds:**

| Threshold | Requires Approval | Action |
|-----------|-------------------|--------|
| Client communication | ✅ YES | Route to `approval-workflow` |
| Payment >$500 | ✅ YES | Route to `approval-workflow` |
| LinkedIn post | ✅ YES | Route to `approval-workflow` |
| Contract/legal language | ✅ YES | Route to `approval-workflow` |
| Internal team email | ❌ NO | Execute directly |
| File processing | ❌ NO | Execute directly |

### Step 5: Take Action

**If approval IS needed:**

```markdown
## NEXT SKILL TO CALL (HARDCODED)

**Skill:** `approval-workflow`

**Command:**
```bash
claude "approve task TASK_ID"
```

**What happens:**
1. Move task to `/Pending_Approval/`
2. Add approval request metadata
3. Wait for user approval
4. After approval: execute → log → move to `/Done/`
```

**If approval is NOT needed:**

```markdown
## EXECUTE DIRECTLY

**For simple tasks:**
- Process task content
- Take required action
- Log result to `/Logs/`
- Move to `/Done/`

**For complex multi-step tasks:**
- Call `task-planner` skill first
- Create `Plan.md` file
- Execute plan steps
- Move to `/Done/`
```

---

## 📋 PRIORITY ASSESSMENT RULES

### HIGH Priority Indicators

**Keywords in subject/body:**
- urgent, asap, deadline, critical, emergency, time-sensitive, important
- blocked, stuck, cannot proceed, need help

**Sender types:**
- Clients with active projects
- Team members reporting blockers
- Financial institutions (banks, payments)
- Legal/government communications

**Examples:**
```
✓ Client asking for deliverable with <24h deadline
✓ Team member blocked and cannot proceed
✓ Payment/invoice issues
✓ Security alerts
```

### MEDIUM Priority Indicators

**Keywords:**
- meeting, call, review, feedback, proposal, update

**Sender types:**
- Regular clients
- Colleagues
- Recruiters
- Service providers

**Examples:**
```
✓ Meeting invitations
✓ Project status updates
✓ Feedback requests
✓ Sales inquiries
```

### LOW Priority Indicators

**Keywords:**
- newsletter, update, notification, FYI, weekly digest

**Sender types:**
- Automated systems
- Newsletter subscriptions
- Social media notifications
- Marketing emails

**Examples:**
```
✓ LinkedIn notifications
✓ Newsletter subscriptions
✓ Product updates
✓ Promotional emails
```

---

## 🎯 TASK ROUTING DECISION TREE

```
Task in /Needs_Action/
        │
        ▼
┌───────────────────┐
│ Assess Priority   │
│ (High/Med/Low)    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Check Approval    │
│ Thresholds        │
└─────────┬─────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
Approval    No Approval
Needed      Needed
    │           │
    │           ├─── Simple Task ──▶ Execute directly
    │           │
    │           └─── Complex Task ──▶ Call task-planner
    │
    ▼
Call approval-workflow
Move to /Pending_Approval/
```

---

## 📝 RESPONSE GUIDELINES

### Email Response Structure

```markdown
1. Greeting (Hi [Name],)
2. Acknowledge their message (Thanks for reaching out...)
3. Address their question/concern
4. Clear next steps or CTA
5. Professional sign-off (Best regards, [Your name])
```

### LinkedIn Response Structure

```markdown
1. Personalized greeting
2. Reference specific detail from their message
3. Provide value/answer
4. Open-ended question to continue conversation
5. Professional closing
```

### What NOT to Do

- ❌ Don't make commitments without approval
- ❌ Don't share sensitive information
- ❌ Don't respond to spam/suspicious messages
- ❌ Don't use overly casual language with clients
- ❌ Don't skip approval for high-stakes tasks

---

## 🚨 RED FLAGS (ESCALATE IMMEDIATELY)

| Issue | Action |
|-------|--------|
| Payment request >$500 | Move to `/Pending_Approval/`, call `approval-workflow` |
| Client complaint | Draft response, move to `/Pending_Approval/`, call `approval-workflow` |
| Legal/contract language | Flag for manual review, move to `/Pending_Approval/` |
| Security alert | Escalate immediately, HIGH priority |
| Phishing/spam suspected | Move to `/Rejected/`, log reason |

---

## 📊 QUALITY CHECKLIST

Before completing task processing:

- [ ] Priority assessed correctly (High/Medium/Low)
- [ ] Approval threshold checked against `Company_Handbook.md`
- [ ] **If approval needed:** Moved to `/Pending_Approval/` + `approval-workflow` called
- [ ] **If no approval:** Task executed or `task-planner` called for complex tasks
- [ ] Response tone is appropriate for sender type
- [ ] Message is clear and concise
- [ ] Call-to-action included (if needed)
- [ ] No sensitive info exposed
- [ ] Result logged to `/Logs/`
- [ ] Task moved to correct folder (`/Done/`, `/Rejected/`, or `/Pending_Approval/`)
- [ ] **Dashboard.md updated** with latest activity

---

## 📋 DASHBOARD UPDATE PROCEDURE

**ALWAYS update Dashboard.md after processing tasks:**

```python
from datetime import datetime, timezone
from pathlib import Path

def update_dashboard(vault_path: Path, processed_count: int, completed_tasks: list):
    """Update Dashboard.md with latest activity"""
    
    dashboard_file = vault_path / "Dashboard.md"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %I:%M %p UTC")
    
    # Count files in each folder
    needs_action_count = len((vault_path / "Needs_Action").glob("*.md"))
    plans_count = len((vault_path / "Plans").glob("*.md"))
    done_count = len((vault_path / "Done").glob("*.md"))
    pending_approval_count = len((vault_path / "Pending_Approval").glob("*.md"))
    
    # Build recent activity section
    activity_items = []
    for task in completed_tasks[-5:]:  # Last 5 tasks
        activity_items.append(f"- ✅ **{task['name']}**: {task['action']} ({timestamp})")
    
    recent_activity = "\n".join(activity_items) if activity_items else "- No new activity"
    
    # Build pending tasks section
    pending_tasks = []
    needs_action_dir = vault_path / "Needs_Action"
    for task_file in needs_action_dir.glob("*.md"):
        content = task_file.read_text()
        frontmatter = yaml.safe_load(content.split('---')[1])
        priority = frontmatter.get('priority', 'medium')
        priority_icon = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
        pending_tasks.append(f"- {priority_icon} [{task_file.name}](Needs_Action/{task_file.name})")
    
    pending_section = "\n".join(pending_tasks) if pending_tasks else "- ✅ No pending tasks"
    
    # Update dashboard content
    dashboard_content = f"""# AI Employee Dashboard

**Last Updated**: {timestamp}

## Recent Activity

{recent_activity}

## Pending Tasks

{pending_section}

**Quick Actions**:
- Review tasks in `/Needs_Action`
- Check plans in `/Plans`
- Review items awaiting approval in `/Pending_Approval`

## System Status

| Component | Status | Last Check |
|-----------|--------|------------|
| Watcher | ✅ Running | {timestamp} |
| Claude Code | ✅ Active | {timestamp} |
| Vault | ✅ Initialized | {timestamp} |

## Task Summary

| Folder | Count |
|--------|-------|
| Needs_Action | {needs_action_count} |
| Plans | {plans_count} |
| Done | {done_count} |
| Pending_Approval | {pending_approval_count} |

## Quick Links

- [[Company_Handbook]] - Rules and policies
- [[Needs_Action/]] - Tasks requiring action
- [[Plans/]] - Execution plans
- [[Logs/]] - System logs

## Notes

Dashboard auto-updated after processing {processed_count} task(s).
"""
    
    dashboard_file.write_text(dashboard_content)
```

**Example Dashboard Update:**

```markdown
# AI Employee Dashboard

**Last Updated**: 2026-03-15 12:30 PM UTC

## Recent Activity

- ✅ **EMAIL_test-of-email-account.md**: Sent confirmation reply via Gmail MCP (2026-03-15 12:22 PM UTC)
- ✅ **LINKEDIN_MSG_...md**: Sent reply in Roman Urdu via LinkedIn (2026-03-15 12:22 PM UTC)

## Pending Tasks

- ✅ No pending tasks

**Quick Actions**:
- Review tasks in `/Needs_Action`
- Check plans in `/Plans`
- Review items awaiting approval in `/Pending_Approval`

## System Status

| Component | Status | Last Check |
|-----------|--------|------------|
| Watcher | ✅ Running | 2026-03-15 12:30 PM UTC |
| Claude Code | ✅ Active | 2026-03-15 12:30 PM UTC |
| Vault | ✅ Initialized | 2026-03-15 12:30 PM UTC |

## Task Summary

| Folder | Count |
|--------|-------|
| Needs_Action | 0 |
| Plans | 0 |
| Done | 16 |
| Pending_Approval | 0 |
```

---

## 📈 PERFORMANCE METRICS

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Response Time (High) | <4 hours | Timestamp comparison |
| Response Time (Medium) | <24 hours | Timestamp comparison |
| Response Time (Low) | <7 days | Timestamp comparison |
| Approval Accuracy | 100% | No unauthorized high-stakes actions |
| Skill Chaining | 100% | `approval-workflow` called when needed |
| Task Completion Rate | >95% | Completed/Total tasks |

---

## 🔗 RELATED SKILLS

- `vault-manager` - File operations (read/write/move)
- `task-planner` - Create `Plan.md` for multi-step tasks
- `approval-workflow` - Handle approval requests
- `email-handler` - Send emails via MCP server
- `social-poster` - Create LinkedIn posts

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: Task Processing from /Needs_Action/*
