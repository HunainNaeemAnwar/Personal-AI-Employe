# AI Employee Dashboard

**Last Updated**: Auto-updated by Claude  
**Refresh**: Run `claude "Update dashboard"` to refresh

---

## 🚨 Quick Status

| Component | Status | Last Check |
|-----------|--------|------------|
| Orchestrator | ⚠️ Check | Run: `ps aux \| grep orchestrator` |
| Gmail Watcher | ⚠️ Check | Check heartbeat |
| Filesystem Watcher | ⚠️ Check | Check heartbeat |
| LinkedIn Watcher | ⚠️ Check | Check heartbeat |
| Claude Code | ✅ Ready | - |

---

## 📊 Task Summary

| Folder | Count | Action Needed |
|--------|-------|---------------|
| 📥 Inbox | [Run: `ls Inbox/*/ \| wc -l`] | Triage |
| ⚠️ Needs_Action | [Run: `ls Needs_Action/ \| wc -l`] | Process |
| 📋 Pending_Approval | [Run: `ls Pending_Approval/ \| wc -l`] | Approve/Reject |
| ✅ Approved | [Run: `ls Approved/ \| wc -l`] | Execute |
| ✨ Done (Today) | [Run: `ls Done/ \| wc -l`] | Review |
| ❌ Rejected | [Run: `ls Rejected/ \| wc -l`] | Archive |

---

## 🎯 Today's Priorities

### High Priority (Do First)
- [ ] [Check Needs_Action for HIGH priority items]

### Medium Priority (Do Today)
- [ ] [Check Needs_Action for MEDIUM priority items]

### Low Priority (Do When Convenient)
- [ ] [Check Needs_Action for LOW priority items]

---

## 📅 Scheduled Tasks

| Time | Task | Status |
|------|------|--------|
| 8:00 AM | Morning Briefing | ⏳ Scheduled |
| 12:00 PM | Inbox Triage | ⏳ Scheduled |
| 6:00 PM | End of Day Review | ⏳ Scheduled |

---

## 🔔 Pending Approvals

| Task | Type | Threshold | Age | Action |
|------|------|-----------|-----|--------|
| [Task Name] | [Email/Payment/Post] | [>$500/Client/etc] | [X days] | [Approve/Reject] |

**Quick Actions**:
```bash
# Approve
claude "approve task TASK_ID"

# Reject
claude "reject task TASK_ID --reason '...'"
```

---

## 📈 Today's Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Tasks Completed | 10 | [Count Done/] | ⚠️ |
| Response Time | <4h | [Calculate] | ⚠️ |
| Inbox Zero | Yes | [Check Inbox/] | ⚠️ |

---

## 🔥 Hot Tasks (Deadlines Today)

| Task | Deadline | Priority | Status |
|------|----------|----------|--------|
| [Task Name] | Today | High | ⏳ Pending |

---

## 📝 Recent Activity

### Last 5 Completed Tasks
1. [Task 1] - [Time]
2. [Task 2] - [Time]
3. [Task 3] - [Time]
4. [Task 4] - [Time]
5. [Task 5] - [Time]

### Last 5 Sent Emails
1. [To whom] - [Subject] - [Time]
2. [To whom] - [Subject] - [Time]
3. [To whom] - [Subject] - [Time]

---

## 🚨 Alerts & Warnings

| Time | Level | Message | Action |
|------|-------|---------|--------|
| [Time] | [Info/Warn/Error] | [Message] | [Action] |

---

## 🔗 Quick Links

- [Company Handbook](Company_Handbook.md) - Rules & policies
- [Business Goals](business_goals.md) - Objectives & targets
- [Vault Workflow Guide](VAULT_WORKFLOW_GUIDE.md) - Complete guide
- [User Profile](user_profile.md) - Your information

### Folders
- [Inbox/](Inbox/) - Raw incoming items
- [Needs_Action/](Needs_Action/) - Tasks to process
- [Pending_Approval/](Pending_Approval/) - Awaiting decision
- [Done/](Done/) - Completed tasks
- [Plans/](Plans/) - Execution plans
- [Logs/](Logs/) - System logs

---

## 🛠️ Quick Commands

```bash
# Triage inbox
claude "Triage inbox - move all files to Needs_Action"

# Process tasks
claude "Use email-triage skill to process all tasks"

# Approve pending
claude "approve task TASK_ID"

# Update this dashboard
claude "Update dashboard with current status"

# Check system health
ps aux | grep orchestrator
cat Logs/*_heartbeat.txt
```

---

## 📊 Weekly Progress

| Week | Revenue Target | Tasks Done | Goals Achieved |
|------|----------------|------------|----------------|
| W11 (Mar 9-15) | $2,500 | [Count] | [List] |
| W12 (Mar 16-22) | $2,500 | - | - |
| W13 (Mar 23-29) | $2,500 | - | - |
| W14 (Mar 30-Apr 5) | $2,500 | - | - |

**Month-to-Date**: $[Sum] / $10,000 ([X]%)

---

## 🎯 Focus for Today

**One Big Thing**: [Most important task for today]

**Supporting Tasks**:
1. [Task 2]
2. [Task 3]
3. [Task 4]

**Don't Forget**:
- [ ] Triage inbox by 12 PM
- [ ] Review pending approvals
- [ ] End of day review at 6 PM

---

*Dashboard auto-refreshes when Claude processes tasks. For manual refresh: `claude "Update dashboard"`*

**Generated**: 2026-03-13  
**Version**: 2.0
