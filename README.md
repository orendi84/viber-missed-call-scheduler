# 📞 Viber Missed Call Scheduler

**Never forget to call someone back again!** 

This automated system monitors Viber missed calls and creates smart calendar reminders scheduled from 6 PM onward with intelligent conflict detection.

## ✨ Features

- 🕕 **Smart 6 PM Scheduling**: All callbacks scheduled from 6:00 PM onward in 15-minute increments
- 🔍 **Intelligent Conflict Detection**: Automatically finds next available time slot
- 📅 **Google Calendar Integration**: Creates 15-minute follow-up events automatically
- 🌍 **Multi-language Support**: English calendar events with proper timezone handling
- 💤 **Sleep/Wake Handling**: Processes missed calls that happened while Mac was sleeping
- 📱 **macOS Notifications**: System notifications for each processed call
- 🔢 **Call Counting**: Tracks multiple missed calls from the same person
- 🚀 **Auto-Recovery**: Automatic restart and monitoring service

## 🎯 How It Works

1. **Miss a Viber call** → Add it to `manual_missed_calls.txt`
2. **System detects** the missed call within 30 seconds  
3. **Calendar event created** at next available 6 PM+ slot (18:00, 18:15, 18:30...)
4. **Notification sent** to inform you of the scheduled callback
5. **Never miss** following up with important calls!

## 🚀 Quick Start

### Prerequisites

- macOS (tested on macOS 14+)
- Python 3.9+ (zoneinfo; the tzdata package covers Windows and minimal environments)
- Google Account with Calendar API access
- Viber installed (optional - system works with manual input)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/viber-missed-call-scheduler.git
cd viber-missed-call-scheduler
```

2. **Install dependencies**
```bash
pip3 install -r requirements.txt
```

3. **Set up Google Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable Calendar API and Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to project directory

4. **Run the setup**
```bash
python3 google_auth.py
```
   - This will open browser for Google authentication
   - Grant access to Calendar and Gmail APIs

### Usage

**Option 1: Manual Start (Testing)**
```bash
python3 viber_missed_calls_v2.py
```

**Option 2: Auto-Start Service (Production)**
```bash
python3 viber_auto_start.py &
```

**Option 3: Always-On Service**
- Add `viber_auto_start.py` to macOS Login Items
- System Preferences → Users & Groups → Login Items

### Adding Missed Calls

Edit `manual_missed_calls.txt` and add calls in this format:
```
2025-09-12 14:30 | John Smith
2025-09-12 16:45 | Maria Garcia  
2025-09-12 17:20 | David Wilson
```

The system will automatically:
- 📅 Create calendar events at 18:00, 18:15, 18:30
- 🔔 Send macOS notifications
- 📊 Track call counts per person
- ⚡ Process within 30 seconds

## 📋 Configuration

### Time Settings
- **Base time**: 6:00 PM (18:00) local time
- **Increment**: 15-minute slots
- **Duration**: 15-minute events
- **Range**: Up to 10:00 PM (fallback to 10 PM if no slots)

### File Locations
- `manual_missed_calls.txt` - Input file for missed calls
- `viber_missed_calls.json` - Processed calls database
- `viber_auto_start.log` - Auto-start service logs
- `viber_monitor.log` - Main monitoring logs

## 🔒 Security & Privacy

- ✅ **Local processing only** - No data sent to external servers
- ✅ **OAuth2 secure authentication** with Google APIs
- ✅ **Sensitive files excluded** from git via `.gitignore`
- ✅ **No credential storage** in repository
- ✅ **Privacy-first design** - You control all data

## 🛠️ Advanced Features

### Sleep/Wake Handling
The system automatically handles Mac sleep/wake scenarios:
- Detects when system was offline for >2 hours
- Processes backlog of missed calls from last 48 hours
- Schedules all missed callbacks appropriately

### Auto-Recovery
- Monitors main process every 5 minutes
- Automatically restarts if monitoring stops
- Handles crashes and system interruptions
- Persistent operation across reboots

### Smart Scheduling
```
Example: 3 missed calls at 2:30 PM
→ Callback 1: 18:00 (Emma Thompson)
→ Callback 2: 18:15 (David Miller)  
→ Callback 3: 18:30 (Sophie Chen)
```

## 📊 System Status

View current system status:
```bash
python3 viber_missed_calls_v2.py view
```

Check auto-start logs:
```bash
tail -f viber_auto_start.log
```

## 🔧 Troubleshooting

### Common Issues

**"No module named 'google'"**
```bash
pip3 install -r requirements.txt
```

**"Credentials not found"**
- Ensure `credentials.json` is in project directory
- Run `python3 google_auth.py` for setup

**"Calendar events not appearing"**
- Check Google Calendar web interface
- Verify timezone settings (Europe/Budapest)
- Ensure primary calendar is selected

**"System not detecting calls"**
- Verify `manual_missed_calls.txt` format
- Check file is in project directory
- Ensure times are within 48-hour window

### Logs
Check logs for debugging:
- `viber_auto_start.log` - Auto-start service
- `viber_monitor.log` - Main monitoring system
- Console output when running manually

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Calendar API for calendar integration
- Viber for missed call inspiration
- macOS notification system for alerts

## 📞 Support

If you find this project helpful, please ⭐ star it on GitHub!

For issues or questions:
- Create an [Issue](https://github.com/YOUR_USERNAME/viber-missed-call-scheduler/issues)
- Check existing [Discussions](https://github.com/YOUR_USERNAME/viber-missed-call-scheduler/discussions)

---

**Made with ❤️ for better call management**