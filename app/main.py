from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import json
import os
from app.chatbot import get_ai_recommendation # On l'importe depuis l'autre fichier

app = FastAPI()

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"status": "Orientation AI est en ligne", "mode": "Ollama/Llama3"}

@app.get("/ask")
def ask_ai(question: str):
    # Ici on appelle la fonction qui est dans chatbot.py
    reponse_ia = get_ai_recommendation(question)
    return {"bot": reponse_ia}