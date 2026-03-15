---
name: inbox-triage
description: Triage inbox items from /Inbox/ folders and move to /Needs_Action/ with priority assessment. Use when user says "triage inbox", "process inbox", "check inbox", or when files exist in /Inbox/gmail/, /Inbox/filesystem/, or /Inbox/linkedin/. Automatically calls email-triage skill after completion.
---

# SKILL: Inbox Triage

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `inbox-triage` skill when:**
- User says: "triage inbox", "process inbox", "check inbox"
- Files exist in `/Inbox/gmail/`, `/Inbox/filesystem/`, or `/Inbox/linkedin/` folders
- Moving files from Inbox → Needs_Action with priority labels

**DO NOT use:** for processing tasks in Needs_Action (use `email-triage` for that)

## Skill Selection Matrix

| User Command | Task Location | Skill to Use | Next Skill |
|--------------|--------------|--------------|------------|
| "Triage inbox" | `/Inbox/*/` | `inbox-triage` | → `email-triage` |
| "Process emails" | `/Needs_Action/` | `email-triage` | → `approval-workflow` (if needed) |
| "Process LinkedIn messages" | `/Needs_Action/` | `email-triage` | → `approval-workflow` (if needed) |
| "Create LinkedIn post" | N/A | `linkedin-posting` | → `approval-workflow` |
| "Approve task" | `/Pending_Approval/` | `approval-workflow` | NONE (final step) |

---

## 🎯 PRIMARY MISSION

> "Move files from /Inbox/<source>/ to /Needs_Action/ with priority labels, then AUTOMATICALLY trigger email-triage skill to process them."

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

## 📊 Quality Checklist

Before completing triage, verify:

- [ ] All Inbox folders checked (gmail, filesystem, linkedin)
- [ ] Priority assessed for each file
- [ ] Files moved to correct folder (Needs_Action or Done)
- [ ] Triage metadata added (timestamp, priority)
- [ ] **HARDCODED: email-triage skill called** to process tasks
- [ ] High-priority items flagged for immediate attention

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Inbox Triage with Hardcoded Skill Chaining*
