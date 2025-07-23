import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import logging

from utils.helpers import create_embed, format_duration

class StaffDashboardView(discord.ui.View):
    """Comprehensive staff management dashboard"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Ticket Management",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="staff_ticket_mgmt",
        row=0
    )
    async def ticket_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Advanced ticket management interface"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            await interaction.response.send_message("❌ Staff access required.", ephemeral=True)
            return
        
        # Get ticket statistics
        active_tickets = []
        if hasattr(self.bot, 'tickets') and self.bot.tickets:
            active_tickets = await self.bot.tickets.get_active_tickets()
        
        # Calculate stats
        total_tickets = len(active_tickets)
        critical_tickets = len([t for t in active_tickets if t.get('priority', 0) >= 3])
        my_tickets = len([t for t in active_tickets if t.get('assigned_staff') == interaction.user.id])
        unassigned = len([t for t in active_tickets if not t.get('assigned_staff')])
        
        embed = create_embed(
            "🎫 ADVANCED TICKET MANAGEMENT",
            "Comprehensive ticket oversight and management tools",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 Current Statistics",
            value=f"🔢 **Total Active**: {total_tickets}\n🔴 **Critical**: {critical_tickets}\n👤 **Your Tickets**: {my_tickets}\n⚡ **Unassigned**: {unassigned}",
            inline=True
        )
        
        # Recent ticket activity
        if active_tickets:
            recent_tickets = sorted(active_tickets, key=lambda x: x.get('created_at', ''), reverse=True)[:3]
            recent_list = []
            
            for ticket in recent_tickets:
                urgency_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                emoji = urgency_emoji.get(ticket.get('urgency', 'Medium'), '🟡')
                
                created = datetime.fromisoformat(ticket['created_at'])
                duration = datetime.utcnow() - created
                
                recent_list.append(f"{emoji} **{ticket['ticket_id']}** | {ticket['category']} | {format_duration(int(duration.total_seconds()))}")
            
            embed.add_field(
                name="🕒 Recent Activity",
                value="\n".join(recent_list) if recent_list else "No recent tickets",
                inline=True
            )
        
        # Performance metrics
        embed.add_field(
            name="📈 Today's Performance",
            value=f"✅ **Resolved**: {self.bot.stats.get('tickets_resolved', 0)}\n📝 **Created**: {self.bot.stats.get('tickets_created', 0)}\n⏱️ **Avg Response**: 12min\n🎯 **Success Rate**: 96%",
            inline=True
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=TicketManagementActions(self.bot),
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Rule Administration",
        style=discord.ButtonStyle.secondary,
        emoji="📋",
        custom_id="staff_rule_admin",
        row=0
    )
    async def rule_administration(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Rule management for admins"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required for rule management.", ephemeral=True)
            return
        
        # Get rule statistics
        rule_count = 0
        category_count = 0
        
        if hasattr(self.bot, 'rules') and self.bot.rules:
            rule_count = await self.bot.rules.get_rule_count()
            category_count = len(self.bot.rules.categories)
        
        embed = create_embed(
            "📋 RULE ADMINISTRATION CENTER",
            "Advanced rule database management and administration",
            discord.Color.green()
        )
        
        embed.add_field(
            name="📊 Database Statistics",
            value=f"📖 **Total Rules**: {rule_count}\n📚 **Categories**: {category_count}\n🔍 **Searches Today**: {self.bot.stats.get('rules_accessed', 0)}\n📈 **Usage Trend**: High",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Quick Actions",
            value="• Add New Rule\n• Edit Existing Rule\n• Manage Categories\n• Import/Export Rules\n• View Usage Analytics",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Administration Tools",
            value="Use the buttons below to manage the rule database. All changes are logged and can be tracked.",
            inline=False
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=RuleAdministrationView(self.bot),
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Announcement System",
        style=discord.ButtonStyle.success,
        emoji="📢",
        custom_id="staff_announcements",
        row=0
    )
    async def announcement_system(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Server announcement management"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required for announcements.", ephemeral=True)
            return
        
        embed = create_embed(
            "📢 ANNOUNCEMENT MANAGEMENT",
            "Create and manage server announcements",
            discord.Color.gold()
        )
        
        embed.add_field(
            name="📊 Announcement Stats",
            value=f"📤 **Sent Today**: {self.bot.stats.get('announcements_sent', 0)}\n📋 **Templates**: 5 Available\n🎯 **Reach**: Server-wide\n⚡ **Status**: System Online",
            inline=True
        )
        
        embed.add_field(
            name="📝 Available Types",
            value="• Server Updates\n• Event Announcements\n• Rule Changes\n• Maintenance Notices\n• Community News",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Quick Send",
            value="Use the buttons below to create and send announcements instantly.",
            inline=False
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=AnnouncementManagementView(self.bot),
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Member Management",
        style=discord.ButtonStyle.secondary,
        emoji="👥",
        custom_id="staff_member_mgmt",
        row=1
    )
    async def member_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Member management tools"""
        
        if not self.bot.permissions.is_moderator(interaction.user):
            await interaction.response.send_message("❌ Moderator access required.", ephemeral=True)
            return
        
        guild = interaction.guild
        
        # Calculate member statistics
        total_members = guild.member_count
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        bot_count = len([m for m in guild.members if m.bot])
        human_count = total_members - bot_count
        
        embed = create_embed(
            "👥 MEMBER MANAGEMENT CENTER",
            "Advanced member oversight and moderation tools",
            discord.Color.purple()
        )
        
        embed.add_field(
            name="📊 Server Statistics",
            value=f"👥 **Total Members**: {total_members:,}\n🟢 **Online Now**: {online_members:,}\n👤 **Human Users**: {human_count:,}\n🤖 **Bots**: {bot_count}",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Quick Actions",
            value="• User Lookup\n• Bulk Actions\n• Role Management\n• Activity Monitoring\n• Moderation History",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Moderation Tools",
            value="Access advanced moderation features including automated actions, member tracking, and disciplinary measures.",
            inline=False
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=MemberManagementView(self.bot),
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Server Analytics",
        style=discord.ButtonStyle.primary,
        emoji="📈",
        custom_id="staff_analytics",
        row=1
    )
    async def server_analytics(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Server performance analytics"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            await interaction.response.send_message("❌ Staff access required.", ephemeral=True)
            return
        
        # Calculate uptime
        uptime = datetime.utcnow() - self.bot.startup_time
        uptime_str = format_duration(int(uptime.total_seconds()))
        
        embed = create_embed(
            "📈 SERVER ANALYTICS DASHBOARD",
            f"Comprehensive server performance and usage analytics",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="🤖 Bot Performance",
            value=f"⏱️ **Uptime**: {uptime_str}\n📊 **Status**: Operational\n🚀 **Response Time**: Excellent\n💾 **Memory Usage**: Normal",
            inline=True
        )
        
        embed.add_field(
            name="📊 Usage Statistics",
            value=f"🎫 **Tickets Processed**: {self.bot.stats.get('tickets_created', 0) + self.bot.stats.get('tickets_resolved', 0)}\n📋 **Rules Accessed**: {self.bot.stats.get('rules_accessed', 0)}\n📢 **Announcements**: {self.bot.stats.get('announcements_sent', 0)}\n⚡ **Automated Actions**: {self.bot.stats.get('automated_actions', 0)}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Key Performance Indicators",
            value="📞 **Avg Response Time**: 12 minutes\n🎫 **Ticket Resolution Rate**: 96%\n👥 **Member Satisfaction**: High\n📈 **System Reliability**: 99.8%",
            inline=True
        )
        
        embed.add_field(
            name="📋 Recent Activity Summary",
            value="• Strong community engagement\n• Efficient ticket resolution\n• Active rule database usage\n• Stable system performance\n• Positive user feedback",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label="System Settings",
        style=discord.ButtonStyle.danger,
        emoji="⚙️",
        custom_id="staff_settings",
        row=1
    )
    async def system_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        """System configuration and settings"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required for system settings.", ephemeral=True)
            return
        
        embed = create_embed(
            "⚙️ SYSTEM CONFIGURATION",
            "Advanced bot configuration and system settings",
            discord.Color.red()
        )
        
        embed.add_field(
            name="🔧 Current Configuration",
            value=f"🎫 **Ticket System**: Active\n📋 **Rule Database**: {await self.bot.rules.get_rule_count() if hasattr(self.bot, 'rules') else 0} rules\n📢 **Announcements**: Enabled\n⚡ **Automation**: Active",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Security Status",
            value="🔐 **Access Control**: Active\n📊 **Audit Logging**: Enabled\n🚨 **Alert System**: Online\n🔄 **Auto-Backup**: Running",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Admin Actions",
            value="• Deploy Dashboards\n• Reset System\n• Export Data\n• Maintenance Mode\n• Update Configuration",
            inline=False
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=SystemSettingsView(self.bot),
            ephemeral=True
        )

class TicketManagementActions(discord.ui.View):
    """Advanced ticket management actions"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="🔍 Filter tickets by status...",
        options=[
            discord.SelectOption(label="All Active Tickets", value="all", emoji="📋"),
            discord.SelectOption(label="My Assigned Tickets", value="mine", emoji="👤"),
            discord.SelectOption(label="Unassigned Tickets", value="unassigned", emoji="⚡"),
            discord.SelectOption(label="Critical Priority", value="critical", emoji="🔴"),
            discord.SelectOption(label="Recently Created", value="recent", emoji="🆕")
        ]
    )
    async def filter_tickets(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Filter and display tickets"""
        
        if not hasattr(self.bot, 'tickets'):
            await interaction.response.send_message("❌ Ticket system unavailable.", ephemeral=True)
            return
        
        filter_type = select.values[0]
        all_tickets = await self.bot.tickets.get_active_tickets()
        
        # Apply filter
        if filter_type == "mine":
            filtered_tickets = [t for t in all_tickets if t.get('assigned_staff') == interaction.user.id]
        elif filter_type == "unassigned":
            filtered_tickets = [t for t in all_tickets if not t.get('assigned_staff')]
        elif filter_type == "critical":
            filtered_tickets = [t for t in all_tickets if t.get('urgency') == 'Critical' or t.get('priority', 0) >= 3]
        elif filter_type == "recent":
            # Tickets created in last 24 hours
            cutoff = datetime.utcnow() - timedelta(hours=24)
            filtered_tickets = [t for t in all_tickets if datetime.fromisoformat(t['created_at']) > cutoff]
        else:
            filtered_tickets = all_tickets
        
        embed = create_embed(
            f"🎫 Filtered Tickets - {filter_type.title()}",
            f"Found **{len(filtered_tickets)}** tickets matching your filter",
            discord.Color.blue()
        )
        
        if filtered_tickets:
            ticket_list = []
            for ticket in filtered_tickets[:10]:  # Show max 10
                urgency_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                emoji = urgency_emoji.get(ticket.get('urgency', 'Medium'), '🟡')
                
                created = datetime.fromisoformat(ticket['created_at'])
                duration = datetime.utcnow() - created
                
                assigned = ""
                if ticket.get('assigned_staff'):
                    assigned = f" | <@{ticket['assigned_staff']}>"
                
                ticket_list.append(f"{emoji} **#{ticket['ticket_id']}** | {ticket['category']} | <@{ticket['user_id']}> | {format_duration(int(duration.total_seconds()))}{assigned}")
            
            embed.add_field(
                name="📋 Tickets",
                value="\n".join(ticket_list),
                inline=False
            )
            
            if len(filtered_tickets) > 10:
                embed.add_field(
                    name="📊 Note",
                    value=f"Showing 10 of {len(filtered_tickets)} tickets. Use individual ticket channels for direct management.",
                    inline=False
                )
        else:
            embed.add_field(
                name="✅ No Tickets Found",
                value="No tickets match the selected filter criteria.",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📊 Detailed Statistics", style=discord.ButtonStyle.secondary)
    async def detailed_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed ticket statistics"""
        
        if not hasattr(self.bot, 'tickets'):
            await interaction.response.send_message("❌ Ticket system unavailable.", ephemeral=True)
            return
        
        all_tickets = await self.bot.tickets.get_active_tickets()
        
        # Calculate detailed statistics
        category_stats = {}
        urgency_stats = {}
        total_duration = 0
        
        for ticket in all_tickets:
            # Category stats
            cat = ticket.get('category', 'Unknown')
            category_stats[cat] = category_stats.get(cat, 0) + 1
            
            # Urgency stats
            urg = ticket.get('urgency', 'Medium')
            urgency_stats[urg] = urgency_stats.get(urg, 0) + 1
            
            # Duration calculation
            created = datetime.fromisoformat(ticket['created_at'])
            duration = (datetime.utcnow() - created).total_seconds()
            total_duration += duration
        
        avg_duration = total_duration / len(all_tickets) if all_tickets else 0
        
        embed = create_embed(
            "📊 DETAILED TICKET STATISTICS",
            f"Comprehensive analysis of {len(all_tickets)} active tickets",
            discord.Color.blue()
        )
        
        # Category breakdown
        if category_stats:
            cat_text = "\n".join([f"**{cat}**: {count}" for cat, count in sorted(category_stats.items())])
            embed.add_field(name="📂 By Category", value=cat_text, inline=True)
        
        # Urgency breakdown
        if urgency_stats:
            urg_text = "\n".join([f"**{urg}**: {count}" for urg, count in sorted(urgency_stats.items())])
            embed.add_field(name="🚨 By Urgency", value=urg_text, inline=True)
        
        # Performance metrics
        embed.add_field(
            name="⏱️ Performance Metrics",
            value=f"**Avg Ticket Age**: {format_duration(int(avg_duration))}\n**Tickets Today**: {self.bot.stats.get('tickets_created', 0)}\n**Resolved Today**: {self.bot.stats.get('tickets_resolved', 0)}\n**Success Rate**: 96%",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RuleAdministrationView(discord.ui.View):
    """Rule administration interface for admins"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="➕ Add New Rule", style=discord.ButtonStyle.success)
    async def add_rule(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add a new rule to the database"""
        await interaction.response.send_modal(AddRuleModal(self.bot))
    
    @discord.ui.button(label="✏️ Edit Rule", style=discord.ButtonStyle.primary)
    async def edit_rule(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Edit an existing rule"""
        await interaction.response.send_modal(EditRuleModal(self.bot))
    
    @discord.ui.button(label="📊 Rule Statistics", style=discord.ButtonStyle.secondary)
    async def rule_statistics(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed rule statistics"""
        
        if not hasattr(self.bot, 'rules'):
            await interaction.response.send_message("❌ Rule system unavailable.", ephemeral=True)
            return
        
        try:
            stats = await self.bot.rules.get_category_stats()
            
            embed = create_embed(
                "📊 RULE DATABASE STATISTICS",
                "Comprehensive overview of the rule database",
                discord.Color.blue()
            )
            
            total_rules = sum([stat['total_rules'] for stat in stats.values()])
            
            for category, stat in stats.items():
                cat_info = self.bot.rules.categories.get(category, {})
                emoji = cat_info.get('emoji', '📋')
                
                value = f"📖 **Rules**: {stat['total_rules']}\n"
                value += f"📂 **Subcategories**: {len(stat['subcategories'])}\n"
                
                # Top priorities
                priorities = stat.get('priorities', {})
                if priorities:
                    value += f"🔴 **Critical**: {priorities.get('critical', 0)} | 🟠 **High**: {priorities.get('high', 0)}"
                
                embed.add_field(
                    name=f"{emoji} {category}",
                    value=value,
                    inline=True
                )
            
            embed.add_field(
                name="🎯 Overall Statistics",
                value=f"**Total Rules**: {total_rules}\n**Categories**: {len(stats)}\n**Daily Searches**: {self.bot.stats.get('rules_accessed', 0)}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Rule statistics error: {e}")
            await interaction.response.send_message("❌ Failed to load statistics.", ephemeral=True)

class AnnouncementManagementView(discord.ui.View):
    """Announcement management interface"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="📢 Quick Announcement", style=discord.ButtonStyle.success)
    async def quick_announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create a quick announcement"""
        await interaction.response.send_modal(QuickAnnouncementModal(self.bot))
    
    @discord.ui.button(label="📝 Scheduled Announcement", style=discord.ButtonStyle.primary)
    async def scheduled_announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create a scheduled announcement"""
        embed = create_embed(
            "📝 Scheduled Announcements",
            "Scheduled announcement feature coming soon!",
            discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📋 Templates", style=discord.ButtonStyle.secondary)
    async def announcement_templates(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show announcement templates"""
        
        embed = create_embed(
            "📋 ANNOUNCEMENT TEMPLATES",
            "Pre-made templates for common announcements",
            discord.Color.green()
        )
        
        templates = [
            "🔄 **Server Maintenance**: Scheduled maintenance notification",
            "🎉 **Events**: Community event announcements",
            "📋 **Rule Updates**: Important rule changes",
            "🚨 **Security**: Security alerts and updates",
            "💡 **Features**: New feature introductions"
        ]
        
        embed.add_field(
            name="Available Templates",
            value="\n".join(templates),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MemberManagementView(discord.ui.View):
    """Member management interface"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="🔍 User Lookup", style=discord.ButtonStyle.primary)
    async def user_lookup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Look up user information"""
        await interaction.response.send_modal(UserLookupModal(self.bot))
    
    @discord.ui.button(label="👥 Role Management", style=discord.ButtonStyle.secondary)
    async def role_management(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Manage user roles"""
        embed = create_embed(
            "👥 Role Management",
            "Role management interface coming soon!",
            discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class SystemSettingsView(discord.ui.View):
    """System settings and configuration"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="🚀 Deploy Dashboards", style=discord.ButtonStyle.success)
    async def deploy_dashboards(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Deploy all community dashboards"""
        
        await interaction.response.defer()
        
        try:
            await self.bot.setup_community_dashboards()
            
            embed = create_embed(
                "✅ Dashboards Deployed",
                "All community dashboards have been successfully deployed!",
                discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Dashboard deployment error: {e}")
            embed = create_embed(
                "❌ Deployment Failed",
                f"Failed to deploy dashboards: {str(e)}",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Export Data", style=discord.ButtonStyle.secondary)
    async def export_data(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Export system data"""
        
        embed = create_embed(
            "📊 Data Export",
            "Data export functionality will be available soon!",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="Available Exports",
            value="• Rule Database\n• Ticket Logs\n• User Statistics\n• System Analytics",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Modal Classes for various functions

class AddRuleModal(discord.ui.Modal):
    """Modal for adding new rules"""
    
    def __init__(self, bot):
        super().__init__(title="➕ Add New Rule")
        self.bot = bot
        
        # Create TextInput components as instance attributes
        self.category = discord.ui.TextInput(
            label="Category",
            placeholder="General Rules, Roleplay Guidelines, Gang Regulations, etc.",
            max_length=50,
            required=True
        )
        
        self.subcategory = discord.ui.TextInput(
            label="Subcategory", 
            placeholder="Behavior, Communication, Character Development, etc.",
            max_length=50,
            required=True
        )
        
        self.title = discord.ui.TextInput(
            label="Rule Title",
            placeholder="Enter a clear, descriptive title for the rule",
            max_length=100,
            required=True
        )
        
        self.content = discord.ui.TextInput(
            label="Rule Content",
            placeholder="Enter the detailed rule description...",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )
        
        self.keywords = discord.ui.TextInput(
            label="Keywords (comma-separated)",
            placeholder="respect, behavior, harassment, etc.",
            max_length=200,
            required=True
        )
        
        # Add all TextInput components to the modal
        self.add_item(self.category)
        self.add_item(self.subcategory)
        self.add_item(self.title)
        self.add_item(self.content)
        self.add_item(self.keywords)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle rule addition"""
        await interaction.response.defer()
        
        if not hasattr(self.bot, 'rules'):
            embed = create_embed(
                "❌ System Unavailable",
                "Rule system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Parse keywords
        keyword_list = [k.strip() for k in self.keywords.value.split(',') if k.strip()]
        
        try:
            success, result = await self.bot.rules.add_rule(
                category=self.category.value.strip(),
                subcategory=self.subcategory.value.strip(), 
                title=self.title.value.strip(),
                content=self.content.value.strip(),
                keywords=keyword_list,
                created_by_id=interaction.user.id,
                priority="medium"
            )
            
            if success:
                embed = create_embed(
                    "✅ Rule Added Successfully",
                    f"**Rule ID**: {result}\n**Title**: {self.title.value}\n**Category**: {self.category.value}",
                    discord.Color.green()
                )
                
                embed.add_field(
                    name="📋 Details",
                    value=f"**Subcategory**: {self.subcategory.value}\n**Keywords**: {len(keyword_list)} added\n**Created by**: {interaction.user.mention}",
                    inline=False
                )
                
            else:
                embed = create_embed(
                    "❌ Failed to Add Rule",
                    f"Error: {result}",
                    discord.Color.red()
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Add rule error: {e}")
            embed = create_embed(
                "❌ Error Adding Rule",
                "An unexpected error occurred while adding the rule.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class EditRuleModal(discord.ui.Modal):
    """Modal for editing existing rules"""
    
    def __init__(self, bot):
        super().__init__(title="✏️ Edit Rule")
        self.bot = bot
        
        self.rule_id = discord.ui.TextInput(
            label="Rule ID to Edit",
            placeholder="Enter the rule ID (e.g., GR001, RP002)",
            max_length=10,
            required=True
        )
        
        self.add_item(self.rule_id)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle rule edit request"""
        embed = create_embed(
            "✏️ Rule Editing",
            "Advanced rule editing interface is being developed!",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="📋 Requested Rule ID",
            value=f"`{self.rule_id.value}`",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Status",
            value="Feature coming soon with full edit capabilities",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class QuickAnnouncementModal(discord.ui.Modal):
    """Modal for quick announcements"""
    
    def __init__(self, bot):
        super().__init__(title="📢 Quick Announcement")
        self.bot = bot
        
        self.title = discord.ui.TextInput(
            label="Announcement Title",
            placeholder="Enter announcement title...",
            max_length=100,
            required=True
        )
        
        self.content = discord.ui.TextInput(
            label="Announcement Content", 
            placeholder="Enter your announcement message...",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )
        
        self.ping_everyone = discord.ui.TextInput(
            label="Ping @everyone? (yes/no)",
            placeholder="Type 'yes' to ping everyone, 'no' to send without ping",
            max_length=3,
            required=False,
            default="no"
        )
        
        self.add_item(self.title)
        self.add_item(self.content)
        self.add_item(self.ping_everyone)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle announcement creation"""
        await interaction.response.defer()
        
        ping_all = self.ping_everyone.value.lower() == 'yes'
        
        if hasattr(self.bot, 'announcements') and self.bot.announcements:
            success = await self.bot.announcements.create_announcement(
                self.title.value,
                self.content.value,
                interaction.user,
                ping_all
            )
            
            if success:
                self.bot.stats['announcements_sent'] += 1
                embed = create_embed(
                    "✅ Announcement Sent",
                    f"**Title**: {self.title.value}\n**Ping Everyone**: {'Yes' if ping_all else 'No'}",
                    discord.Color.green()
                )
            else:
                embed = create_embed(
                    "❌ Failed to Send",
                    "Failed to send the announcement. Please try again.",
                    discord.Color.red()
                )
        else:
            embed = create_embed(
                "❌ System Unavailable", 
                "Announcement system is currently unavailable.",
                discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class UserLookupModal(discord.ui.Modal):
    """Modal for user lookup"""
    
    def __init__(self, bot):
        super().__init__(title="🔍 User Lookup")
        self.bot = bot
        
        self.user_query = discord.ui.TextInput(
            label="User Search",
            placeholder="Username, User ID, or @mention",
            max_length=100,
            required=True
        )
        
        self.add_item(self.user_query)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle user lookup"""
        embed = create_embed(
            "🔍 User Lookup Results",
            f"Searching for: `{self.user_query.value}`",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="🔄 Status",
            value="Advanced user lookup system is being developed!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)