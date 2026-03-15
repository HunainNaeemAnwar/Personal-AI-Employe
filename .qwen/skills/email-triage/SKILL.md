---
name: email-triage
description: Process email and LinkedIn message tasks from /Needs_Action/ folder. Use when user says "process emails", "process LinkedIn messages", "process file drops", "handle tasks in Needs_Action", or when files in /Needs_Action/ have type email, linkedin_message, or file_drop. Assesses priority using Company_Handbook.md, checks approval thresholds, uses Playwright MCP for LinkedIn messages, Email MCP for emails, and routes to approval-workflow skill if approval needed.
---

# SKILL: Email Triage

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `email-triage` skill when:**
- User says: "process emails" → Process email tasks from `/Needs_Action/`
- User says: "process LinkedIn messages" → Process LinkedIn message tasks from `/Needs_Action/`
- User says: "process file drops" → Process file drop tasks from `/Needs_Action/`
- Files are in `/Needs_Action/` folder (NOT Inbox)
- Task type is: `email`, `linkedin_message`, `file_drop`

**DO NOT use:** 
- `inbox-triage` (that's for Inbox → Needs_Action)
- `task-planning` (that's for complex multi-step tasks only)
- `approval-workflow` (use ONLY if threshold exceeded)

## Skill Selection Matrix

| User Command | Task Location | Task Type | Skill to Use | Next Skill |
|--------------|--------------|-----------|--------------|------------|
| "Triage inbox" | `/Inbox/*/` | Any | `inbox-triage` | → `email-triage` |
| "Process emails" | `/Needs_Action/` | Email | `email-triage` | → `approval-workflow` (if needed) |
| "Process LinkedIn messages" | `/Needs_Action/` | LinkedIn | `email-triage` | → `approval-workflow` (if needed) |
| "Process file drops" | `/Needs_Action/` | File | `email-triage` | None |
| "Plan this complex task" | `/Needs_Action/` | Multi-step | `task-planning` | → Specified skill |
| "Approve task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` | NONE |

---

## 🎯 PRIMARY MISSION

> "Read task files from Needs_Action, assess priority, check approval thresholds, then either execute (send email/LinkedIn) OR move to Pending_Approval and trigger approval-workflow skill."

---

## 🔄 Task Processing Workflow WITH SKILL CHAINING

### **Step 4: Take Action WITH HARDCODED SKILL CHAINING**

**If approval IS needed:**

```markdown
## NEXT SKILL TO CALL (HARDCODED)

**Skill:** `approval-workflow`

**Command:**
```bash
claude "approve task TASK_ID"
```

**What happens:**
1. Move task to /Pending_Approval/
2. Add approval request metadata
3. Wait for user to run: "approve task TASK_ID"
4. approval-workflow skill will:
   - Move to /Approved/
   - Execute (send email/LinkedIn)
   - Log result
   - Move to /Done/
```

**If approval is NOT needed:**

```bash
# For LinkedIn Messages - Use Playwright MCP (REQUIRED)
"Navigate to https://www.linkedin.com/messaging"
"Click on search box"
"Type: [Recipient Name]"
"Click on first result"
"Click on message input"
"Type: [DRAFTED_RESPONSE]"
"Press Enter to send"
"Take screenshot"
"Log to /Logs/linkedin_messages.log"
"Move to /Done/"

# For Emails - Use Email MCP
claude "Send email using MCP: [draft content]"
"Log to /Logs/email_sent.log"
"Move to /Done/"
```

---

## 🔗 HARDCODED SKILL CHAINS

### **After Email-Triage Completes:**

**Scenario 1: Approval Needed**
```markdown
## NEXT SKILL TO CALL (HARDCODED)

**Skill:** `approval-workflow`

**When:** Task exceeds approval thresholds (client email, payment >$500, LinkedIn post)

**Command:**
```bash
# Move to Pending_Approval first
mv AI_Employee_Vault/Needs_Action/TASK_ID.md AI_Employee_Vault/Pending_Approval/

# Then tell user to approve
"Task moved to Pending_Approval. Run: claude 'approve task TASK_ID'"
```

**What approval-workflow does:**
1. Moves task from Pending_Approval → Approved
2. Executes task (sends email/LinkedIn)
3. Logs result
4. Moves to Done/
```

**Scenario 2: No Approval Needed**
```markdown
## EXECUTE DIRECTLY

**For LinkedIn Messages:**
- Use Playwright MCP to send
- Log to /Logs/linkedin_messages.log
- Move to /Done/

**For Emails:**
- Use Email MCP to send
- Log to /Logs/email_sent.log
- Move to /Done/

**NO additional skill needed**
```

---

## 📊 Quality Checklist

Before completing task, verify:

- [ ] Priority assessed correctly (High/Medium/Low)
- [ ] Approval threshold checked
- [ ] **If approval needed:** Moved to Pending_Approval + approval-workflow called
- [ ] **If no approval:** Task executed (email/LinkedIn sent)
- [ ] Response tone is appropriate
- [ ] Message is clear and concise
- [ ] Call-to-action included (if needed)
- [ ] No sensitive info exposed
- [ ] Result logged to /Logs/
- [ ] Task moved to correct folder

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Email & Task Processing with Hardcoded Skill Chaining*
