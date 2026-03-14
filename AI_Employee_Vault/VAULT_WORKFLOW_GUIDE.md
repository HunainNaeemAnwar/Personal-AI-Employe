# AI Employee Vault - Complete Workflow Guide

**Version**: 1.0.0  
**Last Updated**: 2026-03-13  
**Status**: Production Ready

---

## 🎯 Overview

The AI Employee Vault is your autonomous assistant's brain, memory, and workspace. It operates 24/7 using **watchers** to monitor external sources and **Claude Code** to process tasks with human oversight.

---

## 📁 Vault Structure

```
AI_Employee_Vault/
├── 📥 Inbox/                    # NEW: Raw incoming items (auto-created by watchers)
│   ├── gmail/                   # Gmail emails
│   ├── filesystem/              # File drops
│   └── linkedin/                # LinkedIn messages
│
├── ⚠️ Needs_Action/             # Tasks requiring attention (triaged from Inbox)
├── 📋 Pending_Approval/         # Awaiting human approval
├── ✅ Approved/                 # Approved, ready for execution
├── ❌ Rejected/                 # Declined tasks
├── ✨ Done/                     # Completed tasks archive
├── 📝 Plans/                    # Execution plans for complex tasks
├── 📊 Briefings/                # Daily/weekly summaries
├── 📧 Summaries/                # Email digests
├── 🔍 Reviews/                  # Task reviews
├── 📈 Reports/                  # Monthly analytics
├── 📜 Logs/                     # System logs
│
├── 📘 Company_Handbook.md       # Business rules & policies
├── 🎯 business_goals.md         # Strategic objectives
├── 👤 user_profile.md           # Your information
└── 📊 Dashboard.md              # Real-time status (auto-updated)
```

---

## 🔄 Complete Workflow

### Phase 1: Detection (Automated)

```
External Event → Watcher Detects → Creates File in /Inbox/<source>/
```

**Watchers** (run 24/7 via orchestrator):

| Watcher | Polls Every | Creates Files In | Example Filename |
|---------|-------------|------------------|------------------|
| Gmail | 60s | `/Inbox/gmail/` | `EMAIL_project-meeting.md` |
| Filesystem | 5s | `/Inbox/filesystem/` | `FILE_DROP_contract-pdf.md` |
| LinkedIn | 300s | `/Inbox/linkedin/` | `LINKEDIN_MSG_john-doe.md` |

**File Naming Convention**:
- **Emails**: `EMAIL_<subject-slug>.md`
- **Files**: `FILE_DROP_<filename-slug>.md`
- **LinkedIn**: `LINKEDIN_MSG_<sender-slug>.md`

---

### Phase 2: Triage (Automated + Manual)

```
/Inbox/<source>/ → Claude Triage → /Needs_Action/
```

**Command**:
```bash
claude "Triage inbox - move all files to Needs_Action with priority"
```

**What Happens**:
1. Claude reads all files in `/Inbox/*/`
2. Assesses priority (High/Medium/Low)
3. Adds triage metadata
4. Moves to `/Needs_Action/`

**Triage Rules** (from `Company_Handbook.md`):

| Priority | Criteria | Response Time |
|----------|----------|---------------|
| **High** | Urgent keywords, client deadlines, financial >$500 | <4 hours |
| **Medium** | Regular communications, important files | <24 hours |
| **Low** | FYI, newsletters, automated notifications | <7 days |

---

### Phase 3: Processing (Claude + Skills)

```
/Needs_Action/ → Claude + Skill → Action Taken
```

**Skill Selection Matrix**:

| Task Type | Location | Skill to Use |
|-----------|----------|--------------|
| Email reply | `/Needs_Action/` | `email-triage` |
| LinkedIn message | `/Needs_Action/` | `email-triage` |
| File processing | `/Needs_Action/` | `email-triage` |
| Complex multi-step | `/Needs_Action/` | `task-planning` → specified skill |
| Approval needed | `/Needs_Action/` | `approval-workflow` |
| LinkedIn post | N/A | `linkedin-posting` |

