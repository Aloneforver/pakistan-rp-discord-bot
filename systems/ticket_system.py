import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import json
import os
import logging

from config.settings import Config
from utils.helpers import create_embed, format_duration, get_timestamp

class AdvancedTicketSystem:
    """Advanced automated ticket management system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets: Dict[str, Dict[str, Any]] = {}
        self.ticket_counter = 0
        self.transcript_dir = "transcripts/"
        
        # Ticket categories with automated responses
        self.categories = {
            "Support": {
                "emoji": "🔧",
                "color": 0x3498DB,
                "auto_response": (
                    "Thank you for contacting Pakistan RP Support! 🔧\n\n"
                    "To help us assist you better, please provide:\n"
                    "📝 **Description**: Detailed explanation of your issue\n"
                    "📱 **Platform**: PC/Mobile\n"
                    "🎮 **In-game name**: Your character name\n"
                    "📸 **Screenshots**: If applicable\n\n"
                    "⏱️ **Expected response time**: 10-15 minutes"
                ),
                "priority_modifier": 0,
                "assigned_roles": [Config.STAFF_ROLE_ID, Config.HELPER_ROLE_ID]
            },
            "Player Report": {
                "emoji": "👤",
                "color": 0xE74C3C,
                "auto_response": (
                    "Thank you for reporting a rule violation! 👤\n\n"
                    "**Required information:**\n"
                    "🎯 **Player name**: Who are you reporting?\n"
                    "📋 **Rule violated**: Which rule was broken?\n"
                    "📸 **Evidence**: Screenshots/videos are REQUIRED\n"
                    "📅 **Date/Time**: When did this occur?\n"
                    "📍 **Location**: Where in the server?\n\n"
                    "⚠️ **Note**: Reports without evidence will be closed\n"
                    "⏱️ **Expected response time**: 15-20 minutes"
                ),
                "priority_modifier": 1,
                "assigned_roles": [Config.MODERATOR_ROLE_ID, Config.STAFF_ROLE_ID]
            },
            "Bug Report": {
                "emoji": "🐛",
                "color": 0xF39C12,
                "auto_response": (
                    "Thank you for reporting a bug! 🐛\n\n"
                    "Please provide detailed information:\n"
                    "🔍 **Bug description**: What exactly happened?\n"
                    "🔄 **Steps to reproduce**: How can we recreate this?\n"
                    "💻 **Device/Platform**: PC, Mobile, etc.\n"
                    "📸 **Screenshots/Video**: Visual proof helps!\n"
                    "⚙️ **Server location**: Where did this occur?\n\n"
                    "🔧 Our development team will investigate this issue\n"
                    "⏱️ **Expected response time**: 20-30 minutes"
                ),
                "priority_modifier": 2,
                "assigned_roles": [Config.ADMIN_ROLE_ID, Config.SENIOR_STAFF_ROLE_ID]
            },
            "Gang Registration": {
                "emoji": "🏢",
                "color": 0x9B59B6,
                "auto_response": (
                    "Welcome to Gang Registration! 🏢\n\n"
                    "**Required information for gang approval:**\n"
                    "🏷️ **Gang name**: Choose a unique name\n"
                    "👑 **Leader**: Gang leader's name\n"
                    "👥 **Members**: List of initial members\n"
                    "📋 **Purpose**: Gang's roleplay purpose\n"
                    "🎨 **Logo**: Gang logo/emblem\n"
                    "💰 **Registration fee**: Confirm payment\n\n"
                    "📚 Please review gang rules before submitting\n"
                    "⏱️ **Expected response time**: 30-45 minutes"
                ),
                "priority_modifier": 0,
                "assigned_roles": [Config.ADMIN_ROLE_ID, Config.SENIOR_STAFF_ROLE_ID]
            },
            "Shop": {
                "emoji": "🛍️",
                "color": 0x2ECC71,
                "auto_response": (
                    "Welcome to Pakistan RP Shop Support! 🛍️\n\n"
                    "**For purchase issues, please provide:**\n"
                    "🛒 **Item name**: What did you purchase?\n"
                    "💳 **Transaction ID**: Payment confirmation\n"
                    "📧 **Email**: Used for purchase\n"
                    "📸 **Receipt**: Screenshot of payment\n"
                    "❓ **Issue**: What went wrong?\n\n"
                    "💰 Refunds processed within 24-48 hours\n"
                    "⏱️ **Expected response time**: 15-25 minutes"
                ),
                "priority_modifier": 1,
                "assigned_roles": [Config.ADMIN_ROLE_ID, Config.STAFF_ROLE_ID]
            },
            "Other": {
                "emoji": "❓",
                "color": 0x95A5A6,
                "auto_response": (
                    "Thank you for contacting us! ❓\n\n"
                    "Since you selected 'Other', please provide:\n"
                    "📝 **Detailed description**: Explain your situation\n"
                    "🎯 **What you need**: How can we help?\n"
                    "📸 **Additional info**: Any relevant screenshots\n\n"
                    "Our staff will review your request and respond appropriately\n"
                    "⏱️ **Expected response time**: 15-20 minutes"
                ),
                "priority_modifier": 0,
                "assigned_roles": [Config.STAFF_ROLE_ID, Config.HELPER_ROLE_ID]
            }
        }
        
        # Urgency levels
        self.urgency_levels = {
            "Low": {"emoji": "🟢", "modifier": 0, "description": "Non-urgent, can wait"},
            "Medium": {"emoji": "🟡", "modifier": 1, "description": "Standard priority"},
            "High": {"emoji": "🟠", "modifier": 2, "description": "Needs quick attention"},
            "Critical": {"emoji": "🔴", "modifier": 3, "description": "Urgent issue"}
        }
    
    async def initialize(self):
        """Initialize ticket system"""
        os.makedirs(self.transcript_dir, exist_ok=True)
        await self.load_active_tickets()
        print("✅ Advanced ticket system ready")
    
    async def create_ticket(self, user: discord.Member, category: str, description: str, urgency: str) -> Dict[str, Any]:
        """Create a new support ticket with automation"""
        try:
            self.ticket_counter += 1
            ticket_id = f"TKT-{self.ticket_counter:04d}"
            
            guild = user.guild
            tickets_category = guild.get_channel(Config.TICKETS_CATEGORY_ID)
            
            if not tickets_category:
                # Create tickets category if it doesn't exist
                tickets_category = await guild.create_category(
                    "🎫 Support Tickets",
                    reason="Auto-created by ticket system"
                )
            
            # Calculate final priority
            category_info = self.categories.get(category, self.categories["Other"])
            urgency_info = self.urgency_levels.get(urgency, self.urgency_levels["Medium"])
            final_priority = category_info["priority_modifier"] + urgency_info["modifier"]
            
            # Create ticket channel
            channel_name = f"ticket-{ticket_id.lower()}-{user.display_name}".replace(" ", "-")
            
            # Set permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
            }
            
            # Add staff permissions based on category
            for role_id in category_info["assigned_roles"]:
                if role_id and role_id != 0:
                    role = guild.get_role(role_id)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(
                            view_channel=True,
                            send_messages=True,
                            read_message_history=True,
                            manage_messages=True,
                            attach_files=True
                        )
            
            # Create the channel
            ticket_channel = await tickets_category.create_text_channel(
                name=channel_name,
                overwrites=overwrites,
                topic=f"🎫 {category} ticket for {user.display_name} | ID: {ticket_id} | {urgency} Priority",
                reason=f"Support ticket created by {user}"
            )
            
            # Store ticket data
            ticket_data = {
                'ticket_id': ticket_id,
                'user_id': user.id,
                'username': str(user),
                'display_name': user.display_name,
                'channel_id': ticket_channel.id,
                'category': category,
                'urgency': urgency,
                'priority': final_priority,
                'description': description,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'open',
                'assigned_staff': None,
                'messages': [],
                'staff_involved': [],
                'last_activity': datetime.utcnow().isoformat()
            }
            
            self.active_tickets[ticket_id] = ticket_data
            
            # Create ticket embed
            embed = discord.Embed(
                title=f"{category_info['emoji']} {category} Ticket #{ticket_id}",
                description=f"**Ticket created for:** {user.mention}\n**Priority:** {urgency_info['emoji']} {urgency}",
                color=category_info["color"],
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Issue Description",
                value=description[:1000] + ("..." if len(description) > 1000 else ""),
                inline=False
            )
            
            embed.add_field(
                name="⏰ Created",
                value=f"<t:{int(datetime.utcnow().timestamp())}:F>",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Category",
                value=f"{category_info['emoji']} {category}",
                inline=True
            )
            
            embed.add_field(
                name="🚨 Urgency",
                value=f"{urgency_info['emoji']} {urgency}",
                inline=True
            )
            
            # Add staff ping based on priority
            staff_ping = ""
            if final_priority >= 3:  # Critical
                staff_ping = f"🚨 **CRITICAL TICKET** 🚨\n"
                if Config.ADMIN_ROLE_ID:
                    staff_ping += f"<@&{Config.ADMIN_ROLE_ID}> "
            elif final_priority >= 2:  # High
                if Config.SENIOR_STAFF_ROLE_ID:
                    staff_ping = f"<@&{Config.SENIOR_STAFF_ROLE_ID}> "
            
            # Send initial message with automated response
            from ui.ticket_views import TicketManagementView
            initial_message = await ticket_channel.send(
                content=f"{staff_ping}{user.mention} Welcome to your support ticket!",
                embed=embed,
                view=TicketManagementView(self, ticket_id)
            )
            
            # Send automated category response
            auto_response_embed = discord.Embed(
                title=f"🤖 Automated Response - {category}",
                description=category_info["auto_response"],
                color=0x3498DB,
                timestamp=datetime.utcnow()
            )
            auto_response_embed.set_footer(text="This is an automated message • Staff will respond soon")
            
            await ticket_channel.send(embed=auto_response_embed)
            
            # Log ticket creation
            await self.log_ticket_action("CREATED", ticket_data, user, f"Category: {category}, Urgency: {urgency}")
            
            # Save to database
            if self.bot.db:
                await self.bot.db.create_ticket(ticket_data)
            
            # Update statistics
            self.bot.stats['tickets_created'] += 1
            
            print(f"✅ Ticket {ticket_id} created for {user} in #{ticket_channel.name}")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'channel': ticket_channel,
                'data': ticket_data
            }
            
        except Exception as e:
            logging.error(f"Failed to create ticket: {e}")
            return {'success': False, 'error': str(e)}
    
    async def close_ticket(self, ticket_id: str, closed_by: discord.Member, reason: str = "Resolved") -> bool:
        """Close a ticket with full logging and transcript"""
        try:
            if ticket_id not in self.active_tickets:
                return False
            
            ticket_data = self.active_tickets[ticket_id]
            ticket_data['status'] = 'closed'
            ticket_data['closed_at'] = datetime.utcnow().isoformat()
            ticket_data['closed_by'] = closed_by.id
            ticket_data['close_reason'] = reason
            
            # Generate and save transcript
            transcript_content = await self.generate_transcript(ticket_id)
            transcript_file = await self.save_transcript(ticket_id, transcript_content)
            
            # Send transcript to user
            user = self.bot.get_user(ticket_data['user_id'])
            if user:
                try:
                    embed = create_embed(
                        f"🎫 Ticket {ticket_id} Closed",
                        f"**Reason**: {reason}\n**Closed by**: {closed_by.mention}\n**Duration**: {self.calculate_duration(ticket_data)}",
                        discord.Color.red()
                    )
                    
                    if transcript_file and os.path.exists(transcript_file):
                        file = discord.File(transcript_file, filename=f"transcript_{ticket_id}.txt")
                        await user.send(embed=embed, file=file)
                    else:
                        await user.send(embed=embed)
                        
                except discord.Forbidden:
                    print(f"⚠️ Could not DM transcript to {user}")
            
            # Send transcript to logs
            await self.send_transcript_to_logs(ticket_id, transcript_file, closed_by)
            
            # Log ticket closure
            await self.log_ticket_action("CLOSED", ticket_data, closed_by, f"Reason: {reason}")
            
            # Update database
            if self.bot.db:
                await self.bot.db.close_ticket(ticket_id, closed_by.id, reason)
            
            # Update statistics
            self.bot.stats['tickets_resolved'] += 1
            
            # Remove from active tickets
            del self.active_tickets[ticket_id]
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to close ticket {ticket_id}: {e}")
            return False
    
    async def generate_transcript(self, ticket_id: str) -> str:
        """Generate a comprehensive ticket transcript"""
        if ticket_id not in self.active_tickets:
            return ""
        
        ticket_data = self.active_tickets[ticket_id]
        
        # Get channel for recent messages
        channel = self.bot.get_channel(ticket_data['channel_id'])
        messages = []
        
        if channel:
            async for message in channel.history(limit=None, oldest_first=True):
                messages.append({
                    'author': str(message.author),
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'attachments': [att.url for att in message.attachments],
                    'embeds': len(message.embeds)
                })
        
        # Generate transcript
        transcript = f"""
