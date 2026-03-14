---
name: approval-workflow
description: Handle approval/rejection workflow for high-stakes tasks
version: 3.0
---

# SKILL: Approval Workflow

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `approval-workflow` skill when:**
- User says: "approve task TASK_ID" → Approve and execute task
- User says: "reject task TASK_ID" → Reject and archive task
- Task exceeds approval thresholds (>$500, client emails, LinkedIn posts)
- Moving tasks: `/Pending_Approval/` → `/Approved/` or `/Rejected/`

**DO NOT use:** for regular tasks without approval requirements (use `email-triage` directly)

## Skill Selection Matrix

| User Command | Task Location | Task Type | Skill to Use | Next Skill |
|--------------|--------------|-----------|--------------|------------|
| "Triage inbox" | `/Inbox/*/` | Any | `inbox-triage` | → `email-triage` |
| "Process emails" | `/Needs_Action/` | Email | `email-triage` | → `approval-workflow` (if needed) |
| "Process LinkedIn messages" | `/Needs_Action/` | LinkedIn | `email-triage` | → `approval-workflow` (if needed) |
| "Create LinkedIn post" | N/A | Post | `linkedin-posting` | → `approval-workflow` |
| "Approve task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` | **NONE (Final Step)** |
| "Reject task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` | **NONE (Final Step)** |

---

## 🎯 PRIMARY MISSION

> "Move tasks from /Pending_Approval/ to /Approved/ (on approval) or /Rejected/ (on rejection), execute the task, log results, and move to /Done/. This is the FINAL skill in the chain."

---

## 💰 Approval Thresholds

### **ALWAYS Require Approval:**

| Action Type | Threshold | Why |
|-------------|-----------|-----|
| **Financial** | Any amount | Money decisions need human oversight |
| **Client Communications** | Any email/message | Brand reputation at stake |
| **LinkedIn Posts** | Any post | Public-facing content |
| **Bulk Operations** | >10 items | Risk of mass errors |
| **Data Deletions** | Any | Irreversible action |
| **System Changes** | Any configuration | Could break system |

---

## 🔄 Approval Workflow WITH SKILL CHAINING

### **Step 1: Task Arrives in Pending_Approval**

```markdown
From: email-triage OR linkedin-posting skill

Task file contains:
---
type: email
task_id: EMAIL_20260314_client-proposal
approval_threshold_exceeded: client_communication
requested_timestamp: 2026-03-14T10:00:00Z
approval_decision: pending
---

## Approval Required: Client Email Response

**Threshold Exceeded**: Client communication

**Proposed Action**: Send email response to client@example.com

**Draft**:
```
Dear Client,
Thank you for your inquiry...
[Full draft email]
```

**Approval Options**:
- Approve: `claude "approve task EMAIL_20260314_client-proposal"`
- Reject: `claude "reject task EMAIL_20260314_client-proposal --reason 'Not ready yet'"`
```

---

### **Step 2: User Approves Task**

**User Command:**
```bash
claude "approve task EMAIL_20260314_client-proposal"
```

**What approval-workflow Does:**

```markdown
## EXECUTION (HARDCODED)

**For Email Tasks:**
1. Move task: Pending_Approval → Approved
2. Send email via Email MCP:
   - Authenticate with Gmail API
   - Send email with draft content
   - Preserve threading (Reply-To headers)
3. Log to /Logs/email_sent.log:
   - Timestamp
   - Recipient
   - Subject
   - Status (sent/failed)
4. Move task: Approved → Done/
5. Update task file with completion timestamp

**For LinkedIn Posts:**
1. Move task: Pending_Approval → Approved
2. Post to LinkedIn via Playwright MCP:
   - Navigate to linkedin.com
   - Click "Start a post"
   - Type post content
   - Click "Post"
   - Take screenshot
3. Log to /Logs/linkedin_posts.log
4. Move task: Approved → Done/

**For LinkedIn Messages:**
1. Move task: Pending_Approval → Approved
2. Send via Playwright MCP:
   - Navigate to linkedin.com/messaging
   - Find conversation
   - Type and send message
   - Take screenshot
3. Log to /Logs/linkedin_messages.log
4. Move task: Approved → Done/

**For Financial/Payments:**
1. Move task: Pending_Approval → Approved
2. Execute payment (via API or manual)
3. Log to /Logs/payments.log
4. Move task: Approved → Done/
```

