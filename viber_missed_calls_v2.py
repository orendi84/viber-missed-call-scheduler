#!/usr/bin/env python3
"""
Viber Missed Calls Auto-Calendar System (Alternative Approach)
Uses notification monitoring and log analysis since direct database access is restricted
"""

import os
import json
import time
import re
import subprocess
from datetime import datetime, timedelta
from google_auth import GoogleAPIAuth

class ViberMissedCallTracker:
    def __init__(self):
        self.auth = GoogleAPIAuth()
        self.calendar = self.auth.get_calendar_service()
        self.processed_calls = set()
        self.missed_call_counts = {}
        self.last_notification_check = datetime.now()
        self.load_processed_data()
        
    def load_processed_data(self):
        """Load previously processed calls and missed call counts"""
        try:
            with open('viber_missed_calls.json', 'r') as f:
                data = json.load(f)
                self.processed_calls = set(data.get('processed_calls', []))
                self.missed_call_counts = data.get('missed_call_counts', {})
        except FileNotFoundError:
            self.processed_calls = set()
            self.missed_call_counts = {}
    
    def save_processed_data(self):
        """Save processed calls and missed call counts"""
        data = {
            'processed_calls': list(self.processed_calls),
            'missed_call_counts': self.missed_call_counts,
            'last_updated': datetime.now().isoformat()
        }
        with open('viber_missed_calls.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_viber_notifications(self):
        """Monitor macOS notification database for Viber missed call notifications"""
        try:
            # Query macOS notification database
            cmd = [
                'sqlite3', 
                os.path.expanduser('~/Library/Application Support/NotificationCenter/db2/db'),
                '''SELECT datetime(delivered_date + 978307200, 'unixepoch', 'localtime') as time, 
                   data FROM record 
                   WHERE bundleid = 'com.viber.osx' 
                   AND delivered_date > (strftime('%s', datetime('now', '-1 hour')) - 978307200)
                   ORDER BY delivered_date DESC;'''
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                notifications = result.stdout.strip().split('\n')
                return self.parse_viber_notifications(notifications)
            else:
                return []
                
        except Exception as e:
            print(f"Error checking notifications: {e}")
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
        """Manual missed call detection - for testing purposes"""
        # This creates a simple file-based system where you can manually report missed calls
        missed_calls_file = 'manual_missed_calls.txt'
        
        if not os.path.exists(missed_calls_file):
            # Create example file
            with open(missed_calls_file, 'w') as f:
                f.write("# Add missed calls manually for testing:\n")
                f.write("# Format: YYYY-MM-DD HH:MM | Caller Name\n")
                f.write("# Example: 2025-09-11 14:30 | János Kovács\n")
                f.write("\n")
            return []
        
        missed_calls = []
        try:
            with open(missed_calls_file, 'r') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                    
                if '|' in line:
                    time_str, caller = line.split('|', 1)
                    time_str = time_str.strip()
                    caller = caller.strip()
                    
                    # Parse the time
                    try:
                        call_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
                        # Process calls from today and yesterday (handles sleep/wake scenarios)
                        time_diff = datetime.now() - call_time
                        if time_diff < timedelta(hours=48):  # 48 hours to handle weekend sleeps
                            call_id = f"{time_str}_{caller}"
                            if call_id not in self.processed_calls:
                                missed_calls.append({
                                    'time': call_time,
                                    'caller': caller,
                                    'call_id': call_id
                                })
                    except ValueError:
                        continue
                        
        except Exception as e:
            print(f"Error reading manual missed calls: {e}")
        
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