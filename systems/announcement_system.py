import discord
from datetime import datetime, timedelta
import logging
from typing import Optional, Dict, Any, List

from config.settings import Config
from utils.helpers import create_embed

class AnnouncementSystem:
    """Advanced announcement system for Pakistan RP Community"""
    
    def __init__(self, bot):
        self.bot = bot
        self.last_announcement_time = {}  # Track cooldowns per user
        self.announcement_templates = {
            "server_maintenance": {
                "title": "🔧 Server Maintenance Notice",
                "template": "**Scheduled Maintenance**\n\n📅 **Date**: {date}\n⏰ **Time**: {time}\n⏱️ **Duration**: {duration}\n\n📋 **What's being done**:\n{details}\n\n⚠️ **Important**: The server will be temporarily unavailable during this time. Please plan accordingly.\n\n📞 **Questions?** Contact staff in <#ticket-creation>",
                "color": 0xF39C12,
                "ping_everyone": True
            },
            "event_announcement": {
                "title": "🎉 Community Event",
                "template": "**Exciting Event Alert!**\n\n🎯 **Event**: {event_name}\n📅 **Date**: {date}\n⏰ **Time**: {time}\n📍 **Location**: {location}\n\n🎁 **Prizes**: {prizes}\n📋 **How to Join**: {join_instructions}\n\n🚀 **Don't miss out on this amazing community event!**\n\n#PakistanRP #CommunityEvent",
                "color": 0x2ECC71,
                "ping_everyone": False
            },
            "rule_update": {
                "title": "📋 Rule Update",
                "template": "**Important Rule Changes**\n\n📝 **What Changed**: {changes}\n📅 **Effective**: {effective_date}\n⚠️ **Action Required**: {action_required}\n\n📚 **Updated Rules**: Check <#{rules_channel}>\n🔍 **Questions?** Use our rule search system or create a ticket\n\n**All players are expected to follow the updated rules immediately.**",
                "color": 0xE74C3C,
                "ping_everyone": True
            },
            "security_alert": {
                "title": "🚨 Security Alert",
                "template": "**Security Notice**\n\n⚠️ **Alert Type**: {alert_type}\n📋 **Details**: {details}\n✅ **Action Taken**: {action_taken}\n\n🔐 **Your Security**:\n• Change your password if requested\n• Don't share personal information\n• Report suspicious activity to staff\n\n📞 **Need Help?** Create a support ticket immediately",
                "color": 0xE74C3C,
                "ping_everyone": True
            },
            "feature_update": {
                "title": "✨ New Features",
                "template": "**Exciting Updates Are Here!**\n\n🆕 **New Features**:\n{features}\n\n🔧 **Improvements**:\n{improvements}\n\n📋 **How to Use**: {usage_instructions}\n\n🎯 **Benefits**: These updates will enhance your roleplay experience!\n\n💬 **Feedback?** Let us know in <#feedback> or create a ticket",
                "color": 0x3498DB,
                "ping_everyone": False
            }
        }
    
    async def create_announcement(self, title: str, content: str, author: discord.Member, 
                                ping_everyone: bool = False, template_name: str = None) -> bool:
        """Create and send an announcement"""
        try:
            # Check cooldown
            if not self.check_cooldown(author):
                return False
            
            # Get announcement channel
            announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENTS_CHANNEL_ID)
            if not announcement_channel:
                logging.error("Announcement channel not found")
                return False
            
            # Create announcement embed
            embed = self.create_announcement_embed(title, content, author, template_name)
            
            # Prepare mention content
            mention_content = ""
            if ping_everyone and self.bot.permissions.can_ping_everyone(author):
                mention_content = "@everyone"
            
            # Send announcement
            message = await announcement_channel.send(
                content=mention_content,
                embed=embed
            )
            
            # Log to database
            if self.bot.db:
                announcement_id = await self.bot.db.create_announcement(
                    title=title,
                    content=content,
                    author_id=author.id,
                    author_name=str(author),
                    ping_everyone=ping_everyone
                )
                
                await self.bot.db.log_action(
                    action_type="ANNOUNCEMENT_CREATED",
                    staff_id=author.id,
                    details=f"Title: {title}, Ping Everyone: {ping_everyone}",
                    channel_id=announcement_channel.id,
                    message_id=message.id
                )
            
            # Update cooldown
            self.last_announcement_time[author.id] = datetime.utcnow()
            
            # Send to logs
            await self.log_announcement(title, content, author, ping_everyone)
            
            print(f"📢 Announcement sent by {author}: {title}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to create announcement: {e}")
            return False
    
    def create_announcement_embed(self, title: str, content: str, author: discord.Member, 
                                template_name: str = None) -> discord.Embed:
        """Create a formatted announcement embed"""
        
        # Get template info if provided
        template_info = self.announcement_templates.get(template_name, {})
        color = template_info.get('color', 0x3498DB)
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=content,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        # Add announcement header
        embed.add_field(
            name="📢 Official Announcement",
            value=f"**From**: {author.mention}\n**Posted**: <t:{int(datetime.utcnow().timestamp())}:F>",
            inline=False
        )
        
        # Add footer
        embed.set_footer(
            text=f"Pakistan RP Official • Posted by {author.display_name}",
            icon_url=author.display_avatar.url
        )
        
        # Add server icon as thumbnail if available
        if author.guild and author.guild.icon:
            embed.set_thumbnail(url=author.guild.icon.url)
        
        return embed
    
    async def create_from_template(self, template_name: str, template_data: Dict[str, str], 
                                 author: discord.Member) -> bool:
        """Create announcement from template"""
        
        if template_name not in self.announcement_templates:
            return False
        
        template = self.announcement_templates[template_name]
        
        try:
            # Format template with provided data
            title = template['title']
            content = template['template'].format(**template_data)
            ping_everyone = template.get('ping_everyone', False)
            
            return await self.create_announcement(
                title=title,
                content=content,
                author=author,
                ping_everyone=ping_everyone,
                template_name=template_name
            )
            
        except KeyError as e:
            logging.error(f"Missing template data: {e}")
            return False
    
    def check_cooldown(self, author: discord.Member) -> bool:
        """Check if user can make an announcement (cooldown check)"""
        
        # Admins have no cooldown
        if self.bot.permissions.is_admin(author):
            return True
        
        # Check cooldown
        if author.id in self.last_announcement_time:
            time_diff = datetime.utcnow() - self.last_announcement_time[author.id]
            if time_diff < timedelta(minutes=Config.ANNOUNCEMENT_COOLDOWN_MINUTES):
                return False
        
        return True
    
    def get_cooldown_remaining(self, author: discord.Member) -> int:
        """Get remaining cooldown time in seconds"""
        
        if self.bot.permissions.is_admin(author):
            return 0
        
        if author.id in self.last_announcement_time:
            time_diff = datetime.utcnow() - self.last_announcement_time[author.id]
            cooldown_time = timedelta(minutes=Config.ANNOUNCEMENT_COOLDOWN_MINUTES)
            
            if time_diff < cooldown_time:
                remaining = cooldown_time - time_diff
                return int(remaining.total_seconds())
        
        return 0
    
    async def log_announcement(self, title: str, content: str, author: discord.Member, 
                             ping_everyone: bool):
        """Log announcement to staff logs"""
        
        if not Config.STAFF_LOGS_CHANNEL_ID:
            return
        
        logs_channel = self.bot.get_channel(Config.STAFF_LOGS_CHANNEL_ID)
        if not logs_channel:
            return
        
        try:
            embed = create_embed(
                "📢 Announcement Created",
                f"**Title**: {title}\n**Author**: {author.mention}\n**Ping Everyone**: {'Yes' if ping_everyone else 'No'}",
                discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Content Preview",
                value=content[:300] + ("..." if len(content) > 300 else ""),
                inline=False
            )
            
            embed.set_footer(text=f"Announcement by {author.display_name}", icon_url=author.display_avatar.url)
            
            await logs_channel.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Failed to log announcement: {e}")
    
    async def schedule_announcement(self, title: str, content: str, author: discord.Member,
                                  schedule_time: datetime, ping_everyone: bool = False) -> bool:
        """Schedule an announcement for later (placeholder for future implementation)"""
        
        # This would require a task scheduler system
        # For now, we'll just log the scheduled announcement
        
        try:
            if self.bot.db:
                await self.bot.db.log_action(
                    action_type="ANNOUNCEMENT_SCHEDULED",
                    staff_id=author.id,
                    details=f"Title: {title}, Scheduled for: {schedule_time.isoformat()}, Ping: {ping_everyone}"
                )
            
            print(f"📅 Announcement scheduled by {author}: {title} for {schedule_time}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to schedule announcement: {e}")
            return False
    
    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available announcement templates"""
        
        templates = []
        for name, template in self.announcement_templates.items():
            templates.append({
                'name': name,
                'title': template['title'],
                'description': template['template'][:100] + "...",
                'color': template.get('color', 0x3498DB),
                'ping_everyone': template.get('ping_everyone', False)
            })
        
        return templates
    
    async def get_announcement_stats(self) -> Dict[str, Any]:
        """Get announcement statistics"""
        
        try:
            if not self.bot.db:
                return {}
            
            # Get stats from database
            stats = {}
            
            # This would require additional database queries
            # For now, return basic stats
            stats['total_sent'] = self.bot.stats.get('announcements_sent', 0)
            stats['templates_available'] = len(self.announcement_templates)
            stats['last_announcement'] = "Recent" if self.last_announcement_time else "None"
            
            return stats
            
        except Exception as e:
            logging.error(f"Failed to get announcement stats: {e}")
            return {}
    
    async def delete_announcement(self, message_id: int, author: discord.Member) -> bool:
        """Delete an announcement message"""
        
        try:
            announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENTS_CHANNEL_ID)
            if not announcement_channel:
                return False
            
            message = await announcement_channel.fetch_message(message_id)
            if not message:
                return False
            
            await message.delete()
            
            # Log deletion
            if self.bot.db:
                await self.bot.db.log_action(
                    action_type="ANNOUNCEMENT_DELETED",
                    staff_id=author.id,
                    details=f"Deleted announcement message ID: {message_id}",
                    channel_id=announcement_channel.id,
                    message_id=message_id
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to delete announcement: {e}")
            return False
    
    async def edit_announcement(self, message_id: int, new_title: str, new_content: str, 
                              author: discord.Member) -> bool:
        """Edit an existing announcement"""
        
        try:
            announcement_channel = self.bot.get_channel(Config.ANNOUNCEMENTS_CHANNEL_ID)
            if not announcement_channel:
                return False
            
            message = await announcement_channel.fetch_message(message_id)
            if not message or not message.embeds:
                return False
            
            # Create new embed with updated content
            new_embed = self.create_announcement_embed(new_title, new_content, author)
            
            # Add edit notice
            new_embed.add_field(
                name="✏️ Edited",
                value=f"Last edited by {author.mention} at <t:{int(datetime.utcnow().timestamp())}:F>",
                inline=False
            )
            
            await message.edit(embed=new_embed)
            
            # Log edit
            if self.bot.db:
                await self.bot.db.log_action(
                    action_type="ANNOUNCEMENT_EDITED",
                    staff_id=author.id,
                    details=f"Edited announcement: {new_title}",
                    channel_id=announcement_channel.id,
                    message_id=message_id
                )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to edit announcement: {e}")
            return False