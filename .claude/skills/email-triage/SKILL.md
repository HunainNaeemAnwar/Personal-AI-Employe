---
name: email-triage
description: Analyze incoming emails and categorize by urgency and action required. Use when processing email tasks from /Needs_Action.
---

# Email Triage

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `email-triage` skill when:**
- User says: "process emails", "process tasks", "process LinkedIn messages"
- Files are in `/Needs_Action/` folder (NOT Inbox)
- Task type is: `email`, `linkedin_message`, `file_drop`
- Need to assess priority and create action plan

**DO NOT use:** 
- `inbox-triage` (that's for Inbox → Needs_Action)
- `task-planning` (that's auto-created by this skill)
- `approval-workflow` (use only if threshold exceeded)

## Skill Selection Matrix

| Task Location | Task Type | Skill to Use |
|--------------|-----------|--------------|
| `/Inbox/*/` | Any | `inbox-triage` |
| `/Needs_Action/` | Email | `email-triage` |
| `/Needs_Action/` | LinkedIn Message | `email-triage` |
| `/Needs_Action/` | File Drop | `email-triage` |
| Complex multi-step | Any | `task-planning` (auto) |
| Needs approval | Any | `approval-workflow` |

---

## Instructions

1. **Read the email task file** from `/Needs_Action`
   - Extract sender, subject, timestamp, and email content
   - Note any metadata (Gmail message ID, priority markers)

2. **Extract key information**:
   - Sender identity and relationship (client, team member, vendor, unknown)
   - Subject line and main topic
   - Email content and context
   - Received timestamp and any deadlines mentioned

3. **Analyze for urgency indicators**:
   - **Keywords**: urgent, asap, deadline, important, critical, emergency, time-sensitive
   - **Sender importance**: Client requests, boss communications, team dependencies
   - **Time sensitivity**: Deadlines mentioned (<24 hours = high, 1-7 days = medium, >7 days = low)
   - **Financial implications**: Payment requests, invoices, contracts
   - **Blocking issues**: Tasks that block others' work

4. **Categorize priority**:
   - **High**: Urgent keywords + important sender + deadline <24 hours, OR financial matters >$100, OR blocking issues
   - **Medium**: Important but not urgent + deadline 1-7 days, OR routine client requests
   - **Low**: Informational only + no deadline + can wait, OR newsletters/updates

5. **Suggest actions**:
   - **Reply**: Draft response needed (provide template)
   - **Forward**: Needs another person's attention (specify who)
   - **Archive**: Informational only, no action needed
   - **Flag**: Requires follow-up or tracking (set reminder)
   - **Escalate**: Requires approval or human decision

6. **Create Plan.md** in `/Plans` with:
   - Priority assessment with justification
   - Suggested actions with checkboxes
   - Draft response if reply is needed
   - Timeline and deadlines
   - Approval requirements (if any)

7. **Move original task file** to `/Done` after plan is created

## Examples

### Example 1: High Priority Client Email

**Input** (`/Needs_Action/EMAIL_20260307T103000Z_invoice-request.md`):
```markdown
---
type: email
source: client@example.com
timestamp: 2026-03-07T10:30:00Z
priority: high
status: pending
subject: Invoice Request for January
---

## Email Content

**From**: John Client <client@example.com>
**Subject**: Invoice Request for January
**Received**: Wed, 7 Mar 2026 10:30:00 +0000

Hi,

Can you send me the invoice for January services? I need it by end of day for our accounting close.

Thanks,
John Client
```

**Output** (`/Plans/PLAN_EMAIL_20260307T103000Z_invoice-request.md`):
```markdown
---
objective: Respond to client invoice request
created: 2026-03-07T10:35:00Z
related_task: EMAIL_20260307T103000Z_invoice-request.md
approval_required: false
---

## Priority Assessment

**HIGH** - Client request with same-day deadline

**Justification**:
- Known client (client@example.com)
- Explicit deadline: "by end of day"
- Financial matter (invoice)
- Blocks client's accounting close

## Action Steps

- [x] Analyze email (completed)
- [ ] Generate January invoice from accounting system
- [ ] Review invoice for accuracy
- [ ] Send invoice via email to client@example.com
- [ ] Log invoice sent in accounting system
- [ ] Move task to /Done

**Timeline**: Complete within 4 hours (by 2:30 PM)

## Draft Response

Subject: Re: Invoice Request for January

Hi John,

I'll generate and send the January invoice within the next hour. You'll receive it at this email address.

The invoice will include:
- Services rendered in January 2026
- Itemized breakdown
- Payment terms and instructions

Please let me know if you need any adjustments or have questions.

Best regards

## Notes

- Client has accounting deadline today
- Invoice should be sent before 2:00 PM to allow review time
- Follow up if no confirmation received by 3:00 PM
```

### Example 2: Low Priority Newsletter

**Input** (`/Needs_Action/EMAIL_20260307T140000Z_newsletter.md`):
```markdown
---
type: email
source: newsletter@techblog.com
timestamp: 2026-03-07T14:00:00Z
priority: low
status: pending
subject: Weekly Tech Digest - March 7, 2026
---

## Email Content

**From**: Tech Blog <newsletter@techblog.com>
**Subject**: Weekly Tech Digest - March 7, 2026
**Received**: Wed, 7 Mar 2026 14:00:00 +0000

This week's top stories:
- New AI developments
- Cloud computing trends
- Security updates

[Newsletter content...]
```

**Output** (`/Plans/PLAN_EMAIL_20260307T140000Z_newsletter.md`):
```markdown
---
objective: Process newsletter email
created: 2026-03-07T14:05:00Z
related_task: EMAIL_20260307T140000Z_newsletter.md
approval_required: false
---

## Priority Assessment

**LOW** - Informational newsletter, no action required

**Justification**:
- Automated newsletter (newsletter@techblog.com)
- No specific action requested
- No deadline or urgency
- Informational content only

## Action Steps

- [x] Analyze email (completed)
- [ ] Archive email for reference
- [ ] Move task to /Done

**Timeline**: Process when convenient (no deadline)

## Recommendation

No response needed. Archive for reference. Consider unsubscribing if newsletters are not valuable.

## Notes

- Newsletter arrives weekly
- Can be processed in batch with other low-priority items
- No follow-up required
```

### Example 3: Medium Priority Team Request

**Input** (`/Needs_Action/EMAIL_20260307T093000Z_meeting-request.md`):
```markdown
---
type: email
source: teammate@company.com
timestamp: 2026-03-07T09:30:00Z
priority: medium
status: pending
subject: Quick sync on project timeline
---

## Email Content

**From**: Sarah Teammate <teammate@company.com>
**Subject**: Quick sync on project timeline
**Received**: Wed, 7 Mar 2026 09:30:00 +0000

Hi,

Can we schedule a 30-minute call this week to discuss the project timeline? I want to make sure we're aligned on deliverables.

Let me know what works for you.

Thanks,
Sarah
```

**Output** (`/Plans/PLAN_EMAIL_20260307T093000Z_meeting-request.md`):
```markdown
---
objective: Schedule meeting with teammate
created: 2026-03-07T09:35:00Z
related_task: EMAIL_20260307T093000Z_meeting-request.md
approval_required: false
---

## Priority Assessment

**MEDIUM** - Team coordination, flexible timeline

**Justification**:
- Internal team member (teammate@company.com)
- Coordination request (not urgent)
- Flexible deadline ("this week")
- Important for project alignment

## Action Steps

- [x] Analyze email (completed)
- [ ] Check calendar availability this week
- [ ] Propose 2-3 meeting time options
- [ ] Send response with proposed times
- [ ] Move task to /Done after response sent

**Timeline**: Respond within 24 hours (by tomorrow 9:30 AM)

## Draft Response

Subject: Re: Quick sync on project timeline

Hi Sarah,

Happy to sync on the project timeline. I have availability this week:

- Thursday, March 9: 2:00 PM - 4:00 PM
- Friday, March 10: 10:00 AM - 12:00 PM, 3:00 PM - 5:00 PM

Let me know which time works best for you, and I'll send a calendar invite.

Looking forward to aligning on deliverables.

Best regards

## Notes

- Team coordination is important but not urgent
- Flexible scheduling within the week
- 30-minute meeting should be sufficient
```

## Decision Tree

Use this decision tree to determine priority:

```
Is there an explicit deadline?
├─ Yes, <24 hours → HIGH
├─ Yes, 1-7 days → MEDIUM
└─ No deadline → Continue...

Is the sender a client or boss?
├─ Yes → Increase priority by one level
└─ No → Continue...

Does it contain urgent keywords?
├─ Yes → Increase priority by one level
└─ No → Continue...

Is it financial (>$100)?
├─ Yes → HIGH
└─ No → Continue...

Is it informational only?
├─ Yes → LOW
└─ No → MEDIUM (default)
```

## Best Practices

1. **Always check Company_Handbook.md** for approval thresholds and escalation rules
2. **Be conservative with HIGH priority** - reserve for truly urgent matters
3. **Provide draft responses** for all reply actions to save time
4. **Include timelines** in all plans to set expectations
5. **Flag for approval** when in doubt about financial or sensitive matters
6. **Consider sender relationship** - clients and bosses get higher priority
7. **Look for blocking issues** - tasks that block others' work are high priority
8. **Check for deadlines in email body** - not just subject line
