import logging
import sqlite3
from datetime import datetime
from typing import Optional

def setup_logging():
    """
    Setup logging configuration
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def log_interaction(prompt: str, response: str, model: str = "llama3.1"):
    """
    Log interaction to SQLite database
    """
    try:
        conn = sqlite3.connect('audit_log.db')
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                prompt TEXT,
                response TEXT,
                model TEXT
            )
        ''')

        # Insert interaction
        cursor.execute('''
            INSERT INTO interactions (timestamp, prompt, response, model)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now().isoformat(), prompt, response, model))

        conn.commit()
        conn.close()

    except Exception as e:
        logging.error(f"Failed to log interaction: {e}")