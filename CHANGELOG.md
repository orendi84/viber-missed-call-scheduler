# 📝 Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web interface for missed call management
- Support for additional messaging apps (WhatsApp, Telegram)
- Mobile app integration
- Advanced analytics and reporting

## [2.0.0] - 2025-09-12

### Added
- 🌅 **Sleep/Wake Handling**: System detects offline periods and processes backlog
- 🔄 **Auto-Recovery Service**: `viber_auto_start.py` monitors and restarts the system
- 🌍 **Timezone Support**: Proper handling of Europe/Budapest timezone
- 📊 **Extended Processing Window**: Now handles calls from last 48 hours
- 🔍 **Smart Conflict Detection**: Improved calendar slot detection algorithm
- 📱 **Enhanced Notifications**: Better macOS notification formatting
- 🔢 **Call Counting**: Tracks multiple missed calls from same person
- 📝 **Comprehensive Logging**: Auto-start and monitoring logs
- 🤖 **LLM Documentation**: Added LLM_CONTEXT.md for AI assistance

### Changed
- **Calendar Events**: All events now created in English language
- **Scheduling Logic**: Moved from immediate 15-minute scheduling to 6 PM+ scheduling
- **Time Window**: Extended from 1 hour to 48 hours for processing missed calls
- **Error Handling**: Improved error messages and recovery mechanisms

### Fixed
- ⏰ **Timezone Issues**: Fixed UTC/local time conflicts in calendar API
- 📅 **Calendar Conflicts**: Proper detection of existing events
- 🔄 **Duplicate Prevention**: Better tracking of processed calls
- 💤 **Sleep Recovery**: System properly handles Mac sleep/wake cycles
- 🔀 **Process Management**: Prevents multiple monitoring processes

### Security
- 🔒 **Enhanced .gitignore**: Comprehensive protection of sensitive data
- 🛡️ **Credential Safety**: Improved OAuth token handling
- 📝 **Data Privacy**: Local-only processing, no external data transmission

## [1.0.0] - 2025-09-11

### Added
- 📞 **Core Functionality**: Basic missed call to calendar event conversion
- 📅 **Google Calendar Integration**: OAuth2 authentication and event creation
- 📧 **Gmail API Support**: Foundation for email-based notifications
- 📱 **macOS Notifications**: System notifications for processed calls
- 📝 **Manual Input System**: File-based missed call entry
- 🔧 **Basic Configuration**: Initial setup and authentication scripts

### Features
- Manual missed call entry via `manual_missed_calls.txt`
- 15-minute calendar events creation
- Google Calendar API integration
- Basic OAuth2 authentication
- Simple notification system

### Technical
- Python 3.8+ compatibility
- Google API client integration
- Basic error handling
- File-based state management

---

## 📋 Version History Summary

- **v2.0.0**: Production-ready with sleep/wake handling and auto-recovery
- **v1.0.0**: Initial working prototype with basic functionality

## 🚀 Upgrade Notes

### From v1.0.0 to v2.0.0

**Breaking Changes:**
- Scheduling moved from immediate to 6 PM+ slots
- Configuration file format may have changed

**Migration Steps:**
1. Backup your `viber_missed_calls.json` file
2. Update to new version
3. Run `python3 viber_auto_start.py &` for auto-recovery
4. Check new LLM_CONTEXT.md for technical details

**New Features:**
- Start using the auto-recovery service for production
- Benefit from sleep/wake handling automatically
- English calendar events (no manual change needed)

## 🔗 Links

- [GitHub Releases](https://github.com/YOUR_USERNAME/viber-missed-call-scheduler/releases)
- [Issues](https://github.com/YOUR_USERNAME/viber-missed-call-scheduler/issues)
- [Contributing Guidelines](CONTRIBUTING.md)
- [License](LICENSE)