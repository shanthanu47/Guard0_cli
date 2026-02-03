import sqlite3
import os

DB_PATH = 'data/mitre.db'

def get_db_connection():
    """Returns a sqlite3 connection to the local database."""
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

def init_db():
    """Initializes the SQLite schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Techniques
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS techniques (
        mitre_id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        url TEXT,
        platforms TEXT
    )
    ''')
    
    # Tactics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tactics (
        name TEXT PRIMARY KEY,
        description TEXT
    )
    ''')
    
    # Technique <-> Tactic Mapping
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS technique_tactics (
        technique_id TEXT,
        tactic_name TEXT,
        PRIMARY KEY (technique_id, tactic_name)
    )
    ''')

    conn.commit()
    conn.close()
