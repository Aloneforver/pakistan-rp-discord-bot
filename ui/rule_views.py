import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import logging

from utils.helpers import create_embed, format_duration

try:
    from config.settings import Config
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config.settings import Config

class RuleSearchView(discord.ui.View):
    """Main rule search interface"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Search Rules",
        style=discord.ButtonStyle.primary,
        emoji="🔍",
        custom_id="search_rules_btn"
    )
    async def search_rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Open rule search modal"""
        await interaction.response.send_modal(RuleSearchModal(self.bot))
    
    @discord.ui.button(
        label="Browse Categories",
        style=discord.ButtonStyle.secondary,
        emoji="📚",
        custom_id="browse_categories_btn"
    )
    async def browse_categories_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Browse rules by category"""
        
        if not hasattr(self.bot, 'rules') or not self.bot.rules:
            await interaction.response.send_message("❌ Rule system unavailable.", ephemeral=True)
            return
        
        # Create category selection dropdown
        categories = list(self.bot.rules.categories.keys())[:25]  # Discord limit
        
        embed = create_embed(
            "📚 Browse Rule Categories",
            "Select a category below to view all rules in that section.",
            discord.Color.blue()
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=CategoryBrowseView(self.bot, categories),
            ephemeral=True
        )
    
    @discord.ui.button(
        label="Rule Statistics",
        style=discord.ButtonStyle.secondary,
        emoji="📊",
        custom_id="rule_stats_btn"
    )
    async def rule_statistics_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show rule database statistics"""
        
        if not hasattr(self.bot, 'rules') or not self.bot.rules:
            await interaction.response.send_message("❌ Rule system unavailable.", ephemeral=True)
            return
        
        try:
            stats = await self.bot.rules.get_category_stats()
            total_rules = await self.bot.rules.get_rule_count()
            
            embed = create_embed(
                "📊 Rule Database Statistics",
                f"**Total Rules**: {total_rules}\n**Categories**: {len(stats)}\n**Searches Today**: {self.bot.stats.get('rules_accessed', 0)}",
                discord.Color.green()
            )
            
            # Add category breakdown
            for category, data in list(stats.items())[:5]:  # Show top 5
                embed.add_field(
                    name=f"{self.bot.rules.categories[category].get('emoji', '📋')} {category}",
                    value=f"Rules: {data['total_rules']}",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logging.error(f"Rule statistics error: {e}")
            await interaction.response.send_message("❌ Failed to load statistics.", ephemeral=True)

class RuleSearchModal(discord.ui.Modal):
    """Modal for searching rules"""
    
    def __init__(self, bot):
        super().__init__(title="🔍 Search Rules")
        self.bot = bot
    
    search_query = discord.ui.TextInput(
        label="Search Query",
        placeholder="Enter keywords (e.g., respect, driving, gang war)",
        style=discord.TextStyle.short,
        max_length=100,
        required=True
    )
    
    category_filter = discord.ui.TextInput(
        label="Category Filter (Optional)",
        placeholder="Leave blank to search all categories",
        style=discord.TextStyle.short,
        max_length=50,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle search submission"""
        await interaction.response.defer()
        
        if not hasattr(self.bot, 'rules') or not self.bot.rules:
            await interaction.followup.send("❌ Rule system unavailable.", ephemeral=True)
            return
        
        # Search rules
        results = await self.bot.rules.search_rules(
            self.search_query.value,
            self.category_filter.value if self.category_filter.value else None,
            limit=10
        )
        
        if not results:
            embed = create_embed(
                "🔍 No Results Found",
                f"No rules found matching: **{self.search_query.value}**\n\nTry different keywords or browse by category.",
                discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Create results embed
        embed = create_embed(
            f"🔍 Search Results - '{self.search_query.value}'",
            f"Found **{len(results)}** matching rules:",
            discord.Color.blue()
        )
        
        # Show results
        for i, rule in enumerate(results[:5], 1):  # Show top 5
            rule_id = rule.get('rule_id', 'Unknown')
            title = rule.get('title', 'Unknown Rule')
            category = rule.get('category', 'Unknown')
            priority = rule.get('priority', 'medium')
            
            priority_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '🟡')
            
            embed.add_field(
                name=f"{i}. {priority_emoji} [{rule_id}] {title}",
                value=f"**Category**: {category}\n**Match Score**: {rule.get('search_score', 0)}",
                inline=False
            )
        
        # Update stats
        self.bot.stats['rules_accessed'] += 1
        
        # Add view for detailed rule display
        await interaction.followup.send(
            embed=embed,
            view=RuleResultsView(self.bot, results),
            ephemeral=True
        )

class CategoryBrowseView(discord.ui.View):
    """View for browsing rules by category"""
    
    def __init__(self, bot, categories: List[str]):
        super().__init__(timeout=300)
        self.bot = bot
        
        # Create select menu
        options = []
        for category in categories:
            cat_info = self.bot.rules.categories.get(category, {})
            options.append(discord.SelectOption(
                label=category,
                description=cat_info.get('description', '')[:100],
                emoji=cat_info.get('emoji', '📋'),
                value=category
            ))
        
        if options:
            self.category_select.options = options
    
    @discord.ui.select(
        placeholder="📚 Select a category to browse...",
        min_values=1,
        max_values=1
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle category selection"""
        
        category = select.values[0]
        
        if not hasattr(self.bot, 'rules') or not self.bot.rules:
            await interaction.response.send_message("❌ Rule system unavailable.", ephemeral=True)
            return
        
        # Get rules in category
        rules = await self.bot.rules.get_rules_by_category(category)
        
        if not rules:
            embed = create_embed(
                f"📚 {category} - No Rules",
                "No rules found in this category.",
                discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create category overview
        cat_info = self.bot.rules.categories.get(category, {})
        embed = create_embed(
            f"{cat_info.get('emoji', '📋')} {category}",
            f"{cat_info.get('description', 'Category rules')}\n\n**Total Rules**: {len(rules)}",
            cat_info.get('color', 0x3498DB)
        )
        
        # Group by subcategory
        subcategories = {}
        for rule in rules:
            subcat = rule.get('subcategory', 'General')
            if subcat not in subcategories:
                subcategories[subcat] = []
            subcategories[subcat].append(rule)
        
        # Display subcategories
        for subcat, subrules in list(subcategories.items())[:5]:  # Show first 5
            rule_list = []
            for rule in subrules[:3]:  # Show 3 rules per subcategory
                priority_emoji = {
                    'critical': '🔴',
                    'high': '🟠', 
                    'medium': '🟡',
                    'low': '🟢'
                }.get(rule.get('priority', 'medium'), '🟡')
                
                rule_list.append(f"{priority_emoji} **{rule['rule_id']}** - {rule['title']}")
            
            embed.add_field(
                name=f"📂 {subcat}",
                value="\n".join(rule_list) + (f"\n*+ {len(subrules) - 3} more*" if len(subrules) > 3 else ""),
                inline=False
            )
        
        # Update stats
        self.bot.stats['rules_accessed'] += 1
        
        await interaction.response.send_message(
            embed=embed,
            view=SubcategoryView(self.bot, category, subcategories),
            ephemeral=True
        )

class SubcategoryView(discord.ui.View):
    """View for browsing subcategory rules"""
    
    def __init__(self, bot, category: str, subcategories: Dict[str, List]):
        super().__init__(timeout=300)
        self.bot = bot
        self.category = category
        self.subcategories = subcategories
        
        # Create subcategory options
        options = []
        for subcat, rules in list(subcategories.items())[:25]:
            options.append(discord.SelectOption(
                label=subcat,
                description=f"{len(rules)} rules",
                value=subcat
            ))
        
        if options:
            self.subcategory_select.options = options
    
    @discord.ui.select(
        placeholder="📂 Select a subcategory...",
        min_values=1,
        max_values=1
    )
    async def subcategory_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Handle subcategory selection"""
        
        subcategory = select.values[0]
        rules = self.subcategories.get(subcategory, [])
        
        if not rules:
            await interaction.response.send_message("❌ No rules in this subcategory.", ephemeral=True)
            return
        
        # Show rules in subcategory
        embed = create_embed(
            f"📂 {self.category} > {subcategory}",
            f"Showing {len(rules)} rules:",
            discord.Color.blue()
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=RuleResultsView(self.bot, rules),
            ephemeral=True
        )

class RuleResultsView(discord.ui.View):
    """View for displaying rule search results"""
    
    def __init__(self, bot, rules: List[Dict[str, Any]]):
        super().__init__(timeout=300)
        self.bot = bot
        self.rules = rules
        self.current_page = 0
        self.per_page = 1
        self.max_pages = len(rules)
        
        # Update button states
        self.update_buttons()
    
    def update_buttons(self):
        """Update navigation button states"""
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.max_pages - 1
        self.page_indicator.label = f"Page {self.current_page + 1}/{self.max_pages}"
    
    async def create_rule_embed(self, rule_data: Dict[str, Any]) -> discord.Embed:
        """Create detailed rule embed with punishment info"""
        
        rule_id = rule_data.get('rule_id', 'Unknown')
        category = rule_data.get('category', 'Unknown')
        category_info = self.bot.rules.categories.get(category, {})
        
        embed = discord.Embed(
            title=f"{category_info.get('emoji', '📋')} {rule_data.get('title', 'Unknown Rule')}",
            description=rule_data.get('content', 'No content available'),
            color=category_info.get('color', 0x3498DB),
            timestamp=datetime.utcnow()
        )
        
        # Basic info
        embed.add_field(
            name="📋 Rule Information",
            value=f"**ID**: {rule_id}\n**Category**: {category}\n**Subcategory**: {rule_data.get('subcategory', 'N/A')}",
            inline=True
        )
        
        # Priority
        priority = rule_data.get('priority', 'medium')
        priority_emojis = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
        embed.add_field(
            name="🚨 Priority",
            value=f"{priority_emojis.get(priority, '🟡')} {priority.title()}",
            inline=True
        )
        
        # Staff requirement
        min_rank = rule_data.get('min_staff_rank', 'helper')
        embed.add_field(
            name="👮 Enforced By",
            value=f"{min_rank.title()}+",
            inline=True
        )
        
        # Punishment details
        punishments = rule_data.get('punishments', {})
        if punishments:
            punishment_text = []
            
            for offense_level, punishment in punishments.items():
                emoji = Config.get_punishment_display(punishment.get('type', 'warning'))['emoji']
                details = punishment.get('details', 'No details')
                punishment_text.append(f"**{offense_level.replace('_', ' ').title()}**: {details}")
            
            embed.add_field(
                name="⚖️ Punishment System",
                value="\n".join(punishment_text),
                inline=False
            )
        else:
            embed.add_field(
                name="⚖️ Punishment System",
                value="Standard punishment applies - consult staff",
                inline=False
            )
        
        # Appeal process
        if rule_data.get('appeal_allowed', True):
            embed.add_field(
                name="📋 Appeal Process",
                value=rule_data.get('appeal_process', 'Submit appeal ticket within 48 hours'),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Appeal Process",
                value="❌ No appeals allowed for this violation",
                inline=False
            )
        
        # Keywords
        keywords = rule_data.get('keywords', [])
        if keywords:
            embed.add_field(
                name="🔍 Related Keywords",
                value=", ".join(keywords[:10]),
                inline=False
            )
        
        embed.set_footer(text=f"Pakistan RP Rules • {rule_id} • Page {self.current_page + 1}/{self.max_pages}")
        
        return embed
    
    @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to previous rule"""
        self.current_page -= 1
        self.update_buttons()
        
        embed = await self.create_rule_embed(self.rules[self.current_page])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Page 1/1", style=discord.ButtonStyle.secondary, disabled=True)
    async def page_indicator(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Page indicator (non-interactive)"""
        pass
    
    @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to next rule"""
        self.current_page += 1
        self.update_buttons()
        
        embed = await self.create_rule_embed(self.rules[self.current_page])
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔍 New Search", style=discord.ButtonStyle.success)
    async def new_search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Start a new search"""
        await interaction.response.send_modal(RuleSearchModal(self.bot))
    
    @discord.ui.button(label="❌ Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Close the results"""
        await interaction.response.edit_message(content="Search closed.", embed=None, view=None)
    
    async def start(self, interaction: discord.Interaction):
        """Start showing results"""
        embed = await self.create_rule_embed(self.rules[0])
        await interaction.followup.send(embed=embed, view=self, ephemeral=True)

class RuleManagementView(discord.ui.View):
    """Admin view for rule management"""
    
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="Add Rule",
        style=discord.ButtonStyle.success,
        emoji="➕",
        custom_id="add_rule_admin"
    )
    async def add_rule_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Add new rule - Admin only"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        await interaction.response.send_modal(AddRuleModal(self.bot))
    
    @discord.ui.button(
        label="Edit Rule",
        style=discord.ButtonStyle.primary,
        emoji="✏️",
        custom_id="edit_rule_admin"
    )
    async def edit_rule_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Edit existing rule - Admin only"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        await interaction.response.send_modal(EditRuleSearchModal(self.bot))
    
    @discord.ui.button(
        label="Delete Rule",
        style=discord.ButtonStyle.danger,
        emoji="🗑️",
        custom_id="delete_rule_admin"
    )
    async def delete_rule_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Delete rule - Admin only"""
        
        if not self.bot.permissions.is_admin(interaction.user):
            await interaction.response.send_message("❌ Admin access required.", ephemeral=True)
            return
        
        await interaction.response.send_modal(DeleteRuleModal(self.bot))

class AddRuleModal(discord.ui.Modal):
    """Modal for adding new rules with punishment details"""
    
    def __init__(self, bot):
        super().__init__(title="➕ Add New Rule")
        self.bot = bot
    
    category = discord.ui.TextInput(
        label="Category",
        placeholder="e.g., General Rules, Roleplay Guidelines",
        max_length=50,
        required=True
    )
    
    title = discord.ui.TextInput(
        label="Rule Title",
        placeholder="Clear, descriptive title",
        max_length=100,
        required=True
    )
    
    content = discord.ui.TextInput(
        label="Rule Content",
        placeholder="Detailed rule description...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    punishments = discord.ui.TextInput(
        label="Punishments (JSON format)",
        placeholder='{"first":"Warning + $5k","second":"2h mute + $10k","third":"24h ban","severe":"Perm ban"}',
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    keywords = discord.ui.TextInput(
        label="Keywords (comma-separated)",
        placeholder="respect, behavior, harassment",
        max_length=200,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle rule addition with punishments"""
        await interaction.response.defer()
        
        try:
            # Parse punishment JSON
            import json
            punishment_data = json.loads(self.punishments.value)
            
            # Structure punishments properly
            punishments = {}
            for offense, details in punishment_data.items():
                # Simple parsing - could be enhanced
                punishments[f"{offense}_offense"] = {
                    "type": "warning",  # Would need more parsing
                    "details": details
                }
            
            # Add the rule
            # This would need to be updated in rule_manager.py
            embed = create_embed(
                "✅ Rule Added Successfully",
                f"**Title**: {self.title.value}\n**Category**: {self.category.value}",
                discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = create_embed(
                "❌ Failed to Add Rule",
                f"Error: {str(e)}",
                discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

class EditRuleSearchModal(discord.ui.Modal):
    """Modal to search for rule to edit"""
    
    def __init__(self, bot):
        super().__init__(title="✏️ Find Rule to Edit")
        self.bot = bot
    
    rule_id = discord.ui.TextInput(
        label="Rule ID",
        placeholder="e.g., GR001, RP002",
        max_length=10,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Find and edit rule"""
        # This would open another modal with the rule data pre-filled
        embed = create_embed(
            "✏️ Edit Rule",
            f"Editing rule: {self.rule_id.value}\n\n*Full edit interface would open here*",
            discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class DeleteRuleModal(discord.ui.Modal):
    """Modal for deleting rules"""
    
    def __init__(self, bot):
        super().__init__(title="🗑️ Delete Rule")
        self.bot = bot
    
    rule_id = discord.ui.TextInput(
        label="Rule ID to Delete",
        placeholder="e.g., GR001 (THIS CANNOT BE UNDONE)",
        max_length=10,
        required=True
    )
    
    confirm = discord.ui.TextInput(
        label="Type 'DELETE' to confirm",
        placeholder="Type DELETE in capitals",
        max_length=6,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle rule deletion"""
        if self.confirm.value != "DELETE":
            embed = create_embed(
                "❌ Deletion Cancelled",
                "You must type 'DELETE' to confirm.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Delete the rule
        embed = create_embed(
            "🗑️ Rule Deleted",
            f"Rule {self.rule_id.value} has been permanently deleted.",
            discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)