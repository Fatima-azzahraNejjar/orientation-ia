import sqlite3
import os
from groq import Groq  # pip install groq

# Bon  jvais trouver un moyen pour la clé après
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_recommendation(user_query):
    # 1. Connexion à la base SQL
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "orientation.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Recherche
    query_search = f"%{user_query}%"
    cursor.execute("SELECT * FROM formations WHERE nom LIKE ? OR domaine LIKE ?", (query_search, query_search))
    rows = cursor.fetchall()
    conn.close()

    # 3. Préparation du contexte
    context = "Données disponibles : " + str(rows) if rows else "Aucune formation spécifique trouvée."

    # 4. Appel à Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Tu es un expert en orientation bienveillant. 
                Voici les infos de notre base de données : {context}. 
                
                CONSIGNES :
                1. Si l'utilisateur dit juste 'Bonjour' ou 'Salut', réponds poliment sans mentionner le SQL ou la base de données.
                2. Si tu trouves des infos dans les données fournies, utilise-les pour conseiller.
                3. Ne parle JAMAIS de 'requête SQL', 'JSON' ou 'rows' à l'utilisateur."""
            },
            {
                "role": "user",
                "content": user_query,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content