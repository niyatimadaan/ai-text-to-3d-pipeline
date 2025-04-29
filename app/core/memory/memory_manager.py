# core/memory/memory_manager.py
import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

class MemoryManager:
    """
    Manages short-term and long-term memory for the AI application.
    Short-term memory persists during a session, while long-term memory
    is stored in SQLite for persistence across sessions.
    """
    
    def __init__(self, db_path: str = "memory.db"):
        """
        Initialize memory systems.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.short_term_memory: Dict[str, Any] = {}
        self.db_path = db_path
        self._initialize_db()
        
    def _initialize_db(self) -> None:
        """Initialize the SQLite database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table for storing creations
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS creations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                creation_date TEXT,
                prompt TEXT,
                enhanced_prompt TEXT, 
                image_path TEXT,
                model_path TEXT,
                video_path TEXT,
                tags TEXT,
                user_id TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            logging.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
    
    def save_to_short_term(self, key: str, value: Any) -> None:
        """
        Save data to short-term memory.
        
        Args:
            key: Memory identifier
            value: Data to store
        """
        self.short_term_memory[key] = value
        logging.info(f"Saved to short-term memory: {key}")
        
    def get_from_short_term(self, key: str) -> Optional[Any]:
        """
        Retrieve data from short-term memory.
        
        Args:
            key: Memory identifier
            
        Returns:
            The stored data or None if not found
        """
        return self.short_term_memory.get(key)
        
    def save_creation(self, 
                     prompt: str, 
                     enhanced_prompt: str, 
                     image_path: str, 
                     model_path: str, 
                     tags: List[str] = None,
                     user_id: str = "default_user") -> int:
        """
        Save a creation to long-term memory.
        
        Args:
            prompt: Original user prompt
            enhanced_prompt: Enhanced prompt used for generation
            image_path: Path to the generated image
            model_path: Path to the generated 3D model
            tags: List of tags describing the creation
            user_id: Identifier for the user
            
        Returns:
            ID of the saved creation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            tags_str = ",".join(tags) if tags else ""
            creation_date = datetime.now().isoformat()
            
            cursor.execute('''
            INSERT INTO creations 
            (creation_date, prompt, enhanced_prompt, image_path, model_path, tags, user_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (creation_date, prompt, enhanced_prompt, image_path, model_path, tags_str, user_id))
            
            creation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"Creation saved to long-term memory with ID: {creation_id}")
            return creation_id
        except Exception as e:
            logging.error(f"Error saving to long-term memory: {e}")
            return -1
    
    def search_creations(self, search_term: str, user_id: str = None) -> List[Dict]:
        """
        Search for creations containing the search term.
        
        Args:
            search_term: Term to search for in prompts, tags
            user_id: Optional filter by user
            
        Returns:
            List of matching creation records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM creations 
            WHERE (prompt LIKE ? OR enhanced_prompt LIKE ? OR tags LIKE ?)
            '''
            params = [f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"]
            
            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)
                
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            logging.error(f"Error searching creations: {e}")
            return []
    
    def get_recent_creations(self, limit: int = 5, user_id: str = None) -> List[Dict]:
        """
        Get most recent creations.
        
        Args:
            limit: Maximum number of results
            user_id: Optional filter by user
            
        Returns:
            List of recent creation records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM creations"
            params = []
            
            if user_id:
                query += " WHERE user_id = ?"
                params.append(user_id)
                
            query += " ORDER BY creation_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            logging.error(f"Error getting recent creations: {e}")
            return []

    def get_all_creations(self, limit: int = 20, user_id: str = None) -> List[Dict]:
        """
        Get all creations.
        
        Args:
            limit: Maximum number of results
            user_id: Optional filter by user
            
        Returns:
            List of all creation records
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM creations"
            params = []
            
            if user_id:
                query += " WHERE user_id = ?"
                params.append(user_id)
                
            query += " ORDER BY creation_date DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return results
        except Exception as e:
            logging.error(f"Error getting all creations: {e}")
            return []