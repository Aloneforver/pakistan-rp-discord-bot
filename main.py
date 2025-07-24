import asyncio
import sys
import logging
import os
from pathlib import Path
from threading import Thread

# Import keep-alive server
from web_server import keep_alive

# Fix Unicode encoding issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Create necessary directories FIRST (before logging setup)
directories = ['logs', 'backups', 'transcripts', 'rule_database', 'automation', 'announcements', 'database']
for directory in directories:
    os.makedirs(directory, exist_ok=True)

# Setup logging
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

# Keep-alive function for Glitch
def keep_alive_glitch():
    def run():
        keep_alive()
    
    Thread(target=run, daemon=True).start()

async def main():
    """Main bot startup function"""
    try:
        # Start the keep-alive web server for Glitch
        print("🌐 Starting multi-endpoint web server for Glitch...")
        keep_alive_glitch()
        
        # Small delay to let server start
        await asyncio.sleep(2)
        
        # Validate configuration
        if not Config.validate_environment():
            print("❌ Environment configuration incomplete. Check Glitch .env file.")
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
║ 🌐 Multi-Endpoint Server: Active          ║
║ 🖥️ Platform: Glitch Hosting               ║
║ 📡 Strategy: Staggered Monitoring         ║
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
    # Start the bot
    asyncio.run(main())
