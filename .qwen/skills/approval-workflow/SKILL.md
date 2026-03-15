---
name: approval-workflow
description: Handle approval/rejection workflow for high-stakes tasks. Use when user says "approve task TASK_ID", "reject task TASK_ID", or when task exceeds thresholds (>$500, client emails, LinkedIn posts, bulk operations >10 items). This is the FINAL skill in the chain - no further skills are called after this. Executes task after approval and moves to /Done/.
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
| "Process emails" | `/Needs_Action/` | Email | `email-triage` | → `approval-workflow` |
| "Process LinkedIn messages" | `/Needs_Action/` | LinkedIn | `email-triage` | → `approval-workflow` |
| "Create LinkedIn post" | N/A | Post | `linkedin-posting` | → `approval-workflow` |
| "Approve task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` | **NONE (Final Step)** |
| "Reject task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` | **NONE (Final Step)** |

---

## 🎯 PRIMARY MISSION

> "Move tasks from /Pending_Approval/ to /Approved/ (on approval) or /Rejected/ (on rejection), execute the task, log results, and move to /Done/. This is the FINAL skill in the chain."

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

## 🔄 Complete Workflow Example

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

# approval-workflow executes using Playwright MCP:
1. Move to Approved/
2. Navigate to LinkedIn: "Navigate to https://www.linkedin.com"
3. Click "Start a post": "Click on 'Start a post' button"
4. Type post: "Type this text: [POST_CONTENT]"
5. Post: "Click on 'Post' button"
6. Verify: "Take screenshot"
7. Log to /Logs/linkedin_posts.log
8. Move to Done/
```

### **For LinkedIn Message Approval:**
```bash
# User approves
claude "approve task LINKEDIN_MSG_TASK_ID"

# approval-workflow executes using Playwright MCP:
1. Move to Approved/
2. Navigate to messaging: "Navigate to https://www.linkedin.com/messaging"
3. Find conversation: "Click on search box", "Type: [Recipient Name]"
4. Send message: "Click on message input", "Type: [MESSAGE]", "Press Enter"
5. Verify: "Take screenshot"
6. Log to /Logs/linkedin_messages.log
7. Move to Done/
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

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Approval/Rejection Workflow (FINAL STEP in skill chain)*