PAKISTAN RP SUPPORT TICKET TRANSCRIPT
=====================================

Ticket ID: {ticket_id}
Category: {ticket_data['category']}
Urgency: {ticket_data['urgency']}
User: {ticket_data['username']} (ID: {ticket_data['user_id']})
Created: {ticket_data['created_at']}
Closed: {ticket_data.get('closed_at', 'N/A')}
Duration: {self.calculate_duration(ticket_data)}

Initial Description:
{ticket_data['description']}

Staff Involved: {', '.join(ticket_data.get('staff_involved', [])) or 'None'}
Close Reason: {ticket_data.get('close_reason', 'N/A')}

=====================================
FULL CONVERSATION LOG
=====================================

"""
        
        for i, msg in enumerate(messages, 1):
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            transcript += f"[{timestamp}] {msg['author']}: {msg['content']}\n"
            
            if msg['attachments']:
                for att in msg['attachments']:
                    transcript += f"    📎 Attachment: {att}\n"
            
            if msg['embeds']:
                transcript += f"    📋 {msg['embeds']} embed(s)\n"
            
            transcript += "\n"
        
        transcript += f"""
=====================================
TICKET SUMMARY
=====================================

Total Messages: {len(messages)}
Ticket Duration: {self.calculate_duration(ticket_data)}
Resolution Status: {ticket_data.get('close_reason', 'Open')}
Generated: {datetime.utcnow().isoformat()}

