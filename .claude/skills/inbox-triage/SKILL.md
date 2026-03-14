---
name: inbox-triage
description: Triage inbox items and move to Needs_Action for processing
version: 3.0
---

# SKILL: Inbox Triage

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `inbox-triage` skill when:**
- User says: "triage inbox", "process inbox", "check inbox"
- Files exist in `/Inbox/*/` folders
- Moving files from Inbox → Needs_Action

**DO NOT use:** email-triage, task-planning, or other skills for inbox triage!

## Skill Selection Matrix

| User Command | Task Location | Skill to Use |
|--------------|--------------|--------------|
| "Triage inbox" | `/Inbox/gmail/` | `inbox-triage` |
| "Triage inbox" | `/Inbox/filesystem/` | `inbox-triage` |
| "Triage inbox" | `/Inbox/linkedin/` | `inbox-triage` |
| "Process emails" | `/Needs_Action/` | `email-triage` |
| "Process LinkedIn messages" | `/Needs_Action/` | `email-triage` |
| "Process file drops" | `/Needs_Action/` | `email-triage` |
| "Plan this complex task" | `/Needs_Action/` | `task-planning` |
| "Approve task TASK_ID" | `/Pending_Approval/` | `approval-workflow` |
| "Create LinkedIn post" | N/A (new content) | `linkedin-posting` |

---

## 🎯 PRIMARY MISSION

> "Move files from /Inbox/<source>/ to /Needs_Action/ with proper priority assessment, then AUTOMATICALLY trigger email-triage skill to process them."

---

## 📋 Triage Workflow WITH SKILL CHAINING

### **Step 1: Check Inbox Folders**
```bash
ls AI_Employee_Vault/Inbox/gmail/
ls AI_Employee_Vault/Inbox/filesystem/
ls AI_Employee_Vault/Inbox/linkedin/
```

### **Step 2: Review Each File**

For each file in Inbox:

1. **Read the file** to understand content
2. **Determine priority** based on:
   - **High**: Urgent keywords, client emails, deadlines
   - **Medium**: Regular communications, important files
   - **Low**: Newsletters, notifications, FYI items

3. **Move to Needs_Action** with priority metadata

### **Step 3: HARDCODED SKILL CHAINING** ⚠️ CRITICAL

**AFTER moving files to Needs_Action, AUTOMATICALLY trigger:**

```bash
# HARDCODED: Always call email-triage after inbox-triage
claude "Use email-triage skill to process all tasks in Needs_Action"
```

**Why?** Inbox-triage ONLY moves files. Email-triage actually PROCESSES them.

---

## ⚠️ IMPORTANT: Execution Rules

**DO NOT move to /Done/ until action is ACTUALLY completed:**

| Task Type | When to Move to Done |
|-----------|---------------------|
| Email reply | ✅ AFTER sending via Gmail MCP |
| LinkedIn message | ✅ AFTER sending via LinkedIn |
| File processing | ✅ AFTER file is processed/extracted |
| FYI/Informational | ✅ Immediately (no action needed) |

**Wrong Workflow** ❌:
```
Read message → Draft response → Move to Done
                          ↓
                  (Never actually sent!)
```

**Correct Workflow** ✅:
```
Read message → Draft response → Execute (send) → Move to Done
                                    ↓
                          Actually send the message!
```

---

## 📊 Priority Guidelines

### **High Priority (Flag for Immediate Attention)**

**Keywords**: urgent, asap, deadline, critical, emergency

**Sender Types**:
- Clients with active projects
- Financial institutions
- Legal/government

**Action**: Move to Needs_Action, flag as HIGH, then call email-triage

---

### **Medium Priority (Process Within 24 Hours)**

**Keywords**: meeting, review, feedback, proposal

**Sender Types**:
- Regular clients
- Colleagues
- Service providers

**Action**: Move to Needs_Action, flag as MEDIUM, then call email-triage

---

### **Low Priority (Process When Convenient)**

**Keywords**: newsletter, update, notification, FYI

**Sender Types**:
- Automated systems
- Marketing emails
- Social media

**Action**: Move to Needs_Action, flag as LOW, then call email-triage

---

## 🔗 HARDCODED SKILL CHAINS

### **After Inbox-Triage Completes:**

```markdown
## NEXT SKILL TO CALL (HARDCODED)

**Skill:** `email-triage`

**Command:**
```bash
claude "Use email-triage skill to process all tasks in Needs_Action"
```

**What email-triage does:**
1. Reads each task file in Needs_Action
2. Assesses priority using Company_Handbook.md
3. Checks if approval is needed
4. If approval needed → Moves to /Pending_Approval/ → Calls `approval-workflow`
5. If no approval → Executes task (sends email/LinkedIn message)
6. Logs result and moves to /Done/
```

---

## 📝 Execution Commands

### **For LinkedIn Messages (via email-triage):**

**Use Playwright MCP (Built-in to Qwen)**
```bash
# 1. Navigate to LinkedIn Messaging
"Navigate to https://www.linkedin.com/messaging"

# 2. Search for recipient
"Click on search box"
"Type: [Recipient Name]"

# 3. Open conversation
"Click on first result"

# 4. Type and send message
"Click on message input"
"Type: [DRAFTED_RESPONSE]"
"Press Enter to send"

# 5. Verify and log
"Take screenshot"
"Log to /Logs/linkedin_messages.log"

# 6. Move to Done
mv AI_Employee_Vault/Needs_Action/linkedin/*.md AI_Employee_Vault/Done/linkedin/
```

### **For Email Replies (via email-triage):**

**Use Email MCP Server**
```bash
# Send via Email MCP Server
claude "Send email using MCP: [draft content]"

# After sending, move to Done
```

---

## 📊 Quality Checklist

Before completing triage, verify:

- [ ] All Inbox folders checked (gmail, filesystem, linkedin)
- [ ] Priority assessed for each file
- [ ] Files moved to correct folder (Needs_Action or Done)
- [ ] Triage metadata added (timestamp, priority)
- [ ] **HARDCODED: email-triage skill called** to process tasks
- [ ] High-priority items flagged for immediate attention

---

## 📈 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Triage Time | <5 minutes | Time from command to completion |
| Priority Accuracy | >95% | Correct priority assignments |
| File Movement | 100% | All files moved to correct folder |
| Skill Chaining | 100% | email-triage called after inbox-triage |
| Metadata Complete | 100% | All files have triage metadata |

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Inbox Triage with Hardcoded Skill Chaining*
