import discord
from datetime import datetime, timedelta
import re
from typing import Union, Optional, List, Dict, Any
import asyncio
import logging

def create_embed(title: str, description: str, color: Union[discord.Color, int] = None) -> discord.Embed:
    """Create a standardized embed with Pakistan RP styling"""
    
    if color is None:
        color = 0x2ECC71  # Default green color
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    
    return embed

def create_success_embed(title: str, description: str) -> discord.Embed:
    """Create a success embed with green color"""
    return create_embed(title, description, discord.Color.green())

def create_error_embed(title: str, description: str) -> discord.Embed:
    """Create an error embed with red color"""
    return create_embed(title, description, discord.Color.red())

def create_warning_embed(title: str, description: str) -> discord.Embed:
    """Create a warning embed with orange color"""
    return create_embed(title, description, discord.Color.orange())

def create_info_embed(title: str, description: str) -> discord.Embed:
    """Create an info embed with blue color"""
    return create_embed(title, description, discord.Color.blue())

def get_timestamp(dt: datetime = None) -> str:
    """Get a formatted timestamp string"""
    if dt is None:
        dt = datetime.utcnow()
    
    return f"<t:{int(dt.timestamp())}:F>"

def get_relative_timestamp(dt: datetime) -> str:
    """Get a relative timestamp string (e.g., '2 hours ago')"""
    return f"<t:{int(dt.timestamp())}:R>"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable format"""
    if seconds <= 0:
        return "0 seconds"
    
    # Convert to timedelta for easier calculation
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds and not days and not hours:  # Only show seconds if less than an hour
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    
    if not parts:
        return "0 seconds"
    
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def sanitize_text(text: str, max_length: int = None) -> str:
    """Sanitize text for display, removing potentially harmful content"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove potential markdown abuse
    text = text.replace('`', '\'').replace('*', '').replace('_', '')
    
    # Truncate if too long
    if max_length and len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text

def extract_user_id(text: str) -> Optional[int]:
    """Extract user ID from mention or text"""
    
    # Match Discord user mention
    mention_match = re.match(r'<@!?(\d+)>', text.strip())
    if mention_match:
        return int(mention_match.group(1))
    
    # Try to parse as direct ID
    if text.strip().isdigit():
        return int(text.strip())
    
    return None

def extract_channel_id(text: str) -> Optional[int]:
    """Extract channel ID from mention or text"""
    
    # Match Discord channel mention
    mention_match = re.match(r'<#(\d+)>', text.strip())
    if mention_match:
        return int(mention_match.group(1))
    
    # Try to parse as direct ID
    if text.strip().isdigit():
        return int(text.strip())
    
    return None

def extract_role_id(text: str) -> Optional[int]:
    """Extract role ID from mention or text"""
    
    # Match Discord role mention
    mention_match = re.match(r'<@&(\d+)>', text.strip())
    if mention_match:
        return int(mention_match.group(1))
    
    # Try to parse as direct ID
    if text.strip().isdigit():
        return int(text.strip())
    
    return None

def parse_time_duration(duration_str: str) -> Optional[int]:
    """Parse duration string to minutes (e.g., '1h30m', '2d', '45m')"""
    
    if not duration_str:
        return None
    
    duration_str = duration_str.lower().strip()
    
    # Regular expression to match time components
    time_regex = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(time_regex, duration_str)
    
    if not match:
        # Try to parse as just minutes
        if duration_str.isdigit():
            return int(duration_str)
        return None
    
    days, hours, minutes, seconds = match.groups()
    
    total_minutes = 0
    if days:
        total_minutes += int(days) * 1440  # 24 * 60
    if hours:
        total_minutes += int(hours) * 60
    if minutes:
        total_minutes += int(minutes)
    if seconds:
        total_minutes += int(seconds) // 60  # Convert seconds to minutes
    
    return total_minutes if total_minutes > 0 else None

