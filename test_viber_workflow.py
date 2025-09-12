#!/usr/bin/env python3
"""
Test script to demonstrate the Viber missed call → Calendar workflow
"""

from datetime import datetime, timedelta
from google_auth import GoogleAPIAuth
import subprocess

def create_test_calendar_event():
    """Create a test calendar event to demonstrate the workflow"""
    
    print("🧪 Testing Viber Missed Call → Calendar Workflow")
    print("=" * 50)
    
    # Initialize Google Calendar
    auth = GoogleAPIAuth()
    calendar = auth.get_calendar_service()
    
    # Simulate a missed call
    caller_name = "Teszt János"
    call_time = datetime.now() - timedelta(minutes=5)  # 5 minutes ago
    missed_count = 1
    
    print(f"📞 Simulating missed call from: {caller_name}")
    print(f"Call time: {call_time.strftime('%H:%M:%S')}")
    
    # Calculate follow-up time (15 minutes after call)
    followup_time = call_time + timedelta(minutes=15)
    
    print(f"📅 Creating calendar reminder for: {followup_time.strftime('%H:%M:%S')}")
    
    # Create calendar event in English
    title = f"📞 Call back: {caller_name}"
    description = f"Follow-up for missed call\n\n" \
                f"Caller: {caller_name}\n" \
                f"Missed call time: {call_time.strftime('%H:%M')}\n" \
                f"Number of missed calls: {missed_count}"
    
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
    
    try:
        created_event = calendar.events().insert(
            calendarId='primary', 
            body=event
        ).execute()
        
        print(f"✅ Calendar event created successfully!")
        print(f"   Title: {title}")
        print(f"   Time: {followup_time.strftime('%H:%M')} ({followup_time.strftime('%Y-%m-%d')})")
        print(f"   Event ID: {created_event['id'][:15]}...")
        
        # Send notification
        send_test_notification(caller_name, call_time, followup_time)
        
        print(f"\n🎯 Workflow completed successfully!")
        print(f"📱 Check your Google Calendar for the reminder")
        print(f"🔔 You should have received a macOS notification")
        
        return created_event['id']
        
    except Exception as e:
        print(f"❌ Error creating calendar event: {e}")
        return None

def send_test_notification(caller_name, call_time, followup_time):
    """Send test notification"""
    title = f"Viber: Missed call"
    subtitle = f"{caller_name}"
    message = f"Missed: {call_time.strftime('%H:%M')}\n✅ Callback scheduled: {followup_time.strftime('%H:%M')}"
    
    applescript = f'''
    display notification "{message}" with title "{title}" subtitle "{subtitle}"
    '''
    
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"📱 Notification sent: {caller_name}")
    except Exception as e:
        print(f"⚠️ Notification error: {e}")

def test_multiple_calls():
    """Test multiple missed calls from same person"""
    print(f"\n🔄 Testing multiple missed calls scenario...")
    
    auth = GoogleAPIAuth()
    calendar = auth.get_calendar_service()
    
    caller_name = "Anna Kovács"
    call_time = datetime.now() - timedelta(minutes=2)
    missed_count = 3  # Third missed call
    followup_time = call_time + timedelta(minutes=15)
    
    # Escalated event for multiple calls in English
    title = f"📞 URGENT - Call back: {caller_name} ({missed_count}x)"
    description = f"MULTIPLE missed calls - follow-up required!\n\n" \
                f"Caller: {caller_name}\n" \
                f"Last missed call: {call_time.strftime('%H:%M')}\n" \
                f"Number of missed calls: {missed_count}\n" \
                f"⚠️ Multiple attempts - might be important!"
    
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
    
    try:
        created_event = calendar.events().insert(
            calendarId='primary', 
            body=event
        ).execute()
        
        print(f"✅ URGENT calendar event created!")
        print(f"   Title: {title}")
        print(f"   Event ID: {created_event['id'][:15]}...")
        
        # Send urgent notification
        urgent_title = f"Viber: {missed_count}x Elmulasztott hívás!"
        urgent_subtitle = f"{caller_name} - SÜRGŐS"
        urgent_message = f"Utolsó hívás: {call_time.strftime('%H:%M')}\n⚠️ {missed_count} elmulasztott hívás!\n✅ Visszahívási emlékeztető: {followup_time.strftime('%H:%M')}"
        
        applescript = f'''
        display notification "{urgent_message}" with title "{urgent_title}" subtitle "{urgent_subtitle}"
        '''
        
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"📱 URGENT notification sent!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test basic workflow
    create_test_calendar_event()
    
    # Test multiple calls scenario
    test_multiple_calls()
    
    print(f"\n🎉 All tests completed!")
    print(f"📅 Check your Google Calendar for 2 new events")
    print(f"🔔 You should have received 2 macOS notifications")