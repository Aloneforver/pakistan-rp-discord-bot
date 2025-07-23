import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging

from utils.helpers import create_embed, format_duration
from config.settings import Config  # FIXED: Added Config import

class TicketCreationView(discord.ui.View):
    """Beautiful ticket creation interface"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Create Support Ticket",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="create_ticket_main"
    )
    async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Main ticket creation button"""
        
        # Check if user already has open tickets
        if hasattr(self.bot, 'tickets') and self.bot.tickets:
            user_tickets = [t for t in self.bot.tickets.active_tickets.values() 
                          if t['user_id'] == interaction.user.id and t['status'] == 'open']
            
            max_tickets = Config.MAX_OPEN_TICKETS_PER_USER if hasattr(Config, 'MAX_OPEN_TICKETS_PER_USER') else 3
            
            if len(user_tickets) >= max_tickets:
                embed = create_embed(
                    "❌ Ticket Limit Reached",
                    f"You already have **{len(user_tickets)}** open tickets.\nPlease wait for them to be resolved before creating new ones.",
                    discord.Color.red()
                )
                
                if user_tickets:
                    ticket_list = "\n".join([f"• **#{t['ticket_id']}** - {t['category']}" for t in user_tickets[:3]])
                    embed.add_field(name="Your Open Tickets", value=ticket_list, inline=False)
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Show ticket creation modal
        await interaction.response.send_modal(TicketCreationModal(self.bot))