def create_progress_bar(current: int, maximum: int, length: int = 20, 
                       filled_char: str = "█", empty_char: str = "░") -> str:
    """Create a visual progress bar"""
    
    if maximum <= 0:
        return empty_char * length
    
    progress = min(current / maximum, 1.0)  # Ensure it doesn't exceed 100%
    filled_length = int(length * progress)
    
    bar = filled_char * filled_length + empty_char * (length - filled_length)
    percentage = int(progress * 100)
    
    return f"{bar} {percentage}%"

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length with suffix"""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_filename(filename: str) -> str:
    """Clean filename for safe file operations"""
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove excessive dots and spaces
    filename = re.sub(r'\.+', '.', filename)
    filename = re.sub(r' +', ' ', filename).strip()
    
    # Ensure it's not empty and not too long
    if not filename:
        filename = "unnamed"
    
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        max_name_length = 95 - len(ext)
        filename = name[:max_name_length] + ('.' + ext if ext else '')
    
    return filename

def validate_discord_invite(invite_url: str) -> bool:
    """Validate if string is a Discord invite URL"""
    
    discord_invite_regex = r'(https?://)?(www\.)?(discord\.(gg|io|me|li)|discordapp\.com/invite)/[A-Za-z0-9-]+'
    return bool(re.match(discord_invite_regex, invite_url))

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text"""
    
    url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_regex, text)

def is_image_url(url: str) -> bool:
    """Check if URL points to an image"""
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

def format_list(items: List[str], conjunction: str = "and") -> str:
    """Format a list into a natural language string"""
    
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return f"{', '.join(items[:-1])}, {conjunction} {items[-1]}"

def create_table(headers: List[str], rows: List[List[str]], 
                max_width: int = 50) -> str:
    """Create a simple text table"""
    
    if not headers or not rows:
        return ""
    
    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Limit column widths
    col_widths = [min(width, max_width) for width in col_widths]
    
    # Create header row
    header_row = "| " + " | ".join(header.ljust(col_widths[i]) for i, header in enumerate(headers)) + " |"
    separator = "|" + "|".join("-" * (width + 2) for width in col_widths) + "|"
    
    # Create data rows
    data_rows = []
    for row in rows:
        formatted_row = "| " + " | ".join(
            truncate_text(str(cell), col_widths[i]).ljust(col_widths[i]) 
            for i, cell in enumerate(row)
        ) + " |"
        data_rows.append(formatted_row)
    
    return "\n".join([header_row, separator] + data_rows)

async def confirm_action(interaction: discord.Interaction, title: str, 
                        description: str, timeout: int = 60) -> bool:
    """Show a confirmation dialog and return user's choice"""
    
    embed = create_embed(title, description, discord.Color.orange())
    
    class ConfirmView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=timeout)
            self.result = None
        
        @discord.ui.button(label="✅ Confirm", style=discord.ButtonStyle.success)
        async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.result = True
            self.stop()
            await interaction.response.edit_message(content="✅ Confirmed!", embed=None, view=None)
        
        @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.danger)
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.result = False
            self.stop()
            await interaction.response.edit_message(content="❌ Cancelled!", embed=None, view=None)
    
    view = ConfirmView()
    
    if interaction.response.is_done():
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    else:
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    await view.wait()
    return view.result

def get_member_display_name(member: Union[discord.Member, discord.User]) -> str:
    """Get the best display name for a member"""
    
    if isinstance(member, discord.Member) and member.display_name != member.name:
        return f"{member.display_name} ({member.name})"
    return member.name

def format_permissions(permissions: discord.Permissions) -> List[str]:
    """Format permissions into readable list"""
    
    perm_names = {
        'administrator': 'Administrator',
        'manage_guild': 'Manage Server',
        'manage_roles': 'Manage Roles',
        'manage_channels': 'Manage Channels',
        'kick_members': 'Kick Members',
        'ban_members': 'Ban Members',
        'manage_messages': 'Manage Messages',
        'mute_members': 'Mute Members',
        'deafen_members': 'Deafen Members',
        'move_members': 'Move Members',
        'use_slash_commands': 'Use Slash Commands',
        'manage_webhooks': 'Manage Webhooks',
        'view_audit_log': 'View Audit Log'
    }
    
    active_perms = []
    for perm, value in permissions:
        if value and perm in perm_names:
            active_perms.append(perm_names[perm])
    
    return active_perms

