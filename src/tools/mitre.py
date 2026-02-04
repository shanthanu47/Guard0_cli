from src.db import get_db_connection
import json

class MitreTool:
    def search_techniques(self, query: str):
        """
        Searches MITRE Techniques by name or ID.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Weighted search: Prioritize Name/ID matches over Description matches
        sql = """
            SELECT mitre_id, name, description, platforms 
            FROM techniques 
            WHERE name LIKE ? OR mitre_id LIKE ? OR description LIKE ?
            ORDER BY 
              CASE 
                WHEN mitre_id LIKE ? THEN 1 
                WHEN name LIKE ? THEN 2 
                ELSE 3 
              END
            LIMIT 5
        """
        wildcard = f"%{query}%"
        # Params: WHERE clause (3) + ORDER BY clause (2)
        cursor.execute(sql, (wildcard, wildcard, wildcard, wildcard, wildcard))
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "id": row["mitre_id"],
                "name": row["name"],
                "description": row["description"][:200] + "...", # Truncate for tokens
                "platforms": json.loads(row["platforms"])
            })
        
        conn.close()
        return results

    def get_technique(self, mitre_id: str):
        """
        Get full details for a specific technique ID (e.g. T1059).
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM techniques WHERE mitre_id = ?", (mitre_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"error": "Technique not found"}
            
        conn.close()
        return dict(row)

mitre_tool = MitreTool()
