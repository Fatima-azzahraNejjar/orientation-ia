import json
import sqlite3
import os

# les chemins
json_path = "data/metiers.json"
db_folder = "data"
db_path = "data/orientation.db"

# 1. ça crée le dossier data s'il n'existe pas
if not os.path.exists(db_folder):
    os.makedirs(db_folder)

# 2. Charger ton JSON
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 3. Créer la base SQL
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 4. ça crée la table formations 
cursor.execute('DROP TABLE IF EXISTS formations')
cursor.execute('''
    CREATE TABLE formations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT,
        domaine TEXT,
        description TEXT
    )
''')

# 5. ça insère les données yes
for item in data:
    cursor.execute('''
        INSERT INTO formations (nom, domaine, description) 
        VALUES (?, ?, ?)
    ''', (item.get('nom'), item.get('domaine'), item.get('description')))

conn.commit()
conn.close()
print("Succès ! Ton fichier 'orientation.db' est prêt dans le dossier data.")