import os
from groq import Groq
from database import get_db_connection

API_KEY = os.environ.get("GROQ_API_KEY")

def get_ai_recommendation(user_query):
    if not API_KEY:
        return "Erreur : La clé API Groq n'est pas configurée dans les paramètres Vercel."

    client = Groq(api_key=API_KEY)

    # CONNEXION NEON
    conn = get_db_connection()
    cursor = conn.cursor()

    search_val = f"%{user_query}%"
    cursor.execute("""
        SELECT nom, domaine, description 
        FROM formations 
        WHERE nom LIKE %s OR domaine LIKE %s OR description LIKE %s
    """, (search_val, search_val, search_val))

    rows = cursor.fetchall()
    conn.close()

    if rows:
        context = "Voici les formations pertinentes trouvées dans notre base :\n"
        for r in rows:
            context += f"- {r[0]} ({r[1]}) : {r[2]}\n"
    else:
        context = "Aucune formation spécifique trouvée dans la base SQL pour cette requête."

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"""Tu es un conseiller d'orientation expert. 
                Utilise ces données : {context}. 
                RÈGLES :
                - Sois encourageant et pro.
                - Ne mentionne jamais 'SQL', 'base de données' ou 'rows'.
                - Si tu trouves des informations ou plateformes , cite-les !
                - Si tu ne trouves rien, réponds avec tes connaissances générales.
                - Si l'utilisateur utilise un ton violent ou irrespectueux rappelles le à l'ordre."""
            },
            {
                "role": "user",
                "content": user_query,
            }
        ],
        model="llama-3.3-70b-versatile",
    )

    return chat_completion.choices[0].message.content
