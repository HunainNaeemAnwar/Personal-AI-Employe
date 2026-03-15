# 🤖 Personal AI Employee - Silver Tier

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)

> **Your 24/7 Autonomous AI Assistant** - Monitors emails, files, and LinkedIn messages. Processes tasks automatically. Sends emails and posts to LinkedIn. All while you sleep.

---

## 📋 Table of Contents

- [Overview](#overview)
- [What You Get](#-what-you-get)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Agent Skills](#-agent-skills)
- [Documentation](#-documentation)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🎯 Overview

**Personal AI Employee** is an autonomous AI agent that manages your personal and business affairs 24/7. Built on top of Claude Code, it transforms your AI from a reactive chatbot into a proactive employee.

### **Silver Tier Features:**

| Feature | Description | Status |
|---------|-------------|--------|
| **Triple Watcher System** | Gmail, File System, LinkedIn monitoring | ✅ Complete |
| **Email Sending** | MCP server for Gmail API with threading | ✅ Complete |
| **LinkedIn Automation** | Message monitoring + post publishing | ✅ Complete |
| **State Persistence** | SQLite database prevents duplicates | ✅ Complete |
| **Approval Workflow** | Human-in-the-loop for sensitive actions | ✅ Complete |
| **Task Planning** | Structured Plan.md files | ✅ Complete |
| **Scheduled Tasks** | 7 automated cron jobs | ✅ Complete |
| **8 Agent Skills** | Reusable AI capabilities | ✅ Complete |

---

## 🎁 What You Get

### **1. Triple Watcher System**

```
┌─────────────────────────────────────────────────────────────┐
│                     WATCHERS (24/7)                         │
├─────────────────────────────────────────────────────────────┤
│  Gmail Watcher      → Monitors inbox every 60 seconds       │
│  File System Watcher → Monitors folder every 5 seconds      │
│  LinkedIn Watcher   → Monitors messages every 5 minutes     │
└─────────────────────────────────────────────────────────────┘
```

**What it does:**
- Detects new emails, file drops, and LinkedIn messages
- Creates task files automatically in your Obsidian vault
- Prevents duplicates with SQLite state tracking
- Self-healing with orchestrator (auto-restart on crash)

---

### **2. Email Automation**

```
┌─────────────────────────────────────────────────────────────┐
│                  EMAIL AUTOMATION                           │
├─────────────────────────────────────────────────────────────┤
│  1. Gmail Watcher detects email → Creates task file         │
│  2. Claude reads task → Drafts response                     │
│  3. Approval workflow (if client email)                     │
│  4. MCP server sends email via Gmail API                    │
│  5. Logged to /Logs/email_sent.log                          │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Email threading support (In-Reply-To headers)
- Retry logic (3 attempts with exponential backoff)
- CC/BCC support
- Attachment support

---

### **3. LinkedIn Automation**

```
┌─────────────────────────────────────────────────────────────┐
│                LINKEDIN AUTOMATION                          │
├─────────────────────────────────────────────────────────────┤
│  INBOUND:                                                   │
│  - Monitor messages every 5 minutes                         │
│  - Create task files for new messages                       │
│  - Auto-mark as read after processing                       │
│                                                             │
│  OUTBOUND:                                                  │
│  - Create business update posts                             │
│  - Draft with hook + value + CTA structure                  │
│  - Approval workflow before publishing                      │
│  - Track performance metrics (views, likes, comments)       │
└─────────────────────────────────────────────────────────────┘
```

---

### **4. Approval Workflow (HITL)**

```
┌─────────────────────────────────────────────────────────────┐
│              APPROVAL WORKFLOW                              │
├─────────────────────────────────────────────────────────────┤
│  High-Stakes Tasks → /Pending_Approval/                     │
│                                                             │
│  You run:                                                   │
│  claude "approve task TASK_ID"  → Executes                  │
│  claude "reject task TASK_ID"   → Discards with reason      │
│                                                             │
│  Thresholds (customizable):                                 │
│  - Client emails → Requires approval                        │
│  - Payments >$500 → Requires approval                       │
│  - LinkedIn posts → Requires approval                       │
└─────────────────────────────────────────────────────────────┘
```

---

### **5. Scheduled Tasks (Cron Jobs)**

| Task | Schedule | Purpose |
|------|----------|---------|
| **Morning Briefing** | Daily 8:00 AM | Overnight activity summary |
| **Weekly LinkedIn Post** | Monday 9:00 AM | Business update draft |
| **Daily Email Summary** | Daily 6:00 PM | End-of-day email recap |
| **Weekly Task Review** | Friday 5:00 PM | Task completion report |
| **Database Backup** | Daily 2:00 AM | State.db backup |
| **System Health Check** | Every 6 hours | Watcher + DB health |
| **Monthly Report** | 1st of month 9:00 AM | Monthly activity report |

---

## 🔄 How It Works

### **Complete Workflow:**

```
┌─────────────┐
│   WATCHERS  │
│  (Detect)   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ /Inbox/     │
│ (Temporary) │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ inbox_triage│
│ (Move)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ /Needs_Action/ │
│ (Ready)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ inbox_      │
│ processor   │
│ (Prioritize)│
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
       ▼              ▼              ▼
┌──────────┐  ┌──────────────┐  ┌──────────────┐
│ Simple   │  │ Complex      │  │ Needs        │
│ Task     │  │ Multi-Step   │  │ Approval     │
│          │  │              │  │              │
│ Execute  │  │ task_planner │  │ approval_    │
│ Directly │  │ → Plan.md    │  │ workflow     │
└────┬─────┘  └──────┬───────┘  └──────┬───────┘
     │               │                  │
     │               ▼                  ▼
     │         Execute Steps      You Approve
     │               │                  │
     └──────────────┼──────────────────┘
                    │
                    ▼
             ┌─────────────┐
             │ Log Result  │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ Move to     │
             │ /Done/      │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │ Update      │
             │ Dashboard   │
             └─────────────┘
```

---

## 🚀 Quick Start

### **Prerequisites:**

- Python 3.13+
- Obsidian v1.10.6+
- Claude Code CLI
- Google Cloud project (for Gmail API)
- LinkedIn account credentials

### **Step 1: Clone & Install**

```bash
# Clone repository
git clone https://github.com/HunainNaeemAnwar/Personal-AI-Employe.git
cd personal-ai-employee

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### **Step 2: Configure MCP Servers**

#### **A. Playwright MCP (For LinkedIn Automation)**

```bash
# Add Playwright MCP via Qwen
qwen mcp add playwright npx "@playwright/mcp@latest"
```

**Output:**
```
MCP server "playwright" is already configured within user settings.
MCP server "playwright" updated in user settings.
```

This enables:
- ✅ LinkedIn message sending
- ✅ Browser automation
- ✅ Screenshot capabilities
- ✅ Web interaction for tasks

#### **B. Email MCP (For Gmail Sending)**

```bash
# Add to ~/.config/claude-code/mcp.json:
{
  "mcpServers": {
    "email-sender": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/personal-ai-employee/mcp_servers/email_sender/server.py"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/home/user/.credentials/gmail-credentials.json",
        "GMAIL_TOKEN_PATH": "/home/user/.credentials/gmail-token.json"
      }
    }
  }
}
```

See `docs/mcp_server_setup.md` for detailed instructions.

### **Step 3: Configure Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

**Required Settings:**
```bash
VAULT_PATH=/home/user/AI_Employee_Vault
GMAIL_CREDENTIALS_PATH=/home/user/.credentials/gmail-credentials.json
GMAIL_TOKEN_PATH=/home/user/.credentials/gmail-token.json
LINKEDIN_USERNAME=your@email.com
LINKEDIN_PASSWORD=your_password
ORCHESTRATOR_WATCHERS=gmail,filesystem,linkedin
```

### **Step 4: Create Vault**

```bash
# Automated vault creation
python vault_setup/create_vault.py --path ~/AI_Employee_Vault
```

This creates:
- `/Inbox/`, `/Needs_Action/`, `/Done/`, `/Plans/`, `/Pending_Approval/` folders
- `Dashboard.md` (auto-updated activity summary)
- `Company_Handbook.md` (rules and approval thresholds)

### **Step 5: Setup Gmail OAuth**

See [`docs/gmail_api_setup.md`](docs/gmail_api_setup.md) for detailed instructions.

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `gmail-credentials.json`
6. Run watcher once to generate token

### **Step 6: Run Orchestrator**

```bash
# Start all watchers
python watchers/orchestrator.py
```

**What happens:**
- Gmail, File System, and LinkedIn watchers start
- Health monitoring begins (heartbeat every 60s)
- Auto-restart on crash enabled
- State database initialized

### **Step 7: Install Scheduled Tasks (Optional)**

```bash
# Linux/Mac (cron)
python -m scheduler.cron_setup setup

# Windows (Task Scheduler)
python -m scheduler.task_scheduler_setup setup
```

### **Step 8: Process Tasks**

```bash
# Triage inbox (Inbox → Needs_Action)
cd ~/AI_Employee_Vault
claude "triage inbox"

# Process all tasks
claude "process all tasks in Needs_Action"
```

---

## 🧠 Agent Skills

**8 specialized AI capabilities** that Claude automatically applies:

| Skill | Purpose | Trigger Command |
|-------|---------|-----------------|
| **`inbox_triage`** | Move files from /Inbox/ → /Needs_Action/ | `"triage inbox"` |
| **`inbox_processor`** | Prioritize & process tasks | `"process tasks in Needs_Action"` |
| **`vault_manager`** | Obsidian file operations | Internal use |
| **`task_planner`** | Create Plan.md for complex tasks | `"create plan for TASK_ID"` |
| **`email_handler`** | Send emails via Gmail MCP | `"send email to..."` |
| **`social_poster`** | Create/publish LinkedIn posts | `"create LinkedIn post"` |
| **`approval_workflow`** | Manage /Pending_Approval/ | `"approve task TASK_ID"` |
| **`scheduler`** | Run scheduled tasks | `"setup cron jobs"` |

**Location:** `.claude/skills/*/SKILL.md`

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| [`docs/setup_guide.md`](docs/setup_guide.md) | Complete setup walkthrough |
| [`docs/gmail_api_setup.md`](docs/gmail_api_setup.md) | Gmail OAuth configuration |
| [`docs/linkedin_api_setup.md`](docs/linkedin_api_setup.md) | LinkedIn integration setup |
| [`docs/mcp_server_setup.md`](docs/mcp_server_setup.md) | Email MCP server config |
| [`docs/scheduling_setup.md`](docs/scheduling_setup.md) | Cron/Task Scheduler setup |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Common issues & solutions |

---

## 📁 Project Structure

```
personal-ai-employee/
├── .claude/
│   └── skills/              # 8 Agent Skills (SKILL.md files)
│       ├── vault_manager/
│       ├── inbox_processor/
│       ├── inbox_triage/
│       ├── task_planner/
│       ├── email_handler/
│       ├── social_poster/
│       ├── approval_workflow/
│       └── scheduler/
├── watchers/
│   ├── base_watcher.py      # Abstract base class
│   ├── gmail_watcher.py     # Gmail monitoring
│   ├── filesystem_watcher.py # File system monitoring
│   ├── linkedin_watcher.py  # LinkedIn monitoring
│   ├── orchestrator.py      # Multi-watcher manager
│   ├── state_manager.py     # SQLite state persistence
│   └── config.py            # Configuration
├── scheduler/
│   ├── cron_setup.py        # Linux/Mac cron setup
│   ├── task_scheduler_setup.py # Windows Task Scheduler
│   └── task_executor.py     # Scheduled task runner
├── mcp_servers/
│   └── email_sender/
│       └── server.py        # Gmail MCP server
├── vault_setup/
│   ├── create_vault.py      # Vault creation script
│   └── templates/
│       ├── dashboard_template.md
│       ├── company_handbook_template.md
│       ├── task_template.md
│       └── plan_template.md
├── tests/
│   ├── unit/
│   └── integration/
├── docs/                    # Documentation
├── .env.example             # Environment template
├── scheduled_tasks.yaml     # Cron job config
├── pyproject.toml           # Python project config
└── README.md                # This file
```

---

## 🗺️ Roadmap

### **🥉 Bronze Tier** (Complete)
- ✅ Single watcher (Gmail OR File System)
- ✅ Basic task detection
- ✅ Claude Code integration
- ✅ 1 Agent Skill

### **🥈 Silver Tier** (Complete - You Are Here)
- ✅ Triple watcher system
- ✅ Email sending via MCP
- ✅ LinkedIn automation
- ✅ State persistence
- ✅ Approval workflow
- ✅ Scheduled tasks
- ✅ 8 Agent Skills

### **🥇 Gold Tier** (Next)
- ⏳ Odoo ERP integration
- ⏳ Social media monitoring (Twitter, Facebook)
- ⏳ Ralph Wiggum autonomous loop
- ⏳ CEO daily briefing

### **💎 Platinum Tier** (Future)
- ⏳ Cloud deployment (AWS/GCP)
- ⏳ 24/7 monitoring dashboard
- ⏳ Multi-user support
- ⏳ Advanced analytics

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

**MIT License** - See [LICENSE](LICENSE) file for details.

Open source and free to use, modify, and distribute.

---

## 📞 Support

- **Issues**: Report bugs on [GitHub Issues](https://github.com/your-username/personal-ai-employee/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/your-username/personal-ai-employee/discussions)
- **Documentation**: See `/docs` folder

---

## 🎉 Success Metrics

**After setup, you should see:**

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Email detection | <2 minutes | Send test email, check /Inbox/gmail/ |
| File detection | <30 seconds | Drop file, check /Inbox/filesystem/ |
| LinkedIn detection | <5 minutes | Send LinkedIn message, check /Inbox/linkedin/ |
| Email sending | <5 seconds | Approve task, verify sent in Gmail |
| No duplicates | 100% | Restart watchers, verify no duplicate tasks |
| Uptime | >99% | Check /Logs/orchestrator.log after 24h |

---

**Built with ❤️ by Hunain**  
**Version**: 0.2.0 (Silver Tier)  
**Last Updated**: 2026-03-15
