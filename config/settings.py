import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for Pakistan RP Community Bot"""
    
    # ========================
    # CORE BOT SETTINGS
    # ========================
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
    BOT_STATUS = os.getenv('BOT_STATUS', 'Pakistan RP Community')
    BOT_ACTIVITY_TYPE = os.getenv('BOT_ACTIVITY_TYPE', 'watching')  # watching, playing, listening
    
    # ========================
    # SERVER CONFIGURATION
    # ========================
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    
    # ========================
    # CHANNEL IDS
    # ========================
    TICKETS_CATEGORY_ID = int(os.getenv('TICKETS_CATEGORY_ID', 0))
    RULES_CHANNEL_ID = int(os.getenv('RULES_CHANNEL_ID', 0))
    ANNOUNCEMENTS_CHANNEL_ID = int(os.getenv('ANNOUNCEMENTS_CHANNEL_ID', 0))
    STAFF_CHAT_ID = int(os.getenv('STAFF_CHAT_ID', 0))
    TICKET_LOGS_CHANNEL_ID = int(os.getenv('TICKET_LOGS_CHANNEL_ID', 0))
    STAFF_LOGS_CHANNEL_ID = int(os.getenv('STAFF_LOGS_CHANNEL_ID', 0))
    
    # ========================
    # ROLE IDS
    # ========================
    ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', 0))
    SENIOR_STAFF_ROLE_ID = int(os.getenv('SENIOR_STAFF_ROLE_ID', 0))
    STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID', 0))
    MODERATOR_ROLE_ID = int(os.getenv('MODERATOR_ROLE_ID', 0))
    HELPER_ROLE_ID = int(os.getenv('HELPER_ROLE_ID', 0))
    
    # ========================
    # TICKET SYSTEM SETTINGS
    # ========================
    MAX_OPEN_TICKETS_PER_USER = int(os.getenv('MAX_OPEN_TICKETS_PER_USER', 3))
    TICKET_AUTO_CLOSE_HOURS = int(os.getenv('TICKET_AUTO_CLOSE_HOURS', 72))  # 3 days
    TICKET_CLEANUP_ENABLED = os.getenv('TICKET_CLEANUP_ENABLED', 'true').lower() == 'true'
    
    # ========================
    # RULE SYSTEM SETTINGS
    # ========================
    RULES_SEARCH_LIMIT = int(os.getenv('RULES_SEARCH_LIMIT', 15))
    RULES_AUTO_BACKUP = os.getenv('RULES_AUTO_BACKUP', 'true').lower() == 'true'
    
    # ========================
    # PUNISHMENT SYSTEM
    # ========================
    PUNISHMENT_TYPES = {
        "warning": {"display": "⚠️ Warning", "color": 0xFFA500},
        "mute": {"display": "🔇 Mute", "color": 0xFF6B6B},
        "kick": {"display": "👢 Kick", "color": 0xE74C3C},
        "temp_ban": {"display": "⏰ Temporary Ban", "color": 0xE74C3C},
        "perm_ban": {"display": "🔒 Permanent Ban", "color": 0x8B0000},
        "fine": {"display": "💰 Fine", "color": 0xF39C12},
        "vehicle_impound": {"display": "🚗 Vehicle Impound", "color": 0x9B59B6},
        "gang_warning": {"display": "🏢 Gang Warning", "color": 0xFF8C00},
        "gang_suspension": {"display": "⏸️ Gang Suspension", "color": 0xDC143C},
        "gang_dissolution": {"display": "💥 Gang Dissolution", "color": 0x8B0000},
        "mass_ban": {"display": "🚫 Mass Ban", "color": 0x800000}
    }
    
    # ========================
    # AUTOMATION SETTINGS
    # ========================
    AUTO_CLEANUP_ENABLED = os.getenv('AUTO_CLEANUP_ENABLED', 'true').lower() == 'true'
    AUTO_BACKUP_INTERVAL_HOURS = int(os.getenv('AUTO_BACKUP_INTERVAL_HOURS', 6))
    AUTO_STATISTICS_UPDATE_MINUTES = int(os.getenv('AUTO_STATISTICS_UPDATE_MINUTES', 15))
    
    # ========================
    # ANNOUNCEMENT SETTINGS
    # ========================
    ANNOUNCEMENT_COOLDOWN_MINUTES = int(os.getenv('ANNOUNCEMENT_COOLDOWN_MINUTES', 30))
    MAX_ANNOUNCEMENT_LENGTH = int(os.getenv('MAX_ANNOUNCEMENT_LENGTH', 2000))
    
    # ========================
    # DATABASE SETTINGS
    # ========================
    DATABASE_CLEANUP_DAYS = int(os.getenv('DATABASE_CLEANUP_DAYS', 30))
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 90))
    
    @staticmethod
    def validate_environment():
        """Validate that all required environment variables are set"""
        required_vars = [
            'BOT_TOKEN',
            'GUILD_ID',
            'ADMIN_ROLE_ID',
            'STAFF_ROLE_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Validate numeric values
        try:
            Config.GUILD_ID = int(os.getenv('GUILD_ID'))
            if Config.GUILD_ID == 0:
                print("❌ GUILD_ID must be a valid Discord server ID")
                return False
        except (ValueError, TypeError):
            print("❌ GUILD_ID must be a valid integer")
            return False
        
        print("✅ Environment configuration validated")
        return True
    
    @staticmethod
    def get_punishment_display(punishment_type: str) -> dict:
        """Get display information for punishment type"""
        return Config.PUNISHMENT_TYPES.get(punishment_type.lower(), {
            "display": f"❓ {punishment_type.title()}",
            "color": 0x95A5A6
        })
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """Format duration in minutes to human readable format"""
        if minutes is None or minutes == 0:
            return "Permanent"
        
        if minutes < 60:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif minutes < 1440:  # Less than 24 hours
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours}h {remaining_minutes}m"
        else:  # 24 hours or more
            days = minutes // 1440
            remaining_hours = (minutes % 1440) // 60
            if remaining_hours == 0:
                return f"{days} day{'s' if days != 1 else ''}"
            else:
                return f"{days}d {remaining_hours}h"