Pakistan RP Community Management System
"""
        
        return transcript
    
    async def save_transcript(self, ticket_id: str, content: str) -> str:
        """Save transcript to file"""
        try:
            filename = f"transcript_{ticket_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(self.transcript_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filepath
        except Exception as e:
            logging.error(f"Failed to save transcript: {e}")
            return ""
    
    async def send_transcript_to_logs(self, ticket_id: str, transcript_file: str, closed_by: discord.Member):
        """Send transcript to logs channel"""
        if not Config.TICKET_LOGS_CHANNEL_ID:
            return
        
        logs_channel = self.bot.get_channel(Config.TICKET_LOGS_CHANNEL_ID)
        if not logs_channel:
            return
        
        try:
            ticket_data = self.active_tickets.get(ticket_id, {})
            
            embed = create_embed(
                f"📄 Ticket Transcript - {ticket_id}",
                f"**Category**: {ticket_data.get('category', 'Unknown')}\n**User**: <@{ticket_data.get('user_id')}>\n**Closed by**: {closed_by.mention}",
                discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 Ticket Details",
                value=f"**Duration**: {self.calculate_duration(ticket_data)}\n**Urgency**: {ticket_data.get('urgency', 'Unknown')}\n**Staff**: {len(ticket_data.get('staff_involved', []))} involved",
                inline=False
            )
            
            if transcript_file and os.path.exists(transcript_file):
                file = discord.File(transcript_file, filename=f"transcript_{ticket_id}.txt")
                await logs_channel.send(embed=embed, file=file)
            else:
                embed.add_field(name="❌ Error", value="Transcript file not generated", inline=False)
                await logs_channel.send(embed=embed)
                
        except Exception as e:
            logging.error(f"Failed to send transcript to logs: {e}")
    
    async def log_ticket_action(self, action: str, ticket_data: Dict, user: discord.Member, details: str):
        """Log ticket actions to staff logs"""
        if not Config.STAFF_LOGS_CHANNEL_ID:
            return
        
        logs_channel = self.bot.get_channel(Config.STAFF_LOGS_CHANNEL_ID)
        if not logs_channel:
            return
        
        try:
            colors = {
                'CREATED': discord.Color.green(),
                'CLOSED': discord.Color.red(),
                'ASSIGNED': discord.Color.blue(),
                'UPDATED': discord.Color.orange()
            }
            
            emojis = {
                'CREATED': '🎫',
                'CLOSED': '🔒',
                'ASSIGNED': '👤',
                'UPDATED': '📝'
            }
            
            embed = create_embed(
                f"{emojis.get(action, '📋')} Ticket {action} - {ticket_data.get('ticket_id', 'Unknown')}",
                f"**User**: {user.mention}\n**Details**: {details}",
                colors.get(action, discord.Color.greyple())
            )
            
            embed.set_footer(text=f"Action by {user.display_name}", icon_url=user.display_avatar.url)
            
            await logs_channel.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Failed to log ticket action: {e}")
    
    def calculate_duration(self, ticket_data: Dict) -> str:
        """Calculate ticket duration"""
        try:
            created = datetime.fromisoformat(ticket_data['created_at'])
            closed = datetime.fromisoformat(ticket_data.get('closed_at', datetime.utcnow().isoformat()))
            
            duration = closed - created
            return format_duration(int(duration.total_seconds()))
        except:
            return "Unknown"
    
    async def get_active_tickets(self) -> List[Dict[str, Any]]:
        """Get all active tickets"""
        return list(self.active_tickets.values())
    
    async def cleanup_old_tickets(self) -> int:
        """Clean up tickets older than auto-close time"""
        cleaned = 0
        auto_close_hours = Config.TICKET_AUTO_CLOSE_HOURS
        
        for ticket_id, ticket_data in list(self.active_tickets.items()):
            created = datetime.fromisoformat(ticket_data['created_at'])
            if datetime.utcnow() - created > timedelta(hours=auto_close_hours):
                # Auto-close old tickets
                channel = self.bot.get_channel(ticket_data['channel_id'])
                if channel:
                    bot_user = self.bot.user
                    await self.close_ticket(ticket_id, bot_user, "Auto-closed due to inactivity")
                    try:
                        await channel.delete(reason=f"Auto-closed ticket {ticket_id}")
                    except:
                        pass
                    cleaned += 1
        
        return cleaned
    
    async def log_message(self, message: discord.Message):
        """Log message for transcript"""
        if not message.channel.name.startswith('ticket-'):
            return
        
        # Extract ticket ID from channel name
        try:
            parts = message.channel.name.split('-')
            if len(parts) >= 2:
                ticket_id = f"TKT-{parts[1].upper()}"
                
                if ticket_id in self.active_tickets:
                    # Update last activity
                    self.active_tickets[ticket_id]['last_activity'] = datetime.utcnow().isoformat()
                    
                    # Track staff involvement
                    if self.bot.permissions.is_staff(message.author):
                        staff_list = self.active_tickets[ticket_id].get('staff_involved', [])
                        if str(message.author) not in staff_list:
                            staff_list.append(str(message.author))
                            self.active_tickets[ticket_id]['staff_involved'] = staff_list
        except Exception as e:
            logging.error(f"Message logging error: {e}")
    
    async def load_active_tickets(self):
        """Load active tickets from database on startup"""
        try:
            if self.bot.db:
                tickets = await self.bot.db.get_active_tickets()
                for ticket in tickets:
                    self.active_tickets[ticket['ticket_id']] = ticket
                print(f"✅ Loaded {len(tickets)} active tickets")
        except Exception as e:
            print(f"⚠️ Could not load active tickets: {e}")