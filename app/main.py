from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import sys

# Configuration du chemin pour trouver chatbot.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Imports de tes fichiers locaux
from chatbot import get_ai_recommendation
from database import get_db_connection
from auth import hash_password, verify_password

app = FastAPI()

# Montage des fichiers statiques (HTML/CSS/JS)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "Orientation AI est en ligne", "mode": "SQL + Auth + Groq"}

# --- PARTIE CHATBOT ---
@app.get("/ask")
def ask_ai(question: str):
    reponse_ia = get_ai_recommendation(question)
    return {"bot": reponse_ia}

# --- PARTIE INSCRIPTION ---
@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # On vérifie si le pseudo existe déjà
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ce pseudo est déjà pris !")
        
        # Hachage du mot de passe (via auth.py)
        hashed_pwd = hash_password(password)
        
        # Insertion du nouvel utilisateur
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hashed_pwd))
        conn.commit()
        return {"message": "Compte créé ! Tu peux maintenant te connecter."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# --- PARTIE CONNEXION ---
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # On cherche l'utilisateur par son pseudo
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Pseudo ou mot de passe incorrect.")
        
        return {"message": "Connexion réussie !", "user_id": user["id"], "username": username}
    finally:
        conn.close()