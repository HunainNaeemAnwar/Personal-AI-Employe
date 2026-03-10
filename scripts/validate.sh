#!/bin/bash
# Silver Tier Validation Helper Script
# This script automates parts of the validation process

set -e

echo "==================================="
echo "Silver Tier Validation Helper"
echo "==================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if dependencies installed
if python -c "import linkedin_api" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} linkedin-api installed"
else
    echo -e "${RED}✗${NC} linkedin-api not installed"
fi

if python -c "import selenium" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} selenium installed"
else
    echo -e "${RED}✗${NC} selenium not installed"
fi

if python -c "import pytest" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} pytest installed"
else
    echo -e "${RED}✗${NC} pytest not installed"
fi

echo ""

# Check vault structure
echo "Checking vault structure..."
if [ -d "AI_Employee_Vault" ]; then
    echo -e "${GREEN}✓${NC} Vault directory exists"

    required_folders=("Needs_Action" "Done" "Rejected" "Pending_Approval" "Approved" "Logs" "Plans" "Briefings" "Summaries" "Reviews" "Reports")
    for folder in "${required_folders[@]}"; do
        if [ -d "AI_Employee_Vault/$folder" ]; then
            echo -e "${GREEN}✓${NC} $folder exists"
        else
            echo -e "${RED}✗${NC} $folder missing"
        fi
    done
else
    echo -e "${RED}✗${NC} Vault directory not found"
    echo "Run: python -m vault_setup.setup"
fi

echo ""

# Check environment variables
echo "Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"

    required_vars=("VAULT_PATH" "WATCH_DIRECTORY" "STATE_DB_PATH")
    for var in "${required_vars[@]}"; do
        if grep -q "^$var=" .env; then
            echo -e "${GREEN}✓${NC} $var configured"
        else
            echo -e "${YELLOW}⚠${NC} $var not configured"
        fi
    done
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "Run: cp .env.example .env"
fi

echo ""

# Run unit tests
echo "Running unit tests..."
if python -m pytest tests/unit/ -v --tb=line -q 2>&1 | tail -5; then
    echo -e "${GREEN}✓${NC} Unit tests passed"
else
    echo -e "${RED}✗${NC} Unit tests failed"
fi

echo ""

# Check state database
echo "Checking state database..."
if [ -f "state.db" ]; then
    echo -e "${GREEN}✓${NC} State database exists"
    db_size=$(du -h state.db | cut -f1)
    echo "  Size: $db_size"

    # Check database health
    if python -c "from watchers.state_manager import StateManager; sm = StateManager(); print('Health:', sm.health_check())" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Database health check passed"
    else
        echo -e "${RED}✗${NC} Database health check failed"
    fi
else
    echo -e "${YELLOW}⚠${NC} State database not found (will be created on first run)"
fi

echo ""

# Check for running processes
echo "Checking for running processes..."
if pgrep -f "watchers.orchestrator" > /dev/null; then
    echo -e "${GREEN}✓${NC} Orchestrator is running"
    echo "  PID: $(pgrep -f 'watchers.orchestrator')"
else
    echo -e "${YELLOW}⚠${NC} Orchestrator is not running"
fi

if pgrep -f "gmail_watcher" > /dev/null; then
    echo -e "${GREEN}✓${NC} Gmail watcher is running"
else
    echo -e "${YELLOW}⚠${NC} Gmail watcher is not running"
fi

if pgrep -f "filesystem_watcher" > /dev/null; then
    echo -e "${GREEN}✓${NC} Filesystem watcher is running"
else
    echo -e "${YELLOW}⚠${NC} Filesystem watcher is not running"
fi

echo ""

# Check recent activity
echo "Checking recent activity..."
if [ -d "AI_Employee_Vault/Needs_Action" ]; then
    task_count=$(ls AI_Employee_Vault/Needs_Action/*.md 2>/dev/null | wc -l)
    echo "Tasks in Needs_Action: $task_count"
fi

if [ -d "AI_Employee_Vault/Logs" ]; then
    if [ -f "AI_Employee_Vault/Logs/filesystem_watcher_heartbeat.txt" ]; then
        heartbeat=$(cat AI_Employee_Vault/Logs/filesystem_watcher_heartbeat.txt)
        echo "Last filesystem heartbeat: $heartbeat"
    fi

    if [ -f "AI_Employee_Vault/Logs/gmail_watcher_heartbeat.txt" ]; then
        heartbeat=$(cat AI_Employee_Vault/Logs/gmail_watcher_heartbeat.txt)
        echo "Last gmail heartbeat: $heartbeat"
    fi
fi

echo ""
echo "==================================="
echo "Validation Status Summary"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Review VALIDATION_GUIDE.md for detailed instructions"
echo "2. Complete T091: Quickstart validation"
echo "3. Complete T092: 24-hour continuous operation test"
echo "4. Complete T093: Performance benchmarks validation"
echo ""
echo "To start orchestrator:"
echo "  python -m watchers.orchestrator"
echo ""
echo "To monitor in real-time:"
echo "  watch -n 5 './scripts/validate.sh'"
echo ""