---

### **Step 3: User Rejects Task**

**User Command:**
```bash
claude "reject task EMAIL_20260314_client-proposal --reason 'Not ready yet'"
```

**What approval-workflow Does:**

```markdown
## REJECTION (HARDCODED)

1. Move task: Pending_Approval → Rejected
2. Add rejection metadata:
   ```markdown
   ---
   rejected_at: 2026-03-14T11:00:00Z
   rejected_by: Hunain Naeem Anwar
   rejection_reason: Not ready yet
   ---
   ```
3. Log to /Logs/rejections.log:
   - Timestamp
   - Task ID
   - Reason
4. Task stays in /Rejected/ (archive)
```

---

## 🔗 SKILL CHAINING (FINAL STEP)

### **approval-workflow is the FINAL skill in the chain**

```markdown
## NO NEXT SKILL TO CALL

**approval-workflow is the end of the chain.**

After approval-workflow completes:
- Task is in /Done/ (if approved) or /Rejected/ (if rejected)
- Action has been executed (email sent, post published, etc.)
- Result has been logged
- No further skill calls needed

**Workflow Complete!** ✅
```

---

## 📊 Complete Workflow Example

```
1. Gmail Watcher detects email
   ↓
2. Creates: /Inbox/gmail/EMAIL_project-inquiry.md
   ↓
3. User: "Triage inbox"
   ↓
4. inbox-triage skill:
   - Reads email
   - Assesses priority (High - client inquiry)
   - Moves to /Needs_Action/
   - **HARDCODED: Calls email-triage skill**
   ↓
5. email-triage skill:
   - Reads task
   - Checks approval (client email = requires approval)
   - Drafts response
   - Moves to /Pending_Approval/
   - **HARDCODED: Tells user to call approval-workflow**
   ↓
6. User: "approve task EMAIL_project-inquiry"
   ↓
7. approval-workflow skill:
   - Moves to /Approved/
   - Sends via Email MCP
   - Logs result
   - Moves to /Done/
   - **NO NEXT SKILL (workflow complete!)**
```

---

## 📝 Execution Guidelines

### **For Email Approval:**
```bash
# User approves
claude "approve task EMAIL_TASK_ID"

# approval-workflow executes:
1. Move to Approved/
2. Send via Email MCP
3. Log to /Logs/email_sent.log
4. Move to Done/
```

### **For LinkedIn Post Approval:**
```bash
# User approves
claude "approve task LINKEDIN_POST_TASK_ID"

# approval-workflow executes:
1. Move to Approved/
2. Post via Playwright MCP
3. Take screenshot
4. Log to /Logs/linkedin_posts.log
5. Move to Done/
```

### **For LinkedIn Message Approval:**
```bash
# User approves
claude "approve task LINKEDIN_MSG_TASK_ID"

# approval-workflow executes:
1. Move to Approved/
2. Send via Playwright MCP
3. Take screenshot
4. Log to /Logs/linkedin_messages.log
5. Move to Done/
```

---

## 📊 Quality Checklist

Before completing approval workflow, verify:

- [ ] Task moved to correct folder (Approved or Rejected)
- [ ] Approval/rejection decision logged
- [ ] **If approved:** Task executed (email sent, post published, etc.)
- [ ] **If approved:** Result logged to appropriate /Logs/ file
- [ ] **If approved:** Task moved to /Done/
- [ ] **If rejected:** Rejection reason recorded
- [ ] **If rejected:** Task moved to /Rejected/
- [ ] **NO next skill called** (this is the final step!)

---

## 📈 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Approval Response Time | <24 hours | Time in Pending_Approval |
| Execution Accuracy | 100% | No failed executions |
| Logging Completeness | 100% | All actions logged |
| Task Movement | 100% | All tasks in correct final folder |

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Task not in Pending_Approval | Check if email-triage moved it there |
| Approval command not working | Verify task ID matches filename |
| Email not sending | Check Email MCP server is running |
| LinkedIn post not publishing | Check Playwright MCP session |
| Task stuck in Approved | Check execution logs for errors |

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Approval/Rejection Workflow (FINAL STEP in skill chain)*