def create_embed_field_chunks(items: List[str], max_length: int = 1024, 
                             separator: str = "\n") -> List[str]:
    """Split items into chunks that fit in embed fields"""
    
    chunks = []
    current_chunk = ""
    
    for item in items:
        test_chunk = current_chunk + separator + item if current_chunk else item
        
        if len(test_chunk) <= max_length:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = item
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def calculate_reading_time(text: str, wpm: int = 200) -> str:
    """Calculate estimated reading time for text"""
    
    word_count = len(text.split())
    minutes = max(1, round(word_count / wpm))
    
    if minutes == 1:
        return "1 minute read"
    else:
        return f"{minutes} minutes read"

async def paginate_embeds(interaction: discord.Interaction, embeds: List[discord.Embed], 
                         timeout: int = 300):
    """Create a paginated embed view"""
    
    if not embeds:
        return
    
    if len(embeds) == 1:
        await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        return
    
    class PaginationView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=timeout)
            self.current_page = 0
            self.max_pages = len(embeds)
            
            # Update button states
            self.update_buttons()
        
        def update_buttons(self):
            self.first_page.disabled = self.current_page == 0
            self.prev_page.disabled = self.current_page == 0
            self.next_page.disabled = self.current_page == self.max_pages - 1
            self.last_page.disabled = self.current_page == self.max_pages - 1
        
        @discord.ui.button(label="⏪", style=discord.ButtonStyle.secondary)
        async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = 0
            self.update_buttons()
            await interaction.response.edit_message(embed=embeds[self.current_page], view=self)
        
        @discord.ui.button(label="◀️", style=discord.ButtonStyle.primary)
        async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page -= 1
            self.update_buttons()
            await interaction.response.edit_message(embed=embeds[self.current_page], view=self)
        
        @discord.ui.button(label="▶️", style=discord.ButtonStyle.primary)
        async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page += 1
            self.update_buttons()
            await interaction.response.edit_message(embed=embeds[self.current_page], view=self)
        
        @discord.ui.button(label="⏩", style=discord.ButtonStyle.secondary)
        async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.current_page = self.max_pages - 1
            self.update_buttons()
            await interaction.response.edit_message(embed=embeds[self.current_page], view=self)
        
        @discord.ui.button(label="❌", style=discord.ButtonStyle.danger)
        async def close_pagination(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(content="Pagination closed.", embed=None, view=None)
    
    # Add page numbers to embeds
    for i, embed in enumerate(embeds):
        embed.set_footer(text=f"Page {i + 1}/{len(embeds)}")
    
    view = PaginationView()
    await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)

def log_error(error: Exception, context: str = ""):
    """Log an error with context"""
    
    error_msg = f"Error in {context}: {type(error).__name__}: {str(error)}"
    logging.error(error_msg)
    print(f"❌ {error_msg}")

def log_info(message: str):
    """Log an info message"""
    
    logging.info(message)
    print(f"ℹ️ {message}")

def log_success(message: str):
    """Log a success message"""
    
    logging.info(f"SUCCESS: {message}")
    print(f"✅ {message}")

def log_warning(message: str):
    """Log a warning message"""
    
    logging.warning(message)
    print(f"⚠️ {message}")

# Decorators

def require_permissions(**perms):
    """Decorator to require specific permissions"""
    def decorator(func):
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if not isinstance(interaction.user, discord.Member):
                await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
                return
            
            missing_perms = []
            for perm, required in perms.items():
                if required and not getattr(interaction.user.guild_permissions, perm, False):
                    missing_perms.append(perm.replace('_', ' ').title())
            
            if missing_perms:
                embed = create_error_embed(
                    "❌ Missing Permissions",
                    f"You need the following permissions: {format_list(missing_perms)}"
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator

def cooldown(rate: int, per: int, key: str = None):
    """Simple cooldown decorator"""
    cooldowns = {}
    
    def decorator(func):
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            user_id = interaction.user.id
            current_time = datetime.utcnow()
            
            # Use custom key or default to function name + user ID
            cooldown_key = f"{key or func.__name__}_{user_id}"
            
            if cooldown_key in cooldowns:
                time_diff = (current_time - cooldowns[cooldown_key]).total_seconds()
                if time_diff < per:
                    remaining = per - time_diff
                    embed = create_warning_embed(
                        "⏰ Cooldown Active",
                        f"Please wait {format_duration(int(remaining))} before using this again."
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            cooldowns[cooldown_key] = current_time
            return await func(self, interaction, *args, **kwargs)
        return wrapper
    return decorator