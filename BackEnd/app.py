from typing import Any, Dict, Set, TypedDict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import requests
import os
from dotenv import load_dotenv
import threading

# Cargar variables de entorno desde .env
load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")

app = FastAPI()

# Configuración de CORS para permitir acceso desde cualquier origen (para el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta al build del frontend (vite / ionic)
build_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chat-llm", "dist"))
assets_path = os.path.join(build_path, "assets")

# ---------- Gestión de sesiones en memoria ----------

class SessionData(TypedDict):
    count: int
    questions: Set[str]

sessions: Dict[str, SessionData] = {}
sessions_lock = threading.Lock()

@app.post("/chat")
async def chat(request: Request) -> Dict[str, Any]:
    body = await request.json()
    user_input = body.get("prompt", "").strip()
    session_id = body.get("session_id")

    if not session_id:
        return {"response": "[Falta session_id]"}

    with sessions_lock:
        if session_id not in sessions:
            sessions[session_id] = {"count": 0, "questions": set()}

        user_session = sessions[session_id]

        if user_input in user_session["questions"]:
            return {"response": "[Ya realizaste esta pregunta, intenta otra distinta.]"}

        user_session["questions"].add(user_input)
        user_session["count"] += 1
        count = user_session["count"]  # Guardamos localmente la cuenta para usar afuera del lock

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": user_input,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return {
                "response": "[Error al comunicarse con el modelo]",
                "status_code": response.status_code,
                "detail": response.text,
            }

        resp_json = response.json()
        model_response = resp_json.get("response", "")

        if count >= 10:
            combined_response = (
                f"{model_response}\n\n✅ Has completado las 10 preguntas. "
                "Tu código validador es: bhGp4YDjN9ZhvWmd"
            )
            return {"response": combined_response}

        return {"response": model_response}

    except Exception as e:
        return {"response": f"[Excepción en el backend: {str(e)}]"}

# ---------- Servir frontend estático ----------

app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

@app.get("/")
async def redirect_to_chat():
    return RedirectResponse(url="/chat")

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    return FileResponse(os.path.join(build_path, "index.html"))
