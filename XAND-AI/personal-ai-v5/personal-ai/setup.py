#!/usr/bin/env python3
"""
Script de setup - Personal AI
"""

import subprocess
import sys
import os
from pathlib import Path

def run(cmd):
    print(f"  → {cmd}")
    return subprocess.run(cmd, shell=True).returncode == 0

def check_ollama():
    result = subprocess.run("ollama --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("⚠️  Ollama não encontrado!")
        print("   Instale em: https://ollama.com")
        print("   Depois execute: ollama pull mistral")
        return False
    print("✅ Ollama encontrado")
    result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
    if "mistral" not in result.stdout.lower():
        print("⬇️  Baixando modelo Mistral (~4GB)...")
        run("ollama pull mistral")
    else:
        print("✅ Mistral disponível")
    return True

def main():
    print("=" * 50)
    print("  Personal AI - Setup")
    print("=" * 50)

    # Verificar Python
    v = sys.version_info
    print(f"✅ Python {v.major}.{v.minor}")

    # Ollama
    check_ollama()

    # Criar diretórios
    for d in ["data", "voices/samples"]:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("✅ Diretórios criados")

    # Instalar dependências
    print("\n📦 Instalando dependências...")
    req = Path(__file__).parent / "backend" / "requirements.txt"
    run(f"{sys.executable} -m pip install -r {req}")

    print("\n" + "=" * 50)
    print("✅ Setup concluído!")
    print("\nPara iniciar:")
    print("  python start.py")
    print("=" * 50)

if __name__ == "__main__":
    main()
