import discord
from typing import Union, List, Optional
import logging

from config.settings import Config

class AdvancedPermissions:
    """Advanced permission system for Pakistan RP Community Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        
        # Permission hierarchy (higher number = higher permissions)
        self.permission_hierarchy = {
            'member': 0,
            'helper': 1,
            'moderator': 2,
            'staff': 3,
            'senior_staff': 4,
            'admin': 5
        }
    
    def get_user_role_level(self, user: Union[discord.Member, discord.User]) -> int:
        """Get the permission level of a user based on their roles"""
        if not isinstance(user, discord.Member):
            return 0  # Non-members have no permissions
        
        max_level = 0
        
        # Check each role for the highest permission level
        for role in user.roles:
            if role.id == Config.ADMIN_ROLE_ID:
                max_level = max(max_level, self.permission_hierarchy['admin'])
            elif role.id == Config.SENIOR_STAFF_ROLE_ID:
                max_level = max(max_level, self.permission_hierarchy['senior_staff'])
            elif role.id == Config.STAFF_ROLE_ID:
                max_level = max(max_level, self.permission_hierarchy['staff'])
            elif role.id == Config.MODERATOR_ROLE_ID:
                max_level = max(max_level, self.permission_hierarchy['moderator'])
            elif role.id == Config.HELPER_ROLE_ID:
                max_level = max(max_level, self.permission_hierarchy['helper'])
        
        return max_level
    
    def get_user_role_name(self, user: Union[discord.Member, discord.User]) -> str:
        """Get the role name of a user"""
        level = self.get_user_role_level(user)
        
        for role_name, role_level in self.permission_hierarchy.items():
            if role_level == level:
                return role_name
        
        return 'member'
    
    def is_admin(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is an admin"""
        return self.get_user_role_level(user) >= self.permission_hierarchy['admin']
    
    def is_senior_staff(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is senior staff or higher"""
        return self.get_user_role_level(user) >= self.permission_hierarchy['senior_staff']
    
    def is_staff(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is staff or higher"""
        return self.get_user_role_level(user) >= self.permission_hierarchy['staff']
    
    def is_moderator(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is moderator or higher"""
        return self.get_user_role_level(user) >= self.permission_hierarchy['moderator']
    
    def is_helper(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user is helper or higher"""
        return self.get_user_role_level(user) >= self.permission_hierarchy['helper']
    
    def can_manage_tickets(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can manage tickets"""
        return self.is_helper(user)
    
    def can_close_tickets(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can close tickets"""
        return self.is_staff(user)
    
    def can_add_rules(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can add rules to database"""
        return self.is_admin(user)
    
    def can_edit_rules(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can edit rules"""
        return self.is_admin(user)
    
    def can_delete_rules(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can delete rules"""
        return self.is_admin(user)
    
    def can_make_announcements(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can make announcements"""
        return self.is_admin(user)
    
    def can_ping_everyone(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can ping everyone in announcements"""
        return self.is_admin(user)
    
    def can_issue_punishment(self, user: Union[discord.Member, discord.User], punishment_type: str) -> bool:
        """Check if user can issue specific types of punishment"""
        user_level = self.get_user_role_level(user)
        
        # Define minimum levels for different punishments
        punishment_requirements = {
            'warning': self.permission_hierarchy['helper'],
            'mute': self.permission_hierarchy['moderator'],
            'kick': self.permission_hierarchy['moderator'],
            'temp_ban': self.permission_hierarchy['staff'],
            'perm_ban': self.permission_hierarchy['senior_staff'],
            'fine': self.permission_hierarchy['moderator'],
            'vehicle_impound': self.permission_hierarchy['moderator'],
            'gang_warning': self.permission_hierarchy['staff'],
            'gang_suspension': self.permission_hierarchy['senior_staff'],
            'gang_dissolution': self.permission_hierarchy['admin'],
            'mass_ban': self.permission_hierarchy['admin']
        }
        
        required_level = punishment_requirements.get(punishment_type, self.permission_hierarchy['admin'])
        return user_level >= required_level
    
    def can_appeal_punishment(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can review punishment appeals"""
        return self.is_senior_staff(user)
    
    def can_access_staff_tools(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can access staff tools"""
        return self.is_helper(user)
    
    def can_view_member_data(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can view member data"""
        return self.is_moderator(user)
    
    def can_manage_member_data(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can manage member data"""
        return self.is_staff(user)
    
    def can_access_analytics(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can access server analytics"""
        return self.is_staff(user)
    
    def can_deploy_dashboards(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can deploy dashboards"""
        return self.is_admin(user)
    
    def can_backup_database(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can create database backups"""
        return self.is_senior_staff(user)
    
    def can_manage_automation(self, user: Union[discord.Member, discord.User]) -> bool:
        """Check if user can manage automation settings"""
        return self.is_admin(user)
    
    def has_higher_role(self, user1: Union[discord.Member, discord.User], 
                       user2: Union[discord.Member, discord.User]) -> bool:
        """Check if user1 has higher role than user2"""
        return self.get_user_role_level(user1) > self.get_user_role_level(user2)
    
    def can_punish_user(self, staff: Union[discord.Member, discord.User], 
                       target: Union[discord.Member, discord.User], 
                       punishment_type: str) -> tuple[bool, str]:
        """
        Check if staff can punish target user
        Returns (can_punish: bool, reason: str)
        """
        
        # Check if staff can issue this type of punishment
        if not self.can_issue_punishment(staff, punishment_type):
            return False, f"You don't have permission to issue {punishment_type} punishments"
        
        # Check if target is a staff member
        if self.is_staff(target):
            # Staff can't punish other staff of equal or higher rank
            if not self.has_higher_role(staff, target):
                return False, "You cannot punish staff members of equal or higher rank"
        
        # Special protection for admins
        if self.is_admin(target) and not self.is_admin(staff):
            return False, "Only admins can punish other admins"
        
        return True, "Permission granted"
    
    def get_permission_display(self, user: Union[discord.Member, discord.User]) -> dict:
        """Get formatted permission information for display"""
        role_name = self.get_user_role_name(user)
        role_level = self.get_user_role_level(user)
        
        # Role colors and emojis
        role_info = {
            'member': {'emoji': '👤', 'color': 0x95A5A6, 'display': 'Member'},
            'helper': {'emoji': '🆘', 'color': 0x3498DB, 'display': 'Helper'},
            'moderator': {'emoji': '🛡️', 'color': 0xE67E22, 'display': 'Moderator'},
            'staff': {'emoji': '👮', 'color': 0xE74C3C, 'display': 'Staff'},
            'senior_staff': {'emoji': '🎖️', 'color': 0x9B59B6, 'display': 'Senior Staff'},
            'admin': {'emoji': '👑', 'color': 0xF1C40F, 'display': 'Administrator'}
        }
        
        info = role_info.get(role_name, role_info['member'])
        info['level'] = role_level
        info['role_name'] = role_name
        
        return info
    
    def get_staff_permissions(self, user: Union[discord.Member, discord.User]) -> List[str]:
        """Get list of permissions for a staff member"""
        permissions = []
        
        if self.is_helper(user):
            permissions.extend([
                "View tickets", "Manage tickets", "Add ticket notes",
                "Access basic staff tools", "View rule database"
            ])
        
        if self.is_moderator(user):
            permissions.extend([
                "Close tickets", "Issue warnings", "Issue fines",
                "Mute users", "Kick users", "Impound vehicles",
                "View member data", "Access moderation tools"
            ])
        
        if self.is_staff(user):
            permissions.extend([
                "Issue temporary bans", "Manage member data",
                "Gang warnings", "Access analytics",
                "Advanced ticket management"
            ])
        
        if self.is_senior_staff(user):
            permissions.extend([
                "Issue permanent bans", "Gang suspension",
                "Review appeals", "Database backups",
                "Advanced member management"
            ])
        
        if self.is_admin(user):
            permissions.extend([
                "Add/Edit/Delete rules", "Make announcements",
                "Ping everyone", "Gang dissolution", "Mass bans",
                "Deploy dashboards", "Manage automation",
                "Full system access"
            ])
        
        return list(set(permissions))  # Remove duplicates
    
    async def log_permission_check(self, user: Union[discord.Member, discord.User], 
                                 action: str, granted: bool, reason: str = ""):
        """Log permission checks for audit purposes"""
        try:
            if self.bot.db:
                await self.bot.db.log_action(
                    action_type="PERMISSION_CHECK",
                    staff_id=user.id,
                    details=f"Action: {action}, Granted: {granted}, Reason: {reason}",
                    user_id=user.id
                )
        except Exception as e:
            logging.error(f"Failed to log permission check: {e}")
    
    def require_permission(self, permission_check_func):
        """Decorator for requiring specific permissions"""
        def decorator(func):
            async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
                if not permission_check_func(interaction.user):
                    role_info = self.get_permission_display(interaction.user)
                    required_role = permission_check_func.__name__.replace('is_', '').replace('can_', '')
                    
                    embed = discord.Embed(
                        title="❌ Insufficient Permissions",
                        description=f"This action requires **{required_role.replace('_', ' ').title()}** permissions or higher.",
                        color=0xE74C3C
                    )
                    
                    embed.add_field(
                        name="Your Current Role",
                        value=f"{role_info['emoji']} {role_info['display']}",
                        inline=True
                    )
                    
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                
                return await func(self, interaction, *args, **kwargs)
            return wrapper
        return decorator