import asyncio
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sqlite3
import aiosqlite

from config.settings import Config

class CommunityDatabase:
    """Advanced database management for Pakistan RP Community Bot"""
    
    def __init__(self):
        self.db_path = "database/community.db"
        self.backup_dir = "backups/"
        
        # Ensure directories exist
        os.makedirs("database", exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize database with all required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign key constraints
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Create tickets table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    channel_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    closed_at TEXT,
                    closed_by INTEGER,
                    close_reason TEXT,
                    status TEXT DEFAULT 'open',
                    assigned_staff INTEGER,
                    staff_involved TEXT DEFAULT '[]',
                    last_activity TEXT
                )
            """)
            
            # Create rule violations table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS rule_violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    rule_id TEXT NOT NULL,
                    violation_type TEXT NOT NULL,
                    punishment_applied TEXT NOT NULL,
                    punishment_duration INTEGER,
                    fine_amount INTEGER DEFAULT 0,
                    issued_by INTEGER NOT NULL,
                    issued_at TEXT NOT NULL,
                    expires_at TEXT,
                    appeal_status TEXT DEFAULT 'none',
                    appeal_reason TEXT,
                    appeal_result TEXT,
                    notes TEXT
                )
            """)
            
            # Create user warnings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    warned_by INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    rule_violated TEXT,
                    warning_level INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create announcements table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS announcements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    author_id INTEGER NOT NULL,
                    author_name TEXT NOT NULL,
                    ping_everyone BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    message_id INTEGER,
                    channel_id INTEGER
                )
            """)
            
            # Create bot statistics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stat_name TEXT NOT NULL,
                    stat_value INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create action logs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_type TEXT NOT NULL,
                    user_id INTEGER,
                    staff_id INTEGER NOT NULL,
                    target_user INTEGER,
                    details TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    channel_id INTEGER,
                    message_id INTEGER
                )
            """)
            
            # Create member data table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS member_data (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    display_name TEXT,
                    join_date TEXT,
                    total_messages INTEGER DEFAULT 0,
                    total_tickets INTEGER DEFAULT 0,
                    warning_count INTEGER DEFAULT 0,
                    last_activity TEXT,
                    is_blacklisted BOOLEAN DEFAULT 0,
                    blacklist_reason TEXT,
                    notes TEXT
                )
            """)
            
            await db.commit()
            print("✅ Database initialized successfully")
    
    async def create_ticket(self, ticket_data: Dict[str, Any]) -> bool:
        """Create a new ticket record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO tickets (
                        ticket_id, user_id, username, display_name, channel_id,
                        category, urgency, priority, description, created_at,
                        status, last_activity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_data['ticket_id'],
                    ticket_data['user_id'],
                    ticket_data['username'],
                    ticket_data['display_name'],
                    ticket_data['channel_id'],
                    ticket_data['category'],
                    ticket_data['urgency'],
                    ticket_data.get('priority', 0),
                    ticket_data['description'],
                    ticket_data['created_at'],
                    ticket_data['status'],
                    ticket_data.get('last_activity', ticket_data['created_at'])
                ))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to create ticket record: {e}")
            return False
    
    async def close_ticket(self, ticket_id: str, closed_by: int, reason: str) -> bool:
        """Close a ticket record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE tickets SET 
                        status = 'closed',
                        closed_at = ?,
                        closed_by = ?,
                        close_reason = ?
                    WHERE ticket_id = ?
                """, (datetime.utcnow().isoformat(), closed_by, reason, ticket_id))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to close ticket: {e}")
            return False
    
    async def get_active_tickets(self) -> List[Dict[str, Any]]:
        """Get all active tickets"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT * FROM tickets WHERE status = 'open'") as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Failed to get active tickets: {e}")
            return []
    
    async def log_rule_violation(self, user_id: int, rule_id: str, violation_type: str, 
                               punishment: Dict[str, Any], issued_by: int, notes: str = "") -> bool:
        """Log a rule violation with punishment details"""
        try:
            expires_at = None
            if punishment.get('duration'):
                expires_at = (datetime.utcnow() + timedelta(minutes=punishment['duration'])).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO rule_violations (
                        user_id, rule_id, violation_type, punishment_applied,
                        punishment_duration, fine_amount, issued_by, issued_at,
                        expires_at, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, rule_id, violation_type, punishment['type'],
                    punishment.get('duration'), punishment.get('fine_amount', 0),
                    issued_by, datetime.utcnow().isoformat(), expires_at, notes
                ))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to log rule violation: {e}")
            return False
    
    async def add_warning(self, user_id: int, warned_by: int, reason: str, 
                         rule_violated: str = "", warning_level: int = 1) -> bool:
        """Add a warning to a user"""
        try:
            expires_at = (datetime.utcnow() + timedelta(days=30)).isoformat()  # Warnings expire in 30 days
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO user_warnings (
                        user_id, warned_by, reason, rule_violated,
                        warning_level, created_at, expires_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, warned_by, reason, rule_violated,
                    warning_level, datetime.utcnow().isoformat(), expires_at
                ))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to add warning: {e}")
            return False
    
    async def get_user_violations(self, user_id: int, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get all violations for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                query = "SELECT * FROM rule_violations WHERE user_id = ?"
                params = [user_id]
                
                if active_only:
                    query += " AND (expires_at IS NULL OR expires_at > ?)"
                    params.append(datetime.utcnow().isoformat())
                
                query += " ORDER BY issued_at DESC"
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Failed to get user violations: {e}")
            return []
    
    async def get_user_warnings(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get warnings for a user"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                
                query = "SELECT * FROM user_warnings WHERE user_id = ?"
                params = [user_id]
                
                if active_only:
                    query += " AND is_active = 1 AND expires_at > ?"
                    params.append(datetime.utcnow().isoformat())
                
                query += " ORDER BY created_at DESC"
                
                async with db.execute(query, params) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"Failed to get user warnings: {e}")
            return []
    
    async def create_announcement(self, title: str, content: str, author_id: int, 
                                author_name: str, ping_everyone: bool = False) -> int:
        """Create an announcement record"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO announcements (
                        title, content, author_id, author_name, ping_everyone, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    title, content, author_id, author_name,
                    ping_everyone, datetime.utcnow().isoformat()
                ))
                announcement_id = cursor.lastrowid
                await db.commit()
                return announcement_id
        except Exception as e:
            logging.error(f"Failed to create announcement: {e}")
            return 0
    
    async def log_action(self, action_type: str, staff_id: int, details: str,
                        user_id: int = None, target_user: int = None,
                        channel_id: int = None, message_id: int = None) -> bool:
        """Log a staff action"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO action_logs (
                        action_type, user_id, staff_id, target_user,
                        details, timestamp, channel_id, message_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    action_type, user_id, staff_id, target_user,
                    details, datetime.utcnow().isoformat(), channel_id, message_id
                ))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to log action: {e}")
            return False
    
    async def update_member_data(self, user_id: int, username: str, display_name: str = None) -> bool:
        """Update or create member data"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR REPLACE INTO member_data (
                        user_id, username, display_name, last_activity
                    ) VALUES (?, ?, ?, ?)
                """, (
                    user_id, username, display_name or username,
                    datetime.utcnow().isoformat()
                ))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to update member data: {e}")
            return False
    
    async def increment_member_messages(self, user_id: int) -> bool:
        """Increment message count for a member"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    UPDATE member_data 
                    SET total_messages = total_messages + 1,
                        last_activity = ?
                    WHERE user_id = ?
                """, (datetime.utcnow().isoformat(), user_id))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to increment member messages: {e}")
            return False
    
    async def update_bot_stats(self, stats: Dict[str, int]) -> bool:
        """Update bot statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for stat_name, stat_value in stats.items():
                    await db.execute("""
                        INSERT OR REPLACE INTO bot_stats (stat_name, stat_value, updated_at)
                        VALUES (?, ?, ?)
                    """, (stat_name, stat_value, datetime.utcnow().isoformat()))
                await db.commit()
                return True
        except Exception as e:
            logging.error(f"Failed to update bot stats: {e}")
            return False
    
    async def get_bot_stats(self) -> Dict[str, int]:
        """Get bot statistics"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute("SELECT stat_name, stat_value FROM bot_stats") as cursor:
                    rows = await cursor.fetchall()
                    return {row['stat_name']: row['stat_value'] for row in rows}
        except Exception as e:
            logging.error(f"Failed to get bot stats: {e}")
            return {}
    
    async def cleanup_old_logs(self, days: int = None) -> int:
        """Clean up old logs and expired records"""
        days = days or Config.LOG_RETENTION_DAYS
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        cleaned = 0
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Clean expired warnings
                cursor = await db.execute("""
                    UPDATE user_warnings SET is_active = 0 
                    WHERE expires_at < ? AND is_active = 1
                """, (datetime.utcnow().isoformat(),))
                cleaned += cursor.rowcount
                
                # Clean old action logs
                cursor = await db.execute("""
                    DELETE FROM action_logs WHERE timestamp < ?
                """, (cutoff_date,))
                cleaned += cursor.rowcount
                
                # Clean old closed tickets
                cursor = await db.execute("""
                    DELETE FROM tickets 
                    WHERE status = 'closed' AND closed_at < ?
                """, (cutoff_date,))
                cleaned += cursor.rowcount
                
                await db.commit()
                
            print(f"🧹 Database cleanup: {cleaned} records cleaned")
            return cleaned
            
        except Exception as e:
            logging.error(f"Database cleanup failed: {e}")
            return 0
    
    async def create_backup(self) -> str:
        """Create a database backup"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(self.backup_dir, f"community_backup_{timestamp}.db")
            
            # Copy database file
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            print(f"💾 Database backup created: {backup_path}")
            return backup_path
            
        except Exception as e:
            logging.error(f"Backup creation failed: {e}")
            return ""
    
    async def get_statistics_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                stats = {}
                
                # Ticket statistics
                async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'") as cursor:
                    stats['active_tickets'] = (await cursor.fetchone())[0]
                
                async with db.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'") as cursor:
                    stats['resolved_tickets'] = (await cursor.fetchone())[0]
                
                # Rule violation statistics
                async with db.execute("SELECT COUNT(*) FROM rule_violations") as cursor:
                    stats['total_violations'] = (await cursor.fetchone())[0]
                
                async with db.execute("""
                    SELECT COUNT(*) FROM rule_violations 
                    WHERE expires_at IS NULL OR expires_at > ?
                """, (datetime.utcnow().isoformat(),)) as cursor:
                    stats['active_punishments'] = (await cursor.fetchone())[0]
                
                # Warning statistics
                async with db.execute("""
                    SELECT COUNT(*) FROM user_warnings 
                    WHERE is_active = 1 AND expires_at > ?
                """, (datetime.utcnow().isoformat(),)) as cursor:
                    stats['active_warnings'] = (await cursor.fetchone())[0]
                
                # Announcement statistics
                async with db.execute("SELECT COUNT(*) FROM announcements") as cursor:
                    stats['total_announcements'] = (await cursor.fetchone())[0]
                
                # Member statistics
                async with db.execute("SELECT COUNT(*) FROM member_data") as cursor:
                    stats['tracked_members'] = (await cursor.fetchone())[0]
                
                return stats
                
        except Exception as e:
            logging.error(f"Failed to get statistics summary: {e}")
            return {}
    
    async def close(self):
        """Close database connections"""
        print("💾 Database connections closed")