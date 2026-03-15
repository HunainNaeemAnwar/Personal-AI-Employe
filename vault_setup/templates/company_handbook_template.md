# Company Handbook

**Version**: 2.0
**Last Updated**: [DATE]
**Review Frequency**: [FREQUENCY, e.g., Quarterly]

---

## 👤 User Profile

**Name**: [YOUR_NAME]

**Professional Brand**:
- [ROLE/TITLE]
- [EXPERTISE_AREA_1]
- [EXPERTISE_AREA_2]

**Links**:
- GitHub: [GITHUB_URL]
- LinkedIn: [LINKEDIN_URL]
- Website: [WEBSITE_URL]

---

## 🤖 AI EMPLOYEE WORKFLOW OVERVIEW

*This section documents how the AI Employee processes tasks from detection to dashboard update.*

### 📁 Vault Folder Structure

```
AI_Employee_Vault/
├── Inbox/
│   ├── gmail/           → [DESCRIPTION]
│   ├── filesystem/      → [DESCRIPTION]
│   └── linkedin/        → [DESCRIPTION]
├── Needs_Action/        → [DESCRIPTION]
├── Plans/               → [DESCRIPTION]
├── Pending_Approval/    → [DESCRIPTION]
├── Approved/            → [DESCRIPTION]
├── Done/                → [DESCRIPTION]
├── Rejected/            → [DESCRIPTION]
├── Logs/                → [DESCRIPTION]
├── Dashboard.md         → [DESCRIPTION]
└── Company_Handbook.md  → [THIS_FILE]
```

---

## 🔄 COMPLETE WORKFLOW STEPS

### **STEP 1: [STEP_NAME]**

**What Happens:**
- [DESCRIPTION_OF_ACTION_1]
- [DESCRIPTION_OF_ACTION_2]

**Trigger:**
- [WHAT_TRIGGERS_THIS_STEP]

**Files Created/Modified:**
```
[FILE_PATH_EXAMPLE]
```

**Skills Involved:**
- `[SKILL_NAME]`

---

### **STEP 2: [STEP_NAME]**

**What Happens:**
- [DESCRIPTION]

**Trigger Command:**
```bash
claude "[COMMAND_TO_TRIGGER]"
```

**Before:**
```
[BEFORE_STATE]
```

**After:**
```
[AFTER_STATE]
```

---

### **STEP 3: [STEP_NAME]**

**What Happens:**
- [DESCRIPTION]

**Decision Points:**
| Condition | Action |
|-----------|--------|
| [CONDITION_1] | [ACTION_1] |
| [CONDITION_2] | [ACTION_2] |

---

### **STEP 4: [STEP_NAME]**

**Approval Commands:**
```bash
# Approve
claude "approve task [TASK_ID]"

# Reject
claude "reject task [TASK_ID] --reason '[REASON]'"
```

**Flow:**
```
[SOURCE_FOLDER] → [DESTINATION_FOLDER] → [EXECUTION] → [FINAL_FOLDER]
```

---

### **STEP 5: [STEP_NAME]**

**Execution by Task Type:**

| Task Type | Skill Used | Action |
|-----------|------------|--------|
| email | `[SKILL]` | [ACTION] |
| linkedin_message | `[SKILL]` | [ACTION] |
| file_drop | `[SKILL]` | [ACTION] |

---

### **STEP 6: LOGGING**

**Log Files:**

| Log File | Tracks |
|----------|--------|
| `/Logs/[LOG_NAME].log` | [WHAT_IT_TRACKS] |
| `/Logs/[LOG_NAME].log` | [WHAT_IT_TRACKS] |

**Log Entry Format:**
```json
{
  "timestamp": "[ISO_TIMESTAMP]",
  "action": "[ACTION_NAME]",
  "details": { },
  "status": "success|failure"
}
```

---

### **STEP 7: DASHBOARD UPDATE**

**Updated By:** `[SKILL_NAME]`

**Dashboard Contains:**
- [ELEMENT_1]
- [ELEMENT_2]
- [ELEMENT_3]

**Update Trigger:**
- [WHEN_DASHBOARD_IS_UPDATED]

---

## 📋 APPROVAL THRESHOLDS

### Communications

| Type | Approval Required? | Process |
|------|-------------------|---------|
| [TYPE_1] | ✅ YES / ❌ NO | [PROCESS] |
| [TYPE_2] | ✅ YES / ❌ NO | [PROCESS] |
| [TYPE_3] | ✅ YES / ❌ NO | [PROCESS] |

### Financial

| Amount Range | Approval Required? | Process |
|--------------|-------------------|---------|
| <$[AMOUNT] | ❌ NO | [PROCESS] |
| $[X]-$[Y] | ⚠️ [ROLE] | [PROCESS] |
| >$[AMOUNT] | ✅ YES | [PROCESS] |

### Data Operations

| Operation | Approval Required? | Notes |
|-----------|-------------------|-------|
| [OPERATION_1] | ✅ YES / ❌ NO | [NOTES] |
| [OPERATION_2] | ✅ YES / ❌ NO | [NOTES] |

---

## 🤖 CLAUDE'S DECISION RULES

### Claude SHOULD:

1. ✅ [RULE_1]
2. ✅ [RULE_2]
3. ✅ [RULE_3]
4. ✅ [RULE_4]
5. ✅ [RULE_5]

### Claude should NOT:

1. ❌ [RESTRICTION_1]
2. ❌ [RESTRICTION_2]
3. ❌ [RESTRICTION_3]
4. ❌ [RESTRICTION_4]
5. ❌ [RESTRICTION_5]

---

## 📊 SKILL REFERENCE

| Skill Name | Purpose | Trigger Command |
|------------|---------|-----------------|
| `inbox_triage` | [PURPOSE] | "[COMMAND]" |
| `inbox_processor` | [PURPOSE] | "[COMMAND]" |
| `vault_manager` | [PURPOSE] | [INTERNAL] |
| `task_planner` | [PURPOSE] | "[COMMAND]" |
| `email_handler` | [PURPOSE] | "[COMMAND]" |
| `social_poster` | [PURPOSE] | "[COMMAND]" |
| `approval_workflow` | [PURPOSE] | "[COMMAND]" |
| `scheduler` | [PURPOSE] | "[COMMAND]" |

---

## 🔧 QUICK COMMANDS

### Daily Workflow
```bash
# Triage inbox
claude "[COMMAND]"

# Process tasks
claude "[COMMAND]"

# Check pending approvals
claude "[COMMAND]"

# Approve task
claude "[COMMAND]"

# Reject task
claude "[COMMAND]"
```

### Scheduled Tasks
```bash
# [TASK_NAME] ([SCHEDULE])
# [TASK_NAME] ([SCHEDULE])
```

---

## 📞 Support

### Documentation
- `business_goals.md` - [DESCRIPTION]
- `.claude/skills/*/SKILL.md` - [DESCRIPTION]

### Logs
- `/Logs/[LOG_NAME].log` - [DESCRIPTION]
- `/Logs/[LOG_NAME].log` - [DESCRIPTION]

### State Database
- `state.db` - [DESCRIPTION]
- Backups: `state_backup_[TIMESTAMP].db`

---

*This handbook is a living document. Update it as your business evolves!*

**Last Updated**: [DATE]
**Version**: [VERSION]
**Next Review**: [DATE]
