#!/usr/bin/env python3
"""
Inicia o Personal AI
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def main():
    print("⚡ Iniciando Personal AI...")

    backend_dir = Path(__file__).parent / "backend"

    # Check if Ollama is running
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        print("✅ Ollama já está rodando")
    except:
        print("⚠️  Ollama não está rodando!")
        print("   Abra outro terminal e execute: ollama serve")
        print("   Depois inicie novamente: python start.py")
        input("   Pressione Enter quando o Ollama estiver rodando...")

    # Start FastAPI
    print("🚀 Iniciando servidor...")
    os.chdir(backend_dir)

    # Open browser after short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
        print("🌐 Abrindo navegador em http://localhost:8000")

    import threading
    t = threading.Thread(target=open_browser)
    t.daemon = True
    t.start()

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Personal AI encerrado.")

if __name__ == "__main__":
    main()
