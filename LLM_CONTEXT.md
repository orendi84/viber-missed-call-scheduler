# 🤖 LLM Context & Documentation

This document provides comprehensive context for Large Language Models (LLMs) working with this codebase.

## 📋 Project Overview

**Project Name**: Viber Missed Call Scheduler  
**Purpose**: Automated system for scheduling callback reminders in Google Calendar  
**Platform**: macOS with Python 3.8+  
**APIs**: Google Calendar API, Gmail API  

## 🏗️ Architecture

### Core Components

1. **`viber_missed_calls_v2.py`** - Main monitoring and scheduling system
   - Class: `ViberMissedCallTracker`
   - Key methods: `process_missed_calls()`, `create_calendar_followup()`, `get_next_callback_time()`
   - Handles: Sleep/wake detection, calendar conflict resolution, timezone handling

2. **`google_auth.py`** - Google API authentication handler
   - OAuth2 flow management
   - Token refresh and storage
   - Service object creation for Calendar and Gmail APIs

3. **`viber_auto_start.py`** - Auto-recovery monitoring service
   - Process health monitoring
   - Automatic restart capabilities
   - Logging and status tracking

4. **`test_viber_workflow.py`** - Demonstration and testing script
   - Shows complete workflow
   - Creates sample calendar events
   - Tests multiple call scenarios

## 🔧 Key Technical Features

### Smart Scheduling Algorithm
```python
def get_next_callback_time(self, caller_name):
    # Starts from 6 PM (18:00) local time
    # 15-minute increments: 18:00, 18:15, 18:30...
    # Checks calendar conflicts using Google Calendar API
    # Timezone conversion: Europe/Budapest ↔ UTC
```

### Sleep/Wake Handling
- Detects system offline periods >2 hours
- Processes missed calls from last 48 hours on wake
- Maintains state in `viber_missed_calls.json`

### Calendar Integration
- Creates 15-minute events with English titles
- Smart conflict detection and resolution
- Proper timezone handling (Europe/Budapest)
- Popup reminders at event time

## 📁 File Structure

```
viber-missed-call-scheduler/
├── viber_missed_calls_v2.py    # Main system
├── google_auth.py              # Authentication
├── viber_auto_start.py         # Auto-recovery
├── test_viber_workflow.py      # Demo/test
├── start_viber_monitor.sh      # Startup script
├── requirements.txt            # Dependencies
├── README.md                   # User documentation
├── LLM_CONTEXT.md             # This file
├── manual_missed_calls_example.txt  # Input format example
└── .gitignore                 # Security exclusions
```

## 🔒 Security Considerations

### Protected Files (in .gitignore)
- `credentials.json` - Google API credentials
- `token.json` - OAuth2 access tokens
- `*.log` - System logs with potential personal data
- `viber_missed_calls.json` - Processed calls database
- `manual_missed_calls.txt` - User's actual missed calls

### Safe for Repository
- All Python source code
- Documentation files
- Example/template files
- Configuration templates

## 📊 Data Flow

1. **Input**: Manual entry in `manual_missed_calls.txt`
   ```
   Format: YYYY-MM-DD HH:MM | Caller Name
   Example: 2025-09-12 14:30 | John Smith
   ```

2. **Processing**: 
   - Parse missed calls from file
   - Check against processed calls database
   - Calculate next available 6 PM+ time slot
   - Create Google Calendar event

3. **Output**:
   - Calendar event created
   - macOS notification sent
   - Database updated with processed call

## 🚀 Usage Patterns

### Development/Testing
```bash
python3 test_viber_workflow.py  # Demo workflow
python3 viber_missed_calls_v2.py  # Manual run
```

### Production
```bash
python3 viber_auto_start.py &  # Background service
```

### Status Checking
```bash
python3 viber_missed_calls_v2.py view  # Show statistics
tail -f viber_auto_start.log  # Monitor service
```

## 🔄 Common Modifications

### Adding New Messaging Apps
1. Create new input parser in `check_manual_missed_calls()`
2. Add app-specific notification detection
3. Update file format documentation

### Changing Schedule Times
1. Modify `base_time` in `get_next_callback_time()`
2. Adjust time increment (currently 15 minutes)
3. Update timezone if needed

### Calendar Customization
1. Modify event templates in `create_calendar_followup()`
2. Adjust reminder settings
3. Change event duration (currently 15 minutes)

## 🐛 Common Issues & Solutions

### Authentication Problems
- **Issue**: "Credentials not found"
- **Solution**: Run `python3 google_auth.py` to setup OAuth2

### Calendar Events Not Appearing
- **Issue**: Events created but not visible
- **Solution**: Check timezone settings and calendar selection

### Process Not Running
- **Issue**: Monitoring stops after sleep
- **Solution**: Use `viber_auto_start.py` for auto-recovery

### Timezone Issues
- **Issue**: Events scheduled at wrong times  
- **Solution**: Verify Europe/Budapest timezone in code

## 🔍 Debugging Tips

### Enable Verbose Logging
```python
# Add to viber_missed_calls_v2.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Calendar API Responses
```python
# Add after calendar.events().insert()
print(f"Created event: {created_event}")
```

### Monitor File Changes
```bash
# Watch input file for changes
tail -f manual_missed_calls.txt
```

## 📚 Dependencies

### Required Python Packages
```
google-auth==2.23.4
google-auth-oauthlib==1.0.0  
google-auth-httplib2==0.1.1
google-api-python-client==2.108.0
```

### System Requirements
- macOS 10.14+ (for notifications)
- Python 3.8+
- Internet connection for Google APIs
- Google account with Calendar access

## 🎯 Extension Ideas

### Potential Enhancements
1. **Web Interface**: Flask/Django dashboard for management
2. **Mobile App**: iOS/Android companion
3. **CRM Integration**: Salesforce, HubSpot connectors
4. **AI Enhancement**: Smart call prioritization
5. **Team Features**: Shared calendars, delegation
6. **Analytics**: Call patterns, response times

### API Integration Opportunities
1. **Slack**: Team notifications
2. **Microsoft Teams**: Enterprise integration  
3. **Zapier**: Workflow automation
4. **IFTTT**: Consumer automation

## 💡 LLM Usage Notes

When helping users with this codebase:

1. **Always respect security** - Never ask for or help commit sensitive files
2. **Focus on functionality** - The system works well, help with extensions
3. **Explain timezone handling** - This was complex to implement correctly
4. **Emphasize testing** - Use `test_viber_workflow.py` for validation
5. **Check authentication** - Most issues stem from Google API setup

## 📝 Change Log

- **v2.0**: Added sleep/wake handling, timezone fixes, auto-recovery
- **v1.0**: Basic missed call scheduling with Google Calendar integration

---

*This documentation is designed to help LLMs understand the codebase structure, functionality, and common modification patterns.*