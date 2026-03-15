import sqlite3
import os
from groq import Groq

# ENV KEY pour Groq API
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def get_ai_recommendation(user_query):
    # 1. Calcul du chemin ABSOLU vers la base de données
    # On remonte d'un cran depuis 'app/' vers la racine, puis on va dans 'data/'
    db_path = os.path.join(os.getcwd(), "data", "orientation.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # --- DEBUG : Pour vérifier dans ton terminal ---
    print(f" Tentative de connexion à : {db_path}")
    if not os.path.exists(db_path):
        print(" ERREUR : Le fichier orientation.db est introuvable à cet endroit !")
    # -----------------------------------------------
    
    print(f"La base existe ? {os.path.exists(db_path)}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 2. Recherche (on nettoie un peu la requête)
    query_search = f"%{user_query}%"
    cursor.execute("SELECT nom, domaine, description FROM formations WHERE nom LIKE ? OR domaine LIKE ?", (query_search, query_search))
    rows = cursor.fetchall()
    conn.close()

    # 3. Préparation du contexte pour l'IA
    if rows:
        context = "Formations trouvées dans notre base :\n"
        for r in rows:
            context += f"- {r[0]} ({r[1]}) : {r[2]}\n"
    else:
        context = "Aucune formation spécifique trouvée dans notre base SQL pour cette recherche."

    # 4. Appel à Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Tu es un expert en orientation bienveillant. 
                Utilise UNIQUEMENT ces infos pour tes recommandations techniques : {context}. 
                
                CONSIGNES :
                1. Sois chaleureux.
                2. Si l'utilisateur pose une question générale, réponds normalement.
                3. Si les données fournies sont pertinentes, cite-les précisément.
                4. NE PARLE JAMAIS de 'base de données', 'SQL' ou 'rows'."""
            },
            {
                "role": "user",
                "content": user_query,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content