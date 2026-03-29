from fastapi import FastAPI, Form, HTTPException
from fastapi.staticfiles import StaticFiles
import os
import sys
import psycopg2
import psycopg2.extras

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import get_ai_recommendation
from database import get_db_connection
from auth import hash_password, verify_password

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "Orientation AI est en ligne", "mode": "SQL + Auth + Groq"}

@app.get("/ask")
def ask_ai(question: str):
    reponse_ia = get_ai_recommendation(question)
    return {"bot": reponse_ia}

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Ce pseudo est déjà pris !")
        hashed_pwd = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_pwd)
        )
        conn.commit()
        return {"message": "Compte créé ! Tu peux maintenant te connecter."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user or not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Pseudo ou mot de passe incorrect.")
        return {"message": "Connexion réussie !", "user_id": user["id"], "username": username}
    finally:
        conn.close()