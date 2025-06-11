import subprocess
import time
import os
import psutil
import requests
from dotenv import load_dotenv
from typing import Optional, List
from subprocess import Popen  # genérico

load_dotenv(dotenv_path="./.env")

OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "")
OLLAMA_EXECUTABLE: str = os.getenv("OLLAMA_EXECUTABLE", "ollama")  # Ruta completa o fallback
NGROK_PATH: str = os.getenv("NGROK_PATH", "ngrok")  # Ruta completa o fallback
NGROK_DOMAIN: str = os.getenv("NGROK_DOMAIN", "chatllm.ngrok.pro")
BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

if not OLLAMA_MODEL:
    raise ValueError("⚠️ Falta la variable OLLAMA_MODEL en el .env")

def kill_port(port: int) -> None:
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.net_connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"⚠️ Matando proceso en puerto {port}: PID {proc.pid}")
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def launch_process(command: List[str], name: str, capture_output: bool = False) -> Optional[Popen[bytes]]:
    try:
        if capture_output:
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            proc = subprocess.Popen(command)
        print(f"✅ {name} iniciado")
        return proc
    except Exception as e:
        print(f"❌ Error al iniciar {name}: {e}")
        return None

def check_ollama_ready(timeout: int = 15) -> bool:
    print("⏳ Verificando que Ollama esté listo...")
    url = "http://localhost:11434/api/tags"
    for _ in range(timeout):
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                print("✅ Ollama responde correctamente.")
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    print("❌ Ollama no respondió a tiempo.")
    return False

def main() -> None:
    kill_port(11434)
    kill_port(BACKEND_PORT)

    print(f"🚀 Iniciando modelo '{OLLAMA_MODEL}' con Ollama...")
    ollama_proc: Optional[Popen[bytes]] = launch_process([OLLAMA_EXECUTABLE, "run", OLLAMA_MODEL], "Ollama")
    time.sleep(3)

    if not check_ollama_ready():
        if ollama_proc:
            ollama_proc.terminate()
        exit(1)

    print("🚀 Iniciando backend (uvicorn)...")
    uvicorn_proc: Optional[Popen[bytes]] = launch_process([
        "uvicorn", "app:app",
        "--host", BACKEND_HOST,
        "--port", str(BACKEND_PORT)
    ], "Uvicorn")
    time.sleep(3)

    print(f"🚀 Iniciando túnel Ngrok con dominio {NGROK_DOMAIN}...")
    ngrok_proc: Optional[Popen[bytes]] = launch_process([
        NGROK_PATH, "http",
        f"--domain={NGROK_DOMAIN}",
        str(BACKEND_PORT)
    ], "Ngrok", capture_output=True)

    if ngrok_proc is None:
        print("❌ No se pudo iniciar Ngrok, abortando todo...")
        if ollama_proc: ollama_proc.terminate()
        if uvicorn_proc: uvicorn_proc.terminate()
        exit(1)

    time.sleep(5)
    if ngrok_proc.poll() is not None:
        stdout: bytes
        stderr: bytes
        try:
            stdout, stderr = ngrok_proc.communicate(timeout=1)
        except Exception:
            stdout, stderr = b"", b""
        print("❌ Ngrok terminó inesperadamente.")
        if stdout:
            print("stdout:", stdout.decode("utf-8", errors="ignore"))
        if stderr:
            print("stderr:", stderr.decode("utf-8", errors="ignore"))
        if ollama_proc: ollama_proc.terminate()
        if uvicorn_proc: uvicorn_proc.terminate()
        exit(1)

    print("🚀 Todo está corriendo correctamente.")
    print("🌐 Acceso público:", f"https://{NGROK_DOMAIN}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🧹 Terminando procesos...")
        if ollama_proc and ollama_proc.poll() is None:
            ollama_proc.terminate()
        if uvicorn_proc and uvicorn_proc.poll() is None:
            uvicorn_proc.terminate()
        if ngrok_proc and ngrok_proc.poll() is None:
            ngrok_proc.terminate()
        print("✅ Todo cerrado correctamente.")

if __name__ == "__main__":
    main()
