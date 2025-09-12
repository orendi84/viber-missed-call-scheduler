#!/bin/bash
# Viber Missed Call Monitor Startup Script
# This script starts the Viber monitoring service

# Wait for system to be fully awake
sleep 5

# Change to the directory containing the Python script
cd /Users/gergoorendi

# Log file for monitoring
LOG_FILE="/Users/gergoorendi/viber_monitor.log"

# Kill any existing monitoring processes to avoid duplicates
pkill -f "viber_missed_calls_v2.py"
sleep 2

# Start the monitoring service
echo "$(date): Starting Viber missed call monitor" >> "$LOG_FILE"
python3 viber_missed_calls_v2.py >> "$LOG_FILE" 2>&1 &

echo "$(date): Viber monitor started with PID $!" >> "$LOG_FILE"