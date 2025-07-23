import discord
from discord.ext import commands, tasks
from typing import Optional, Dict, Any, List
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os

try:
    from config.settings import Config
    from core.database import CommunityDatabase
    from core.permissions import AdvancedPermissions
    from systems.ticket_system import AdvancedTicketSystem
    from systems.rule_manager import RuleManagementSystem
    from systems.announcement_system import AnnouncementSystem
    from systems.automation_engine import AutomationEngine
    from ui.dashboards import DashboardManager
    from utils.helpers import create_embed, get_timestamp, format_duration
except ImportError as e:
    print(f"❌ Import error in community_bot.py: {e}")
    raise

class PakistanRPCommunityBot(commands.Bot):
    """Advanced Community Management Bot for Pakistan RP Server"""
    
    def __init__(self):
        intents = discord.Intents.all()
        
        # Activity setup
        activity_type = getattr(discord.ActivityType, Config.BOT_ACTIVITY_TYPE.lower(), discord.ActivityType.watching)
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            status=discord.Status.online,
            activity=discord.Activity(type=activity_type, name=Config.BOT_STATUS),
            help_command=None  # We'll create custom help
        )
        
        # Core systems
        self.db: Optional[CommunityDatabase] = None
        self.permissions: Optional[AdvancedPermissions] = None
        self.tickets: Optional[AdvancedTicketSystem] = None
        self.rules: Optional[RuleManagementSystem] = None
        self.announcements: Optional[AnnouncementSystem] = None
        self.automation: Optional[AutomationEngine] = None
        self.dashboards: Optional[DashboardManager] = None
        
        # Bot state
        self.startup_time = datetime.utcnow()
        self.stats = {
            'tickets_created': 0,
            'tickets_resolved': 0,
            'rules_accessed': 0,
            'announcements_sent': 0,
            'automated_actions': 0
        }
        
    async def setup_hook(self):
        """Initialize all bot systems"""
        try:
            print("🔧 Initializing Pakistan RP Community Systems...")
            
            # Initialize core database
            self.db = CommunityDatabase()
            await self.db.initialize()
            print("✅ Community database initialized")
            
            # Initialize permissions system
            self.permissions = AdvancedPermissions(self)
            print("✅ Advanced permissions system initialized")
            
            # Initialize ticket system
            self.tickets = AdvancedTicketSystem(self)
            await self.tickets.initialize()
            print("✅ Advanced ticket system initialized")
            
            # Initialize rule management system
            self.rules = RuleManagementSystem(self)
            await self.rules.initialize()
            print("✅ Rule management system initialized")
            
            # Initialize announcement system
            self.announcements = AnnouncementSystem(self)
            print("✅ Announcement system initialized")
            
            # Initialize automation engine
            self.automation = AutomationEngine(self)
            await self.automation.initialize()
            print("✅ Automation engine initialized")
            
            # Initialize dashboard manager
            self.dashboards = DashboardManager(self)
            await self.dashboards.initialize()
            print("✅ Dashboard manager initialized")
            
            # Setup persistent views
            await self.setup_persistent_views()
            print("✅ Persistent views registered")
            
            # Load admin commands
            await self.load_admin_commands()
            print("✅ Admin commands loaded")
            
            # Setup automatic dashboards
            await self.setup_community_dashboards()
            print("✅ Community dashboards deployed")
            
            # Start background tasks
            self.start_background_tasks()
            print("✅ Background automation started")
            
            # Sync commands
            guild = discord.Object(id=Config.GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print("✅ Commands synchronized")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            logging.error(f"Bot setup failed: {e}")
            raise
    
    async def setup_persistent_views(self):
        """Register all persistent views for dashboards"""
        try:
            from ui.ticket_views import TicketCreationView, TicketManagementView
            from ui.rule_views import RuleSearchView
            from ui.staff_views import StaffDashboardView
            from ui.announcement_views import AnnouncementView
            
            # Register all persistent views
            self.add_view(TicketCreationView(self))
            # Skip TicketManagementView as it needs a ticket_id
            # self.add_view(TicketManagementView(self))
            self.add_view(RuleSearchView(self))
            self.add_view(StaffDashboardView(self))
            self.add_view(AnnouncementView(self))
            
            print("✅ All persistent views registered")
            
        except Exception as e:
            print(f"⚠️ Persistent views setup failed: {e}")
    
    async def setup_community_dashboards(self):
        """Deploy community dashboards to appropriate channels"""
        try:
            guild = self.get_guild(Config.GUILD_ID)
            if not guild:
                return
            
            # Deploy ticket creation dashboard
            await self.deploy_ticket_dashboard(guild)
            
            # Deploy rule search dashboard  
            await self.deploy_rule_dashboard(guild)
            
            # Deploy staff management dashboard
            await self.deploy_staff_dashboard(guild)
            
        except Exception as e:
            print(f"⚠️ Dashboard deployment failed: {e}")
            logging.error(f"Dashboard deployment error: {e}")
    
    async def deploy_ticket_dashboard(self, guild: discord.Guild):
        """Deploy the ticket creation dashboard"""
        # Find or create ticket creation channel
        ticket_channel = discord.utils.get(guild.text_channels, name="ticket-creation")
        
        if not ticket_channel:
            # Create ticket creation channel (FIXED: using create_text_channel instead of create_category)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    send_messages=False,
                    add_reactions=False,
                    create_public_threads=False
                )
            }
            
            ticket_channel = await guild.create_text_channel(
                name="ticket-creation",
                topic="🎫 Create support tickets here | Read-only channel",
                overwrites=overwrites
            )
            
            print(f"✅ Created #ticket-creation channel")
        
        # Clear existing messages
        try:
            await ticket_channel.purge(limit=100)
        except:
            pass
        
        # Create beautiful ticket creation interface
        embed = discord.Embed(
            title="🎫 PAKISTAN RP SUPPORT CENTER",
            description="Welcome to our automated support system! Click the button below to create a ticket for assistance.",
            color=0x2ECC71,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋 Available Categories",
            value=(
                "🔧 **Support** - General help and questions\n"
                "👤 **Player Report** - Report rule violations\n"
                "🐛 **Bug Report** - Technical issues and bugs\n"
                "🏢 **Gang Registration** - Gang-related requests\n"
                "🛍️ **Shop** - Purchase and transaction issues\n"
                "❓ **Other** - Anything else"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Quick Response Times",
            value="📞 **Support**: ~10 minutes\n📋 **Reports**: ~15 minutes\n🐛 **Bugs**: ~30 minutes",
            inline=True
        )
        
        embed.add_field(
            name="📊 Service Status",
            value="🟢 **All Systems**: Operational\n⚡ **Response Time**: Excellent\n👥 **Staff Online**: Available",
            inline=True
        )
        
        embed.set_footer(text="Pakistan RP Community • Automated Support System")
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        from ui.ticket_views import TicketCreationView
        await ticket_channel.send(embed=embed, view=TicketCreationView(self))
        
        print(f"✅ Ticket dashboard deployed to #{ticket_channel.name}")
    
    async def deploy_rule_dashboard(self, guild: discord.Guild):
        """Deploy the rule search dashboard"""
        # Find rules channel
        rules_channel = guild.get_channel(Config.RULES_CHANNEL_ID) if Config.RULES_CHANNEL_ID else None
        
        if not rules_channel:
            print("⚠️ Rules channel not found, skipping rule dashboard")
            return
        
        # Create rule search interface
        embed = discord.Embed(
            title="📋 PAKISTAN RP RULES DATABASE",
            description="Search through our comprehensive rule database instantly!",
            color=0x3498DB,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔍 How to Search",
            value="Click the **Search Rules** button below and type keywords related to your question.",
            inline=False
        )
        
        embed.add_field(
            name="📚 Rule Categories",
            value="• General Server Rules\n• Roleplay Guidelines\n• Gang Regulations\n• Vehicle Rules\n• Property Guidelines\n• Staff Protocols",
            inline=True
        )
        
        embed.add_field(
            name="📊 Database Stats",
            value=f"📖 **Total Rules**: {await self.rules.get_rule_count() if self.rules else 'Loading...'}\n🔄 **Last Updated**: Recently\n✅ **Status**: Active",
            inline=True
        )
        
        from ui.rule_views import RuleSearchView
        await rules_channel.send(embed=embed, view=RuleSearchView(self))
        
        print(f"✅ Rule dashboard deployed to #{rules_channel.name}")
    
    async def deploy_staff_dashboard(self, guild: discord.Guild):
        """Deploy staff management dashboard"""
        staff_channel = guild.get_channel(Config.STAFF_CHAT_ID) if Config.STAFF_CHAT_ID else None
        
        if not staff_channel:
            print("⚠️ Staff channel not found, skipping staff dashboard")
            return
        
        # Create comprehensive staff dashboard
        embed = discord.Embed(
            title="🎛️ PAKISTAN RP STAFF COMMAND CENTER",
            description="Advanced management tools for Pakistan RP staff team",
            color=0xE74C3C,
            timestamp=datetime.utcnow()
        )
        
        # Get current stats
        active_tickets = len(await self.tickets.get_active_tickets()) if self.tickets else 0
        
        embed.add_field(
            name="📊 Current Status",
            value=f"🎫 **Active Tickets**: {active_tickets}\n👥 **Online Staff**: {len([m for m in guild.members if not m.bot and m.status == discord.Status.online and self.permissions.is_staff(m)])}\n📈 **Server Health**: Excellent",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Quick Actions",
            value="• Ticket Management\n• Rule Administration\n• Announcement System\n• Member Management\n• Server Analytics",
            inline=True
        )
        
        from ui.staff_views import StaffDashboardView
        await staff_channel.send(embed=embed, view=StaffDashboardView(self))
        
        print(f"✅ Staff dashboard deployed to #{staff_channel.name}")
    
    def start_background_tasks(self):
        """Start all background automation tasks"""
        if not self.auto_ticket_cleanup.is_running():
            self.auto_ticket_cleanup.start()
        
        if not self.update_statistics.is_running():
            self.update_statistics.start()
        
        if not self.automated_maintenance.is_running():
            self.automated_maintenance.start()
    
    @tasks.loop(minutes=30)
    async def auto_ticket_cleanup(self):
        """Automatically clean up old tickets"""
        try:
            if self.tickets:
                cleaned = await self.tickets.cleanup_old_tickets()
                if cleaned > 0:
                    self.stats['automated_actions'] += cleaned
                    print(f"🧹 Auto-cleaned {cleaned} old tickets")
        except Exception as e:
            logging.error(f"Auto ticket cleanup error: {e}")
    
    @tasks.loop(minutes=15)
    async def update_statistics(self):
        """Update bot statistics"""
        try:
            if self.db:
                await self.db.update_bot_stats(self.stats)
        except Exception as e:
            logging.error(f"Statistics update error: {e}")
    
    @tasks.loop(hours=6)
    async def automated_maintenance(self):
        """Perform automated maintenance tasks"""
        try:
            if self.db:
                await self.db.cleanup_old_logs()
                self.stats['automated_actions'] += 1
                print("🔧 Automated maintenance completed")
        except Exception as e:
            logging.error(f"Automated maintenance error: {e}")
    
    async def load_admin_commands(self):
        """Load admin-only commands"""
        try:
            @self.tree.command(name="setup_dashboards", description="Setup all community dashboards (Admin only)")
            async def setup_dashboards(interaction: discord.Interaction):
                if not self.permissions.is_admin(interaction.user):
                    await interaction.response.send_message("❌ Admin permission required.", ephemeral=True)
                    return
                
                await interaction.response.defer()
                await self.setup_community_dashboards()
                
                embed = create_embed(
                    "✅ Setup Complete",
                    "All community dashboards have been deployed successfully!",
                    discord.Color.green()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            
            @self.tree.command(name="announce", description="Create a server announcement (Admin only)")
            async def announce(interaction: discord.Interaction, title: str, message: str, ping_everyone: bool = False):
                if not self.permissions.is_admin(interaction.user):
                    await interaction.response.send_message("❌ Admin permission required.", ephemeral=True)
                    return
                
                if self.announcements:
                    success = await self.announcements.create_announcement(title, message, interaction.user, ping_everyone)
                    if success:
                        self.stats['announcements_sent'] += 1
                        await interaction.response.send_message("✅ Announcement sent successfully!", ephemeral=True)
                    else:
                        await interaction.response.send_message("❌ Failed to send announcement.", ephemeral=True)
            
            @self.tree.command(name="add_rule", description="Add a new rule to the database (Admin only)")
            async def add_rule(interaction: discord.Interaction, category: str, title: str, content: str, 
                             subcategory: str = "General", keywords: str = "", priority: str = "medium"):
                if not self.permissions.is_admin(interaction.user):
                    await interaction.response.send_message("❌ Admin permission required.", ephemeral=True)
                    return
                
                if self.rules:
                    # Parse keywords
                    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()] if keywords else []
                    
                    # Default punishments based on priority
                    default_punishments = {
                        "low": {
                            "first_offense": {"type": "warning", "duration": None, "fine": 1000, "details": "Warning + $1,000 fine"},
                            "second_offense": {"type": "warning", "duration": None, "fine": 2500, "details": "Warning + $2,500 fine"},
                            "third_offense": {"type": "mute", "duration": 30, "fine": 5000, "details": "30 min mute + $5,000 fine"},
                            "severe": {"type": "kick", "duration": None, "fine": 10000, "details": "Kick + $10,000 fine"}
                        },
                        "medium": {
                            "first_offense": {"type": "warning", "duration": None, "fine": 2500, "details": "Warning + $2,500 fine"},
                            "second_offense": {"type": "mute", "duration": 60, "fine": 5000, "details": "1 hour mute + $5,000 fine"},
                            "third_offense": {"type": "temp_ban", "duration": 360, "fine": 15000, "details": "6 hour ban + $15,000 fine"},
                            "severe": {"type": "temp_ban", "duration": 1440, "fine": 0, "details": "24 hour ban"}
                        },
                        "high": {
                            "first_offense": {"type": "warning", "duration": None, "fine": 5000, "details": "Warning + $5,000 fine"},
                            "second_offense": {"type": "mute", "duration": 120, "fine": 10000, "details": "2 hour mute + $10,000 fine"},
                            "third_offense": {"type": "temp_ban", "duration": 1440, "fine": 25000, "details": "24 hour ban + $25,000 fine"},
                            "severe": {"type": "perm_ban", "duration": None, "fine": 0, "details": "Permanent ban"}
                        },
                        "critical": {
                            "first_offense": {"type": "temp_ban", "duration": 1440, "fine": 0, "details": "24 hour ban"},
                            "second_offense": {"type": "perm_ban", "duration": None, "fine": 0, "details": "Permanent ban"},
                            "third_offense": {"type": "perm_ban", "duration": None, "fine": 0, "details": "Permanent ban"},
                            "severe": {"type": "perm_ban", "duration": None, "fine": 0, "details": "Permanent ban + hardware ban"}
                        }
                    }
                    
                    punishments = default_punishments.get(priority.lower(), default_punishments["medium"])
                    
                    success, result = await self.rules.add_rule(
                        category=category, 
                        subcategory=subcategory,
                        title=title, 
                        content=content, 
                        keywords=keyword_list,
                        created_by_id=interaction.user.id,
                        priority=priority,
                        punishments=punishments,
                        appeal_allowed=priority.lower() != "critical",
                        appeal_process="Submit appeal ticket within 48 hours" if priority.lower() != "critical" else "No appeals",
                        min_staff_rank="helper" if priority.lower() in ["low", "medium"] else "moderator"
                    )
                    if success:
                        await interaction.response.send_message(f"✅ Rule '{title}' added to category '{category}' with ID: {result}!", ephemeral=True)
                    else:
                        await interaction.response.send_message(f"❌ Failed to add rule: {result}", ephemeral=True)
            
            @self.tree.command(name="bot_stats", description="View bot statistics")
            async def bot_stats(interaction: discord.Interaction):
                if not self.permissions.is_staff(interaction.user):
                    await interaction.response.send_message("❌ Staff permission required.", ephemeral=True)
                    return
                
                uptime = datetime.utcnow() - self.startup_time
                uptime_str = format_duration(int(uptime.total_seconds()))
                
                embed = create_embed(
                    "📊 Bot Statistics",
                    f"**Uptime**: {uptime_str}\n**Server**: {interaction.guild.name}",
                    discord.Color.blue()
                )
                
                embed.add_field(
                    name="🎫 Ticket System",
                    value=f"Created: {self.stats['tickets_created']}\nResolved: {self.stats['tickets_resolved']}",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Rule System",
                    value=f"Accessed: {self.stats['rules_accessed']}",
                    inline=True
                )
                
                embed.add_field(
                    name="⚡ Automation",
                    value=f"Actions: {self.stats['automated_actions']}",
                    inline=True
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            
            print("✅ Admin commands loaded successfully")
            
        except Exception as e:
            print(f"⚠️ Admin command loading failed: {e}")
    
    async def on_ready(self):
        """Bot ready event"""
        guild = self.get_guild(Config.GUILD_ID)
        
        print(f"""
╔══════════════════════════════════════════════╗
║     🇵🇰 PAKISTAN RP COMMUNITY BOT ONLINE       ║
╠══════════════════════════════════════════════╣
║ Bot: {self.user.name:<36} ║
║ Server: {guild.name[:30]:<30} ║
║ Members: {guild.member_count:<31} ║
║ Features: Advanced Automation System        ║
║ Status: All Systems Operational             ║
╚══════════════════════════════════════════════╝
        """)
        
        # Send startup notification
        if Config.STAFF_CHAT_ID:
            staff_channel = guild.get_channel(Config.STAFF_CHAT_ID)
            if staff_channel:
                embed = create_embed(
                    "🚀 Community Bot Online",
                    "Pakistan RP Community Bot v2.0 is now operational with full automation!",
                    discord.Color.green()
                )
                embed.add_field(
                    name="✅ Active Systems",
                    value="• Advanced Ticket Management\n• Smart Rule Database\n• Announcement System\n• Automation Engine\n• Staff Tools",
                    inline=False
                )
                await staff_channel.send(embed=embed)
    
    async def on_message(self, message: discord.Message):
        """Handle messages for logging and automation"""
        if message.author.bot:
            return
        
        # Log messages in ticket channels
        if self.tickets and message.channel.name.startswith('ticket-'):
            await self.tickets.log_message(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def close(self):
        """Clean shutdown"""
        print("👋 Shutting down Pakistan RP Community Bot...")
        
        # Cancel all tasks
        for task in [self.auto_ticket_cleanup, self.update_statistics, self.automated_maintenance]:
            if task.is_running():
                task.cancel()
        
        # Close database
        if self.db:
            await self.db.close()
        
        await super().close()
        print("✅ Pakistan RP Community Bot shutdown complete")