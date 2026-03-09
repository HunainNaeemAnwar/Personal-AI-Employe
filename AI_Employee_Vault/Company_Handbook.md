# Company Handbook

**Version**: 1.0
**Last Updated**: 2026-03-09

---

## Rules of Engagement

### Communication Standards
- Always maintain professional tone in all communications
- Respond to urgent requests within 4 hours
- Use clear, concise language
- Include relevant context in responses

### Priority Guidelines

**High Priority** (process immediately):
- Keywords: urgent, asap, deadline, critical, emergency
- Client requests with same-day deadlines
- Financial matters (invoices, payments)
- Legal documents requiring signature

**Medium Priority** (process within 24 hours):
- Regular client communications
- Internal team requests
- Document reviews
- Routine administrative tasks

**Low Priority** (process when convenient):
- Newsletters and informational emails
- Non-urgent updates
- General inquiries
- Archive/reference materials

---

## Approval Thresholds

### Financial Transactions
- **< $100**: No approval required
- **$100 - $500**: Manager approval required
- **> $500**: Executive approval required

### Communications
- **Client emails**: Draft for review, send after approval
- **Internal emails**: Send directly
- **External partnerships**: Require approval
- **Social media posts**: Require approval

### Data Operations
- **Single record updates**: No approval required
- **Bulk operations (>10 records)**: Require approval
- **Data exports**: Require approval
- **System configuration changes**: Require approval

---

## Task Processing Workflow

1. **Detection**: Watcher creates task file in `/Needs_Action`
2. **Triage**: Claude analyzes priority and urgency
3. **Planning**: Execution plan created in `/Plans`
4. **Approval Check**: If threshold met, move to `/Pending_Approval`
5. **Execution**: Perform actions (manual in Bronze tier)
6. **Completion**: Move task to `/Done`

---

## Security & Privacy

### Sensitive Information
- Never commit credentials to git
- Store API keys in `.env` file only
- Rotate credentials every 90 days
- Use restrictive file permissions (600) for credentials

### Data Handling
- Personal data: Handle according to privacy policy
- Financial data: Encrypt at rest
- Client data: Maintain confidentiality
- Logs: Retain for 90 days, then archive

---

## Error Handling

### Watcher Failures
- Log error to `/Logs` folder
- Continue monitoring (don't crash)
- Retry with exponential backoff
- Alert if persistent failures

### Claude Processing Errors
- Create clarification request in `/Pending_Approval`
- Include error details in task notes
- Flag for manual review

---

## Customization

Edit this handbook to match your specific:
- Business rules and policies
- Approval workflows
- Priority definitions
- Communication standards

---

## Support

- **Documentation**: See `/docs` folder
- **Issues**: Report on GitHub
- **Logs**: Check `/Logs` for debugging
