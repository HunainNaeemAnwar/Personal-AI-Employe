#!/usr/bin/env python3
"""
24-Hour Continuous Operation Monitor for Silver Tier Watchers

This script monitors the orchestrator and watchers for 24 hours,
logging uptime, crashes, and performance metrics.

Usage:
    python scripts/monitor_24h.py

Output:
    - Logs to AI_Employee_Vault/Logs/monitor_24h.log
    - Creates summary report at end of 24 hours
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
MONITOR_DURATION_HOURS = 24
HEALTH_CHECK_INTERVAL = 60  # seconds
LOG_PATH = Path("AI_Employee_Vault/Logs/monitor_24h.log")
ORCHESTRATOR_PID = None
START_TIME = None

def log(message):
    """Write log message with timestamp."""
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    
    # Append to log file
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(log_line + "\n")

def check_orchestrator_health():
    """Check if orchestrator process is running."""
    global ORCHESTRATOR_PID
    
    if ORCHESTRATOR_PID is None:
        return False
    
    try:
        # Check if process exists
        os.kill(ORCHESTRATOR_PID, 0)
        return True
    except OSError:
        return False

def check_watcher_heartbeats():
    """Check heartbeat files for all watchers."""
    logs_dir = Path("AI_Employee_Vault/Logs")
    watchers = ["gmail", "filesystem", "linkedin"]
    status = {}
    
    for watcher in watchers:
        heartbeat_file = logs_dir / f"{watcher}_watcher_heartbeat.txt"
        if heartbeat_file.exists():
            try:
                content = heartbeat_file.read_text().strip()
                heartbeat_time = datetime.fromisoformat(content.replace("Z", "+00:00"))
                age = (datetime.now(heartbeat_time.tzinfo) - heartbeat_time).total_seconds()
                status[watcher] = "healthy" if age < 120 else "stale"
            except Exception as e:
                status[watcher] = f"error: {e}"
        else:
            status[watcher] = "no heartbeat file"
    
    return status

def start_orchestrator():
    """Start the orchestrator process."""
    global ORCHESTRATOR_PID
    
    log("Starting orchestrator...")
    process = subprocess.Popen(
        ["python", "watchers/orchestrator.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    ORCHESTRATOR_PID = process.pid
    log(f"Orchestrator started with PID {ORCHESTRATOR_PID}")
    return process

def stop_orchestrator():
    """Stop the orchestrator process."""
    global ORCHESTRATOR_PID
    
    if ORCHESTRATOR_PID:
        log(f"Stopping orchestrator (PID {ORCHESTRATOR_PID})...")
        try:
            os.kill(ORCHESTRATOR_PID, signal.SIGTERM)
            time.sleep(5)
            # Force kill if still running
            try:
                os.kill(ORCHESTRATOR_PID, 0)
                os.kill(ORCHESTRATOR_PID, signal.SIGKILL)
            except OSError:
                pass  # Already stopped
            log("Orchestrator stopped")
        except Exception as e:
            log(f"Error stopping orchestrator: {e}")
        ORCHESTRATOR_PID = None

def run_monitoring():
    """Run 24-hour monitoring loop."""
    global START_TIME
    
    START_TIME = datetime.now()
    end_time = START_TIME + timedelta(hours=MONITOR_DURATION_HOURS)
    
    log("="*60)
    log(f"Starting 24-hour monitoring at {START_TIME.isoformat()}")
    log(f"Expected end time: {end_time.isoformat()}")
    log("="*60)
    
    # Start orchestrator
    orchestrator = start_orchestrator()
    time.sleep(10)  # Wait for initialization
    
    # Monitoring statistics
    stats = {
        "health_checks": 0,
        "crashes_detected": 0,
        "restarts_performed": 0,
        "uptime_seconds": 0,
        "downtime_seconds": 0,
    }
    
    last_check = START_TIME
    
    try:
        while datetime.now() < end_time:
            current_time = datetime.now()
            
            # Health check
            stats["health_checks"] += 1
            
            if check_orchestrator_health():
                stats["uptime_seconds"] += HEALTH_CHECK_INTERVAL
                
                # Check watcher heartbeats
                heartbeats = check_watcher_heartbeats()
                all_healthy = all(s == "healthy" for s in heartbeats.values())
                
                if not all_healthy:
                    log(f"⚠ Watcher health issue: {heartbeats}")
            else:
                stats["crashes_detected"] += 1
                stats["downtime_seconds"] += HEALTH_CHECK_INTERVAL
                log("❌ Orchestrator crashed, restarting...")
                
                # Restart orchestrator
                stop_orchestrator()
                time.sleep(5)
                orchestrator = start_orchestrator()
                stats["restarts_performed"] += 1
            
            # Progress report every hour
            elapsed = (current_time - START_TIME).total_seconds() / 3600
            if (current_time - last_check).total_seconds() >= 3600:
                uptime_pct = (stats["uptime_seconds"] / elapsed / 3600 * 100) if elapsed > 0 else 0
                log(f"Progress: {elapsed:.1f}h / {MONITOR_DURATION_HOURS}h | Uptime: {uptime_pct:.1f}% | Restarts: {stats['restarts_performed']}")
                last_check = current_time
            
            # Wait for next check
            time.sleep(HEALTH_CHECK_INTERVAL)
    
    except KeyboardInterrupt:
        log("\nMonitoring interrupted by user")
    
    finally:
        # Generate final report
        stop_orchestrator()
        generate_report(stats)

def generate_report(stats):
    """Generate final monitoring report."""
    end_time = datetime.now()
    total_duration = (end_time - START_TIME).total_seconds()
    
    uptime_pct = (stats["uptime_seconds"] / total_duration * 100) if total_duration > 0 else 0
    
    report = f"""
{'='*60}
24-HOUR MONITORING REPORT
{'='*60}

Start Time: {START_TIME.isoformat()}
End Time: {end_time.isoformat()}
Total Duration: {total_duration/3600:.2f} hours

STATISTICS:
- Health Checks Performed: {stats['health_checks']}
- Crashes Detected: {stats['crashes_detected']}
- Restarts Performed: {stats['restarts_performed']}
- Uptime: {stats['uptime_seconds']/3600:.2f} hours ({uptime_pct:.1f}%)
- Downtime: {stats['downtime_seconds']/3600:.2f} hours ({100-uptime_pct:.1f}%)

SUCCESS CRITERIA:
- Target Uptime: 99%
- Actual Uptime: {uptime_pct:.1f}%
- Status: {'✅ PASS' if uptime_pct >= 99 else '❌ FAIL'}

{'='*60}
"""
    
    print(report)
    
    # Save report
    report_path = Path("AI_Employee_Vault/Logs/monitor_24h_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    
    log(f"Report saved to {report_path}")

if __name__ == "__main__":
    run_monitoring()
