---
name: social-poster
description: Create, draft, and schedule LinkedIn posts for business development and lead generation
version: 1.0.0
---

# SKILL: Social Poster

## 🎯 PRIMARY MISSION

> "Create engaging LinkedIn posts for business development, draft content with proper structure (hook, value, CTA), add relevant hashtags, and publish via LinkedIn watcher or manual posting."

---

## ⚠️ WHEN TO USE THIS SKILL

**ALWAYS use `social-poster` skill when:**
- User says: "create LinkedIn post"
- User says: "post business update"
- User says: "share milestone on LinkedIn"
- Scheduled task for weekly LinkedIn post (Monday 9 AM)
- Business milestone achieved (project completed, revenue goal, etc.)
- Need to generate leads through content marketing

**DO NOT use:**
- `inbox-processor` (that's for incoming tasks, not posting)
- `approval-workflow` (use AFTER drafting - LinkedIn posts require approval)
- `email-handler` (that's for Gmail, not LinkedIn)

---

## 📋 LINKEDIN POST STRUCTURE

### The PERFECT Post Formula

```
[HOOK]        - Grab attention in first 3 lines
[VALUE]       - Deliver insight, story, or lesson
[CONTEXT]     - Add personal experience or data
[CTA]         - Call-to-action or question
[HASHTAGS]    - 3-5 relevant hashtags
```

### Hook Examples

| Type | Example |
|------|---------|
| **Contrarian** | "Most productivity advice is worthless. Here's what actually works..." |
| **Number-driven** | "I just processed 1,000 tasks with zero manual input..." |
| **Story** | "3 months ago, I almost gave up on this project..." |
| **Question** | "What if your email inbox managed itself?" |
| **List** | "7 lessons from building an AI employee:" |

### Value Section Guidelines

- **Keep it scannable**: Short paragraphs, bullet points, white space
- **Deliver insight**: Teach something, share a lesson, provide value
- **Be specific**: Use numbers, data, concrete examples
- **Show vulnerability**: Share failures, not just successes

### CTA Examples

- "What's your experience with [topic]?"
- "Drop a comment if this resonates"
- "Share your biggest challenge below"
- "DM me if you want to learn more"

---

## 🔄 POST CREATION WORKFLOW

### Step 1: Identify the Story

**Sources for posts:**
- Completed project milestones
- System achievements (1000 tasks processed, 99% uptime)
- Lessons learned from implementation
- Before/after comparisons
- Industry insights from user's experience

### Step 2: Draft the Post

```python
# Create post file
vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
post_file = vault_path / "Needs_Action" / f"LINKEDIN_POST_{timestamp}.md"

content = f"""---
type: linkedin_post
post_content: |
  [POST CONTENT HERE]
hashtags:
  - AIAutomation
  - Productivity
  - TechInnovation
scheduled_time: {scheduled_time}
approval_status: pending
---

# LinkedIn Post Draft

## Post Content

[Full post text with line breaks]

## Hashtags

#AIAutomation #Productivity #TechInnovation

## Performance Tracking

- Views: [Track after posting]
- Likes: [Track after posting]
- Comments: [Track after posting]
- Shares: [Track after posting]
"""
```

### Step 3: Request Approval

**ALL LinkedIn posts require approval before publishing:**

```bash
# Move to Pending_Approval
mv AI_Employee_Vault/Needs_Action/LINKEDIN_POST_*.md AI_Employee_Vault/Pending_Approval/

# Notify user
"Post drafted and moved to /Pending_Approval/"
"Run: claude 'approve task TASK_ID' to publish"
```

### Step 4: Publish to LinkedIn

**After approval, publish via LinkedIn watcher:**

```python
# Use LinkedIn watcher's post_to_linkedin method
from watchers.linkedin_watcher import LinkedInWatcher

watcher = LinkedInWatcher(
    vault_path=vault_path,
    username=os.getenv("LINKEDIN_USERNAME"),
    password=os.getenv("LINKEDIN_PASSWORD")
)

success = watcher.post_to_linkedin(
    content=post_content,
    hashtags=hashtags
)

if success:
    # Log and move to Done
    log_post_published(post_id, post_url)
    move_to_done()
else:
    # Log error, retry or notify
    log_error("LinkedIn post failed")
```

---

## 📝 POST TEMPLATES

### Template 1: Milestone Announcement

```markdown
🎉 [Achievement]!

[Specific metric or accomplishment]

What I learned:
• [Lesson 1]
• [Lesson 2]
• [Lesson 3]

[Personal reflection or what's next]

[CTA - question or invitation]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Example:**

```markdown
🎉 Just hit 1,000 automated tasks with zero manual intervention!

My AI Employee system has been running 24/7 for 30 days straight:
• 99% uptime
• 50% reduction in email triage time
• Zero duplicate tasks after 10 system restarts

What I learned building autonomous systems:

1. Start small - Bronze tier first, then scale
2. Human-in-the-loop is critical for trust
3. Persistent state prevents chaos on restart

The best part? It just works. I wake up to processed emails, organized tasks, and clear priorities.

Building AI that actually delivers value (not just demos) is incredibly rewarding.

What's your biggest automation win this year?

#AIAutomation #ProductivityHacks #TechInnovation #AutonomousAgents
```

### Template 2: Lesson Learned

```markdown
[Contrarian statement or surprising insight]

[Context - why this matters]

Here's what I discovered:

[Key insight with supporting detail]

[Personal example or data]

The takeaway:

[Actionable advice]

[CTA - question for engagement]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Example:**

```markdown
Most AI agents fail because they skip the boring stuff.

Everyone wants to build autonomous AI. Nobody wants to build the infrastructure.

After processing 500+ tasks through my AI Employee, here's what actually matters:

→ Persistent state (SQLite, not just context)
→ Structured folders (Obsidian vault, not chat history)
→ Approval workflows (HITL for high-stakes actions)
→ Retry logic (because APIs WILL fail)

The unsexy truth: Great AI is 10% prompts, 90% plumbing.

Once I added state management and approval workflows, everything changed:
• 99% task completion rate
• Zero unauthorized actions
• 24/7 reliable operation

Stop chasing shiny models. Start building boring infrastructure.

Your future self (and your users) will thank you.

What's the most underrated part of your AI stack?

#AIAgents #SoftwareEngineering #Automation #BuildInPublic
```

### Template 3: Before/After

```markdown
BEFORE: [Pain point or struggle]

AFTER: [Resolution or achievement]

The journey:

[Timeline or key milestones]

Key lessons:

• [Lesson 1]
• [Lesson 2]
• [Lesson 3]

[Encouragement or insight]

[CTA]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Example:**

```markdown
BEFORE: Spending 2 hours daily on email triage

AFTER: AI processes everything while I sleep

The 90-day journey:

Day 1: "This will never work for my complex inbox"
Day 30: "Okay, it's handling 50% of my emails"
Day 60: "Why am I even checking email before coffee?"
Day 90: "I forgot what inbox zero felt like"

Key lessons from automating my digital life:

• Start with rules, add AI gradually
• Approval workflows build trust fast
• Logging everything = peace of mind

The best automation feels like magic to others and like breathing to you.

If you're on the fence about automating [X]: Start today. Future you will wonder how you lived without it.

What's the first task you'd automate if you could?

#Automation #Productivity #WorkLifeBalance #AI
```

### Template 4: Industry Insight

```markdown
[Observation about industry trend]

[Why this matters now]

[Data point or personal experience]

My prediction:

[Forward-looking statement]

[Question for engagement]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Example:**

```markdown
AI agents are where web development was in 1999.

Everyone's excited. Nobody knows the right patterns yet.

After building and running an AI Employee for 500+ hours:

The "Ralph Loop" pattern (fresh context + file-based state) outperforms:
→ Long-running agents (context pollution)
→ Chat-based workflows (no persistence)
→ Pure prompting (no structure)

My prediction:

In 2 years, every knowledge worker will have:
✓ Personal AI agent
✓ Obsidian-style knowledge base
✓ Approval workflow for important actions
✓ 24/7 autonomous operation

The question isn't IF this becomes standard.

It's WHO adopts it first.

Are you building with agents yet? What's blocking you?

#FutureOfWork #AIAgents #KnowledgeWork #Productivity
```

---

## 🎯 HASHTAG STRATEGY

### Best Practices

| Guideline | Detail |
|-----------|--------|
| **Count** | 3-5 hashtags (LinkedIn recommends 3) |
| **Relevance** | Must relate to post content |
| **Mix** | 1-2 broad + 2-3 niche |
| **Placement** | At end of post, after blank line |

### Recommended Hashtags by Category

**AI/Automation:**
```
#AIAutomation #AIAgents #MachineLearning #Automation #AutonomousAgents
```

**Productivity:**
```
#ProductivityHacks #TimeManagement #WorkSmarter #Efficiency #Productivity
```

**Business/Tech:**
```
#TechInnovation #DigitalTransformation #BusinessAutomation #SaaS #Startup
```

**Personal Brand:**
```
#BuildInPublic #Entrepreneurship #Leadership #CareerAdvice #ProfessionalGrowth
```

---

## 📊 PERFORMANCE TRACKING

### Metrics to Track

| Metric | What It Means | Good Benchmark |
|--------|---------------|----------------|
| **Views** | Reach/impressions | 500+ per post |
| **Likes** | Basic engagement | 30+ likes |
| **Comments** | Deep engagement | 5+ comments |
| **Shares** | Viral potential | 2+ shares |

### Tracking Template

```markdown
## Performance Metrics

| Metric | 24h | 7d | 30d |
|--------|-----|----|-----|
| Views | 000 | 000 | 000 |
| Likes | 00 | 00 | 00 |
| Comments | 0 | 0 | 0 |
| Shares | 0 | 0 | 0 |

Last Updated: [timestamp]
```

---

## 🚨 APPROVAL REQUIREMENTS

**ALL LinkedIn posts require approval before publishing:**

1. Draft post in `/Needs_Action/`
2. Move to `/Pending_Approval/`
3. User reviews content, tone, hashtags
4. User runs: `claude "approve task TASK_ID"`
5. Post published to LinkedIn
6. Log result, move to `/Done/`

**Why approval is required:**
- Public-facing content represents your brand
- Tone must match your voice
- Hashtags should align with strategy
- Timing may need adjustment

---

## 📈 QUALITY CHECKLIST

Before publishing LinkedIn post:

- [ ] Hook grabs attention in first 3 lines
- [ ] Value delivered (insight, lesson, or story)
- [ ] Post is scannable (short paragraphs, white space)
- [ ] CTA included (question or invitation)
- [ ] 3-5 relevant hashtags added
- [ ] Tone matches personal/professional brand
- [ ] No typos or grammar errors
- [ ] Approval obtained (moved to `/Pending_Approval/`)
- [ ] Performance tracking template ready
- [ ] Post logged to `/Logs/linkedin_posts.log`

---

## 🔗 RELATED SKILLS

- `inbox-processor` - Processes incoming LinkedIn messages
- `approval-workflow` - Handles approval for LinkedIn posts
- `vault-manager` - File operations for post files
- `task-planner` - Creates plans for content campaigns
- `scheduler` - Triggers weekly LinkedIn post tasks

---

*Last Updated: 2026-03-15*
*Version: 1.0.0*
*Primary Focus: LinkedIn Post Creation & Publishing*
