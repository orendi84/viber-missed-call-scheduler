# 🤝 Contributing to Viber Missed Call Scheduler

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Development Tips](#development-tips)

## 🤖 Code of Conduct

This project follows a simple principle: **Be respectful, be helpful, be collaborative.**

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- macOS 10.14+ (for full functionality)
- Python 3.8+
- Google account for API access
- Basic knowledge of Python and APIs

### First Steps

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/viber-missed-call-scheduler.git
   cd viber-missed-call-scheduler
   ```
3. **Set up the development environment** (see below)

## 🔧 Development Setup

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Set Up Google APIs
- Create a project in [Google Cloud Console](https://console.cloud.google.com)
- Enable Calendar API and Gmail API
- Create OAuth 2.0 credentials
- Download `credentials.json` to project root
- Run authentication: `python3 google_auth.py`

### 3. Test the Setup
```bash
python3 test_viber_workflow.py
```

### 4. Run the Main System
```bash
python3 viber_missed_calls_v2.py
```

## 📝 Contributing Guidelines

### Types of Contributions

We welcome contributions in these areas:

#### 🐛 Bug Fixes
- Fix timezone handling issues
- Resolve calendar API errors
- Improve error handling
- Fix notification problems

#### ✨ New Features
- Support for additional messaging apps (WhatsApp, Telegram, etc.)
- Web interface for management
- Mobile app integration
- Advanced scheduling options
- Analytics and reporting

#### 📚 Documentation
- Improve setup instructions
- Add troubleshooting guides
- Create video tutorials
- Enhance code comments

#### 🧪 Testing
- Add unit tests
- Create integration tests
- Improve test coverage
- Add performance tests

### Development Standards

#### Code Style
- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

#### Security
- **Never commit sensitive data** (credentials, tokens, personal info)
- Always use `.gitignore` for sensitive files
- Follow OAuth best practices
- Validate all user inputs

#### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update LLM_CONTEXT.md for architectural changes
- Include usage examples

## 🔄 Pull Request Process

### Before Submitting

1. **Test thoroughly** - Ensure your changes work
2. **Update documentation** - Keep docs in sync
3. **Follow code style** - Consistent formatting
4. **Check security** - No sensitive data committed

### Submission Steps

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/amazing-new-feature
   ```

2. **Make your changes** with clear commit messages:
   ```bash
   git commit -m "Add support for WhatsApp missed calls
   
   - Implement WhatsApp notification parsing
   - Add configuration for WhatsApp integration
   - Update documentation with WhatsApp setup
   
   🤖 Generated with [Claude Code](https://claude.ai/code)"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/amazing-new-feature
   ```

4. **Create Pull Request** on GitHub with:
   - Clear description of changes
   - Screenshots/demos if applicable
   - Link to related issues
   - Testing instructions

### Review Process

1. **Automated checks** will run (future: CI/CD)
2. **Manual review** by maintainers
3. **Feedback incorporation** if needed
4. **Merge** when approved

## 🐛 Issue Reporting

### Bug Reports

Use this template for bug reports:

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen.

**Actual Behavior**
What actually happens.

**Environment**
- macOS version:
- Python version:
- Package versions:

**Screenshots/Logs**
Include relevant screenshots or log files.
```

### Feature Requests

Use this template for feature requests:

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How do you think this should work?

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Any other relevant information.
```

## 💻 Development Tips

### Understanding the Codebase

1. **Start with `LLM_CONTEXT.md`** - Comprehensive technical overview
2. **Read the main README.md** - User-facing documentation  
3. **Run the test workflow** - See the system in action
4. **Check existing issues** - See what's being worked on

### Common Development Tasks

#### Adding a New Messaging App

1. **Extend input parsing** in `check_manual_missed_calls()`
2. **Add app-specific logic** for notifications
3. **Update documentation** with setup instructions
4. **Add test cases** for the new app

#### Modifying Calendar Behavior

1. **Update `create_calendar_followup()`** for event creation
2. **Modify `get_next_callback_time()`** for scheduling logic
3. **Test timezone handling** thoroughly
4. **Update examples** in documentation

#### Improving Error Handling

1. **Add try-catch blocks** around API calls
2. **Provide meaningful error messages** to users
3. **Log errors appropriately** for debugging
4. **Test error conditions** thoroughly

### Testing Your Changes

#### Manual Testing
```bash
# Test basic functionality
python3 test_viber_workflow.py

# Test with real data
echo "2025-12-25 10:00 | Test Contact" >> manual_missed_calls.txt
python3 viber_missed_calls_v2.py

# Check calendar events created
# Check logs for errors
```

#### Automated Testing (Future)
```bash
# Run unit tests
python3 -m pytest tests/

# Run integration tests  
python3 -m pytest tests/integration/

# Check code coverage
coverage run -m pytest
coverage report
```

## 🔒 Security Guidelines

### What NOT to Commit
- `credentials.json` - Google API credentials
- `token.json` - OAuth access tokens  
- `*.log` files - May contain personal data
- `viber_missed_calls.json` - User's call history
- Personal `manual_missed_calls.txt` files

### What IS Safe to Commit
- Source code files (`*.py`)
- Documentation (`*.md`)
- Configuration templates
- Example files (sanitized)
- Test files (with mock data)

### Best Practices
- Always review your changes before committing
- Use `git diff` to check what you're committing
- Test with example data, not real personal data
- Follow the principle of least privilege for API access

## 🆘 Getting Help

### Resources
- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and general discussion
- **Documentation** - Start with README.md and LLM_CONTEXT.md

### Response Times
- **Issues**: Usually within 48 hours
- **Pull Requests**: Within 1 week for initial review
- **Questions**: Best effort, usually within a few days

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributors graph

Thank you for helping make this project better! 🚀

---

*This contributing guide was crafted to be helpful for both human developers and LLMs working with the codebase.*