import discord
from discord.ext import commands
from typing import Dict, Any, Optional, List, Tuple
import asyncio
import json
import os
import logging
import re
from datetime import datetime

from config.settings import Config
from utils.helpers import create_embed

class RuleManagementSystem:
    """Advanced rule management and search system for Pakistan RP"""
    
    def __init__(self, bot):
        self.bot = bot
        self.rules_database = {}
        self.categories = {}
        self.search_cache = {}
        self.rule_database_file = "rule_database/rules.json"
        self.categories_file = "rule_database/categories.json"
        
        # Predefined categories for Pakistan RP
        self.default_categories = {
            "General Rules": {
                "description": "Basic server rules that apply to everyone",
                "subcategories": ["Behavior", "Communication", "Account Rules", "General Conduct"],
                "color": 0x3498DB,
                "emoji": "📋"
            },
            "Roleplay Guidelines": {
                "description": "Rules for maintaining quality roleplay",
                "subcategories": ["Character Development", "Realistic Actions", "Meta-gaming", "Power-gaming", "Fear RP"],
                "color": 0x2ECC71,
                "emoji": "🎭"
            },
            "Gang Regulations": {
                "description": "Rules specific to gang activities and management",
                "subcategories": ["Gang Formation", "Territory Rules", "Gang Wars", "Recruitment", "Gang Events"],
                "color": 0xE74C3C,
                "emoji": "🏢"
            },
            "Vehicle Rules": {
                "description": "Transportation and vehicle-related regulations",
                "subcategories": ["Driving Rules", "Vehicle Ownership", "Modifications", "Racing", "Traffic Laws"],
                "color": 0xF39C12,
                "emoji": "🚗"
            },
            "Property Guidelines": {
                "description": "Property ownership and management rules",
                "subcategories": ["House Ownership", "Business Rules", "Property Sales", "Rent System", "Property Events"],
                "color": 0x9B59B6,
                "emoji": "🏠"
            },
            "Economic System": {
                "description": "Rules governing the server economy",
                "subcategories": ["Money Management", "Job Rules", "Trading", "Banking", "Investments"],
                "color": 0x1ABC9C,
                "emoji": "💰"
            },
            "Staff Protocols": {
                "description": "Rules and procedures for staff members",
                "subcategories": ["Admin Duties", "Moderator Guidelines", "Helper Responsibilities", "Punishment Guidelines", "Staff Conduct"],
                "color": 0xE67E22,
                "emoji": "👮"
            },
            "Event Rules": {
                "description": "Rules for server events and special activities",
                "subcategories": ["Event Participation", "Event Hosting", "Rewards System", "Special Events", "Community Events"],
                "color": 0x8E44AD,
                "emoji": "🎉"
            }
        }
    
    async def initialize(self):
        """Initialize rule management system"""
        # Ensure directories exist
        os.makedirs("rule_database", exist_ok=True)
        
        # Load existing rules and categories
        await self.load_rules_database()
        await self.load_categories()
        
        # If no categories exist, create defaults
        if not self.categories:
            self.categories = self.default_categories.copy()
            await self.save_categories()
        
        print(f"✅ Rule system initialized with {len(self.rules_database)} rules in {len(self.categories)} categories")
    
    async def load_rules_database(self):
        """Load rules from JSON file"""
        try:
            if os.path.exists(self.rule_database_file):
                with open(self.rule_database_file, 'r', encoding='utf-8') as f:
                    self.rules_database = json.load(f)
                print(f"📚 Loaded {len(self.rules_database)} rules from database")
            else:
                self.rules_database = {}
                # Create sample rules for demonstration
                await self.create_sample_rules()
        except Exception as e:
            logging.error(f"Failed to load rules database: {e}")
            self.rules_database = {}
    
    async def load_categories(self):
        """Load categories from JSON file"""
        try:
            if os.path.exists(self.categories_file):
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load categories: {e}")
            self.categories = {}
    
    async def save_rules_database(self):
        """Save rules to JSON file"""
        try:
            with open(self.rule_database_file, 'w', encoding='utf-8') as f:
                json.dump(self.rules_database, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save rules database: {e}")
            return False
    
    async def save_categories(self):
        """Save categories to JSON file"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"Failed to save categories: {e}")
            return False
    
    async def create_sample_rules(self):
        """Create sample rules for demonstration"""
        sample_rules = {
            "GR001": {
                "title": "Respect All Players",
                "content": "All players must treat each other with respect. Harassment, discrimination, or toxic behavior will result in immediate punishment.",
                "category": "General Rules",
                "subcategory": "Behavior",
                "keywords": ["respect", "harassment", "toxic", "behavior", "discrimination"],
                "created_by": "System",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "priority": "high",
                "punishments": {
                    "first_offense": {
                        "type": "warning",
                        "duration": None,
                        "fine": 5000,
                        "details": "Verbal warning + $5,000 fine"
                    },
                    "second_offense": {
                        "type": "mute",
                        "duration": 120,  # 2 hours in minutes
                        "fine": 10000,
                        "details": "2 hour mute + $10,000 fine"
                    },
                    "third_offense": {
                        "type": "temp_ban",
                        "duration": 1440,  # 24 hours
                        "fine": 25000,
                        "details": "24 hour ban + $25,000 fine"
                    },
                    "severe": {
                        "type": "perm_ban",
                        "duration": None,
                        "fine": 0,
                        "details": "Permanent ban - no appeal"
                    }
                },
                "appeal_allowed": True,
                "appeal_process": "Submit appeal ticket with evidence within 48 hours",
                "min_staff_rank": "helper"
            },
            "GR002": {
                "title": "No Cheating or Exploiting",
                "content": "The use of cheats, hacks, mods, or exploitation of game bugs is strictly prohibited and will result in permanent ban.",
                "category": "General Rules",
                "subcategory": "General Conduct",
                "keywords": ["cheating", "hacks", "mods", "exploits", "bugs", "ban"],
                "created_by": "System",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "priority": "critical",
                "punishments": {
                    "first_offense": {
                        "type": "perm_ban",
                        "duration": None,
                        "fine": 0,
                        "details": "Immediate permanent ban"
                    },
                    "second_offense": {
                        "type": "perm_ban",
                        "duration": None,
                        "fine": 0,
                        "details": "N/A - Already banned"
                    },
                    "third_offense": {
                        "type": "perm_ban",
                        "duration": None,
                        "fine": 0,
                        "details": "N/A - Already banned"
                    },
                    "severe": {
                        "type": "perm_ban",
                        "duration": None,
                        "fine": 0,
                        "details": "Hardware ban + IP ban"
                    }
                },
                "appeal_allowed": False,
                "appeal_process": "No appeals for cheating violations",
                "min_staff_rank": "moderator"
            },
            "RP001": {
                "title": "Stay in Character",
                "content": "Players must maintain their character at all times during roleplay. Breaking character (OOC in IC) is not allowed.",
                "category": "Roleplay Guidelines",
                "subcategory": "Character Development",
                "keywords": ["character", "roleplay", "ooc", "ic", "breaking character"],
                "created_by": "System",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "priority": "high",
                "punishments": {
                    "first_offense": {
                        "type": "warning",
                        "duration": None,
                        "fine": 2500,
                        "details": "Warning + $2,500 fine"
                    },
                    "second_offense": {
                        "type": "mute",
                        "duration": 30,
                        "fine": 5000,
                        "details": "30 minute mute + $5,000 fine"
                    },
                    "third_offense": {
                        "type": "kick",
                        "duration": None,
                        "fine": 10000,
                        "details": "Kick from server + $10,000 fine"
                    },
                    "severe": {
                        "type": "temp_ban",
                        "duration": 720,  # 12 hours
                        "fine": 0,
                        "details": "12 hour ban"
                    }
                },
                "appeal_allowed": True,
                "appeal_process": "Submit ticket explaining the situation",
                "min_staff_rank": "helper"
            },
            "RP002": {
                "title": "Realistic Actions Only",
                "content": "All actions must be realistic and appropriate for the roleplay scenario. Unrealistic stunts or actions are prohibited.",
                "category": "Roleplay Guidelines",
                "subcategory": "Realistic Actions",
                "keywords": ["realistic", "actions", "stunts", "appropriate", "scenario"],
                "created_by": "System",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "priority": "medium",
                "punishments": {
                    "first_offense": {
                        "type": "warning",
                        "duration": None,
                        "fine": 1000,
                        "details": "Warning + $1,000 fine"
                    },
                    "second_offense": {
                        "type": "vehicle_impound",
                        "duration": 60,
                        "fine": 5000,
                        "details": "Vehicle impound (1 hour) + $5,000 fine"
                    },
                    "third_offense": {
                        "type": "temp_ban",
                        "duration": 360,  # 6 hours
                        "fine": 15000,
                        "details": "6 hour ban + $15,000 fine"
                    },
                    "severe": {
                        "type": "temp_ban",
                        "duration": 1440,  # 24 hours
                        "fine": 0,
                        "details": "24 hour ban"
                    }
                },
                "appeal_allowed": True,
                "appeal_process": "Provide video evidence of the incident",
                "min_staff_rank": "helper"
            },
            "VH001": {
                "title": "Traffic Laws Must Be Followed",
                "content": "Players must follow all traffic laws while driving. Reckless driving without RP reason is prohibited.",
                "category": "Vehicle Rules",
                "subcategory": "Driving Rules",
                "keywords": ["traffic", "driving", "laws", "reckless", "vehicle"],
                "created_by": "System",
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "priority": "medium",
                "punishments": {
                    "first_offense": {
                        "type": "fine",
                        "duration": None,
                        "fine": 2000,
                        "details": "$2,000 traffic fine"
                    },
                    "second_offense": {
                        "type": "vehicle_impound",
                        "duration": 30,
                        "fine": 5000,
                        "details": "Vehicle impound (30 min) + $5,000 fine"
                    },
                    "third_offense": {
                        "type": "vehicle_impound",
                        "duration": 120,
                        "fine": 10000,
                        "details": "Vehicle impound (2 hours) + $10,000 fine + License suspension"
                    },
                    "severe": {
                        "type": "temp_ban",
                        "duration": 720,
                        "fine": 25000,
                        "details": "12 hour ban + $25,000 fine + Permanent license revocation"
                    }
                },
                "appeal_allowed": True,
                "appeal_process": "Submit dashcam footage or witness testimony",
                "min_staff_rank": "helper"
            }
        }
        
        self.rules_database.update(sample_rules)
        await self.save_rules_database()
        print(f"✅ Created {len(sample_rules)} sample rules")
    
    async def search_rules(self, query: str, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search rules by query with advanced matching"""
        
        if not query and not category:
            return []
        
        query_lower = query.lower() if query else ""
        results = []
        
        for rule_id, rule_data in self.rules_database.items():
            score = 0
            
            # Category filter
            if category and rule_data.get('category') != category:
                continue
            
            if query:
                # Title matching (highest weight)
                if query_lower in rule_data.get('title', '').lower():
                    score += 100
                
                # Exact keyword match (high weight)
                keywords = rule_data.get('keywords', [])
                for keyword in keywords:
                    if query_lower == keyword.lower():
                        score += 80
                    elif query_lower in keyword.lower():
                        score += 40
                
                # Content matching (medium weight)
                if query_lower in rule_data.get('content', '').lower():
                    score += 30
                
                # Subcategory matching (low weight)
                if query_lower in rule_data.get('subcategory', '').lower():
                    score += 20
                
                # Rule ID matching
                if query_lower in rule_id.lower():
                    score += 60
            else:
                # No query, just category filter
                score = 10
            
            if score > 0:
                rule_data['rule_id'] = rule_id
                rule_data['search_score'] = score
                results.append(rule_data)
        
        # Sort by score and priority
        def sort_key(rule):
            priority_scores = {'critical': 1000, 'high': 500, 'medium': 100, 'low': 50}
            priority_score = priority_scores.get(rule.get('priority', 'medium'), 100)
            return rule['search_score'] + priority_score
        
        results.sort(key=sort_key, reverse=True)
        
        # Update search statistics
        if self.bot:
            self.bot.stats['rules_accessed'] += 1
        
        return results[:limit]
    
    async def add_rule(self, category: str, subcategory: str, title: str, content: str, 
                      keywords: List[str], created_by_id: int, priority: str = "medium",
                      punishments: Dict[str, Dict[str, Any]] = None, appeal_allowed: bool = True,
                      appeal_process: str = None, min_staff_rank: str = "helper") -> Tuple[bool, str]:
        """Add a new rule to the database"""
        
        # Generate rule ID
        category_prefix = self.get_category_prefix(category)
        existing_ids = [rid for rid in self.rules_database.keys() if rid.startswith(category_prefix)]
        
        # Find next available number
        max_num = 0
        for rid in existing_ids:
            try:
                num = int(rid[len(category_prefix):])
                max_num = max(max_num, num)
            except:
                pass
        
        rule_id = f"{category_prefix}{max_num + 1:03d}"
        
        # Validate inputs
        if not title or not content:
            return False, "Title and content are required"
        
        if category not in self.categories:
            return False, f"Invalid category: {category}"
        
        if subcategory not in self.categories[category].get('subcategories', []):
            return False, f"Invalid subcategory: {subcategory}"
        
        # Create rule data
        rule_data = {
            "title": title,
            "content": content,
            "category": category,
            "subcategory": subcategory,
            "keywords": keywords if isinstance(keywords, list) else [keywords],
            "created_by": created_by_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "priority": priority.lower() if priority.lower() in ['low', 'medium', 'high', 'critical'] else 'medium',
            "punishments": punishments or {
                "first_offense": {
                    "type": "warning",
                    "duration": None,
                    "fine": 5000,
                    "details": "Warning + $5,000 fine"
                },
                "second_offense": {
                    "type": "mute",
                    "duration": 60,
                    "fine": 10000,
                    "details": "1 hour mute + $10,000 fine"
                },
                "third_offense": {
                    "type": "temp_ban",
                    "duration": 1440,
                    "fine": 25000,
                    "details": "24 hour ban + $25,000 fine"
                },
                "severe": {
                    "type": "perm_ban",
                    "duration": None,
                    "fine": 0,
                    "details": "Permanent ban"
                }
            },
            "appeal_allowed": appeal_allowed,
            "appeal_process": appeal_process or "Submit appeal ticket within 48 hours",
            "min_staff_rank": min_staff_rank
        }
        
        # Add to database
        self.rules_database[rule_id] = rule_data
        
        # Save to file
        success = await self.save_rules_database()
        
        if success:
            return True, rule_id
        else:
            # Remove from memory if save failed
            del self.rules_database[rule_id]
            return False, "Failed to save rule to database"
    
    async def update_rule(self, rule_id: str, title: str = None, content: str = None, 
                         keywords: List[str] = None, updated_by_id: int = None, 
                         priority: str = None, punishments: Dict[str, Dict[str, Any]] = None,
                         appeal_allowed: bool = None, appeal_process: str = None,
                         min_staff_rank: str = None) -> bool:
        """Update an existing rule"""
        
        if rule_id not in self.rules_database:
            return False
        
        rule_data = self.rules_database[rule_id]
        
        # Update fields if provided
        if title:
            rule_data['title'] = title
        if content:
            rule_data['content'] = content
        if keywords:
            rule_data['keywords'] = keywords if isinstance(keywords, list) else [keywords]
        if priority and priority.lower() in ['low', 'medium', 'high', 'critical']:
            rule_data['priority'] = priority.lower()
        if punishments:
            rule_data['punishments'] = punishments
        if appeal_allowed is not None:
            rule_data['appeal_allowed'] = appeal_allowed
        if appeal_process:
            rule_data['appeal_process'] = appeal_process
        if min_staff_rank:
            rule_data['min_staff_rank'] = min_staff_rank
        
        # Update metadata
        rule_data['last_updated'] = datetime.utcnow().isoformat()
        if updated_by_id:
            rule_data['updated_by'] = updated_by_id
        
        # Save to file
        return await self.save_rules_database()
    
    async def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule from the database"""
        
        if rule_id not in self.rules_database:
            return False
        
        del self.rules_database[rule_id]
        return await self.save_rules_database()
    
    async def get_rule_by_id(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule by ID"""
        
        rule_data = self.rules_database.get(rule_id)
        if rule_data:
            rule_data = rule_data.copy()
            rule_data['rule_id'] = rule_id
            return rule_data
        return None
    
    async def get_rules_by_category(self, category: str, subcategory: str = None) -> List[Dict[str, Any]]:
        """Get all rules in a specific category"""
        
        rules = []
        for rule_id, rule_data in self.rules_database.items():
            if rule_data.get('category') == category:
                if subcategory is None or rule_data.get('subcategory') == subcategory:
                    rule_copy = rule_data.copy()
                    rule_copy['rule_id'] = rule_id
                    rules.append(rule_copy)
        
        # Sort by priority and creation date
        def sort_key(rule):
            priority_scores = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            return (priority_scores.get(rule.get('priority', 'medium'), 2), rule.get('created_at', ''))
        
        rules.sort(key=sort_key, reverse=True)
        return rules
    
    async def get_category_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for each category"""
        
        stats = {}
        for category in self.categories:
            rules = await self.get_rules_by_category(category)
            subcategory_counts = {}
            priority_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            
            for rule in rules:
                subcat = rule.get('subcategory', 'Other')
                subcategory_counts[subcat] = subcategory_counts.get(subcat, 0) + 1
                
                priority = rule.get('priority', 'medium')
                priority_counts[priority] += 1
            
            stats[category] = {
                'total_rules': len(rules),
                'subcategories': subcategory_counts,
                'priorities': priority_counts,
                'last_updated': max([rule.get('last_updated', '') for rule in rules] or [''])
            }
        
        return stats
    
    def get_category_prefix(self, category: str) -> str:
        """Get the prefix for rule IDs based on category"""
        prefixes = {
            "General Rules": "GR",
            "Roleplay Guidelines": "RP",
            "Gang Regulations": "GG",
            "Vehicle Rules": "VH",
            "Property Guidelines": "PR",
            "Economic System": "EC",
            "Staff Protocols": "ST",
            "Event Rules": "EV"
        }
        return prefixes.get(category, "RU")
    
    async def get_rule_count(self) -> int:
        """Get total number of rules"""
        return len(self.rules_database)
    
    async def create_rule_embed(self, rule_data: Dict[str, Any]) -> discord.Embed:
        """Create a formatted embed for a rule"""
        
        rule_id = rule_data.get('rule_id', 'Unknown')
        category = rule_data.get('category', 'Unknown')
        category_info = self.categories.get(category, {})
        
        embed = discord.Embed(
            title=f"{category_info.get('emoji', '📋')} {rule_data.get('title', 'Unknown Rule')}",
            description=rule_data.get('content', 'No content available'),
            color=category_info.get('color', 0x3498DB),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋 Rule Information",
            value=f"**ID**: {rule_id}\n**Category**: {category}\n**Subcategory**: {rule_data.get('subcategory', 'N/A')}",
            inline=True
        )
        
        # Priority indicator
        priority = rule_data.get('priority', 'medium')
        priority_emojis = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
        
        embed.add_field(
            name="🚨 Priority",
            value=f"{priority_emojis.get(priority, '🟡')} {priority.title()}",
            inline=True
        )
        
        # Keywords
        keywords = rule_data.get('keywords', [])
        if keywords:
            embed.add_field(
                name="🔍 Keywords",
                value=", ".join(keywords[:5]) + ("..." if len(keywords) > 5 else ""),
                inline=True
            )
        
        # Creation info
        created_at = rule_data.get('created_at', '')
        if created_at:
            try:
                created_dt = datetime.fromisoformat(created_at)
                embed.add_field(
                    name="📅 Created",
                    value=f"<t:{int(created_dt.timestamp())}:D>",
                    inline=True
                )
            except:
                pass
        
        embed.set_footer(text=f"Pakistan RP Rules Database • Rule {rule_id}")
        
        return embed
    
    async def export_rules(self, format_type: str = "json") -> Optional[str]:
        """Export rules in various formats"""
        
        if format_type == "json":
            try:
                export_data = {
                    "categories": self.categories,
                    "rules": self.rules_database,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_rules": len(self.rules_database)
                }
                
                filename = f"rule_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join("rule_database", filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                return filepath
            except Exception as e:
                logging.error(f"Failed to export rules: {e}")
                return None
        
        return None
    
    async def import_rules(self, filepath: str) -> Tuple[bool, str]:
        """Import rules from file"""
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Backup current data
            backup_rules = self.rules_database.copy()
            backup_categories = self.categories.copy()
            
            # Import categories if present
            if 'categories' in import_data:
                self.categories.update(import_data['categories'])
                await self.save_categories()
            
            # Import rules
            imported_count = 0
            if 'rules' in import_data:
                for rule_id, rule_data in import_data['rules'].items():
                    if rule_id not in self.rules_database:
                        self.rules_database[rule_id] = rule_data
                        imported_count += 1
            
            # Save imported rules
            success = await self.save_rules_database()
            
            if success:
                return True, f"Successfully imported {imported_count} rules"
            else:
                # Restore backup on failure
                self.rules_database = backup_rules
                self.categories = backup_categories
                return False, "Failed to save imported rules"
                
        except Exception as e:
            logging.error(f"Failed to import rules: {e}")
            return False, f"Import failed: {str(e)}"
    
    async def check_user_violations(self, user_id: int, rule_id: str) -> int:
        """Check how many times a user violated a specific rule"""
        if hasattr(self.bot, 'db') and self.bot.db:
            violations = await self.bot.db.get_user_violations(user_id, active_only=False)
            same_rule_violations = [v for v in violations if v.get('rule_id') == rule_id]
            return len(same_rule_violations)
        return 0
    
    async def get_appropriate_punishment(self, user_id: int, rule_id: str) -> Dict[str, Any]:
        """Get appropriate punishment based on offense count"""
        offense_count = await self.check_user_violations(user_id, rule_id)
        rule = await self.get_rule_by_id(rule_id)
        
        if not rule or 'punishments' not in rule:
            return {
                "type": "warning",
                "duration": None,
                "fine": 5000,
                "details": "Standard warning + $5,000 fine"
            }
        
        punishments = rule['punishments']
        
        if offense_count == 0:
            return punishments.get('first_offense', punishments.get('severe'))
        elif offense_count == 1:
            return punishments.get('second_offense', punishments.get('severe'))
        elif offense_count == 2:
            return punishments.get('third_offense', punishments.get('severe'))
        else:
            return punishments.get('severe', {
                "type": "perm_ban",
                "duration": None,
                "fine": 0,
                "details": "Repeat offender - permanent ban"
            })