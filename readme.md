# 🇵🇰 Pakistan RP Community Bot 2.0

**Advanced Automation System for Discord Community Management**

A powerful, feature-rich Discord bot designed specifically for Pakistan RP servers with advanced ticket management, rule database system, automated punishments, staff tools, and comprehensive community management features.

## ✨ Features

### 🎫 **Advanced Ticket System**
- **Category-Based Support**: Support, Player Reports, Bug Reports, Gang Registration, Shop, Other
- **Automated Responses**: Instant category-specific guidance
- **Priority Levels**: Low, Medium, High, Critical with different response times
- **Smart Assignment**: Auto-assign based on category and staff availability
- **Complete Transcripts**: Full conversation logs saved and sent via DM
- **Auto-Close**: Inactive tickets automatically closed after configurable time
- **Staff Management**: Advanced ticket oversight and bulk operations

### 📋 **Smart Rule Database**
- **300+ Rules Supported**: Comprehensive rule management system
- **Advanced Search**: Keyword-based search with relevance scoring
- **Category System**: 8 main categories with 40+ subcategories
- **Punishment System**: Detailed punishment tracking with:
  - First, Second, Third offense penalties
  - Time periods (minutes/hours/days)
  - Fine amounts (in-game currency)
  - Appeal processes
  - Staff discretion levels
- **Real-time Updates**: Rules updated instantly across the server

### 🎛️ **Beautiful Dashboards**
- **Ticket Creation Dashboard**: User-friendly ticket creation interface
- **Rule Search Dashboard**: Interactive rule browsing and searching
- **Staff Command Center**: Comprehensive staff management tools
- **Mobile Friendly**: Works perfectly on all devices
- **Auto-Deploy**: Commands to instantly deploy all dashboards

### 📢 **Announcement System**
- **Template System**: Pre-made templates for common announcements
- **Rich Formatting**: Beautiful embeds with server branding
- **Permission Controls**: Admin-only access with ping restrictions
- **Cooldown System**: Prevents announcement spam
- **Audit Logging**: Complete announcement tracking

### ⚡ **Advanced Automation**
- **Ticket Auto-Close**: Automatically close inactive tickets
- **Database Backups**: Regular automated backups
- **Warning Expiration**: Auto-expire old warnings
- **Data Cleanup**: Remove old logs and records
- **Performance Monitoring**: System health tracking
- **Violation Tracking**: Repeat offender detection

### 👮 **Permission System**
- **Role Hierarchy**: Member → Helper → Moderator → Staff → Senior Staff → Admin
- **Granular Permissions**: Specific permissions for each action
- **Punishment Authorization**: Role-based punishment permissions
- **Staff Protection**: Staff cannot punish equal/higher rank members
- **Audit Logging**: Complete permission check logging

### 📊 **Analytics & Reporting**
- **Live Statistics**: Real-time system metrics
- **Performance Reports**: Detailed analytics dashboards
- **Usage Tracking**: Feature usage monitoring
- **Error Reporting**: Comprehensive error tracking
- **Success Metrics**: Ticket resolution rates and response times

## 🚀 Quick Setup

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- Discord Server with Admin permissions

### Installation

1. **Clone/Download the Bot**
   ```bash
   git clone <repository-url>
   cd pakistan-rp-bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   - Copy `.env.template` to `.env`
   - Fill in all required values (see Configuration section)

4. **Run the Bot**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Required Settings

#### Bot Token
1. Go to https://discord.com/developers/applications
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Add the token to your `.env` file

#### Server Setup
1. Enable Developer Mode in Discord
2. Right-click your server → "Copy ID" → Add to `GUILD_ID`
3. Create/identify required channels and add their IDs
4. Create/identify required roles and add their IDs

#### Channel IDs Required
- `TICKETS_CATEGORY_ID` - Category for ticket channels
- `RULES_CHANNEL_ID` - Channel for rule database
- `ANNOUNCEMENTS_CHANNEL_ID` - Channel for announcements
- `STAFF_CHAT_ID` - Staff-only channel

#### Role IDs Required
- `ADMIN_ROLE_ID` - Highest permission level
- `SENIOR_STAFF_ROLE_ID` - Senior staff role
- `STAFF_ROLE_ID` - Regular staff role
- `MODERATOR_ROLE_ID` - Moderator role
- `HELPER_ROLE_ID` - Helper role

### Bot Permissions
Your bot needs these permissions:
- Read Messages/View Channels
- Send Messages
- Manage Messages
- Embed Links
- Attach Files
- Read Message History
- Use Slash Commands
- Manage Channels
- Manage Roles
- Add Reactions
- Use External Emojis

## 📝 Usage Guide

### For Server Members

#### Creating Support Tickets
1. Go to `#ticket-creation` channel
2. Click "🎫 Create Support Ticket"
3. Select category and urgency
4. Describe your issue in detail
5. Wait for staff response in your private ticket channel

#### Searching Rules
1. Go to `#rules` channel
2. Click "🔍 Search Rules" button
3. Enter keywords related to your question
4. Browse results or use category dropdown

### For Staff Members

