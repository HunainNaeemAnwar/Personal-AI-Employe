---
name: task-planning
description: Create structured Plan.md files for complex multi-step tasks requiring 3+ steps. Use when user says "plan this task", "create execution plan", "break down this task", or when task involves multiple systems (email + LinkedIn + files), has dependencies, or requires coordinated execution. ALWAYS specifies which skill to use for execution in the Plan.md file.
---

# SKILL: Task Planning

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `task-planning` skill when:**
- User says: "plan this task", "create execution plan"
- Task requires 3+ steps to complete
- Task involves multiple systems (email + LinkedIn + files)
- Task has dependencies or prerequisites
- **IMPORTANT:** After creating plan, MUST specify which skill to use for execution

**DO NOT use:** for simple single-step tasks (use `email-triage` directly)

## Skill Selection Matrix

| User Command | Task Complexity | Skill to Use | Next Skill |
|--------------|----------------|--------------|------------|
| "Triage inbox" | Simple | `inbox-triage` | → `email-triage` |
| "Process emails" | Simple | `email-triage` | → `approval-workflow` (if needed) |
| "Process LinkedIn messages" | Simple | `email-triage` | → `approval-workflow` (if needed) |
| "Plan this complex task" | Complex (3+ steps) | `task-planning` | → Specified in Plan.md |
| "Create LinkedIn post" | Simple | `linkedin-posting` | → `approval-workflow` |
| "Approve task TASK_ID" | Final step | `approval-workflow` | NONE |

---

## 🎯 PRIMARY MISSION

> "Create structured Plan.md files in /Plans/ folder for complex multi-step tasks, documenting objective, actions, execution steps, reasoning, and MOST IMPORTANTLY - specifying which skill to use for execution."

---

## 📝 Plan.md Template

```markdown
---
task_id: TASK_ID
created_at: 2026-03-14T10:00:00Z
status: pending
---

# Task Plan: [Task Title]

## ⚠️ Required Skill for Execution
**Use this skill:** `[skill-name]`

**Example:**
- `email-triage` - For processing emails/LinkedIn messages
- `linkedin-posting` - For creating LinkedIn posts
- `approval-workflow` - For approval/rejection decisions

## Objective
[What needs to be accomplished]

## Context
[Background information and constraints]

## Proposed Actions
1. [Action 1]
2. [Action 2]
3. [Action 3]

## Execution Steps

### Step 1: [Action 1 Detail]
- **Status**: pending
- **Description**: [What this step does]
- **Command**: [Command to run]
- **Started At**: null
- **Completed At**: null

### Step 2: [Action 2 Detail]
- **Status**: pending
- **Description**: [What this step does]
- **Command**: [Command to run]
- **Started At**: null
- **Completed At**: null

## Reasoning Notes
[Document decision rationale and alternatives considered]

## Alternative Approaches
### Alternative 1: [Title]
**Description**: [What this alternative would do]
**Pros**: [Advantages]
**Cons**: [Disadvantages]
**Rejected Because**: [Why not chosen]
```

---

## 🔗 HARDCODED SKILL CHAINS

### **After Task-Planning Completes:**

```markdown
## NEXT SKILL TO CALL (SPECIFIED IN PLAN.md)

**Skill:** [Specified in Plan.md "Required Skill for Execution" section]

**Command:**
```bash
claude "Use [skill-name] to execute plan PLAN_TASK_ID"
```

**What happens:**
1. User reviews Plan.md
2. User runs command to execute plan with specified skill
3. Specified skill executes the plan
4. If approval needed → Calls `approval-workflow`
5. Workflow continues based on specified skill
```

---

## 📊 Quality Checklist

Before completing plan creation, verify:

- [ ] **Required Skill specified** (MOST IMPORTANT!)
- [ ] Objective is clear and actionable
- [ ] Context provides necessary background
- [ ] Proposed actions are in logical order
- [ ] Execution steps have checkboxes for tracking
- [ ] Reasoning notes document decisions
- [ ] Alternative approaches considered
- [ ] Plan.md saved to /Plans/ folder
- [ ] User instructed on how to execute plan

---

## 📈 Performance Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Plan Completeness | 100% | All sections filled |
| Skill Specified | 100% | Required Skill section present |
| Plan Execution Rate | >80% | Plans that get executed |
| User Satisfaction | >90% | User confirms plan is helpful |

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: Complex Task Planning with Hardcoded Skill Specification*
