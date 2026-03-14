---
name: email-triage
description: Analyze incoming emails and LinkedIn messages, then process or route to approval
version: 3.0
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

| User Command | Task Location | Task Type | Skill to Use |
|--------------|--------------|-----------|--------------|
| "Triage inbox" | `/Inbox/*/` | Any | `inbox-triage` |
| "Process emails" | `/Needs_Action/` | Email | `email-triage` |
| "Process LinkedIn messages" | `/Needs_Action/` | LinkedIn Message | `email-triage` |
| "Process file drops" | `/Needs_Action/` | File Drop | `email-triage` |
| "Plan this complex task" | `/Needs_Action/` | Multi-step | `task-planning` |
| "Approve task TASK_ID" | `/Pending_Approval/` | Any | `approval-workflow` |

---

## 🎯 PRIMARY MISSION

> "Read task files from Needs_Action, assess priority, check approval thresholds, then either execute (send email/LinkedIn) OR move to Pending_Approval and trigger approval-workflow skill."

---

## 📋 Priority Assessment Rules

### **HIGH Priority (Do Within 4 Hours)**

**Keywords**: urgent, asap, deadline, critical, emergency, time-sensitive

**Sender Types**:
- Clients with active projects
- Team members blocked on work
- Financial institutions (banks, payments)
- Legal/government communications

**Examples**:
- Client asking for deliverable with <24h deadline
- Team member blocked and can't proceed
- Payment/invoice issues
- Security alerts

**Action**: Process immediately, escalate if needed

---

### **MEDIUM Priority (Do Within 24 Hours)**

**Keywords**: meeting, call, review, feedback, proposal

**Sender Types**:
- Regular clients
- Colleagues
- Recruiters
- Service providers

**Examples**:
- Meeting invitations
- Project updates
- Feedback requests
- Sales inquiries

**Action**: Process within 24 hours during business days

---

### **LOW Priority (Do When Convenient)**

**Keywords**: newsletter, update, notification, FYI

**Sender Types**:
- Automated systems
- Newsletters
- Social media notifications
- Marketing emails

**Examples**:
- LinkedIn notifications
- Newsletter subscriptions
- Product updates
- Promotional emails

**Action**: Process when convenient, can batch process

---

## 🔄 Task Processing Workflow WITH SKILL CHAINING

### **Step 1: Read Task File**
```markdown
1. Extract metadata (type, priority, timestamp)
2. Read content (email body, message, file details)
3. Identify sender/creator
4. Check for deadlines/urgency
```

### **Step 2: Assess Priority**
```markdown
1. Check for urgent keywords (urgent, asap, deadline)
2. Evaluate sender importance (client, team, unknown)
3. Check financial implications
4. Determine if blocking others
5. Assign: High/Medium/Low
```

### **Step 3: Check Approval Thresholds**
```markdown
Refer to Company_Handbook.md:

Financial:
- >$500 → Requires approval

Communications:
- Client emails → Requires approval (draft first)
- LinkedIn posts → Requires approval

Data Operations:
- Delete/Bulk operations → Requires approval
```

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
# For LinkedIn messages - Use Playwright MCP
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

# For emails - Use Email MCP
claude "Send email using MCP: [draft content]"
"Log to /Logs/email_sent.log"
"Move to /Done/"
```

---

## 📝 Email Response Guidelines

### **Tone & Style**
- **Professional but friendly**
- **Clear and concise**
- **Action-oriented**
- **Free of typos/grammar errors**

### **Structure**
```markdown
1. Greeting (Hi [Name],)
2. Acknowledge their message (Thanks for reaching out...)
3. Address their question/concern
4. Clear next steps or CTA
5. Professional sign-off (Best regards, [Your name])
```

### **What NOT to Do**
- ❌ Don't make commitments without approval
- ❌ Don't share sensitive information
- ❌ Don't respond to spam
- ❌ Don't use overly casual language with clients

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

## 🚨 Red Flags (Escalate Immediately)

| Issue | Action |
|-------|--------|
| Payment request >$500 | Move to Pending_Approval, call approval-workflow |
| Client complaint | Draft response, move to Pending_Approval, call approval-workflow |
| Legal/contract language | Flag for manual review |
| Security alert | Escalate immediately |
| Phishing/spam suspected | Move to Rejected, log reason |

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

## 📈 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Response Time (High) | <4 hours | Timestamp comparison |
| Response Time (Medium) | <24 hours | Timestamp comparison |
| Response Time (Low) | <7 days | Timestamp comparison |
| Approval Accuracy | 100% | No unauthorized actions |
| Skill Chaining | 100% | approval-workflow called when needed |
| Task Completion Rate | >95% | Completed/Total tasks |

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Email & Task Processing with Hardcoded Skill Chaining*
