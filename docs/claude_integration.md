# Claude Code Integration Guide

**Feature**: Bronze Tier - Personal AI Employee
**Purpose**: Instructions for using Claude Code to process tasks in the Obsidian vault

## Overview

Claude Code is the AI reasoning engine that processes tasks detected by Watchers. This guide explains how to use Claude Code to read tasks from `/Needs_Action`, create execution plans, and manage the task lifecycle.

## Prerequisites

- Obsidian vault created and configured
- At least one Watcher running (Gmail or File System)
- Claude Code CLI installed and authenticated
- Task files present in `/Needs_Action` folder

## Basic Workflow

### 1. Navigate to Vault

```bash
cd ~/AI_Employee_Vault  # Or your vault path
```

### 2. Process Tasks

Run Claude Code with a prompt to process tasks:

```bash
claude "Process all tasks in /Needs_Action"
```

### 3. Review Results

Check the following folders:
- `/Plans/` - Execution plans created by Claude
- `/Done/` - Completed tasks
- `/Pending_Approval/` - Tasks requiring human approval

## Common Prompts

### Process All Tasks

```bash
claude "Process all tasks in /Needs_Action. For each task, create a plan in /Plans and move the task to /Done."
```

### Process Specific Task

```bash
claude "Process the task EMAIL_20260307T103000Z_invoice-request.md in /Needs_Action. Create a detailed plan with action steps."
```

### Prioritize Tasks

```bash
claude "Review all tasks in /Needs_Action and prioritize them by urgency. Create plans for high-priority tasks first."
```

### Triage Emails

```bash
claude "Use the email-triage skill to analyze all email tasks in /Needs_Action. Categorize by priority and suggest actions."
```

### Create Summary

```bash
claude "Create a summary of all tasks in /Needs_Action and /Plans. Update Dashboard.md with current status."
```

### Review Pending Approvals

```bash
claude "Review all items in /Pending_Approval and provide recommendations for approval or rejection."
```

## Task Processing Pattern

Claude Code follows this pattern when processing tasks:

1. **Read Task**: Load task file from `/Needs_Action`
2. **Analyze Content**: Extract key information and context
3. **Determine Actions**: Identify required steps
4. **Create Plan**: Write execution plan to `/Plans`
5. **Move Task**: Move original task to `/Done`

## Plan File Structure

Plans created by Claude follow this structure:

```markdown
---
objective: What needs to be accomplished
created: 2026-03-07T10:35:00Z
related_task: EMAIL_20260307T103000Z_invoice-request.md
approval_required: false
---

## Priority Assessment
**HIGH** - Client request with same-day deadline

## Action Steps
- [x] Analyze email (completed)
- [ ] Generate January invoice
- [ ] Send invoice via email
- [ ] Log in accounting system
- [ ] Move task to /Done

## Draft Response
[If applicable, draft email or message]

## Notes
[Additional context or considerations]
```

## Agent Skills

Claude Code automatically applies Agent Skills when relevant. The Bronze tier includes:

### Email Triage Skill

Automatically invoked for email tasks. Provides:
- Priority assessment (high/medium/low)
- Urgency analysis
- Suggested actions (reply/forward/archive/flag)
- Draft responses when appropriate

**Trigger**: Any task with `type: email` in frontmatter

**Example**:
```bash
claude "Process email tasks using the email-triage skill"
```

## Advanced Usage

### Batch Processing

Process multiple tasks in one command:

```bash
claude "Process all high-priority tasks in /Needs_Action. Create plans for each and move to /Done."
```

### Conditional Processing

Apply rules based on task attributes:

```bash
claude "For email tasks from clients, create detailed plans with draft responses. For internal emails, create simple action lists."
```

### Integration with Company Handbook

Reference your policies:

```bash
claude "Process tasks according to the rules in Company_Handbook.md. Flag any that require approval per the thresholds."
```

### Update Dashboard

Keep your dashboard current:

```bash
claude "Update Dashboard.md with: 1) Count of tasks in each folder, 2) Summary of recent activity, 3) System status"
```

## Task Lifecycle

```
Watcher Detects → /Needs_Action
                      ↓
              Claude Processes
                      ↓
              Creates Plan → /Plans
                      ↓
         Requires Approval? → /Pending_Approval
                      ↓
              Task Complete → /Done
```

## Error Handling

If Claude encounters issues:

1. **Malformed Task Files**: Claude will report validation errors
2. **Missing Information**: Claude will create clarification requests in `/Pending_Approval`
3. **Unclear Instructions**: Claude will ask for guidance

## Best Practices

### 1. Regular Processing

Process tasks at regular intervals:
```bash
# Morning routine
claude "Process all overnight tasks in /Needs_Action"

# Midday check
claude "Process new tasks and update Dashboard.md"

# Evening summary
claude "Create end-of-day summary and archive completed tasks"
```

### 2. Use Specific Prompts

Be specific about what you want:
- ✅ "Create a plan for the invoice request email with draft response"
- ❌ "Do something with the email"

### 3. Leverage Skills

Explicitly invoke skills when needed:
```bash
claude "Use email-triage skill to analyze all email tasks"
```

### 4. Review Plans Before Execution

Always review plans in `/Plans` before taking action, especially for:
- Financial transactions
- External communications
- Bulk operations

### 5. Keep Vault Organized

Regularly archive completed tasks:
```bash
# Move old tasks to archive
mv ~/AI_Employee_Vault/Done/* ~/AI_Employee_Vault/Archive/$(date +%Y-%m)/
```

## Troubleshooting

### Claude Can't Find Vault

**Problem**: Claude reports it can't access the vault

**Solution**:
```bash
# Ensure you're in the vault directory
cd ~/AI_Employee_Vault
pwd  # Should show vault path

# Try with absolute path
cd /full/path/to/AI_Employee_Vault
claude "Process tasks"
```

### Tasks Not Being Processed

**Problem**: Claude doesn't process tasks as expected

**Solution**:
1. Check task file format: `cat /Needs_Action/TASK_FILE.md`
2. Verify YAML frontmatter is valid
3. Ensure required fields are present (type, source, timestamp, priority, status)

### Plans Not Created

**Problem**: No plans appear in `/Plans` folder

**Solution**:
1. Check folder exists: `ls -la /Plans`
2. Verify Claude has write permissions
3. Try explicit instruction: `claude "Create a plan in /Plans for task X"`

## Next Steps

After mastering basic Claude integration:

1. **Silver Tier**: Add MCP servers for automated actions (email sending, etc.)
2. **Gold Tier**: Implement Ralph Wiggum loop for autonomous multi-step execution
3. **Platinum Tier**: Deploy to cloud for 24/7 operation

## Support

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: Report bugs on GitHub Issues
- **Specifications**: See `/specs/001-bronze-tier/` for complete design documents