class TicketCreationModal(discord.ui.Modal):
    """Advanced ticket creation modal with all options"""
    
    def __init__(self, bot):
        super().__init__(title="🎫 Create Support Ticket")
        self.bot = bot
    
    # Category selection
    category = discord.ui.TextInput(
        label="Category",
        placeholder="Support, Player Report, Bug Report, Gang Registration, Shop, Other",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    
    # Issue description
    description = discord.ui.TextInput(
        label="Describe Your Issue",
        placeholder="Please provide detailed information about your problem or request...",
        style=discord.TextStyle.paragraph,
        max_length=2000,
        required=True
    )
    
    # Urgency level
    urgency = discord.ui.TextInput(
        label="Urgency Level",
        placeholder="Low, Medium, High, Critical",
        style=discord.TextStyle.short,
        max_length=20,
        required=False,
        default="Medium"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle ticket creation submission"""
        await interaction.response.defer()
        
        # Validate category
        valid_categories = ["Support", "Player Report", "Bug Report", "Gang Registration", "Shop", "Other"]
        category = self.category.value.title()
        
        if category not in valid_categories:
            # Find closest match or default to "Other"
            category_lower = self.category.value.lower()
            for valid_cat in valid_categories:
                if valid_cat.lower() in category_lower or category_lower in valid_cat.lower():
                    category = valid_cat
                    break
            else:
                category = "Other"
        
        # Validate urgency
        valid_urgency = ["Low", "Medium", "High", "Critical"]
        urgency = self.urgency.value.title() if self.urgency.value else "Medium"
        
        if urgency not in valid_urgency:
            urgency = "Medium"
        
        # Create the ticket
        if hasattr(self.bot, 'tickets') and self.bot.tickets:
            result = await self.bot.tickets.create_ticket(
                interaction.user,
                category,
                self.description.value,
                urgency
            )
            
            if result['success']:
                embed = create_embed(
                    "✅ Ticket Created Successfully!",
                    f"**Ticket ID**: #{result['ticket_id']}\n**Category**: {category}\n**Priority**: {urgency}\n**Channel**: {result['channel'].mention}",
                    discord.Color.green()
                )
                
                embed.add_field(
                    name="🚀 Next Steps",
                    value="1. Check the ticket channel created for you\n2. Provide any additional information requested\n3. Wait for staff response\n4. Our team will assist you shortly!",
                    inline=False
                )
                
                embed.set_footer(text=f"Ticket created • Expected response: {self.get_response_time(category)}")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = create_embed(
                    "❌ Ticket Creation Failed",
                    f"Sorry, we couldn't create your ticket right now.\n**Error**: {result.get('error', 'Unknown error')}",
                    discord.Color.red()
                )
                embed.add_field(
                    name="What to do",
                    value="Please try again in a few moments or contact staff directly if the issue persists.",
                    inline=False
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "The ticket system is currently unavailable. Please contact staff directly.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    def get_response_time(self, category: str) -> str:
        """Get expected response time for category"""
        times = {
            "Support": "10-15 minutes",
            "Player Report": "15-20 minutes", 
            "Bug Report": "20-30 minutes",
            "Gang Registration": "30-45 minutes",
            "Shop": "15-25 minutes",
            "Other": "15-20 minutes"
        }
        return times.get(category, "15-20 minutes")

class TicketManagementView(discord.ui.View):
    """Ticket management interface for individual tickets"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
        self.bot = ticket_system.bot
    
    @discord.ui.button(
        label="Close Ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="close_ticket_btn"
    )
    async def close_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close ticket button - staff only"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            embed = create_embed(
                "❌ Permission Denied",
                "Only staff members can close tickets.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show close confirmation modal
        await interaction.response.send_modal(CloseTicketModal(self.ticket_system, self.ticket_id))
    
    @discord.ui.button(
        label="Add Note",
        style=discord.ButtonStyle.secondary,
        emoji="📝",
        custom_id="add_note_btn"
    )
    async def add_note_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add staff note button"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            embed = create_embed(
                "❌ Permission Denied",
                "Only staff members can add notes.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.send_modal(AddNoteModal(self.ticket_system, self.ticket_id))
    
    @discord.ui.button(
        label="Assign to Me",
        style=discord.ButtonStyle.primary,
        emoji="👤",
        custom_id="assign_ticket_btn"
    )
    async def assign_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Assign ticket to staff member"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            embed = create_embed(
                "❌ Permission Denied",
                "Only staff members can assign tickets.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Assign ticket
        if self.ticket_id in self.ticket_system.active_tickets:
            ticket_data = self.ticket_system.active_tickets[self.ticket_id]
            ticket_data['assigned_staff'] = interaction.user.id
            
            embed = create_embed(
                "✅ Ticket Assigned",
                f"Ticket **#{self.ticket_id}** has been assigned to {interaction.user.mention}",
                discord.Color.green()
            )
            
            embed.add_field(
                name="📋 Ticket Details",
                value=f"**Category**: {ticket_data['category']}\n**Urgency**: {ticket_data['urgency']}\n**Created**: <t:{int(datetime.fromisoformat(ticket_data['created_at']).timestamp())}:R>",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
            # Log assignment
            await self.ticket_system.log_ticket_action(
                "ASSIGNED",
                ticket_data,
                interaction.user,
                f"Self-assigned ticket #{self.ticket_id}"
            )
    
    @discord.ui.button(
        label="Ticket Info",
        style=discord.ButtonStyle.secondary,
        emoji="ℹ️",
        custom_id="ticket_info_btn"
    )
    async def ticket_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed ticket information"""
        
        if self.ticket_id not in self.ticket_system.active_tickets:
            embed = create_embed(
                "❌ Ticket Not Found",
                "This ticket no longer exists in the system.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        ticket_data = self.ticket_system.active_tickets[self.ticket_id]
        
        # Calculate duration
        created = datetime.fromisoformat(ticket_data['created_at'])
        duration = datetime.utcnow() - created
        
        embed = create_embed(
            f"ℹ️ Ticket Information - #{self.ticket_id}",
            f"**Status**: {ticket_data['status'].title()}\n**Duration**: {format_duration(int(duration.total_seconds()))}",
            discord.Color.blue()
        )
        
        embed.add_field(
            name="👤 User Information",
            value=f"**User**: <@{ticket_data['user_id']}>\n**Display Name**: {ticket_data['display_name']}",
            inline=True
        )
        
        embed.add_field(
            name="🎫 Ticket Details",
            value=f"**Category**: {ticket_data['category']}\n**Urgency**: {ticket_data['urgency']}\n**Priority Score**: {ticket_data.get('priority', 'N/A')}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=f"**Created**: <t:{int(created.timestamp())}:F>\n**Messages**: {len(ticket_data.get('messages', []))}\n**Staff Involved**: {len(ticket_data.get('staff_involved', []))}",
            inline=False
        )
        
        if ticket_data.get('assigned_staff'):
            embed.add_field(
                name="👥 Assignment",
                value=f"**Assigned to**: <@{ticket_data['assigned_staff']}>",
                inline=True
            )
        
        embed.add_field(
            name="📝 Original Description",
            value=ticket_data['description'][:500] + ("..." if len(ticket_data['description']) > 500 else ""),
            inline=False
        )
        
        embed.set_footer(text=f"Ticket ID: {self.ticket_id}")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CloseTicketModal(discord.ui.Modal):
    """Modal for closing tickets with reason"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(title=f"🔒 Close Ticket #{ticket_id}")
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    close_reason = discord.ui.TextInput(
        label="Reason for Closing",
        placeholder="Issue resolved, duplicate ticket, user request, etc.",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True,
        default="Issue resolved"
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle ticket closure"""
        await interaction.response.defer()
        
        success = await self.ticket_system.close_ticket(
            self.ticket_id,
            interaction.user,
            self.close_reason.value
        )
        
        if success:
            embed = create_embed(
                "🔒 Ticket Closed Successfully",
                f"**Ticket**: #{self.ticket_id}\n**Reason**: {self.close_reason.value}\n**Closed by**: {interaction.user.mention}",
                discord.Color.red()
            )
            
            embed.add_field(
                name="📋 What Happens Next",
                value="• Transcript sent to user via DM\n• Transcript logged to ticket logs\n• Channel will be deleted in 30 seconds\n• Ticket marked as resolved",
                inline=False
            )
            
            embed.set_footer(text="Thank you for using Pakistan RP Support System")
            
            await interaction.followup.send(embed=embed)
            
            # Delete channel after delay
            await asyncio.sleep(30)
            try:
                await interaction.channel.delete(reason=f"Ticket {self.ticket_id} closed by {interaction.user}")
            except Exception as e:
                logging.error(f"Failed to delete ticket channel: {e}")
        else:
            embed = create_embed(
                "❌ Failed to Close Ticket",
                "An error occurred while closing the ticket. Please try again.",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class AddNoteModal(discord.ui.Modal):
    """Modal for adding staff notes to tickets"""
    
    def __init__(self, ticket_system, ticket_id: str):
        super().__init__(title=f"📝 Add Note to #{ticket_id}")
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
    
    note_content = discord.ui.TextInput(
        label="Staff Note",
        placeholder="Add internal notes for other staff members...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle note addition"""
        
        embed = create_embed(
            "📝 Staff Note Added",
            self.note_content.value,
            discord.Color.orange()
        )
        
        embed.set_author(
            name=f"Staff Note by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url
        )
        
        embed.set_footer(text=f"Internal Note • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
        
        await interaction.response.send_message(embed=embed)
        
        # Log note addition
        if self.ticket_id in self.ticket_system.active_tickets:
            await self.ticket_system.log_ticket_action(
                "UPDATED",
                self.ticket_system.active_tickets[self.ticket_id],
                interaction.user,
                f"Added staff note: {self.note_content.value[:100]}{'...' if len(self.note_content.value) > 100 else ''}"
            )

class StaffTicketOverview(discord.ui.View):
    """Staff overview of all tickets"""
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="🔍 Filter tickets by category...",
        options=[
            discord.SelectOption(label="All Tickets", value="all", emoji="📋"),
            discord.SelectOption(label="Support", value="Support", emoji="🔧"),
            discord.SelectOption(label="Player Report", value="Player Report", emoji="👤"),
            discord.SelectOption(label="Bug Report", value="Bug Report", emoji="🐛"),
            discord.SelectOption(label="Gang Registration", value="Gang Registration", emoji="🏢"),
            discord.SelectOption(label="Shop", value="Shop", emoji="🛍️"),
            discord.SelectOption(label="Other", value="Other", emoji="❓")
        ]
    )
    async def filter_tickets(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Filter tickets by category"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            await interaction.response.send_message("❌ Staff only feature.", ephemeral=True)
            return
        
        category = select.values[0]
        
        if hasattr(self.bot, 'tickets') and self.bot.tickets:
            all_tickets = await self.bot.tickets.get_active_tickets()
            
            if category == "all":
                filtered_tickets = all_tickets
            else:
                filtered_tickets = [t for t in all_tickets if t['category'] == category]
            
            embed = create_embed(
                f"🎫 Tickets Overview - {category}",
                f"Found **{len(filtered_tickets)}** tickets matching your filter",
                discord.Color.blue()
            )
            
            if filtered_tickets:
                ticket_list = []
                for ticket in filtered_tickets[:10]:  # Show max 10
                    urgency_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🟠", "Critical": "🔴"}
                    emoji = urgency_emoji.get(ticket['urgency'], '🟡')
                    
                    created = datetime.fromisoformat(ticket['created_at'])
                    duration = datetime.utcnow() - created
                    
                    ticket_list.append(
                        f"{emoji} **#{ticket['ticket_id']}** | {ticket['category']} | <@{ticket['user_id']}> | {format_duration(int(duration.total_seconds()))}"
                    )
                
                embed.add_field(
                    name="📋 Active Tickets",
                    value="\n".join(ticket_list),
                    inline=False
                )
                
                if len(filtered_tickets) > 10:
                    embed.add_field(
                        name="📊 Note",
                        value=f"Showing 10 of {len(filtered_tickets)} tickets. Use ticket management tools for full list.",
                        inline=False
                    )
            else:
                embed.add_field(
                    name="✅ No Tickets Found",
                    value="No active tickets match your filter criteria.",
                    inline=False
                )
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "Ticket system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="📊 Ticket Statistics", style=discord.ButtonStyle.secondary)
    async def ticket_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show ticket statistics"""
        
        if not self.bot.permissions.is_staff(interaction.user):
            await interaction.response.send_message("❌ Staff only feature.", ephemeral=True)
            return
        
        if hasattr(self.bot, 'tickets') and self.bot.tickets:
            active_tickets = await self.bot.tickets.get_active_tickets()
            
            # Calculate statistics
            total_active = len(active_tickets)
            categories = {}
            urgency_counts = {}
            avg_duration = 0
            
            for ticket in active_tickets:
                # Count categories
                cat = ticket['category']
                categories[cat] = categories.get(cat, 0) + 1
                
                # Count urgency levels
                urg = ticket['urgency']
                urgency_counts[urg] = urgency_counts.get(urg, 0) + 1
                
                # Calculate average duration
                created = datetime.fromisoformat(ticket['created_at'])
                duration = (datetime.utcnow() - created).total_seconds()
                avg_duration += duration
            
            if total_active > 0:
                avg_duration = avg_duration / total_active
            
            embed = create_embed(
                "📊 Ticket System Statistics",
                f"**Total Active Tickets**: {total_active}",
                discord.Color.blue()
            )
            
            if categories:
                cat_text = "\n".join([f"**{cat}**: {count}" for cat, count in categories.items()])
                embed.add_field(name="📋 By Category", value=cat_text, inline=True)
            
            if urgency_counts:
                urg_text = "\n".join([f"**{urg}**: {count}" for urg, count in urgency_counts.items()])
                embed.add_field(name="🚨 By Urgency", value=urg_text, inline=True)
            
            embed.add_field(
                name="⏱️ Performance",
                value=f"**Avg Duration**: {format_duration(int(avg_duration))}\n**Created Today**: {self.bot.stats['tickets_created']}\n**Resolved Today**: {self.bot.stats['tickets_resolved']}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = create_embed(
                "❌ System Unavailable",
                "Ticket system is currently unavailable.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)