#### Managing Tickets
1. Go to `#staff-chat` channel
2. Use Staff Dashboard for ticket overview
3. Access individual tickets for management
4. Close tickets with proper documentation

#### Adding Rules (Admins Only)
1. Use Staff Dashboard → Rule Administration
2. Click "➕ Add New Rule"
3. Fill in all required information including:
   - Category and subcategory
   - Rule content and keywords
   - Punishment details for each offense level
   - Appeal information

#### Creating Announcements (Admins Only)
1. Use Staff Dashboard → Announcement System
2. Choose custom announcement or template
3. Fill in required information
4. Review and send

### Admin Commands

#### Slash Commands Available:
- `/setup_dashboards` - Deploy all community dashboards
- `/announce` - Create server announcement
- `/add_rule` - Add new rule to database
- `/bot_stats` - View bot statistics

## 🗂️ File Structure

```
pakistan-rp-bot/
├── main.py                     # Bot entry point
├── config/
│   └── settings.py            # Configuration management
├── core/
│   ├── community_bot.py       # Main bot class
│   ├── database.py           # Database management
│   └── permissions.py        # Permission system
├── systems/
│   ├── ticket_system.py      # Ticket management
│   ├── rule_manager.py       # Rule database
│   ├── announcement_system.py # Announcements
│   └── automation_engine.py  # Automation tasks
├── ui/
│   ├── dashboards.py         # Dashboard manager
│   ├── ticket_views.py       # Ticket interfaces
│   ├── rule_views.py         # Rule interfaces
│   ├── staff_views.py        # Staff interfaces
│   └── announcement_views.py # Announcement interfaces
├── utils/
│   └── helpers.py            # Utility functions
├── database/                 # SQLite database files
├── backups/                  # Automated backups
├── transcripts/              # Ticket transcripts
├── rule_database/            # Rule JSON files
├── automation/               # Automation configs
├── logs/                     # Bot logs
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔧 Customization

### Adding New Rule Categories
1. Edit `rule_manager.py`
2. Add new category to `default_categories`
3. Include emoji, color, and subcategories
4. Restart bot and redeploy dashboards

### Modifying Punishment System
1. Edit rule database entries
2. Update punishment types in `config/settings.py`
3. Adjust staff permission requirements

### Custom Announcement Templates
1. Edit `systems/announcement_system.py`
2. Add new templates to `announcement_templates`
3. Include template fields and formatting

## 📊 Database Schema

The bot uses SQLite with the following main tables:
- `tickets` - Ticket information and status
- `rule_violations` - Punishment tracking
- `user_warnings` - Warning system
- `announcements` - Announcement logs
- `bot_stats` - System statistics
- `action_logs` - Staff action auditing
- `member_data` - User information

## 🛠️ Troubleshooting

### Common Issues

**Bot won't start:**
- Check your bot token is correct
- Verify all required environment variables are set
- Ensure Python 3.8+ is installed

**Dashboards not working:**
- Run `/setup_dashboards` command
- Check channel permissions
- Verify channel IDs in `.env`

**Tickets not creating:**
- Check tickets category permissions
- Verify `TICKETS_CATEGORY_ID` is correct
- Ensure bot can manage channels

**Rules not loading:**
- Check `RULES_CHANNEL_ID` in `.env`
- Verify bot has permissions in rules channel
- Run dashboard setup command

### Support
If you encounter issues:
1. Check the logs in `logs/bot.log`
2. Verify your configuration in `.env`
3. Ensure all permissions are properly set
4. Check Discord API status

## 🔄 Updates & Maintenance

### Regular Maintenance
- Bot automatically creates database backups every 6 hours
- Old logs cleaned up automatically after 90 days
- Ticket transcripts saved permanently
- Statistics updated every 15 minutes

### Manual Maintenance
- Use `/bot_stats` to monitor performance
- Check `#staff-logs` for system messages
- Review ticket resolution rates
- Update rules as needed

## ⚡ Performance

### Optimizations Included
- Efficient database queries with SQLite
- Async operations throughout
- Memory-efficient data structures
- Automatic cleanup tasks
- Caching for frequently accessed data

### Recommended Server Specs
- **Minimum**: 1GB RAM, 1 CPU core
- **Recommended**: 2GB RAM, 2 CPU cores
- **Storage**: 5GB+ for logs and transcripts

## 📈 Analytics

### Metrics Tracked
- Ticket creation and resolution rates
- Rule search usage
- Staff response times
- System uptime and performance
- User engagement statistics
- Error rates and types

### Reports Available
- Daily/weekly/monthly activity reports
- Staff performance analytics
- Popular rule searches
- System health monitoring

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a development branch
3. Install development dependencies:
   ```bash
   pip install black pylint pytest pytest-asyncio
   ```
4. Make your changes
5. Run tests and formatting
6. Submit a pull request

### Code Standards
- Follow PEP 8 Python style guide
- Use type hints where possible
- Include comprehensive docstrings
- Write tests for new features
- Maintain backward compatibility

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Discord.py library developers
- Pakistan RP community for feedback and testing
- All contributors and beta testers

---

**Pakistan RP Community Bot 2.0** - Professional Discord Community Management
**Zero AI Dependency** - **Maximum Automation** - **Enterprise Grade**