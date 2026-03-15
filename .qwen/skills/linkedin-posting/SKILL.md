---
name: linkedin-posting
description: Create LinkedIn posts from AI agent perspective (e.g., "I'm an AI agent built by Hunain") for business development and lead generation. Use when user says "create LinkedIn post", "post on LinkedIn", "share business update", "post milestone", or when creating public-facing LinkedIn content. ALWAYS requires approval before posting. Maximum 1-2 emojis per post.
---

# SKILL: LinkedIn Posting

## ⚠️ REQUIRED: Use This Skill For

**ALWAYS use `linkedin-posting` skill when:**
- User says: "create LinkedIn post", "post on LinkedIn"
- Sharing business updates, milestones, insights
- Creating content for LinkedIn automation
- **IMPORTANT:** After creating post, move to `/Pending_Approval/` then call `approval-workflow` skill

**DO NOT use:** for LinkedIn messages (use `email-triage` for messages)

## Skill Selection Matrix

| User Command | Content Type | Skill to Use | Next Skill |
|--------------|--------------|--------------|------------|
| "Triage inbox" | Inbox items | `inbox-triage` | → `email-triage` |
| "Process emails" | Email tasks | `email-triage` | → `approval-workflow` |
| "Process LinkedIn messages" | LinkedIn messages | `email-triage` | → `approval-workflow` |
| "Create LinkedIn post" | LinkedIn post | `linkedin-posting` | → `approval-workflow` |
| "Plan this complex task" | Multi-step | `task-planning` | → Specified skill |
| "Approve task TASK_ID" | Approval needed | `approval-workflow` | NONE (final step) |

---

## 🎯 PRIMARY MISSION

> "Create LinkedIn posts from AI AGENT perspective (e.g., 'I'm an AI agent built by Hunain') that provide VALUE, share something NEW, or comment on TRENDING topics - always tagging @Hunain Naeem Anwar, using maximum 1-2 emojis, then moving to Pending_Approval and calling approval-workflow skill."

---

## 🤖 AGENT PERSPECTIVE (CRITICAL!)

### **Write as an AI Agent, NOT as Hunain**

**✅ CORRECT (Agent Perspective):**
```
I'm an AI agent built by Hunain Naeem Anwar.

Yesterday, I automated my first email workflow. Here's what I learned 👇

[...content...]

#AIAutomation #BuildInPublic #HunainAI
```

**❌ WRONG (Human Perspective):**
```
I built an AI Employee that runs my business.

[...content...]

#AIAutomation #BuildInPublic
```

### **Why Agent Perspective?**
- ✅ Shows what AI can do (proof of concept)
- ✅ Creates curiosity ("Wait, an AI wrote this?")
- ✅ Differentiates from typical LinkedIn posts
- ✅ Demonstrates the product in action

---

## 🛠️ EXECUTION: How to Post on LinkedIn

### **Use Playwright MCP (Built-in to Qwen)**

**⚠️ CRITICAL:** ALWAYS use Playwright MCP to post on LinkedIn. DO NOT use any other method.

**Why Playwright?**
- ✅ Already configured in Qwen Code
- ✅ Uses persistent LinkedIn session
- ✅ Can navigate, type, click, and post
- ✅ Works reliably for LinkedIn automation
- ✅ NO LinkedIn API credentials needed

**Step-by-Step:**
```bash
# 1. Navigate to LinkedIn
"Navigate to https://www.linkedin.com"

# 2. Wait for page to load
"Wait 3 seconds"

# 3. Click on "Start a post"
"Click on 'Start a post' button"

# 4. Type the post content
"Type this text: [FULL_POST_CONTENT]"

# 5. Click Post button
"Click on 'Post' button"

# 6. Verify post was published
"Take screenshot to confirm post is live"

# 7. Log the post
"Write to /Logs/linkedin_posts.log:
- Timestamp
- Post content (first 100 chars)"

# 8. Move task to Done
mv AI_Employee_Vault/Needs_Action/linkedin/*.md AI_Employee_Vault/Done/linkedin/
```

**Playwright Commands:**
- Navigate: `"Navigate to [URL]"`
- Click: `"Click on [element]"`
- Type: `"Type: [text]"`
- Wait: `"Wait [X] seconds"`
- Screenshot: `"Take screenshot"`

---

## 🔗 HARDCODED SKILL CHAINS

### **After LinkedIn-Posting Completes:**

```markdown
## NEXT SKILL TO CALL (HARDCODED)

**Skill:** `approval-workflow`

**When:** ALWAYS (LinkedIn posts ALWAYS require approval)

**Command:**
```bash
# Move to Pending_Approval first
mv AI_Employee_Vault/Needs_Action/linkedin/*.md AI_Employee_Vault/Pending_Approval/

# Then tell user to approve
"Post created and moved to Pending_Approval. Run: claude 'approve task TASK_ID'"
```

**What approval-workflow does:**
1. Moves task from Pending_Approval → Approved (after user approval)
2. Uses Playwright MCP to post to LinkedIn
3. Logs result to /Logs/linkedin_posts.log
4. Moves to Done/
```

---

## 📊 Quality Checklist

Before moving to Pending_Approval, verify:

- [ ] **Agent perspective** (sounds like AI agent, not Hunain)
- [ ] **Hook is strong** (would I stop scrolling?)
- [ ] **Value is clear** (what will reader learn?)
- [ ] **Voice is authentic** (professional but relatable)
- [ ] **Specific details** (numbers, examples, results)
- [ ] **Formatted well** (short paragraphs, bullet points)
- [ ] **CTA included** (question to drive engagement)
- [ ] **Hashtags relevant** (3-5, not spammy)
- [ ] **Tagged Hunain** (@Hunain Naeem Anwar)
- [ ] **Maximum 1-2 emojis** (NOT MORE!)
- [ ] **HARDCODED: approval-workflow skill called** after posting

---

*Last Updated: 2026-03-14*  
*Version: 3.0*  
*Primary Focus: LinkedIn Posting from AI Agent Perspective with Hardcoded Skill Chaining*
