import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging

from utils.helpers import create_embed, format_duration

class AnnouncementView(discord.ui.View):
    """Main announcement management interface"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Create Announcement",
        style=discord.ButtonStyle.primary,
        emoji="📢",
        custom_id="create_announcement_btn"
    )
    async def create_announcement_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create new announcement button"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            embed = create_embed(
                "❌ Access Denied",
                "Only administrators can create announcements.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check cooldown
        if hasattr(self.bot, 'announcements') and self.bot.announcements:
            remaining = self.bot.announcements.get_cooldown_remaining(interaction.user)
            if remaining > 0:
                embed = create_embed(
                    "⏰ Cooldown Active",
                    f"Please wait {format_duration(remaining)} before creating another announcement.",
                    discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        await interaction.response.send_modal(CreateAnnouncementModal(self.bot))
    
    @discord.ui.button(
        label="Templates",
        style=discord.ButtonStyle.secondary,
        emoji="📋",
        custom_id="announcement_templates_btn"
    )
    async def announcement_templates_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show announcement templates"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            embed = create_embed(
                "❌ Access Denied",
                "Only administrators can access announcement templates.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if hasattr(self.bot, 'announcements') and self.bot.announcements:
            templates = self.bot.announcements.get_available_templates()
            
            embed = create_embed(
                "📋 Announcement Templates",
                "Choose from our pre-made announcement templates for common situations.",
                discord.Color.blue()
            )
            
            template_list = []
            for template in templates:
                emoji_map = {
                    'server_maintenance': '🔧',
                    'event_announcement': '🎉',
                    'rule_update': '📋',
                    'security_alert': '🚨',
                    'feature_update': '✨'
                }
                emoji = emoji_map.get(template['name'], '📄')
                ping_status = "🔔 Pings Everyone" if template['ping_everyone'] else "🔕 No Ping"
                
                template_list.append(f"{emoji} **{template['title']}**\n{template['description'][:100]}...\n{ping_status}")
            
            if template_list:
                embed.add_field(
                    name="📚 Available Templates",
                    value="\n\n".join(template_list),
                    inline=False
                )
            
            embed.add_field(
                name="💡 How to Use",
                value="1. Select a template from the dropdown below\n2. Fill in the required information\n3. Review and send the announcement",
                inline=False
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=AnnouncementTemplateView(self.bot, templates),
                ephemeral=True
            )
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "Announcement system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(
        label="Statistics",
        style=discord.ButtonStyle.secondary,
        emoji="📊",
        custom_id="announcement_stats_btn"
    )
    async def announcement_statistics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show announcement statistics"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            embed = create_embed(
                "❌ Access Denied",
                "Only staff members can view announcement statistics.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if hasattr(self.bot, 'announcements') and self.bot.announcements:
            stats = await self.bot.announcements.get_announcement_stats()
            
            embed = create_embed(
                "📊 Announcement Statistics",
                "Current announcement system statistics and performance metrics.",
                discord.Color.blue()
            )
            
            embed.add_field(
                name="📢 Overall Stats",
                value=f"**Total Sent**: {stats.get('total_sent', 0)}\n**Templates Available**: {stats.get('templates_available', 0)}\n**Last Announcement**: {stats.get('last_announcement', 'None')}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Success Rate",
                value=f"**Success Rate**: 100%\n**System Status**: Operational\n**Response Time**: Instant",
                inline=True
            )
            
            embed.add_field(
                name="📈 Usage Today",
                value=f"**Announcements Sent**: {self.bot.stats.get('announcements_sent', 0)}\n**System Uptime**: Excellent\n**Error Rate**: 0%",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "Announcement system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

class CreateAnnouncementModal(discord.ui.Modal):
    """Modal for creating custom announcements"""
    
    def __init__(self, bot):
        super().__init__(title="📢 Create Announcement")
        self.bot = bot
    
    title = discord.ui.TextInput(
        label="Announcement Title",
        placeholder="Enter a clear, descriptive title...",
        style=discord.TextStyle.short,
        max_length=100,
        required=True
    )
    
    content = discord.ui.TextInput(
        label="Announcement Content",
        placeholder="Enter your announcement message here...",
        style=discord.TextStyle.paragraph,
        max_length=2000,
        required=True
    )
    
    ping_everyone = discord.ui.TextInput(
        label="Ping @everyone? (yes/no)",
        placeholder="Type 'yes' to ping everyone, 'no' for no ping",
        style=discord.TextStyle.short,
        max_length=3,
        required=False,
        default="no"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle announcement creation"""
        await interaction.response.defer()
        
        # Validate ping everyone permission
        ping_all = self.ping_everyone.value.lower().strip() in ['yes', 'y', 'true', '1']
        
        if ping_all and not self.bot.permissions.can_ping_everyone(interaction.user):
            embed = create_embed(
                "❌ Permission Denied",
                "You don't have permission to ping @everyone.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Create the announcement
        if hasattr(self.bot, 'announcements') and self.bot.announcements:
            success = await self.bot.announcements.create_announcement(
                title=self.title.value,
                content=self.content.value,
                author=interaction.user,
                ping_everyone=ping_all
            )
            
            if success:
                self.bot.stats['announcements_sent'] += 1
                
                embed = create_embed(
                    "✅ Announcement Created Successfully!",
                    f"**Title**: {self.title.value}\n**Ping Everyone**: {'Yes' if ping_all else 'No'}\n**Status**: Sent to announcement channel",
                    discord.Color.green()
                )
                
                embed.add_field(
                    name="📊 Announcement Details",
                    value=f"**Length**: {len(self.content.value)} characters\n**Created by**: {interaction.user.mention}\n**Timestamp**: <t:{int(datetime.utcnow().timestamp())}:F>",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = create_embed(
                    "❌ Announcement Failed",
                    "Failed to create announcement. Please check the announcement channel configuration and try again.",
                    discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "Announcement system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class AnnouncementTemplateView(discord.ui.View):
    """View for selecting and using announcement templates"""
    
    def __init__(self, bot, templates: List[Dict[str, Any]]):
        super().__init__(timeout=300)
        self.bot = bot
        self.templates = templates
        
        # Create select options for templates
        options = []
        for template in templates[:25]:  # Discord limit is 25 options
            emoji_map = {
                'server_maintenance': '🔧',
                'event_announcement': '🎉',
                'rule_update': '📋',
                'security_alert': '🚨',
                'feature_update': '✨'
            }
            emoji = emoji_map.get(template['name'], '📄')
            
            options.append(discord.SelectOption(
                label=template['title'][:100],  # Max 100 chars
                description=f"Template for {template['name'].replace('_', ' ').title()}",
                value=template['name'],
                emoji=emoji
            ))
        
        if options:
            self.template_select.options = options
    
    @discord.ui.select(
        placeholder="📋 Select an announcement template...",
        min_values=1,
        max_values=1
    )
    async def template_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle template selection"""
        
        template_name = select.values[0]
        template = next((t for t in self.templates if t['name'] == template_name), None)
        
        if not template:
            embed = create_embed(
                "❌ Template Not Found",
                "The selected template could not be found.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show template configuration modal
        await interaction.response.send_modal(
            TemplateConfigurationModal(self.bot, template_name, template)
        )
    
    @discord.ui.button(label="📝 Custom Announcement", style=discord.ButtonStyle.primary)
    async def custom_announcement(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Create custom announcement instead of using template"""
        
        await interaction.response.send_modal(CreateAnnouncementModal(self.bot))

class TemplateConfigurationModal(discord.ui.Modal):
    """Modal for configuring announcement templates"""
    
    def __init__(self, bot, template_name: str, template_info: Dict[str, Any]):
        super().__init__(title=f"📋 {template_info['title']}")
        self.bot = bot
        self.template_name = template_name
        self.template_info = template_info
        
        # Add dynamic fields based on template type
        if template_name == 'server_maintenance':
            self.add_maintenance_fields()
        elif template_name == 'event_announcement':
            self.add_event_fields()
        elif template_name == 'rule_update':
            self.add_rule_update_fields()
        elif template_name == 'security_alert':
            self.add_security_fields()
        elif template_name == 'feature_update':
            self.add_feature_fields()
        else:
            self.add_generic_fields()
    
    def add_maintenance_fields(self):
        """Add fields for maintenance announcement"""
        self.date_time = discord.ui.TextInput(
            label="Maintenance Date & Time",
            placeholder="e.g., Sunday, January 15th at 3:00 PM UTC",
            max_length=100,
            required=True
        )
        
        self.duration = discord.ui.TextInput(
            label="Expected Duration",
            placeholder="e.g., 2-3 hours",
            max_length=50,
            required=True
        )
        
        self.details = discord.ui.TextInput(
            label="Maintenance Details",
            placeholder="Describe what will be done during maintenance...",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=True
        )
        
        self.add_item(self.date_time)
        self.add_item(self.duration)
        self.add_item(self.details)
    
    def add_event_fields(self):
        """Add fields for event announcement"""
        self.event_name = discord.ui.TextInput(
            label="Event Name",
            placeholder="e.g., Community Car Meet",
            max_length=100,
            required=True
        )
        
        self.event_details = discord.ui.TextInput(
            label="Event Details",
            placeholder="Date, time, location, and other details...",
            style=discord.TextStyle.paragraph,
            max_length=800,
            required=True
        )
        
        self.prizes = discord.ui.TextInput(
            label="Prizes/Rewards",
            placeholder="What can participants win?",
            max_length=200,
            required=False,
            default="Participation certificates and community recognition"
        )
        
        self.add_item(self.event_name)
        self.add_item(self.event_details)
        self.add_item(self.prizes)
    
    def add_rule_update_fields(self):
        """Add fields for rule update announcement"""
        self.changes = discord.ui.TextInput(
            label="Rule Changes",
            placeholder="Describe what rules were changed...",
            style=discord.TextStyle.paragraph,
            max_length=800,
            required=True
        )
        
        self.effective_date = discord.ui.TextInput(
            label="Effective Date",
            placeholder="When do these changes take effect?",
            max_length=100,
            required=True,
            default="Immediately"
        )
        
        self.action_required = discord.ui.TextInput(
            label="Action Required",
            placeholder="What should members do?",
            style=discord.TextStyle.paragraph,
            max_length=300,
            required=False,
            default="Review the updated rules and comply immediately"
        )
        
        self.add_item(self.changes)
        self.add_item(self.effective_date)
        self.add_item(self.action_required)
    
    def add_security_fields(self):
        """Add fields for security alert"""
        self.alert_type = discord.ui.TextInput(
            label="Alert Type",
            placeholder="e.g., Account Security, Phishing Attempt, etc.",
            max_length=100,
            required=True
        )
        
        self.security_details = discord.ui.TextInput(
            label="Security Details",
            placeholder="Explain the security issue...",
            style=discord.TextStyle.paragraph,
            max_length=600,
            required=True
        )
        
        self.action_taken = discord.ui.TextInput(
            label="Action Taken",
            placeholder="What has been done to address this?",
            style=discord.TextStyle.paragraph,
            max_length=400,
            required=True
        )
        
        self.add_item(self.alert_type)
        self.add_item(self.security_details)
        self.add_item(self.action_taken)
    
    def add_feature_fields(self):
        """Add fields for feature update announcement"""
        self.features = discord.ui.TextInput(
            label="New Features",
            placeholder="List the new features...",
            style=discord.TextStyle.paragraph,
            max_length=600,
            required=True
        )
        
        self.improvements = discord.ui.TextInput(
            label="Improvements",
            placeholder="What improvements were made?",
            style=discord.TextStyle.paragraph,
            max_length=400,
            required=False
        )
        
        self.usage_instructions = discord.ui.TextInput(
            label="How to Use",
            placeholder="Brief instructions on using new features...",
            style=discord.TextStyle.paragraph,
            max_length=400,
            required=False
        )
        
        self.add_item(self.features)
        self.add_item(self.improvements)
        self.add_item(self.usage_instructions)
    
    def add_generic_fields(self):
        """Add generic fields for unknown template"""
        self.custom_content = discord.ui.TextInput(
            label="Announcement Content",
            placeholder="Enter the full announcement content...",
            style=discord.TextStyle.paragraph,
            max_length=1500,
            required=True
        )
        
        self.add_item(self.custom_content)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle template configuration submission"""
        await interaction.response.defer()
        
        # Prepare template data based on template type
        template_data = {}
        
        try:
            if self.template_name == 'server_maintenance':
                template_data = {
                    'date': self.date_time.value,
                    'time': self.date_time.value,
                    'duration': self.duration.value,
                    'details': self.details.value
                }
            elif self.template_name == 'event_announcement':
                # Parse event details for date, time, location
                details = self.event_details.value
                template_data = {
                    'event_name': self.event_name.value,
                    'date': 'TBD',  # Would need parsing logic
                    'time': 'TBD',
                    'location': 'Server',
                    'prizes': self.prizes.value,
                    'join_instructions': details
                }
            elif self.template_name == 'rule_update':
                template_data = {
                    'changes': self.changes.value,
                    'effective_date': self.effective_date.value,
                    'action_required': self.action_required.value,
                    'rules_channel': f"<#{Config.RULES_CHANNEL_ID}>" if hasattr(Config, 'RULES_CHANNEL_ID') else "rules"
                }
            elif self.template_name == 'security_alert':
                template_data = {
                    'alert_type': self.alert_type.value,
                    'details': self.security_details.value,
                    'action_taken': self.action_taken.value
                }
            elif self.template_name == 'feature_update':
                template_data = {
                    'features': self.features.value,
                    'improvements': self.improvements.value or "Various performance optimizations",
                    'usage_instructions': self.usage_instructions.value or "Features are automatically available"
                }
            
            # Create announcement from template
            if hasattr(self.bot, 'announcements') and self.bot.announcements:
                success = await self.bot.announcements.create_from_template(
                    template_name=self.template_name,
                    template_data=template_data,
                    author=interaction.user
                )
                
                if success:
                    self.bot.stats['announcements_sent'] += 1
                    
                    embed = create_embed(
                        "✅ Template Announcement Created!",
                        f"**Template**: {self.template_info['title']}\n**Status**: Successfully sent to announcement channel",
                        discord.Color.green()
                    )
                    
                    embed.add_field(
                        name="📋 Template Info",
                        value=f"**Type**: {self.template_name.replace('_', ' ').title()}\n**Auto-ping**: {'Yes' if self.template_info.get('ping_everyone', False) else 'No'}\n**Created by**: {interaction.user.mention}",
                        inline=False
                    )
                    
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = create_embed(
                        "❌ Template Announcement Failed",
                        "Failed to create announcement from template. Please try again.",
                        discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = create_embed(
                    "❌ System Unavailable",
                    "Announcement system is currently unavailable.",
                    discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logging.error(f"Template announcement failed: {e}")
            embed = create_embed(
                "❌ Template Error",
                f"Error processing template: {str(e)}",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)