**Example Commands**:
```bash
# Process emails/LinkedIn messages
claude "Use email-triage skill to process all tasks in Needs_Action"

# Process specific task
claude "Use email-triage skill to process LINKEDIN_MSG_john-doe.md"

# Create plan for complex task
claude "Use task-planning skill to create plan for TASK_ID"
```

---

### Phase 4: Execution (Depends on Task)

#### Simple Tasks (1-2 steps):
```
Read → Draft Response → Execute → Move to /Done/
```

**Example - Email Reply**:
```bash
# 1. Claude drafts response
# 2. For Gmail: Uses Email MCP server to send
# 3. For LinkedIn: Uses Playwright MCP to send
# 4. Logs to /Logs/email_sent.log
# 5. Moves to /Done/
```

#### Complex Tasks (3+ steps):
```
Read → Create Plan.md → Execute Steps → Move to /Done/
```

**Plan.md Format**:
```markdown
---
task_id: TASK_ID
created_at: 2026-03-13T10:00:00Z
status: pending
---

# Task Plan: Task Title

## ⚠️ Required Skill for Execution
**Use this skill:** `email-triage`

## Task Analysis
**Objective**: What needs to be done
**Context**: Background information
**Constraints**: Limitations

## Proposed Actions
1. Action 1
2. Action 2
3. Action 3

## Execution Steps
### Step 1: Description
- **Status**: pending/in_progress/completed
- **Command**: What to run
- **Started At**: timestamp
- **Completed At**: timestamp

## Reasoning Notes
Why this approach was chosen

## Alternative Approaches
Other options considered and rejected
```

---

### Phase 5: Approval (If Required)

**Approval Thresholds** (from `Company_Handbook.md`):

| Action Type | Threshold | Approval Required |
|-------------|-----------|-------------------|
| Financial | >$500 | ✅ Yes |
| Client Communications | Any | ✅ Yes |
| Social Media Posts | Any | ✅ Yes |
| Bulk Operations | >10 items | ✅ Yes |
| Data Deletions | Any | ✅ Yes |

**Approval Workflow**:
```
/Needs_Action/ → Exceeds Threshold → /Pending_Approval/ → You Decide
```

**Commands**:
```bash
# Approve task
claude "approve task TASK_ID"

# Reject task
claude "reject task TASK_ID --reason 'Not priority right now'"
```

**After Approval**:
- ✅ Approved → `/Approved/` → Execute → `/Done/`
- ❌ Rejected → `/Rejected/` → Archive

---

### Phase 6: Completion

```
Task Executed → Log Result → Move to /Done/
```

**What Gets Logged**:
- Email sent → `/Logs/email_sent.log`
- LinkedIn message sent → `/Logs/linkedin_sent.log`
- File processed → `/Logs/file_processing.log`
- Task completed → Task file updated with completion timestamp

**Done Folder Structure**:
```
Done/
├── gmail/
├── filesystem/
├── linkedin/
└── ...
```

---

## 🤖 Claude's Reasoning Process

### Step 1: Read Task File
```markdown
1. Extract metadata (type, priority, timestamp)
2. Read content (email body, message, file details)
3. Identify sender/creator
4. Check for deadlines/urgency
```

### Step 2: Assess Priority
```markdown
1. Check for urgent keywords (urgent, asap, deadline)
2. Evaluate sender importance (client, team, unknown)
3. Check financial implications
4. Determine if blocking others
5. Assign: High/Medium/Low
```

### Step 3: Determine Action Type
```markdown
1. Is response needed? → Draft reply
2. Is file processing needed? → Extract/analyze
3. Is approval needed? → Move to Pending_Approval
4. Is it FYI only? → Move to Done
```

### Step 4: Execute or Plan
```markdown
Simple (1-2 steps):
  → Execute immediately
  → Log result
  → Move to Done

Complex (3+ steps):
  → Create Plan.md
  → Document reasoning
  → Specify skill for execution
  → Execute step-by-step
  → Update plan status
  → Move to Done
```

### Step 5: Document Decision
```markdown
Always document:
- Why this priority was assigned
- Why this action was chosen
- Alternative approaches considered
- Trade-offs evaluated
```

