#!/usr/bin/env python3
"""
Viber Missed Call Monitor - Auto Starter
This script ensures the monitoring service is always running
"""

import subprocess
import time
import os
import signal
import sys
from datetime import datetime

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    
    # Also write to log file
    with open("/Users/gergoorendi/viber_auto_start.log", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def is_monitor_running():
    """Check if monitoring process is already running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'viber_missed_calls_v2.py'], 
                              capture_output=True, text=True)
        return len(result.stdout.strip()) > 0
    except:
        return False

def start_monitor():
    """Start the monitoring service"""
    try:
        # Change to correct directory
        os.chdir("/Users/gergoorendi")
        
        # Start the process in background
        process = subprocess.Popen([
            'python3', 'viber_missed_calls_v2.py'
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        log(f"Started Viber monitor with PID {process.pid}")
        return process
        
    except Exception as e:
        log(f"Error starting monitor: {e}")
        return None

def main():
    log("Viber Auto-Starter launched")
    
    # Wait a bit for system to settle after wake/boot
    time.sleep(10)
    
    try:
        while True:
            if not is_monitor_running():
                log("Monitor not running, starting it...")
                start_monitor()
                time.sleep(5)  # Give it time to start
                
                if is_monitor_running():
                    log("✅ Monitor started successfully")
                else:
                    log("❌ Failed to start monitor, will retry in 60 seconds")
            else:
                log("✅ Monitor is running")
            
            # Check every 5 minutes
            time.sleep(300)
            
    except KeyboardInterrupt:
        log("Auto-starter stopped by user")
    except Exception as e:
        log(f"Error in auto-starter: {e}")

if __name__ == "__main__":
    main()