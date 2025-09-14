#!/usr/bin/env python3
"""
Viber Missed Calls Auto-Calendar System (Security Enhanced)
Uses notification monitoring and log analysis since direct database access is restricted
Enhanced with comprehensive security improvements and operational features
"""

import os
import json
import time
import re
import subprocess
import logging
import logging.handlers
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import functools
from pathlib import Path

from google_auth import GoogleAPIAuth

# Security and operational enhancements
class SecurityError(Exception):
    """Custom exception for security-related errors"""
    pass

class OperationResult:
    """Result wrapper for operations with error handling"""
    def __init__(self, success: bool, data: Any = None, error: str = None):
        self.success = success
        self.data = data
        self.error = error

def setup_secure_logging() -> logging.Logger:
    """Setup secure, structured logging"""
    logger = logging.getLogger('viber_scheduler')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        # Create logs directory
        log_dir = Path.home() / '.viber_scheduler' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        
        # File handler with rotation
        log_file = log_dir / 'viber_scheduler.log'
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def validate_caller_name(name: str) -> str:
    """Validate and sanitize caller names"""
    if not name or not isinstance(name, str):
        raise SecurityError("Invalid caller name")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\'\\\x00-\x1f\x7f-\x9f]', '', name.strip())
    
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    if not sanitized:
        raise SecurityError("Caller name cannot be empty after sanitization")
    
    return sanitized

