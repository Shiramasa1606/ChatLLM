from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta al build de Vite
build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chat-llm", "dist"))
assets_path = os.path.join(build_path, "assets")

# Endpoint POST al modelo de Ollama
@app.post("/chat")
async def chat(request: Request) -> Dict[str, Any]:
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
            return {
                "response": "[Error al comunicarse con el modelo]",
                "status_code": response.status_code,
                "detail": response.text
            }
    except Exception as e:
        return {"response": f"[Excepción del backend: {str(e)}]"}

# Montar assets (JS/CSS)
app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

# Redirigir raíz a /chat
@app.get("/")
async def redirect_to_chat():
    return RedirectResponse(url="/chat")

# SPA routing: devolver index.html para cualquier ruta no gestionada
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(os.path.join(build_path, "index.html"))
