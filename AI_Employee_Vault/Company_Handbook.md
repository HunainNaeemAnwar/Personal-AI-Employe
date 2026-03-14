# Company Handbook

**Version**: 2.0  
**Last Updated**: 2026-03-13  
**Owner**: Hunain Naeem Anwar

---

## 👤 User Profile

**Name**: Hunain Naeem Anwar

**Technical Skills**:
- Frontend: HTML, CSS, Tailwind CSS, Next.js, TypeScript
- Backend: Python, FastAPI
- AI/LLM: Prompt Engineering, Context Engineering, OpenAI Agents SDK, Claude Code
- Automation: Building autonomous AI agents

**Education**: GIAIC (Governor's Initiative on Artificial Intelligence & Computing)

**Professional Brand**:
- AI Automation Specialist
- Full-Stack Developer with AI expertise
- Building autonomous AI agents for productivity

**Links**:
- GitHub: https://github.com/HunainNaeemAnwar
- LinkedIn: https://linkedin.com/in/hunain-naeem-anwar

---

## 📋 Rules of Engagement

### Communication Standards

**Tone**: Professional, friendly, concise

**Response Times**:
- High Priority: <4 hours
- Medium Priority: <24 hours
- Low Priority: <7 days

**Email Guidelines**:
- Always include clear subject lines
- Use proper greetings and sign-offs
- Keep messages concise but complete
- Include call-to-action when needed

**LinkedIn Guidelines**:
- Professional tone always
- Add value in every post
- Engage with comments promptly
- Share insights, not just promotions

---

## 🎯 Priority Guidelines

### High Priority (Process Immediately)

**Keywords**:
- urgent, asap, deadline, critical, emergency, time-sensitive

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

**Action**: Process within 4 hours, escalate if needed

---

### Medium Priority (Process Within 24 Hours)

**Keywords**:
- meeting, call, review, feedback, proposal

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

### Low Priority (Process When Convenient)

**Keywords**:
- newsletter, update, notification, FYI

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

## 💰 Approval Thresholds

### Financial Transactions

| Amount | Approval Required | Notes |
|--------|-------------------|-------|
| <$100 | ❌ No | Auto-approve |
| $100-$500 | ⚠️ Manager | Requires review |
| >$500 | ✅ Executive | Requires explicit approval |

**Examples**:
- Software subscriptions <$100 → Auto-approve
- Equipment purchase $300 → Manager approval
- Contractor payment $1000 → Executive approval

---

### Communications

| Type | Approval Required | Notes |
|------|-------------------|-------|
| Client emails | ✅ Yes | Draft for review before sending |
| Internal emails | ❌ No | Send directly |
| LinkedIn messages | ❌ No | Send directly (unless sensitive) |
| LinkedIn posts | ✅ Yes | Requires approval before posting |
| Partnership inquiries | ✅ Yes | Requires review |

---

### Data Operations

| Operation | Approval Required | Notes |
|-----------|-------------------|-------|
| Single record update | ❌ No | Auto-approve |
| Bulk update (>10 records) | ✅ Yes | Requires review |
| Data export | ✅ Yes | Security review needed |
| Data deletion | ✅ Yes | irreversible action |
| System config changes | ✅ Yes | Impact assessment needed |

---

## 🔄 Task Processing Workflow

### Step 1: Detection
```
Watcher detects new item → Creates file in /Inbox/<source>/
```

### Step 2: Triage
```
/Inbox/ → Claude triage → /Needs_Action/ with priority
```

### Step 3: Processing
```
/Needs_Action/ → Claude + Skill → Action taken
```

### Step 4: Approval (If Required)
```
Exceeds threshold → /Pending_Approval/ → You approve/reject
```

### Step 5: Execution
```
Approved → Execute → Log → /Done/
```

---

## 🤖 AI Employee Behavior

### Decision Making

**Claude should**:
1. Read task file completely
2. Assess priority using guidelines above
3. Determine if approval is needed
4. Draft response or action plan
5. Execute or wait for approval
6. Log result
7. Move to Done

**Claude should NOT**:
- Send client emails without approval
- Post on social media without approval
- Process payments without approval
- Delete data without approval
- Make commitments on your behalf

---

### Skill Usage

**Required Skills**:
- `inbox-triage` - Move Inbox → Needs_Action
- `email-triage` - Process emails/LinkedIn messages
- `task-planning` - Create plans for complex tasks
- `approval-workflow` - Handle approvals
- `linkedin-posting` - Create LinkedIn posts

**Skill Selection**:
```markdown
| Task Type | Skill to Use |
|-----------|--------------|
| Inbox triage | inbox-triage |
| Email reply | email-triage |
| LinkedIn message | email-triage |
| Complex task | task-planning |
| Approval needed | approval-workflow |
| LinkedIn post | linkedin-posting |
```

---

## 📊 Quality Standards

### Response Quality

**All responses should be**:
- Professional and courteous
- Clear and concise
- Action-oriented
- Free of typos/grammar errors

**Review Checklist**:
- [ ] Tone is appropriate
- [ ] Message is clear
- [ ] Call-to-action included (if needed)
- [ ] No sensitive info exposed
- [ ] Links work (if included)

---

### Task Completion

**Before moving to Done**:
- [ ] All steps completed
- [ ] Result logged
- [ ] Follow-ups scheduled (if needed)
- [ ] Plan.md updated (if used)

---

## 🔐 Security & Privacy

### Credential Management

**NEVER**:
- Store passwords in vault
- Commit .env to git
- Share API keys in task files
- Log sensitive information

**ALWAYS**:
- Use environment variables
- Store credentials in ~/.credentials/
- Rotate passwords every 90 days
- Use 2FA where available

---

### Data Handling

**Personal Data**:
- Don't process without consent
- Minimize data collection
- Secure at rest and in transit
- Delete when no longer needed

**Client Data**:
- Maintain confidentiality
- Don't share without permission
- Use secure channels
- Follow NDAs

---

## 📈 Performance Metrics

### Response Time SLAs

| Priority | Target | Maximum |
|----------|--------|---------|
| High | <2 hours | <4 hours |
| Medium | <12 hours | <24 hours |
| Low | <3 days | <7 days |

### Quality Metrics

| Metric | Target |
|--------|--------|
| Task completion rate | >95% |
| Approval accuracy | 100% |
| Duplicate prevention | 100% |
| System uptime | >99% |

---

## 🚨 Error Handling

### Watcher Failures

**If watcher crashes**:
1. Log error to /Logs/
2. Restart automatically (orchestrator handles)
3. Alert if >3 consecutive failures
4. Manual intervention if persistent

### Processing Errors

**If Claude encounters error**:
1. Log error details
2. Create clarification request
3. Move to Pending_Approval
4. Flag for manual review

---

## 📝 Customization

### Edit This Handbook When:

- Business rules change
- Approval thresholds need adjustment
- New communication channels added
- Team structure changes
- Compliance requirements update

### Review Schedule:

- **Weekly**: Check if rules are working
- **Monthly**: Update thresholds if needed
- **Quarterly**: Major review and update

---

## 📞 Support

### Documentation
- `VAULT_WORKFLOW_GUIDE.md` - Complete workflow
- `business_goals.md` - Strategic objectives
- `.claude/skills/*/SKILL.md` - Skill documentation

### Logs
- `/Logs/orchestrator.log` - System health
- `/Logs/*_watcher.log` - Watcher activity
- `/Logs/email_sent.log` - Sent emails

### State
- `state.db` - Processed items
- `Dashboard.md` - Real-time status

---

*This handbook is a living document. Update it as your business evolves!*

**Last Updated**: 2026-03-13  
**Version**: 2.0  
**Next Review**: 2026-04-13
