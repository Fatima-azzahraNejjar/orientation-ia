import json
import os
from app.database import get_db_connection, init_db

JSON_PATH = "data/metiers.json"

def sync_json_to_sql():
    # 1. On s'assure que les tables existent d'abord
    init_db()

    # 2. On récupère la connexion depuis database.py
    conn = get_db_connection()
    cursor = conn.cursor()

    # 3. SYNCHRONISATION DU JSON
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = 0
            for item in data.get('formations', []):
                # On formate la description
                desc = f"Salaire: {item['debouches']['salaire_moyen']}. Plateformes: {', '.join(item['plateformes'])}"
                
                # INSERT OR IGNORE : Si le métier existe déjà , il ne fait rien parce qu'on a SQL ET JSON, donc on veut éviter les doublons
                cursor.execute('''
                    INSERT OR IGNORE INTO formations (nom, domaine, description) 
                    VALUES (?, ?, ?)
                ''', (item['nom'], "Général", desc))
                
                if cursor.rowcount > 0:
                    count += 1
            
            conn.commit()
            print(f" {count} nouveaux métiers du JSON ajoutés au SQL.")
        except Exception as e:
            print(f" Erreur lors de la lecture du JSON : {e}")
    else:
        print("Fichier metiers.json introuvable.")

    conn.close()

if __name__ == "__main__":
    sync_json_to_sql()