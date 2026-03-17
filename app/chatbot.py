import sqlite3
import os
from groq import Groq

# 1. On récupère la clé API de Vercel
API_KEY = os.environ.get("GROQ_API_KEY")

def get_ai_recommendation(user_query):
    # Sécurité : Si la clé n'est pas sur Vercel, on arrête tout proprement
    if not API_KEY:
        return "Erreur : La clé API Groq n'est pas configurée dans les paramètres Vercel."
    
    # On crée le client Groq ici pour éviter les crashs au démarrage
    client = Groq(api_key=API_KEY)

    # 2. CALCUL DU CHEMIN (pour Vercel)
    # On trouve où on est (dossier 'app'), on remonte, puis on va dans 'data'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    db_path = os.path.join(root_dir, "data", "orientation.db")
    
    # 3. CONNEXION ET RECHERCHE SQL
    if not os.path.exists(db_path):
        # Si ça affiche ça, c'est que le dossier 'data' ou le fichier .db n'est pas sur GitHub
        return "Erreur : La base de données 'orientation.db' est introuvable."

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # On cherche dans NOM, DOMAINE et DESCRIPTION 
    search_val = f"%{user_query}%"
    cursor.execute("""
        SELECT nom, domaine, description 
        FROM formations 
        WHERE nom LIKE ? OR domaine LIKE ? OR description LIKE ?
    """, (search_val, search_val, search_val))
    
    rows = cursor.fetchall()
    conn.close()

    # 4. PRÉPARATION DU CONTEXTE
    if rows:
        context = "Voici les formations pertinentes trouvées dans notre base :\n"
        for r in rows:
            context += f"- {r[0]} ({r[1]}) : {r[2]}\n"
    else:
        context = "Aucune formation spécifique trouvée dans la base SQL pour cette requête."

    # 5. APPEL À L'IA (GROQ)
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Tu es un conseiller d'orientation expert. 
                Utilise ces données SQL : {context}. 
                
                RÈGLES :
                - Sois encourageant et pro.
                - Ne mentionne jamais 'SQL', 'base de données' ou 'rows'.
                - Si les données SQL contiennent des plateformes (ex: UCAS, Unedassis), cite-les !
                - Si tu ne trouves rien en SQL, réponds avec tes connaissances générales mais précise que c'est en dehors de notre base spécifique."""
            },
            {
                "role": "user",
                "content": user_query,
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content