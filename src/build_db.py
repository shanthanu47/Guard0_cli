import requests
import os
import json
from mitreattack.stix20 import MitreAttackData
from src.db import get_db_connection, init_db

MITRE_JSON_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
JSON_PATH = "data/enterprise-attack.json"

def download_data():
    if not os.path.exists(JSON_PATH):
        print("Downloading MITRE ATT&CK Data...")
        response = requests.get(MITRE_JSON_URL)
        with open(JSON_PATH, 'wb') as f:
            f.write(response.content)
        print("Download Complete.")
    else:
        print("MITRE Data already exists locally.")

def build_database():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Parsing STIX data (this may take a moment)...")
    mitre_data = MitreAttackData(JSON_PATH)
    
    # Get all techniques (Enterprise)
    # remove_revoked_deprecated=True handles the complexity of old IDs
    techniques = mitre_data.get_techniques(remove_revoked_deprecated=True)
    
    print(f"Insering {len(techniques)} techniques into SQLite...")
    
    for t in techniques:
        # STIX Object properties:
        # t.name, t.description, t.external_references (for ID)
        
        # 1. Extract MITRE ID (e.g. T1059)
        mitre_id = None
        url = None
        for ref in t.external_references:
            if ref.source_name == "mitre-attack":
                mitre_id = ref.external_id
                url = ref.url
                break
        
        if not mitre_id:
            continue

        # 2. Extract Platforms
        platforms = json.dumps(t.x_mitre_platforms) if hasattr(t, 'x_mitre_platforms') else "[]"
        
        # 3. Insert Technique
        cursor.execute('''
            INSERT OR REPLACE INTO techniques (mitre_id, name, description, url, platforms)
            VALUES (?, ?, ?, ?, ?)
        ''', (mitre_id, t.name, t.description, url, platforms))

        # 4. Insert Tactics (Many-to-Many)
        if hasattr(t, 'kill_chain_phases'):
            for phase in t.kill_chain_phases:
                if phase.kill_chain_name == "mitre-attack":
                    tactic_slug = phase.phase_name # e.g. "execution"
                    
                    # Insert Tactic Name (Unique)
                    cursor.execute('''
                        INSERT OR IGNORE INTO tactics (name, description) VALUES (?, ?)
                    ''', (tactic_slug, ""))
                    
                    # Link
                    cursor.execute('''
                        INSERT OR REPLACE INTO technique_tactics (technique_id, tactic_name)
                        VALUES (?, ?)
                    ''', (mitre_id, tactic_slug))

    conn.commit()
    conn.close()
    print("Database built successfully!")

if __name__ == "__main__":
    download_data()
    build_database()
