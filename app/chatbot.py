import ollama
import json
import os

def get_ai_recommendation(user_query):
    # 1. Le but est de lui faire charger les données depuis le JSON 
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "metiers.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. C'est la consigne pour l'IA dcp les gens !!
    consigne = f"""
    Tu es un expert en orientation scolaire. 
    Voici tes données de référence (format JSON) : {data}
    
    L'utilisateur te demande : "{user_query}"
    
    Réponds en utilisant les informations du JSON. Si la formation demandée est présente, 
    donne les détails sur les notes, le prix et les plateformes (Parcoursup, UCAS, etc.).
    Sois encourageant et précis.
    """

    # 3. Appeler Ollama
    response = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': consigne},
    ])
    
    return response['message']['content']