import asyncio
import discord
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, Optional, List, Callable
import json
import os

from config.settings import Config
from utils.helpers import create_embed, format_duration

class AutomationEngine:
    """Advanced automation system for Pakistan RP Community Bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.automation_rules = {}
        self.scheduled_tasks = {}
        self.automation_stats = {
            'tickets_auto_closed': 0,
            'warnings_auto_expired': 0,
            'backups_created': 0,
            'cleanup_actions': 0,
            'auto_responses_sent': 0
        }
        
        # Load automation configuration
        self.config_file = "automation/automation_config.json"
        self.load_automation_config()
    
    async def initialize(self):
        """Initialize automation engine"""
        
        # Ensure automation directory exists
        os.makedirs("automation", exist_ok=True)
        
        # Setup default automation rules
        await self.setup_default_rules()
        
        # Start automated tasks
        await self.start_automation_tasks()
        
        print("⚡ Automation engine initialized")
    
    def load_automation_config(self):
        """Load automation configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.automation_rules.update(config.get('rules', {}))
                    self.automation_stats.update(config.get('stats', {}))
                print(f"⚡ Loaded {len(self.automation_rules)} automation rules")
            else:
                self.create_default_config()
        except Exception as e:
            logging.error(f"Failed to load automation config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default automation configuration"""
        default_config = {
            "rules": {
                "ticket_auto_close": {
                    "enabled": True,
                    "conditions": {
                        "inactive_hours": 72,
                        "no_staff_response": True
                    },
                    "actions": ["close_ticket", "send_transcript", "notify_user"]
                },
                "warning_auto_expire": {
                    "enabled": True,
                    "conditions": {
                        "expire_days": 30
                    },
                    "actions": ["expire_warning", "notify_staff"]
                },
                "auto_backup": {
                    "enabled": True,
                    "conditions": {
                        "interval_hours": 6
                    },
                    "actions": ["create_backup", "cleanup_old_backups"]
                },
                "rule_violation_tracking": {
                    "enabled": True,
                    "conditions": {
                        "track_repeat_offenders": True,
                        "escalation_threshold": 3
                    },
                    "actions": ["escalate_punishment", "notify_senior_staff"]
                },
                "member_activity_tracking": {
                    "enabled": True,
                    "conditions": {
                        "track_messages": True,
                        "inactive_days": 30
                    },
                    "actions": ["update_activity", "mark_inactive"]
                }
            },
            "stats": self.automation_stats
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            print("✅ Created default automation configuration")
        except Exception as e:
            logging.error(f"Failed to create default config: {e}")
    
    async def setup_default_rules(self):
        """Setup default automation rules"""
        
        # Auto-close inactive tickets
        await self.add_automation_rule(
            rule_name="ticket_auto_close",
            condition=self.check_inactive_tickets,
            action=self.auto_close_tickets,
            interval_minutes=30,
            enabled=True
        )
        
        # Auto-expire warnings
        await self.add_automation_rule(
            rule_name="warning_auto_expire",
            condition=self.check_expired_warnings,
            action=self.expire_warnings,
            interval_minutes=60,
            enabled=True
        )
        
        # Auto-backup database
        await self.add_automation_rule(
            rule_name="auto_backup",
            condition=self.check_backup_needed,
            action=self.create_automated_backup,
            interval_minutes=360,  # 6 hours
            enabled=True
        )
        
        # Track rule violations
        await self.add_automation_rule(
            rule_name="violation_tracking",
            condition=self.check_repeat_offenders,
            action=self.handle_repeat_offenders,
            interval_minutes=120,
            enabled=True
        )
        
        # Clean up old data
        await self.add_automation_rule(
            rule_name="data_cleanup",
            condition=self.check_cleanup_needed,
            action=self.cleanup_old_data,
            interval_minutes=1440,  # Daily
            enabled=True
        )
    
    async def add_automation_rule(self, rule_name: str, condition: Callable, 
                                action: Callable, interval_minutes: int, 
                                enabled: bool = True):
        """Add a new automation rule"""
        
        rule = {
            'name': rule_name,
            'condition': condition,
            'action': action,
            'interval': interval_minutes,
            'enabled': enabled,
            'last_run': None,
            'run_count': 0,
            'success_count': 0,
            'error_count': 0
        }
        
        self.automation_rules[rule_name] = rule
        
        if enabled:
            # Schedule the rule
            task = asyncio.create_task(self.run_automation_rule(rule))
            self.scheduled_tasks[rule_name] = task
    
    async def run_automation_rule(self, rule: Dict[str, Any]):
        """Run an automation rule continuously"""
        
        rule_name = rule['name']
        interval = rule['interval']
        
        while rule['enabled']:
            try:
                # Check if conditions are met
                if await rule['condition']():
                    # Execute action
                    result = await rule['action']()
                    if result:
                        rule['success_count'] += 1
                        self.automation_stats['cleanup_actions'] += 1
                    else:
                        rule['error_count'] += 1
                
                rule['last_run'] = datetime.utcnow().isoformat()
                rule['run_count'] += 1
                
            except Exception as e:
                logging.error(f"Automation rule '{rule_name}' failed: {e}")
                rule['error_count'] += 1
            
            # Wait for next interval
            await asyncio.sleep(interval * 60)
    
    async def start_automation_tasks(self):
        """Start all enabled automation tasks"""
        
        for rule_name, rule in self.automation_rules.items():
            if rule.get('enabled', False):
                if rule_name not in self.scheduled_tasks:
                    task = asyncio.create_task(self.run_automation_rule(rule))
                    self.scheduled_tasks[rule_name] = task
        
        print(f"⚡ Started {len(self.scheduled_tasks)} automation tasks")
    
    async def stop_automation_tasks(self):
        """Stop all automation tasks"""
        
        for task_name, task in self.scheduled_tasks.items():
            task.cancel()
        
        self.scheduled_tasks.clear()
        print("⚡ All automation tasks stopped")
    
    # CONDITION CHECKS
    
    async def check_inactive_tickets(self) -> bool:
        """Check if there are tickets that need auto-closing"""
        if not hasattr(self.bot, 'tickets') or not self.bot.tickets:
            return False
        
        auto_close_hours = Config.TICKET_AUTO_CLOSE_HOURS
        cutoff_time = datetime.utcnow() - timedelta(hours=auto_close_hours)
        
        for ticket_id, ticket_data in self.bot.tickets.active_tickets.items():
            created = datetime.fromisoformat(ticket_data['created_at'])
            last_activity = datetime.fromisoformat(ticket_data.get('last_activity', ticket_data['created_at']))
            
            if last_activity < cutoff_time:
                return True
        
        return False
    
    async def check_expired_warnings(self) -> bool:
        """Check if there are warnings that need expiring"""
        try:
            if not self.bot.db:
                return False
            
            # Check for expired warnings in database
            # This would be implemented with a database query
            return True  # Placeholder
        except Exception as e:
            logging.error(f"Failed to check expired warnings: {e}")
            return False
    
    async def check_backup_needed(self) -> bool:
        """Check if database backup is needed"""
        try:
            backup_interval = Config.AUTO_BACKUP_INTERVAL_HOURS
            
            # Check if enough time has passed since last backup
            # This would check the last backup timestamp
            return True  # Placeholder - implement backup timestamp checking
        except Exception as e:
            logging.error(f"Failed to check backup needed: {e}")
            return False
    
    async def check_repeat_offenders(self) -> bool:
        """Check for repeat offenders who need escalated punishment"""
        try:
            if not self.bot.db:
                return False
            
            # This would query the database for users with multiple violations
            return False  # Placeholder
        except Exception as e:
            logging.error(f"Failed to check repeat offenders: {e}")
            return False
    
    async def check_cleanup_needed(self) -> bool:
        """Check if data cleanup is needed"""
        return True  # Always return true for daily cleanup
    
    # AUTOMATION ACTIONS
    
    async def auto_close_tickets(self) -> bool:
        """Automatically close inactive tickets"""
        try:
            if not hasattr(self.bot, 'tickets') or not self.bot.tickets:
                return False
            
            closed_count = await self.bot.tickets.cleanup_old_tickets()
            
            if closed_count > 0:
                self.automation_stats['tickets_auto_closed'] += closed_count
                
                # Notify staff
                await self.notify_staff_automation(
                    "🎫 Auto-Closed Tickets",
                    f"Automatically closed {closed_count} inactive tickets due to inactivity."
                )
                
                print(f"⚡ Auto-closed {closed_count} inactive tickets")
            
            return closed_count > 0
            
        except Exception as e:
            logging.error(f"Auto-close tickets failed: {e}")
            return False
    
    async def expire_warnings(self) -> bool:
        """Expire old warnings"""
        try:
            if not self.bot.db:
                return False
            
            expired_count = 0
            
            # This would implement warning expiration logic
            # For now, just update the stat
            self.automation_stats['warnings_auto_expired'] += expired_count
            
            if expired_count > 0:
                await self.notify_staff_automation(
                    "⚠️ Warnings Expired",
                    f"Automatically expired {expired_count} old warnings."
                )
            
            return expired_count > 0
            
        except Exception as e:
            logging.error(f"Expire warnings failed: {e}")
            return False
    
    async def create_automated_backup(self) -> bool:
        """Create automated database backup"""
        try:
            if not self.bot.db:
                return False
            
            backup_path = await self.bot.db.create_backup()
            
            if backup_path:
                self.automation_stats['backups_created'] += 1
                
                await self.notify_staff_automation(
                    "💾 Automated Backup",
                    f"Database backup created successfully.\n**Location**: `{backup_path}`"
                )
                
                print(f"⚡ Automated backup created: {backup_path}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Automated backup failed: {e}")
            return False
    
    async def handle_repeat_offenders(self) -> bool:
        """Handle repeat offenders with escalated punishments"""
        try:
            # This would implement repeat offender detection and escalation
            # For now, just placeholder
            return False
            
        except Exception as e:
            logging.error(f"Handle repeat offenders failed: {e}")
            return False
    
    async def cleanup_old_data(self) -> bool:
        """Clean up old data from database"""
        try:
            if not self.bot.db:
                return False
            
            cleaned_count = await self.bot.db.cleanup_old_logs()
            
            if cleaned_count > 0:
                self.automation_stats['cleanup_actions'] += 1
                
                await self.notify_staff_automation(
                    "🧹 Data Cleanup",
                    f"Cleaned up {cleaned_count} old records from database."
                )
            
            return cleaned_count > 0
            
        except Exception as e:
            logging.error(f"Data cleanup failed: {e}")
            return False
    
    async def notify_staff_automation(self, title: str, description: str):
        """Send automation notification to staff"""
        
        if not Config.STAFF_LOGS_CHANNEL_ID:
            return
        
        logs_channel = self.bot.get_channel(Config.STAFF_LOGS_CHANNEL_ID)
        if not logs_channel:
            return
        
        try:
            embed = create_embed(
                f"⚡ {title}",
                description,
                discord.Color.blue()
            )
            
            embed.add_field(
                name="🤖 Automation Engine",
                value=f"**Time**: <t:{int(datetime.utcnow().timestamp())}:F>\n**Status**: Completed Successfully",
                inline=False
            )
            
            embed.set_footer(text="Pakistan RP Automation System")
            
            await logs_channel.send(embed=embed)
            
        except Exception as e:
            logging.error(f"Failed to send automation notification: {e}")
    
    # MANAGEMENT FUNCTIONS
    
    async def enable_rule(self, rule_name: str) -> bool:
        """Enable an automation rule"""
        
        if rule_name not in self.automation_rules:
            return False
        
        rule = self.automation_rules[rule_name]
        rule['enabled'] = True
        
        # Start the task if not already running
        if rule_name not in self.scheduled_tasks:
            task = asyncio.create_task(self.run_automation_rule(rule))
            self.scheduled_tasks[rule_name] = task
        
        await self.save_automation_config()
        return True
    
    async def disable_rule(self, rule_name: str) -> bool:
        """Disable an automation rule"""
        
        if rule_name not in self.automation_rules:
            return False
        
        rule = self.automation_rules[rule_name]
        rule['enabled'] = False
        
        # Stop the task if running
        if rule_name in self.scheduled_tasks:
            self.scheduled_tasks[rule_name].cancel()
            del self.scheduled_tasks[rule_name]
        
        await self.save_automation_config()
        return True
    
    async def get_automation_status(self) -> Dict[str, Any]:
        """Get current automation status"""
        
        status = {
            'total_rules': len(self.automation_rules),
            'active_rules': len([r for r in self.automation_rules.values() if r.get('enabled', False)]),
            'running_tasks': len(self.scheduled_tasks),
            'stats': self.automation_stats.copy(),
            'rules': {}
        }
        
        for rule_name, rule in self.automation_rules.items():
            status['rules'][rule_name] = {
                'enabled': rule.get('enabled', False),
                'last_run': rule.get('last_run'),
                'run_count': rule.get('run_count', 0),
                'success_count': rule.get('success_count', 0),
                'error_count': rule.get('error_count', 0),
                'success_rate': (rule.get('success_count', 0) / max(rule.get('run_count', 1), 1)) * 100
            }
        
        return status
    
    async def save_automation_config(self):
        """Save automation configuration to file"""
        
        try:
            config = {
                'rules': {name: {k: v for k, v in rule.items() if k not in ['condition', 'action']} 
                         for name, rule in self.automation_rules.items()},
                'stats': self.automation_stats
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
        except Exception as e:
            logging.error(f"Failed to save automation config: {e}")
    
    async def create_automation_report(self) -> discord.Embed:
        """Create automation status report"""
        
        status = await self.get_automation_status()
        
        embed = discord.Embed(
            title="⚡ Automation Engine Status",
            description="Current status of all automated systems",
            color=0x2ECC71,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Overview",
            value=f"**Total Rules**: {status['total_rules']}\n**Active Rules**: {status['active_rules']}\n**Running Tasks**: {status['running_tasks']}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Statistics",
            value=f"**Tickets Auto-Closed**: {status['stats']['tickets_auto_closed']}\n**Backups Created**: {status['stats']['backups_created']}\n**Cleanup Actions**: {status['stats']['cleanup_actions']}",
            inline=True
        )
        
        # Show top performing rules
        top_rules = sorted(
            status['rules'].items(),
            key=lambda x: x[1]['run_count'],
            reverse=True
        )[:3]
        
        if top_rules:
            rule_text = []
            for rule_name, rule_data in top_rules:
                status_emoji = "🟢" if rule_data['enabled'] else "🔴"
                rule_text.append(f"{status_emoji} **{rule_name}**: {rule_data['run_count']} runs")
            
            embed.add_field(
                name="🏆 Top Rules",
                value="\n".join(rule_text),
                inline=False
            )
        
        embed.set_footer(text="Pakistan RP Automation Engine")
        
        return embed