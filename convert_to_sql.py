import json
import sqlite3
import os

json_path = "data/metiers.json"
db_path = "data/orientation.db"

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS formations')
cursor.execute('CREATE TABLE formations (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, domaine TEXT, description TEXT)')

# LA CORRECTION EST ICI : on boucle sur data['formations']
for item in data.get('formations', []):
    # On crée une description qui contient tout (salaire, plateformes, etc.)
    desc = f"Salaire: {item['debouches']['salaire_moyen']}. Plateformes: {', '.join(item['plateformes'])}"
    cursor.execute('INSERT INTO formations (nom, domaine, description) VALUES (?, ?, ?)', 
                   (item.get('nom'), "Lettres", desc))

conn.commit()
conn.close()
print("Base SQL remplie avec succès !")