---

## 📋 Daily Workflow

### Morning Routine (10 minutes)

```bash
# 1. Check Dashboard
cat AI_Employee_Vault/Dashboard.md

# 2. Read Morning Briefing
cat AI_Employee_Vault/Briefings/morning_2026-03-13.md

# 3. Triage Inbox
claude "Triage inbox - move all files to Needs_Action with priority"

# 4. Check Pending Approvals
ls AI_Employee_Vault/Pending_Approval/

# 5. Approve/Reject
claude "approve task TASK_ID"
```

### During Day (As Needed)

```bash
# Process accumulated tasks
claude "Use email-triage skill to process all tasks in Needs_Action"

# Check status
ls AI_Employee_Vault/Needs_Action/
ls AI_Employee_Vault/Done/

# Drop file for processing
cp document.pdf AI_Employee_Dropbox/
```

### Evening Routine (5 minutes)

```bash
# 1. Check what was completed
ls -lt AI_Employee_Vault/Done/ | head -10

# 2. Review Dashboard
cat AI_Employee_Vault/Dashboard.md

# 3. Note pending items for tomorrow
```

### Weekly Review (30 minutes, Friday)

```bash
# 1. Read Weekly Report
cat AI_Employee_Vault/Reports/weekly_2026-W11.md

# 2. Review completed tasks
ls AI_Employee_Vault/Done/

# 3. Clear old tasks
# Archive or delete tasks older than 30 days

# 4. Update business goals
nano AI_Employee_Vault/business_goals.md
```

---

## 🛠️ Commands Reference

### Start System
```bash
# Start all watchers
python -m watchers.orchestrator

# Start specific watcher
python -m watchers.gmail_watcher
python -m watchers.filesystem_watcher
python -m watchers.linkedin_watcher

# Check if running
ps aux | grep orchestrator
```

### Triage & Processing
```bash
# Triage inbox
claude "Triage inbox - move all files to Needs_Action"

# Process tasks with specific skill
claude "Use email-triage skill to process all tasks"
claude "Use task-planning skill for complex tasks"
claude "Use approval-workflow for pending approvals"

# Process specific task
claude "Process LINKEDIN_MSG_john-doe.md"
```

### Approval Workflow
```bash
# List pending approvals
ls AI_Employee_Vault/Pending_Approval/

# Approve
claude "approve task TASK_ID"

# Reject
claude "reject task TASK_ID --reason 'Not priority'"
```

### Status Checks
```bash
# Check inbox
ls AI_Employee_Vault/Inbox/*/

# Check needs action
ls AI_Employee_Vault/Needs_Action/

# Check completed
ls -lt AI_Employee_Vault/Done/ | head -20

# Check logs
tail -50 AI_Employee_Vault/Logs/orchestrator.log
cat AI_Employee_Vault/Logs/*_heartbeat.txt
```

---

## 🔧 Configuration

### Company_Handbook.md

Edit to customize:
- **Approval Thresholds** ($ amounts, action types)
- **Priority Rules** (keywords, sender types)
- **Response Time SLAs**
- **Communication Standards**

### business_goals.md

Update quarterly:
- **Revenue Targets**
- **Active Projects**
- **Key Metrics**
- **Subscription List** (for audit)

### user_profile.md

Keep updated:
- **Your Skills**
- **Contact Info**
- **Professional Brand**
- **Links** (GitHub, LinkedIn)

---

## 📊 Monitoring & Health

### Watcher Health
```bash
# Check heartbeats (should be <120s old)
cat AI_Employee_Vault/Logs/*_heartbeat.txt

# Check orchestrator log
tail -100 AI_Employee_Vault/Logs/orchestrator.log

# Check for errors
grep -i error AI_Employee_Vault/Logs/*.log
```

### State Database
```bash
# Check processed items
python -c "
import sqlite3
conn = sqlite3.connect('AI_Employee_Vault/state.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM processed_items')
print(f'Processed items: {cursor.fetchone()[0]}')
conn.close()
"
```

