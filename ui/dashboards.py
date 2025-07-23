import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging

from config.settings import Config
from utils.helpers import create_embed

class DashboardManager:
    """Advanced dashboard management system for Pakistan RP"""
    
    def __init__(self, bot):
        self.bot = bot
        self.deployed_dashboards = {}
        self.dashboard_stats = {
            'ticket_dashboard_uses': 0,
            'rule_dashboard_uses': 0,
            'staff_dashboard_uses': 0,
            'total_interactions': 0
        }
    
    async def initialize(self):
        """Initialize dashboard manager"""
        print("✅ Dashboard manager ready")
    
    async def deploy_all_dashboards(self, guild: discord.Guild) -> Dict[str, bool]:
        """Deploy all community dashboards"""
        
        results = {}
        
        # Deploy ticket creation dashboard
        results['ticket_dashboard'] = await self.deploy_ticket_creation_dashboard(guild)
        
        # Deploy rule search dashboard
        results['rule_dashboard'] = await self.deploy_rule_search_dashboard(guild)
        
        # Deploy staff management dashboard
        results['staff_dashboard'] = await self.deploy_staff_dashboard(guild)
        
        # Deploy announcement dashboard (if needed)
        results['announcement_dashboard'] = await self.deploy_announcement_dashboard(guild)
        
        return results
    
    async def deploy_ticket_creation_dashboard(self, guild: discord.Guild) -> bool:
        """Deploy the beautiful ticket creation dashboard"""
        
        try:
            # Find or create ticket creation channel
            ticket_channel = discord.utils.get(guild.text_channels, name="ticket-creation")
            
            if not ticket_channel:
                # Create channel with proper permissions
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(
                        send_messages=False,
                        add_reactions=False,
                        create_public_threads=False,
                        create_private_threads=False,
                        use_slash_commands=True,
                        view_channel=True,
                        read_message_history=True
                    ),
                    guild.me: discord.PermissionOverwrite(
                        send_messages=True,
                        manage_messages=True,
                        embed_links=True,
                        view_channel=True
                    )
                }
                
                # Add staff permissions
                for role_id in [Config.ADMIN_ROLE_ID, Config.SENIOR_STAFF_ROLE_ID, Config.STAFF_ROLE_ID, Config.MODERATOR_ROLE_ID]:
                    if role_id:
                        role = guild.get_role(role_id)
                        if role:
                            overwrites[role] = discord.PermissionOverwrite(
                                send_messages=True,
                                manage_messages=True,
                                view_channel=True
                            )
                
                ticket_channel = await guild.create_text_channel(
                    name="ticket-creation",
                    topic="🎫 Create support tickets here | Automated support system",
                    overwrites=overwrites,
                    reason="Created by Pakistan RP Community Bot"
                )
                
                print(f"✅ Created #ticket-creation channel")
            
            # Clear existing messages
            try:
                await ticket_channel.purge(limit=100, check=lambda m: m.author == guild.me)
            except:
                pass
            
            # Create main ticket creation embed
            main_embed = discord.Embed(
                title="🎫 PAKISTAN RP SUPPORT CENTER",
                description="**Welcome to our 24/7 automated support system!**\n\nOur advanced ticket system provides instant assistance with categorized support, automated responses, and professional staff handling.",
                color=0x2ECC71,
                timestamp=datetime.utcnow()
            )
            
            # Add feature highlights
            main_embed.add_field(
                name="🚀 Why Use Our Ticket System?",
                value="• **Instant Response** - Get immediate automated guidance\n• **Professional Staff** - Experienced team ready to help\n• **Category-Based** - Specialized support for your needs\n• **Transcript System** - Complete conversation history\n• **Priority Support** - Urgent issues handled faster",
                inline=False
            )
            
            main_embed.add_field(
                name="📋 Available Support Categories",
                value=(
                    "🔧 **General Support** - Questions, help, and guidance\n"
                    "👤 **Player Reports** - Report rule violations with evidence\n"
                    "🐛 **Bug Reports** - Technical issues and glitches\n"
                    "🏢 **Gang Registration** - Official gang applications\n"
                    "🛍️ **Shop Support** - Purchase and transaction help\n"
                    "❓ **Other Issues** - Everything else we can help with"
                ),
                inline=True
            )
            
            main_embed.add_field(
                name="⚡ Response Times",
                value="📞 **General Support**: ~10 min\n📋 **Reports**: ~15 min\n🐛 **Bug Reports**: ~20 min\n🏢 **Gang Reg**: ~30 min\n🛍️ **Shop**: ~15 min\n❓ **Other**: ~15 min",
                inline=True
            )
            
            main_embed.add_field(
                name="📊 Service Status",
                value="🟢 **All Systems**: Operational\n⚡ **Bot Status**: Online\n👥 **Staff**: Available\n🎯 **Success Rate**: 98%",
                inline=True
            )
            
            # Add instructions
            main_embed.add_field(
                name="📝 How to Create a Ticket",
                value="1. Click the **\"🎫 Create Support Ticket\"** button below\n2. Select your issue category from the list\n3. Describe your problem in detail\n4. Choose urgency level (Low/Medium/High/Critical)\n5. Submit and wait for your private ticket channel\n\n✨ **That's it!** Our system handles the rest automatically.",
                inline=False
            )
            
            main_embed.set_footer(
                text="Pakistan RP Community • Professional Support System",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            main_embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
            
            # Import and send with view
            from ui.ticket_views import TicketCreationView
            await ticket_channel.send(embed=main_embed, view=TicketCreationView(self.bot))
            
            # Send additional info embed
            info_embed = discord.Embed(
                title="💡 Important Information",
                description="Please read before creating a ticket",
                color=0x3498DB
            )
            
            info_embed.add_field(
                name="📋 Before Creating a Ticket",
                value="• Check if your question is answered in <#rules>\n• Use the rule search system for rule-related questions\n• Make sure you have all necessary information ready\n• Be patient - our staff will respond as quickly as possible",
                inline=False
            )
            
            info_embed.add_field(
                name="⚠️ Ticket Guidelines",
                value="• **One issue per ticket** - Don't mix multiple problems\n• **Be descriptive** - The more detail, the better we can help\n• **Stay respectful** - Treat staff with courtesy\n• **Be patient** - Quality support takes time\n• **Provide evidence** - Screenshots help solve problems faster",
                inline=False
            )
            
            info_embed.add_field(
                name="🚫 What NOT to do",
                value="• Don't create spam tickets\n• Don't be rude to staff members\n• Don't create tickets for non-issues\n• Don't share personal information publicly\n• Don't abuse the system",
                inline=False
            )
            
            await ticket_channel.send(embed=info_embed)
            
            # Store dashboard info
            self.deployed_dashboards['ticket_creation'] = {
                'channel_id': ticket_channel.id,
                'deployed_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            print(f"✅ Ticket creation dashboard deployed to #{ticket_channel.name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to deploy ticket creation dashboard: {e}")
            return False
    
    async def deploy_rule_search_dashboard(self, guild: discord.Guild) -> bool:
        """Deploy the rule search dashboard"""
        
        try:
            # Find rules channel
            rules_channel = guild.get_channel(Config.RULES_CHANNEL_ID) if Config.RULES_CHANNEL_ID else None
            
            if not rules_channel:
                rules_channel = discord.utils.get(guild.text_channels, name="rules")
                
                if not rules_channel:
                    print("⚠️ Rules channel not found, skipping rule dashboard deployment")
                    return False
            
            # Create rule database embed
            rule_embed = discord.Embed(
                title="📋 PAKISTAN RP RULES DATABASE",
                description="**Advanced rule search system with 300+ comprehensive rules**\n\nInstantly search through our complete rule database using keywords, categories, or browse by topics. Get detailed information including punishments, appeal processes, and staff guidance.",
                color=0x3498DB,
                timestamp=datetime.utcnow()
            )
            
            # Add search features
            rule_embed.add_field(
                name="🔍 Search Features",
                value="• **Keyword Search** - Find rules instantly\n• **Category Browsing** - Explore by topics\n• **Smart Matching** - AI-powered relevance\n• **Detailed Results** - Full rule information\n• **Punishment Details** - Know the consequences\n• **Appeal Information** - Contest unfair actions",
                inline=True
            )
            
            # Add rule categories
            rule_embed.add_field(
                name="📚 Rule Categories",
                value="📋 **General Rules** - Basic server conduct\n🎭 **Roleplay Guidelines** - RP quality standards\n🏢 **Gang Regulations** - Gang-specific rules\n🚗 **Vehicle Rules** - Driving and transport\n🏠 **Property Guidelines** - Ownership rules\n💰 **Economic System** - Money and trading\n👮 **Staff Protocols** - Administrative procedures\n🎉 **Event Rules** - Special event guidelines",
                inline=True
            )
            
            # Add database stats
            rule_count = await self.bot.rules.get_rule_count() if hasattr(self.bot, 'rules') else 0
            
            rule_embed.add_field(
                name="📊 Database Statistics",
                value=f"📖 **Total Rules**: {rule_count}\n📂 **Categories**: 8 Main Categories\n🏷️ **Subcategories**: 40+ Specific Topics\n🔄 **Last Updated**: Recently\n✅ **Status**: Active & Current\n🎯 **Accuracy**: 100% Verified",
                inline=True
            )
            
            rule_embed.add_field(
                name="💡 How to Search",
                value="**Option 1: Keyword Search**\n1. Click \"🔍 Search Rules\" button\n2. Type keywords like 'respect', 'driving', 'gang'\n3. Get instant results with relevance scoring\n\n**Option 2: Category Browse**\n1. Use the dropdown menu below\n2. Select a category to explore\n3. Browse all rules in that section",
                inline=False
            )
            
            rule_embed.add_field(
                name="🎯 Pro Tips",
                value="• Use specific keywords for better results\n• Check punishment details to understand consequences\n• Look for related rules in the same category\n• Contact staff if you need clarification\n• Appeal system available for disputed actions",
                inline=False
            )
            
            rule_embed.set_footer(
                text="Pakistan RP Rules Database • Updated Regularly",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            # Import and send with view
            from ui.rule_views import RuleSearchView
            await rules_channel.send(embed=rule_embed, view=RuleSearchView(self.bot))
            
            # Send additional usage guide
            guide_embed = discord.Embed(
                title="📖 Rule Database Usage Guide",
                color=0x2ECC71
            )
            
            guide_embed.add_field(
                name="🔤 Search Examples",
                value="• `respect` - Find all respect-related rules\n• `driving reckless` - Traffic violation rules\n• `gang war` - Gang conflict regulations\n• `property ownership` - Property rules\n• `staff abuse` - Staff conduct guidelines",
                inline=True
            )
            
            guide_embed.add_field(
                name="📋 Understanding Results",
                value="• **Rule ID** - Unique identifier\n• **Priority Level** - 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low\n• **Category** - Main rule section\n• **Punishment** - Consequences for violation\n• **Appeal** - Whether you can contest",
                inline=True
            )
            
            await rules_channel.send(embed=guide_embed)
            
            # Store dashboard info
            self.deployed_dashboards['rule_search'] = {
                'channel_id': rules_channel.id,
                'deployed_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            print(f"✅ Rule search dashboard deployed to #{rules_channel.name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to deploy rule search dashboard: {e}")
            return False
    
    async def deploy_staff_dashboard(self, guild: discord.Guild) -> bool:
        """Deploy staff management dashboard"""
        
        try:
            staff_channel = guild.get_channel(Config.STAFF_CHAT_ID) if Config.STAFF_CHAT_ID else None
            
            if not staff_channel:
                staff_channel = discord.utils.get(guild.text_channels, name="staff-chat")
                
                if not staff_channel:
                    print("⚠️ Staff channel not found, skipping staff dashboard deployment")
                    return False
            
            # Create staff dashboard embed
            staff_embed = discord.Embed(
                title="🎛️ PAKISTAN RP STAFF COMMAND CENTER",
                description="**Advanced staff management suite with comprehensive automation**\n\nAccess all administrative tools, monitor community health, manage tickets, handle announcements, and oversee the entire server from this centralized dashboard.",
                color=0xE74C3C,
                timestamp=datetime.utcnow()
            )
            
            # Get current statistics
            active_tickets = 0
            if hasattr(self.bot, 'tickets') and self.bot.tickets:
                active_tickets = len(list(self.bot.tickets.active_tickets.values()))
            
            online_staff = len([
                m for m in guild.members 
                if not m.bot and m.status != discord.Status.offline and self.bot.permissions.is_staff(m)
            ])
            
            staff_embed.add_field(
                name="📊 Live Server Status",
                value=f"🎫 **Active Tickets**: {active_tickets}\n👥 **Online Staff**: {online_staff}\n📈 **Server Health**: Excellent\n⚡ **Bot Status**: Fully Operational\n🔧 **All Systems**: Green",
                inline=True
            )
            
            staff_embed.add_field(
                name="🎯 Quick Access Tools",
                value="• **Ticket Management** - Full ticket oversight\n• **Rule Administration** - Database management\n• **Announcements** - Server-wide messaging\n• **Member Management** - User oversight\n• **Analytics Dashboard** - Performance metrics\n• **System Settings** - Configuration tools",
                inline=True
            )
            
            staff_embed.add_field(
                name="📈 Today's Activity",
                value=f"🎫 **Tickets Created**: {self.bot.stats.get('tickets_created', 0)}\n✅ **Tickets Resolved**: {self.bot.stats.get('tickets_resolved', 0)}\n📋 **Rules Accessed**: {self.bot.stats.get('rules_accessed', 0)}\n📢 **Announcements**: {self.bot.stats.get('announcements_sent', 0)}\n⚡ **Auto Actions**: {self.bot.stats.get('automated_actions', 0)}",
                inline=True
            )
            
            staff_embed.add_field(
                name="🔧 Advanced Features",
                value="• **Real-time Monitoring** - Live system status\n• **Automated Responses** - Smart ticket handling\n• **Bulk Operations** - Mass management tools\n• **Analytics & Reports** - Detailed insights\n• **Permission Management** - Role-based access\n• **Audit Logging** - Complete action tracking",
                inline=False
            )
            
            staff_embed.add_field(
                name="⚡ Automation Status",
                value="🟢 **Ticket Auto-Close**: Active\n🟢 **Rule Violations**: Tracked\n🟢 **Database Backups**: Running\n🟢 **Activity Monitoring**: Live\n🟢 **Cleanup Tasks**: Scheduled",
                inline=True
            )
            
            staff_embed.add_field(
                name="📱 Mobile Friendly",
                value="This dashboard works perfectly on mobile devices. All staff can access full functionality from anywhere.",
                inline=True
            )
            
            staff_embed.set_footer(
                text="Pakistan RP Staff Command Center • Professional Tools",
                icon_url=guild.icon.url if guild.icon else None
            )
            
            # Import and send with view
            from ui.staff_views import StaffDashboardView
            await staff_channel.send(embed=staff_embed, view=StaffDashboardView(self.bot))
            
            # Store dashboard info
            self.deployed_dashboards['staff_dashboard'] = {
                'channel_id': staff_channel.id,
                'deployed_at': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            print(f"✅ Staff dashboard deployed to #{staff_channel.name}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to deploy staff dashboard: {e}")
            return False
    
    async def deploy_announcement_dashboard(self, guild: discord.Guild) -> bool:
        """Deploy announcement dashboard for admins"""
        
        try:
            # This would be for a separate announcement management channel
            # For now, we'll skip this as announcements are handled in staff dashboard
            
            self.deployed_dashboards['announcement_dashboard'] = {
                'status': 'integrated_with_staff',
                'deployed_at': datetime.utcnow().isoformat()
            }
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to deploy announcement dashboard: {e}")
            return False
    
    async def update_dashboard_stats(self, dashboard_type: str, interaction_type: str = "use"):
        """Update dashboard usage statistics"""
        
        stat_key = f"{dashboard_type}_dashboard_{interaction_type}s"
        
        if stat_key in self.dashboard_stats:
            self.dashboard_stats[stat_key] += 1
        
        self.dashboard_stats['total_interactions'] += 1
        
        # Update bot stats
        if self.bot.db:
            await self.bot.db.update_bot_stats(self.dashboard_stats)
    
    async def get_dashboard_status(self) -> Dict[str, Any]:
        """Get status of all deployed dashboards"""
        
        status = {
            'deployed_dashboards': len(self.deployed_dashboards),
            'active_dashboards': len([d for d in self.deployed_dashboards.values() if d.get('status') == 'active']),
            'total_interactions': self.dashboard_stats['total_interactions'],
            'dashboards': self.deployed_dashboards.copy(),
            'usage_stats': self.dashboard_stats.copy()
        }
        
        return status
    
    async def refresh_dashboard(self, guild: discord.Guild, dashboard_type: str) -> bool:
        """Refresh a specific dashboard"""
        
        if dashboard_type == 'ticket_creation':
            return await self.deploy_ticket_creation_dashboard(guild)
        elif dashboard_type == 'rule_search':
            return await self.deploy_rule_search_dashboard(guild)
        elif dashboard_type == 'staff_dashboard':
            return await self.deploy_staff_dashboard(guild)
        elif dashboard_type == 'all':
            results = await self.deploy_all_dashboards(guild)
            return all(results.values())
        
        return False
    
    async def create_dashboard_report(self) -> discord.Embed:
        """Create dashboard status report"""
        
        status = await self.get_dashboard_status()
        
        embed = discord.Embed(
            title="🎛️ Dashboard Status Report",
            description="Current status of all community dashboards",
            color=0x3498DB,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Overview",
            value=f"**Deployed**: {status['deployed_dashboards']}\n**Active**: {status['active_dashboards']}\n**Total Uses**: {status['total_interactions']:,}",
            inline=True
        )
        
        # Dashboard status
        dashboard_status = []
        for name, info in status['dashboards'].items():
            status_emoji = "🟢" if info.get('status') == 'active' else "🔴"
            dashboard_status.append(f"{status_emoji} **{name.replace('_', ' ').title()}**")
        
        if dashboard_status:
            embed.add_field(
                name="🎯 Dashboard Status",
                value="\n".join(dashboard_status),
                inline=True
            )
        
        embed.add_field(
            name="📈 Usage Statistics",
            value=f"🎫 **Ticket Dashboard**: {status['usage_stats'].get('ticket_dashboard_uses', 0)}\n📋 **Rule Dashboard**: {status['usage_stats'].get('rule_dashboard_uses', 0)}\n👮 **Staff Dashboard**: {status['usage_stats'].get('staff_dashboard_uses', 0)}",
            inline=True
        )
        
        embed.set_footer(text="Pakistan RP Dashboard Manager")
        
        return embed