def secure_subprocess_run(cmd: List[str], timeout: int = 30) -> OperationResult:
    """Secure subprocess execution with timeout and validation"""
    try:
        # Validate command
        if not cmd or not all(isinstance(arg, str) for arg in cmd):
            return OperationResult(False, error="Invalid command arguments")
        
        # Execute with timeout
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False
        )
        
        return OperationResult(True, {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return OperationResult(False, error=f"Command timed out after {timeout}s")
    except Exception as e:
        return OperationResult(False, error=f"Subprocess error: {str(e)}")

class ViberMissedCallTracker:
    def __init__(self):
        # Initialize secure logging
        self.logger = setup_secure_logging()
        self.logger.info("Initializing Viber Missed Call Tracker with security enhancements")
        
        try:
            self.auth = GoogleAPIAuth()
            self.calendar = self.auth.get_calendar_service()
            self.processed_calls = set()
            self.missed_call_counts = {}
            self.last_notification_check = datetime.now()
            
            # Create secure data directory
            self.data_dir = Path.home() / '.viber_scheduler' / 'data'
            self.data_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            
            self.load_processed_data()
            self.logger.info("Viber Missed Call Tracker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize tracker: {str(e)}")
            raise
        
    def load_processed_data(self):
        """Load previously processed calls and missed call counts"""
        data_file = self.data_dir / 'viber_missed_calls.json'
        
        try:
            if data_file.exists():
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.processed_calls = set(data.get('processed_calls', []))
                    self.missed_call_counts = data.get('missed_call_counts', {})
                    self.logger.info(f"Loaded {len(self.processed_calls)} processed calls")
            else:
                self.logger.info("No existing data file found, starting fresh")
        except FileNotFoundError:
            self.processed_calls = set()
            self.missed_call_counts = {}
    
    def save_processed_data(self):
        """Save processed calls and missed call counts"""
        data_file = self.data_dir / 'viber_missed_calls.json'
        
        try:
            data = {
                'processed_calls': list(self.processed_calls),
                'missed_call_counts': self.missed_call_counts,
                'last_updated': datetime.now().isoformat()
            }
            
            # Write to temp file first, then atomic rename
            temp_file = data_file.with_suffix('.json.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Set secure permissions
            temp_file.chmod(0o600)
            
            # Atomic rename
            temp_file.rename(data_file)
            
            self.logger.info(f"Saved {len(self.processed_calls)} processed calls to secure storage")
            
        except Exception as e:
            self.logger.error(f"Failed to save data: {str(e)}")
            raise
    
    def check_viber_notifications(self):
        """Monitor macOS notification database for Viber missed call notifications"""
        try:
            self.logger.info("Checking Viber notifications for missed calls")
            
            # Secure database path validation
            db_path = Path.home() / 'Library' / 'Application Support' / 'NotificationCenter' / 'db2' / 'db'
            if not db_path.exists():
                self.logger.warning("Notification database not found")
                return []
            
            # Prepare secure SQL query
            query = '''SELECT datetime(delivered_date + 978307200, 'unixepoch', 'localtime') as time, 
                              data FROM record 
                       WHERE bundleid = 'com.viber.osx' 
                       AND delivered_date > (strftime('%s', datetime('now', '-1 hour')) - 978307200)
                       ORDER BY delivered_date DESC;'''
            
            # Execute with secure subprocess
            cmd = ['sqlite3', str(db_path), query]
            result = secure_subprocess_run(cmd, timeout=10)
            
            if not result.success:
                self.logger.error(f"Failed to query notification database: {result.error}")
                return []
            
            if result.data['returncode'] == 0:
                notifications = result.data['stdout'].strip().split('\n')
                return self.parse_viber_notifications(notifications)
            else:
                self.logger.warning(f"Database query returned error code: {result.data['returncode']}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error checking notifications: {e}")
            return []
    
    def parse_viber_notifications(self, notifications):
        """Parse Viber notifications for missed calls"""
        missed_calls = []
        
        for notification in notifications:
            if not notification.strip():
                continue
                
            parts = notification.split('|')
            if len(parts) < 2:
                continue
                
            time_str = parts[0]
            notification_data = parts[1]
            
            # Look for missed call indicators in the notification
            if any(keyword in notification_data.lower() for keyword in ['missed call', 'elmulasztott', 'hívás']):
                # Try to extract caller name from notification
                caller = self.extract_caller_from_notification(notification_data)
                if caller:
                    missed_calls.append({
                        'time': time_str,
                        'caller': caller,
                        'notification_data': notification_data
                    })
        
        return missed_calls
    
    def extract_caller_from_notification(self, notification_data):
        """Extract caller name from notification data"""
        # This is a simplified approach - Viber notification format may vary
        # Common patterns: "Missed call from [Name]" or similar
        patterns = [
            r'from\s+([^,\n]+)',
            r'([^:]+):\s*missed',
            r'hívás\s+([^,\n]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, notification_data, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Unknown Caller"
    
    def monitor_viber_activity(self):
        """Alternative: Monitor Viber application activity"""
        try:
            # Check if Viber is running and get recent activity
            # This is a simplified approach - could be enhanced with more sophisticated monitoring
            
            # For demonstration, let's create a manual trigger system
            # You can enhance this to monitor actual Viber activity logs
            
            return self.check_manual_missed_calls()
            
        except Exception as e:
            print(f"Error monitoring Viber activity: {e}")
            return []
    
    def check_manual_missed_calls(self):
        """Manual missed call detection with security validation"""
        missed_calls_file = Path('manual_missed_calls.txt')
        
        if not missed_calls_file.exists():
            # Create example file with secure permissions
            try:
                with open(missed_calls_file, 'w') as f:
                    f.write("# Add missed calls manually for testing:\n")
                    f.write("# Format: YYYY-MM-DD HH:MM | Caller Name\n")
                    f.write("# Example: 2025-09-11 14:30 | János Kovács\n")
                    f.write("\n")
                missed_calls_file.chmod(0o600)
                self.logger.info("Created manual missed calls template file")
            except Exception as e:
                self.logger.error(f"Failed to create template file: {e}")
            return []
        
        # Security: Check file size limit
        try:
            if missed_calls_file.stat().st_size > 1024 * 1024:  # 1MB limit
                self.logger.error("Manual missed calls file too large")
                return []
        except Exception as e:
            self.logger.error(f"Error checking file size: {e}")
            return []
        
        missed_calls = []
        try:
            with open(missed_calls_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                    
                if '|' in line:
                    try:
                        time_str, caller_raw = line.split('|', 1)
                        time_str = time_str.strip()
                        
                        # Validate and sanitize caller name
                        caller = validate_caller_name(caller_raw.strip())
                        
                        # Parse the time with validation
                        call_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                        
                        # Validate date is reasonable
                        now = datetime.now()
                        if call_time > now + timedelta(days=1):
                            self.logger.warning(f"Line {line_num}: Future date ignored: {time_str}")
                            continue
                            
                        # Process calls from today and yesterday (handles sleep/wake scenarios)
                        time_diff = now - call_time
                        if time_diff < timedelta(hours=48):  # 48 hours to handle weekend sleeps
                            call_id = f"{time_str}_{caller}"
                            if call_id not in self.processed_calls:
                                missed_calls.append({
                                    'time': call_time,
                                    'caller': caller,
                                    'call_id': call_id
                                })
                                
                    except ValueError as e:
                        self.logger.warning(f"Line {line_num}: Invalid format - {e}")
                    except SecurityError as e:
                        self.logger.error(f"Line {line_num}: Security error - {e}")
                        
        except Exception as e:
            self.logger.error(f"Error reading manual missed calls: {e}")
        
        self.logger.info(f"Found {len(missed_calls)} new manual missed calls")
        return missed_calls
    
    def get_next_callback_time(self, caller_name):
        """Get the next available callback time starting from 6 PM"""
        try:
            today = datetime.now().date()
            base_time = datetime.combine(today, datetime.min.time().replace(hour=18, minute=0))  # 6 PM today
            
            # Convert to UTC for API query (subtract 2 hours for Europe/Budapest timezone)
            base_time_utc = base_time - timedelta(hours=2)
            
            # Get events for today starting from 6 PM local time (4 PM UTC) to 10 PM local time (8 PM UTC)
            time_min = base_time_utc.isoformat() + 'Z'
            time_max = (base_time_utc + timedelta(hours=4)).isoformat() + 'Z'  # Until 10 PM local
            
            events_result = self.calendar.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            existing_events = events_result.get('items', [])
            
            print(f"   🔍 Found {len(existing_events)} existing events between 6-10 PM")
            
            # Find next available 15-minute slot
            current_slot = base_time
            for i in range(16):  # Check 4 hours worth of 15-minute slots
                slot_end = current_slot + timedelta(minutes=15)
                
                # Check if this slot conflicts with existing events
                slot_free = True
                for event in existing_events:
                    event_start_str = event['start'].get('dateTime', event['start'].get('date'))
                    event_end_str = event['end'].get('dateTime', event['end'].get('date'))
                    
                    # Parse datetime strings properly
                    try:
                        if 'T' in event_start_str:
                            # Remove timezone info for comparison
                            event_start = datetime.fromisoformat(event_start_str.split('+')[0].split('Z')[0])
                            event_end = datetime.fromisoformat(event_end_str.split('+')[0].split('Z')[0])
                        else:
                            # All-day event, skip
                            continue
                            
                        # Check for conflict
                        if (current_slot < event_end and slot_end > event_start):
                            print(f"   ❌ Slot {current_slot.strftime('%H:%M')} conflicts with: {event.get('summary', 'Event')}")
                            slot_free = False
                            break
                    except Exception as e:
                        print(f"   ⚠️ Error parsing event time: {e}")
                        continue
                
                if slot_free:
                    print(f"   ✅ Found free slot: {current_slot.strftime('%H:%M')}")
                    return current_slot
                
                current_slot += timedelta(minutes=15)
            
            # If no free slot found, default to 10 PM
            return base_time.replace(hour=22, minute=0)
            
        except Exception as e:
            print(f"Error finding callback time: {e}")
            # Fallback to 6 PM
            today = datetime.now().date()
            return datetime.combine(today, datetime.min.time().replace(hour=18, minute=0))
    
    def create_calendar_followup(self, caller_name, call_time, missed_count):
        """Create a follow-up task scheduled from 6 PM onward in Google Calendar"""
        try:
            # Parse call time
            if isinstance(call_time, str):
                call_datetime = datetime.strptime(call_time, '%Y-%m-%d %H:%M:%S')
            else:
                call_datetime = call_time
            
            # Get next available slot starting from 6 PM
            followup_time = self.get_next_callback_time(caller_name)
            
            # Create event title and description in English
            if missed_count == 1:
                title = f"📞 Call back: {caller_name}"
                description = f"Follow-up for missed call\n\n" \
                            f"Caller: {caller_name}\n" \
                            f"Missed call time: {call_datetime.strftime('%H:%M')}\n" \
                            f"Number of missed calls: {missed_count}"
            else:
                title = f"📞 URGENT - Call back: {caller_name} ({missed_count}x)"
                description = f"MULTIPLE missed calls - follow-up required!\n\n" \
                            f"Caller: {caller_name}\n" \
                            f"Last missed call: {call_datetime.strftime('%H:%M')}\n" \
                            f"Number of missed calls: {missed_count}\n" \
                            f"⚠️ Multiple attempts - might be important!"
            
            # Create calendar event
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': followup_time.isoformat(),
                    'timeZone': 'Europe/Budapest',
                },
                'end': {
                    'dateTime': (followup_time + timedelta(minutes=15)).isoformat(),
                    'timeZone': 'Europe/Budapest',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'popup', 'minutes': 0},
                    ],
                },
            }
            
            # Use primary calendar
            created_event = self.calendar.events().insert(
                calendarId='primary', 
                body=event
            ).execute()
            
            print(f"✅ Calendar event created: {title}")
            print(f"   Time: {followup_time.strftime('%H:%M')} ({followup_time.strftime('%Y-%m-%d')})")
            
            return created_event['id'], followup_time
            
        except Exception as e:
            print(f"❌ Error creating calendar event: {e}")
            return None, None
    
    def send_notification(self, caller_name, call_time, missed_count, followup_time):
        """Send macOS notification about missed call and created follow-up"""
        if isinstance(call_time, str):
            call_datetime = datetime.strptime(call_time, '%Y-%m-%d %H:%M:%S')
        else:
            call_datetime = call_time
        
        if missed_count == 1:
            title = f"Viber: Missed call"
            subtitle = f"{caller_name}"
            message = f"Missed: {call_datetime.strftime('%H:%M')}\n✅ Callback scheduled: {followup_time.strftime('%H:%M')}"
        else:
            title = f"Viber: {missed_count}x Missed calls!"
            subtitle = f"{caller_name} - URGENT"
            message = f"Last call: {call_datetime.strftime('%H:%M')}\n⚠️ {missed_count} missed calls!\n✅ Callback scheduled: {followup_time.strftime('%H:%M')}"
        
        applescript = f'''
        display notification "{message}" with title "{title}" subtitle "{subtitle}"
        '''
        
        try:
            subprocess.run(['osascript', '-e', applescript], check=True)
        except Exception as e:
            print(f"Notification error: {e}")
    
    def process_missed_calls(self):
        """Process new missed calls and create follow-up tasks"""
        # Try notification monitoring first
        missed_calls = self.check_viber_notifications()
        
        # Fallback to manual monitoring
        if not missed_calls:
            missed_calls = self.monitor_viber_activity()
        
        new_calls_processed = 0
        for call in missed_calls:
            call_id = call.get('call_id', f"{call['time']}_{call['caller']}")
            
            # Skip if already processed
            if call_id in self.processed_calls:
                continue
            
            caller_name = call['caller']
            call_time = call['time']
            
            # Update missed call count for this caller
            if caller_name not in self.missed_call_counts:
                self.missed_call_counts[caller_name] = 0
            self.missed_call_counts[caller_name] += 1
            
            missed_count = self.missed_call_counts[caller_name]
            
            print(f"\n📞 New missed call: {caller_name}")
            if isinstance(call_time, datetime):
                print(f"   Time: {call_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"   Time: {call_time}")
            print(f"   Missed calls from this person: {missed_count}")
            
            # Create calendar follow-up
            event_id, followup_time = self.create_calendar_followup(caller_name, call_time, missed_count)
            
            if event_id:
                # Send notification
                self.send_notification(caller_name, call_time, missed_count, followup_time)
                
                # Mark as processed
                self.processed_calls.add(call_id)
                new_calls_processed += 1
        
        if new_calls_processed > 0:
            print(f"\n✅ Processed {new_calls_processed} new missed calls")
            self.save_processed_data()
        
        return new_calls_processed
    
    def check_wake_up_backlog(self):
        """Check for missed calls that happened while system was sleeping"""
        print("🌅 Checking for missed calls while system was offline...")
        
        # Check if there's a significant gap since last update
        try:
            with open('viber_missed_calls.json', 'r') as f:
                data = json.load(f)
                last_updated_str = data.get('last_updated')
                if last_updated_str:
                    last_updated = datetime.fromisoformat(last_updated_str)
                    time_since_last = datetime.now() - last_updated
                    
                    if time_since_last > timedelta(hours=2):
                        print(f"⏰ System was offline for {int(time_since_last.total_seconds()//3600)} hours")
                        print("🔍 Checking for backlog missed calls...")
                        
                        # Process any missed calls from the offline period
                        backlog_calls = self.process_missed_calls()
                        if backlog_calls > 0:
                            print(f"✅ Processed {backlog_calls} missed calls from offline period")
                        else:
                            print("📭 No missed calls found during offline period")
                    else:
                        print("✅ System was recently active, no backlog check needed")
        except FileNotFoundError:
            print("📝 First time running, no backlog to check")

    def run_monitor(self):
        """Main monitoring loop"""
        print("📞 Viber Missed Call Tracker Started")
        print("📅 Creating 15-minute follow-up calendar tasks")
        print("🔢 Tracking missed call counts per contact")
        print(f"📝 Manual testing: Edit 'manual_missed_calls.txt' to add test calls")
        print("💤 Handles MacBook sleep/wake scenarios automatically")
        print("\nPress Ctrl+C to stop\n")
        
        # Check for backlog from sleep/offline period
        self.check_wake_up_backlog()
        
        try:
            while True:
                new_calls = self.process_missed_calls()
                
                if new_calls == 0:
                    print(".", end="", flush=True)  # Show activity
                
                # Wait 30 seconds before next check
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Viber missed call tracker...")
            self.save_processed_data()
        except Exception as e:
            print(f"\n❌ Error in monitor: {e}")
            self.save_processed_data()

def view_missed_calls():
    """View tracked missed calls"""
    try:
        with open('viber_missed_calls.json', 'r') as f:
            data = json.load(f)
        
        print("📞 VIBER MISSED CALLS TRACKER")
        print("=" * 40)
        
        missed_counts = data.get('missed_call_counts', {})
        if missed_counts:
            print("\n📊 Missed call counts by contact:")
            for caller_name, count in missed_counts.items():
                print(f"   {caller_name}: {count} missed calls")
        
        processed_calls = data.get('processed_calls', [])
        print(f"\n📈 Total processed calls: {len(processed_calls)}")
        
        last_updated = data.get('last_updated')
        if last_updated:
            print(f"Last updated: {last_updated}")
            
    except FileNotFoundError:
        print("No missed calls data found yet.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        view_missed_calls()
    else:
        tracker = ViberMissedCallTracker()
        tracker.run_monitor()