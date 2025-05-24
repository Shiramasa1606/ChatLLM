from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "java-herencia-model")

app = FastAPI()

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("prompt", "")

    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": user_input,
            "stream": False
        })

        if response.status_code == 200:
            return {"response": response.json().get("response")}
        else:
            return {"response": "[Error al comunicarse con el modelo]"}
    except Exception as e:
        return {"response": f"[Excepción del backend: {str(e)}]"}
