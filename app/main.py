from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from chatbot import get_ai_recommendation

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    # On change juste le texte pour savoir qu'on est en mode Rapide/SQL
    return {"status": "Orientation AI est en ligne", "mode": "SQL + Groq API"}

@app.get("/ask")
def ask_ai(question: str):
    reponse_ia = get_ai_recommendation(question)
    return {"bot": reponse_ia}