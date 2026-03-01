"""
LLM - Integração com Ollama (Mistral local)
Persona: XAND.AI
"""

import httpx
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "mistral"

async def chat_with_mistral(system_prompt: str, messages: List[Dict]) -> str:
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_predict": 1024,
        }
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]


def build_system_prompt(user_data: dict, session_type: str, session_name: str) -> str:
    logs = user_data.get("logs", [])
    decisions = user_data.get("decisions", [])

    if logs:
        avg_energy = sum(l["energy"] for l in logs) / len(logs)
        avg_focus = sum(l["focus"] for l in logs) / len(logs)
        total_study = sum(l["study_hours"] for l in logs)
    else:
        avg_energy = avg_focus = total_study = 0

    good_decisions = [d for d in decisions if d["result"] == "bom"]
    bad_decisions = [d for d in decisions if d["result"] == "ruim"]
    patterns = identify_patterns(decisions, logs)

    base = f"""Você é XAND.AI — o alter ego digital e coach pessoal do usuário.
Você não é um assistente genérico. Você é uma versão mais objetiva, estratégica e analítica dele mesmo.
Seu nome é XAND.AI. Quando apresentado, diga: "Sou XAND.AI, seu alter ego digital."

PERFIL DO USUÁRIO:
- Atleta de vôlei de areia (campeonato paranaense)
- Estudante: Canguru de Matemática, ENEM, Machine Learning, Programação
- Objetivo: alta performance simultânea em estudo e esporte
- Acorda cedo (4:40-5:00), hábito de 2+ meses
- Pratica calistenia além do vôlei

MÉTRICAS RECENTES ({len(logs)} registros):
- Energia média: {avg_energy:.1f}/10
- Foco médio: {avg_focus:.1f}/10
- Horas de estudo acumuladas: {total_study:.1f}h
- Decisões bem-sucedidas: {len(good_decisions)} de {len(good_decisions)+len(bad_decisions)}

PADRÕES IDENTIFICADOS:
{patterns}

HISTÓRICO RECENTE:"""

    for log in logs[:5]:
        base += f"""
[{log['date']}] Energia:{log['energy']} Foco:{log['focus']} Estudo:{log['study_hours']}h
  ✓ {log['did_well'][:100] if log['did_well'] else 'N/A'}
  ✗ {log['needs_improvement'][:100] if log['needs_improvement'] else 'N/A'}"""

    base += "\n\nDECISÕES RECENTES:"
    for d in decisions[:8]:
        emoji = "✅" if d["result"] == "bom" else "❌"
        base += f"\n{emoji} [{d['date']}|{d['type']}] {d['choice'][:80]}"

    if session_type == "rotina":
        base += """

MODO: ORGANIZADOR DE ROTINA
Como XAND.AI neste modo você:
1. Planeja rotinas detalhadas considerando treino + estudo + recuperação
2. Faz recomendações baseadas nos padrões reais do usuário
3. Alerta quando há risco de procrastinação (baseado no histórico)
4. Lembra que quebra de expectativa → frustração → celular é um padrão recorrente
5. Ajusta planos conforme energia e foco reportados

Seja direto, estratégico e use os dados reais. Nada de conselhos genéricos."""
    else:
        base += f"""

MODO: CHAT — {session_name}
Como XAND.AI responda com objetividade e use o histórico sempre que relevante.
Seja honesto mesmo que a verdade seja difícil de ouvir."""

    base += "\n\nSempre responda em português brasileiro. Seja conciso e direto."
    return base


def identify_patterns(decisions: list, logs: list) -> str:
    patterns = []

    frustration = [d for d in decisions if "frustração" in d.get("reason","").lower() or "expectativa" in d.get("reason","").lower()]
    if frustration:
        patterns.append(f"⚠️  Quebra de expectativa → procrastinação (ocorreu {len(frustration)}x)")

    good_sleep = [d for d in decisions if "sono bom" in d.get("reason","").lower()]
    if good_sleep:
        patterns.append(f"✅ Sono de qualidade → melhor performance (confirmado {len(good_sleep)}x)")

    overperf = [d for d in decisions if "subiu pra cabeça" in d.get("reason","").lower()]
    if overperf:
        patterns.append("⚠️  Sessão de alto desempenho → risco de pausas desordenadas depois")

    if logs:
        high = [l for l in logs if l["focus"] >= 7]
        if high:
            patterns.append(f"✅ {len(high)} dias com foco ≥7/10 registrados")

    return "\n".join(patterns) if patterns else "Poucos dados ainda — continue registrando!"
