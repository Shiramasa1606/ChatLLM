from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Habilita CORS para que tu frontend pueda acceder al backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O especifica ["http://localhost:3000"] por seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    user_input = body.get("prompt", "")

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "java-herencia-modelo",  # Asegúrate que coincida con tu modelo
        "prompt": user_input,
        "stream": False
    })

    if response.status_code == 200:
        return {"response": response.json().get("response")}
    else:
        return {"response": "[Error al comunicarse con el modelo]"}