### Performance Metrics
```bash
# File detection time (should be <5s)
# Email detection time (should be <2min)
# LinkedIn polling (should be 5min intervals)

# Check logs for timing
grep "Created task file" AI_Employee_Vault/Logs/*.log
```

---

## 🚨 Troubleshooting

### Tasks Not Being Created
```bash
# 1. Check if watchers are running
ps aux | grep watcher

# 2. Check heartbeats
cat AI_Employee_Vault/Logs/*_heartbeat.txt

# 3. Check watcher logs
tail -50 AI_Employee_Vault/Logs/gmail_watcher.log

# 4. Restart orchestrator
pkill -f orchestrator
python -m watchers.orchestrator
```

### Duplicate Tasks Appearing
```bash
# 1. Check state database
python -c "
import sqlite3
conn = sqlite3.connect('AI_Employee_Vault/state.db')
cursor = conn.cursor()
cursor.execute('SELECT source, source_id, COUNT(*) FROM processed_items GROUP BY source, source_id HAVING COUNT(*) > 1')
print(cursor.fetchall())
conn.close()
"

# 2. If duplicates exist, clear state
python -c "import sqlite3; conn = sqlite3.connect('AI_Employee_Vault/state.db'); conn.execute('DELETE FROM processed_items'); conn.commit(); conn.close()"

# 3. Restart watchers
```

### Claude Not Processing Correctly
```bash
# 1. Check skill files exist
ls .claude/skills/*/SKILL.md

# 2. Verify skill is being used
# Claude should say: "Using email-triage skill"

# 3. Re-read skill documentation
cat .claude/skills/email-triage/SKILL.md
```

### Gmail Watcher Crashing
```bash
# Usually OAuth credentials issue
# 1. Check credentials exist
ls -la ~/.credentials/gmail-*.json

# 2. Re-authenticate
python -c "from watchers.gmail_watcher import GmailWatcher; GmailWatcher(...)"

# 3. Or disable Gmail in .env
# ORCHESTRATOR_WATCHERS=filesystem,linkedin
```

---

## 📈 Metrics & KPIs

### Daily Metrics (Track in Briefings)
- Tasks processed
- Emails sent
- Response time (avg)
- Approval decisions

### Weekly Metrics (Track in Reports)
- Task completion rate
- Priority distribution
- Time to triage
- Time to complete

### Monthly Metrics (Track in Reports)
- Total tasks processed
- Revenue impact
- System uptime
- Error rate

---

## 🎓 Best Practices

### 1. Keep Inbox Zero
- Triage daily
- Don't let files accumulate in `/Inbox/`

### 2. Use Skills Correctly
- Always specify which skill to use
- Follow skill workflows exactly
- Don't skip steps

### 3. Document Decisions
- Always add reasoning notes
- Explain why priority was assigned
- Document alternative approaches

### 4. Review Regularly
- Morning briefings (daily)
- Weekly reports (Friday)
- Monthly reviews (end of month)

### 5. Keep Handbook Updated
- Update thresholds as business grows
- Add new priority rules
- Document edge cases

---

## 🔐 Security

### Secrets Management
- Never commit `.env` to git
- Store credentials in `~/.credentials/`
- Rotate passwords every 90 days

### Data Privacy
- Don't process personal data without consent
- Encrypt sensitive files
- Follow GDPR/privacy policies

### Access Control
- Only you can approve high-value tasks
- Review logs weekly
- Monitor for unusual activity

---

## 📞 Support

### Documentation
- This guide (`VAULT_WORKFLOW_GUIDE.md`)
- `Company_Handbook.md` - Business rules
- `.claude/skills/*/SKILL.md` - Skill documentation

### Logs
- `/Logs/orchestrator.log` - Main process
- `/Logs/*_watcher.log` - Individual watchers
- `/Logs/email_sent.log` - Sent emails
- `/Logs/linkedin_sent.log` - Sent LinkedIn messages

### State Database
- `state.db` - Processed items tracking
- Backup: `state_backup_YYYYMMDD_HHMMSS.db`

---

*Last Updated: 2026-03-13*  
*Version: 1.0.0*  
*Status: Production Ready*
