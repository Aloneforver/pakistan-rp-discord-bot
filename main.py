import asyncio
import sys
import logging
import os
from pathlib import Path

# Import keep-alive server
from web_server import keep_alive

# Fix Unicode encoding issues on Windows FIRST
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Create necessary directories FIRST (before logging setup)
directories = ['logs', 'backups', 'transcripts', 'rule_database', 'automation', 'announcements', 'database']
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# NOW setup logging (after directories exist)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)

# Ensure we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.community_bot import PakistanRPCommunityBot
    from config.settings import Config
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Please ensure all files are in the correct directories")
    sys.exit(1)

async def main():
    """Main bot startup function"""
    try:
        # Start the keep-alive web server
        print("🌐 Starting keep-alive web server...")
        keep_alive()
        
        # Validate configuration
        if not Config.validate_environment():
            print("❌ Environment configuration incomplete. Check .env file.")
            sys.exit(1)
        
        # Display startup banner
        print(f"""
╔═══════════════════════════════════════════╗
║    🇵🇰 PAKISTAN RP COMMUNITY BOT 2.0        ║
║         Advanced Automation System         ║
╠═══════════════════════════════════════════╣
║ 📊 Server ID: {Config.GUILD_ID:<25} ║
║ 🎫 Ticket System: Enhanced & Automated    ║
║ 📋 Rule Database: Searchable & Smart      ║
║ 🎛️ Dashboards: Modern UI/UX              ║
║ ⚡ Automation: Maximum Efficiency         ║
║ 🚫 AI Dependency: Completely Removed      ║
║ 🌐 Keep-Alive Server: Active              ║
╚═══════════════════════════════════════════╝
        """)
        
        print("🔄 Initializing Pakistan RP Community Bot...")
        
        # Initialize and start bot
        bot = PakistanRPCommunityBot()
        async with bot:
            await bot.start(Config.BOT_TOKEN)
            
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown requested by user")
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        logging.error(f"Bot startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())