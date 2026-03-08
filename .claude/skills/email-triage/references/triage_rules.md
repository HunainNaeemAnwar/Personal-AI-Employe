# Email Triage Rules

## Urgency Keywords

### High Priority Keywords
- urgent
- asap
- deadline
- critical
- emergency
- time-sensitive
- immediate
- important
- priority

### Time-Based Indicators
- "by end of day" → HIGH
- "by tomorrow" → HIGH
- "this week" → MEDIUM
- "when you can" → LOW
- "no rush" → LOW

## Sender Priority Matrix

| Sender Type | Base Priority | Adjustment |
|-------------|---------------|------------|
| Client | MEDIUM | +1 level if deadline |
| Boss/Manager | MEDIUM | +1 level if urgent keywords |
| Team Member | MEDIUM | No adjustment |
| Vendor | LOW | +1 level if blocking |
| Newsletter | LOW | No adjustment |
| Unknown | LOW | +1 level if urgent keywords |

## Financial Thresholds

From Company_Handbook.md:

- **Under $50**: Auto-approve routine expenses → MEDIUM
- **$50-$100**: Create plan, flag for review → MEDIUM
- **Over $100**: Require explicit approval → HIGH

## Action Type Guidelines

### Reply
- Client requests → Always provide draft
- Team questions → Provide brief response
- Vendor inquiries → Standard template

### Forward
- Technical issues → Forward to IT
- Financial matters → Forward to accounting
- Legal questions → Forward to legal team

### Archive
- Newsletters → Archive immediately
- Confirmations → Archive after verification
- FYI emails → Archive after reading

### Flag for Follow-up
- Pending responses → Flag with 2-day reminder
- Waiting on others → Flag with 1-week reminder
- Long-term projects → Flag with monthly reminder

## Priority Escalation Rules

Escalate priority if:
1. Multiple urgency indicators present
2. Sender is client + deadline mentioned
3. Financial amount >$100
4. Blocks other team members' work
5. Legal or compliance implications

## De-escalation Rules

Lower priority if:
1. Informational only (no action required)
2. Automated/system-generated
3. Newsletter or marketing
4. Already handled by someone else
5. Duplicate of existing task

## Response Time Targets

| Priority | Response Time | Action Time |
|----------|---------------|-------------|
| HIGH | <2 hours | Same day |
| MEDIUM | <24 hours | Within 3 days |
| LOW | <3 days | When convenient |

## Special Cases

### Out of Office
- Sender has OOO reply → Lower priority by 1 level
- Urgent + OOO → Keep HIGH, note in plan

### Bulk/Mass Emails
- To: multiple recipients → Likely LOW priority
- CC: you → MEDIUM priority (FYI)
- BCC: you → LOW priority (informational)

### Thread Continuations
- Reply to ongoing thread → Match original priority
- New topic in thread → Reassess priority
- Long thread (>5 messages) → Consider archiving

## Keywords to Watch

### Positive Indicators (Increase Priority)
- "need your help"
- "can you"
- "please review"
- "action required"
- "decision needed"

### Negative Indicators (Decrease Priority)
- "FYI"
- "for your information"
- "no action needed"
- "just letting you know"
- "when you have time"
